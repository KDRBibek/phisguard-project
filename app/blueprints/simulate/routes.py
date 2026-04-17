from flask import Blueprint, jsonify, request, render_template, redirect
from urllib.parse import quote
from app.extensions import db
from app.models import Email, UserAction, SmsAction, DetectionResult
from app.services.auth_store import extract_token, get_user_id_from_token
from app.services.detector import analyze_email, analyze_sms
from app.blueprints.simulate.services import (
    update_campaign_target,
    compute_email_time_to_action_seconds,
    compute_sms_time_to_action_seconds,
    load_sms_messages,
    generate_dummy_emails,
)
import json

bp = Blueprint('simulate', __name__)


def _email_result_payload(email, action, time_to_action_seconds):
    if action == 'click':
        if email.is_phishing:
            return {
                'correct': False,
                'message': 'You clicked a phishing link. In real life this could steal credentials or install malware.',
                'tip': email.feedback or 'Check the sender and hover over links before clicking.',
                'time_to_action_seconds': time_to_action_seconds,
            }
        return {
            'correct': True,
            'message': 'You clicked a legitimate link. Good job staying calm and checking context.',
            'tip': email.feedback or 'Still verify domains and requests even if it looks normal.',
            'time_to_action_seconds': time_to_action_seconds,
        }

    if email.is_phishing:
        return {
            'correct': True,
            'message': 'Correct! You reported a phishing email.',
            'tip': email.feedback or 'Reporting suspicious emails helps protect others.',
            'time_to_action_seconds': time_to_action_seconds,
        }
    return {
        'correct': False,
        'message': 'This email was legitimate, so reporting it was not needed.',
        'tip': 'Check for urgency, mismatched domains, and requests for credentials before reporting.',
        'time_to_action_seconds': time_to_action_seconds,
    }


def _sms_result_payload(message, action, time_to_action_seconds):
    if action == 'click':
        correct = not message['is_phishing']
        return {
            'correct': correct,
            'message': 'Correct. This SMS appears legitimate.' if correct else 'Incorrect. This was a phishing SMS.',
            'tip': message.get('feedback') or '',
            'time_to_action_seconds': time_to_action_seconds,
        }

    correct = message['is_phishing']
    return {
        'correct': correct,
        'message': 'Correct. You reported a phishing SMS.' if correct else 'Incorrect. This SMS appears legitimate.',
        'tip': message.get('feedback') or '',
        'time_to_action_seconds': time_to_action_seconds,
    }


def _feedback_entry_from_email_action(action_row):
    email = db.session.get(Email, action_row.email_id)
    if not email:
        return None
    action_for_payload = 'click' if action_row.action == 'clicked' else 'report'
    payload = _email_result_payload(email, action_for_payload, action_row.time_to_action_seconds)
    return {
        'item_id': email.id,
        'channel': 'email',
        'subject': email.subject,
        'sender': email.sender,
        'action': action_row.action,
        'correct': payload['correct'],
        'message': payload['message'],
        'tip': payload.get('tip'),
        'time_to_action_seconds': action_row.time_to_action_seconds,
        'created_at': action_row.created_at.isoformat() if action_row.created_at else None,
    }


def _feedback_entry_from_sms_action(action_row):
    message = _get_message_or_404(action_row.message_id)
    if not message:
        return None
    action_for_payload = 'click' if action_row.action == 'clicked' else 'report'
    payload = _sms_result_payload(message, action_for_payload, action_row.time_to_action_seconds)
    return {
        'item_id': message['id'],
        'channel': 'sms',
        'subject': message.get('subject') or f"SMS from {message.get('sender', '')}",
        'sender': message.get('sender') or '',
        'action': action_row.action,
        'correct': payload['correct'],
        'message': payload['message'],
        'tip': payload.get('tip'),
        'time_to_action_seconds': action_row.time_to_action_seconds,
        'created_at': action_row.created_at.isoformat() if action_row.created_at else None,
    }


def _load_feedback_for_user(user_id):
    if not user_id:
        return []

    items = []

    email_actions = (
        UserAction.query.filter_by(user_id=user_id)
        .filter(UserAction.action.in_(['clicked', 'reported']))
        .order_by(UserAction.created_at.desc(), UserAction.id.desc())
        .all()
    )
    for row in email_actions:
        entry = _feedback_entry_from_email_action(row)
        if entry:
            items.append(entry)

    sms_actions = (
        SmsAction.query.filter_by(user_id=user_id)
        .filter(SmsAction.action.in_(['clicked', 'reported']))
        .order_by(SmsAction.created_at.desc(), SmsAction.id.desc())
        .all()
    )
    for row in sms_actions:
        entry = _feedback_entry_from_sms_action(row)
        if entry:
            items.append(entry)

    items.sort(key=lambda item: item.get('created_at') or '', reverse=True)
    return items


@bp.route('/l/<int:email_id>', methods=['GET'])
def link_redirect(email_id):
    """Safe tracking link for outbound simulation emails.

    Records a click (without requiring an auth token) and redirects to an
    in-app safe page so recipients never go to an external URL.
    """

    email = db.get_or_404(Email, email_id)
    db.session.add(UserAction(email_id=email_id, action='clicked', user_id=None))
    update_campaign_target(email_id, 'clicked')
    db.session.commit()

    if email.is_phishing:
        return redirect('/phished')

    safe_url = '/safe-link'
    if email.link_url:
        safe_url = f"/safe-link?channel=Email&url={quote(str(email.link_url), safe='')}"
    return redirect(safe_url)


@bp.route('/api/generate_emails', methods=['POST'])
def api_generate_emails():
    data = request.get_json() or {}
    try:
        count = int(data.get('count', 10))
    except Exception:
        count = 10
    created = generate_dummy_emails(count)
    return jsonify([e.to_dict() for e in created])


@bp.route('/api/awareness')
def api_awareness():
    token = extract_token(request)
    user_id = get_user_id_from_token(token)
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401

    actions = UserAction.query.filter_by(user_id=user_id).filter(UserAction.action.in_(['clicked', 'reported'])).all()
    total = 0
    correct = 0
    for a in actions:
        email = db.session.get(Email, a.email_id)
        if not email:
            continue
        if a.action == 'reported':
            total += 1
            if email.is_phishing:
                correct += 1
        elif a.action == 'clicked':
            total += 1
            if not email.is_phishing:
                correct += 1

    pct = (correct / total * 100) if total > 0 else None
    return jsonify({'total_checked': total, 'correct': correct, 'accuracy_percent': pct})


@bp.route('/api/feedback', methods=['GET'])
def api_feedback():
    token = extract_token(request)
    user_id = get_user_id_from_token(token)
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401

    return jsonify(_load_feedback_for_user(user_id))


@bp.route('/api/feedback/reset', methods=['POST'])
def api_feedback_reset():
    token = extract_token(request) or (request.get_json() or {}).get('token')
    user_id = get_user_id_from_token(token)
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401

    UserAction.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    SmsAction.query.filter_by(user_id=user_id).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/api/emails')
def api_emails():
    emails = Email.query.order_by(Email.id).all()
    return jsonify([e.to_dict() for e in emails])


@bp.route('/api/emails/<int:email_id>')
def api_email(email_id):
    email = db.get_or_404(Email, email_id)
    return jsonify(email.to_dict())


@bp.route('/api/emails/<int:email_id>/open', methods=['POST'])
def api_open(email_id):
    email = db.get_or_404(Email, email_id)
    token = extract_token(request) or (request.get_json() or {}).get('token')
    user_id = get_user_id_from_token(token)
    db.session.add(UserAction(email_id=email_id, action='opened', user_id=user_id))
    update_campaign_target(email_id, 'opened')
    db.session.commit()
    return jsonify(email.to_dict())


@bp.route('/api/emails/<int:email_id>/click', methods=['POST'])
def api_click(email_id):
    email = db.get_or_404(Email, email_id)
    token = extract_token(request) or (request.get_json() or {}).get('token')
    user_id = get_user_id_from_token(token)
    time_to_action_seconds = compute_email_time_to_action_seconds(email_id, user_id)
    db.session.add(UserAction(email_id=email_id, action='clicked', user_id=user_id, time_to_action_seconds=time_to_action_seconds))
    update_campaign_target(email_id, 'clicked')
    db.session.commit()

    return jsonify(_email_result_payload(email, 'click', time_to_action_seconds))


@bp.route('/api/emails/<int:email_id>/report', methods=['POST'])
def api_report(email_id):
    email = db.get_or_404(Email, email_id)
    token = extract_token(request) or (request.get_json() or {}).get('token')
    user_id = get_user_id_from_token(token)
    time_to_action_seconds = compute_email_time_to_action_seconds(email_id, user_id)
    db.session.add(UserAction(email_id=email_id, action='reported', user_id=user_id, time_to_action_seconds=time_to_action_seconds))
    update_campaign_target(email_id, 'reported')
    db.session.commit()

    return jsonify(_email_result_payload(email, 'report', time_to_action_seconds))


@bp.route('/api/sms')
def api_sms():
    messages = load_sms_messages()
    return jsonify(messages)


def _get_message_or_404(message_id):
    messages = load_sms_messages()
    message = next((m for m in messages if m['id'] == message_id), None)
    return message


def _save_detection_result(channel, payload, result, user_id):
    record = DetectionResult(
        channel=channel,
        message_ref_id=payload.get('message_ref_id'),
        sender=(payload.get('sender') or '')[:255],
        subject=(payload.get('subject') or '')[:255],
        body=payload.get('body') or '',
        link_url=(payload.get('link_url') or '')[:500],
        risk_score=int(result.get('risk_score', 0)),
        verdict=result.get('verdict') or 'safe',
        reasons=json.dumps(result.get('reasons') or []),
        user_id=user_id,
    )
    db.session.add(record)
    db.session.commit()
    return record


@bp.route('/api/detector/analyze-email', methods=['POST'])
def api_detector_analyze_email():
    data = request.get_json() or {}
    token = extract_token(request) or data.get('token')
    user_id = get_user_id_from_token(token)

    email_id = data.get('email_id')
    payload = {
        'sender': data.get('sender') or '',
        'subject': data.get('subject') or '',
        'body': data.get('body') or '',
        'link_url': data.get('link_url') or '',
        'message_ref_id': None,
    }

    if email_id is not None:
        try:
            email_id = int(email_id)
        except (TypeError, ValueError):
            return jsonify({'error': 'invalid email_id'}), 400
        email = db.session.get(Email, email_id)
        if not email:
            return jsonify({'error': 'email not found'}), 404
        payload = {
            'sender': email.sender,
            'subject': email.subject,
            'body': email.body,
            'link_url': email.link_url,
            'message_ref_id': email.id,
        }
    elif not payload['body']:
        return jsonify({'error': 'missing email content'}), 400

    result = analyze_email(
        sender=payload['sender'],
        subject=payload['subject'],
        body=payload['body'],
        link_url=payload['link_url'],
    )
    saved = _save_detection_result('email', payload, result, user_id)
    return jsonify({
        **result,
        'analysis_id': saved.id,
        'message_ref_id': payload.get('message_ref_id'),
    })


@bp.route('/api/detector/analyze-sms', methods=['POST'])
def api_detector_analyze_sms():
    data = request.get_json() or {}
    token = extract_token(request) or data.get('token')
    user_id = get_user_id_from_token(token)

    message_id = data.get('message_id')
    payload = {
        'sender': data.get('sender') or '',
        'subject': 'SMS',
        'body': data.get('body') or '',
        'link_url': data.get('link_url') or '',
        'message_ref_id': None,
    }

    if message_id is not None:
        try:
            message_id = int(message_id)
        except (TypeError, ValueError):
            return jsonify({'error': 'invalid message_id'}), 400
        message = _get_message_or_404(message_id)
        if not message:
            return jsonify({'error': 'sms not found'}), 404
        payload = {
            'sender': message.get('sender') or '',
            'subject': 'SMS',
            'body': message.get('body') or '',
            'link_url': message.get('link_url') or '',
            'message_ref_id': message.get('id'),
        }
    elif not payload['body']:
        return jsonify({'error': 'missing sms content'}), 400

    result = analyze_sms(
        sender=payload['sender'],
        body=payload['body'],
        link_url=payload['link_url'],
    )
    saved = _save_detection_result('sms', payload, result, user_id)
    return jsonify({
        **result,
        'analysis_id': saved.id,
        'message_ref_id': payload.get('message_ref_id'),
    })


@bp.route('/api/sms/<int:message_id>/open', methods=['POST'])
def api_sms_open(message_id):
    token = extract_token(request) or (request.get_json() or {}).get('token')
    user_id = get_user_id_from_token(token)
    message = _get_message_or_404(message_id)
    if not message:
        return jsonify({'error': 'sms not found'}), 404
    db.session.add(SmsAction(message_id=message_id, action='opened', user_id=user_id))
    db.session.commit()
    return jsonify(message)


@bp.route('/api/sms/<int:message_id>/click', methods=['POST'])
def api_sms_click(message_id):
    token = extract_token(request) or (request.get_json() or {}).get('token')
    user_id = get_user_id_from_token(token)
    message = _get_message_or_404(message_id)
    if not message:
        return jsonify({'error': 'sms not found'}), 404
    time_to_action_seconds = compute_sms_time_to_action_seconds(message_id, user_id)
    db.session.add(SmsAction(message_id=message_id, action='clicked', user_id=user_id, time_to_action_seconds=time_to_action_seconds))
    db.session.commit()
    result = _sms_result_payload(message, 'click', time_to_action_seconds)
    return jsonify(result)


@bp.route('/api/sms/<int:message_id>/report', methods=['POST'])
def api_sms_report(message_id):
    token = extract_token(request) or (request.get_json() or {}).get('token')
    user_id = get_user_id_from_token(token)
    message = _get_message_or_404(message_id)
    if not message:
        return jsonify({'error': 'sms not found'}), 404
    time_to_action_seconds = compute_sms_time_to_action_seconds(message_id, user_id)
    db.session.add(SmsAction(message_id=message_id, action='reported', user_id=user_id, time_to_action_seconds=time_to_action_seconds))
    db.session.commit()
    result = _sms_result_payload(message, 'report', time_to_action_seconds)
    return jsonify(result)


@bp.route('/inbox')
def inbox():
    emails = Email.query.order_by(Email.id).all()
    return render_template("inbox.html", emails=emails)


@bp.route('/email/<int:email_id>')
def view_email(email_id):
    email = db.get_or_404(Email, email_id)
    db.session.add(UserAction(email_id=email_id, action="opened"))
    update_campaign_target(email_id, 'opened')
    db.session.commit()
    return render_template("email.html", email=email)


@bp.route("/click/<int:email_id>")
def click_email(email_id):
    email = db.get_or_404(Email, email_id)
    db.session.add(UserAction(email_id=email_id, action="clicked"))
    update_campaign_target(email_id, 'clicked')
    db.session.commit()

    if email.is_phishing:
        return render_template(
            "feedback.html",
            correct=False,
            message="You clicked a phishing link. In real life this could steal credentials or install malware.",
            tip=email.feedback or "Check the sender and hover over links before clicking."
        )
    return render_template(
        "feedback.html",
        correct=True,
        message="You clicked a legitimate link. Good job staying calm and checking context.",
        tip=email.feedback or "Still verify domains and requests even if it looks normal."
    )


@bp.route("/report/<int:email_id>")
def report_email(email_id):
    email = db.get_or_404(Email, email_id)
    db.session.add(UserAction(email_id=email_id, action="reported"))
    update_campaign_target(email_id, 'reported')
    db.session.commit()

    if email.is_phishing:
        return render_template(
            "feedback.html",
            correct=True,
            message="Correct! You reported a phishing email.",
            tip=email.feedback or "Reporting suspicious emails helps protect others."
        )
    return render_template(
        "feedback.html",
        correct=False,
        message="This email was legitimate, so reporting it was not needed.",
        tip="Check for urgency, mismatched domains, and requests for credentials before reporting."
    )
