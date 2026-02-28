from flask import Blueprint, jsonify, request, render_template
from auth_store import extract_token, get_user_id_from_token
from helpers import (
    update_campaign_target,
    compute_email_time_to_action_seconds,
    generate_dummy_emails,
    seed_emails,
)
from models import db, Email, UserAction

bp = Blueprint('emails', __name__)


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
    actions = UserAction.query.filter(UserAction.action.in_(['clicked', 'reported'])).all()
    total = 0
    correct = 0
    for a in actions:
        email = Email.query.get(a.email_id)
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


@bp.route('/api/emails')
def api_emails():
    emails = Email.query.order_by(Email.id).all()
    return jsonify([e.to_dict() for e in emails])


@bp.route('/api/emails/<int:email_id>')
def api_email(email_id):
    email = Email.query.get_or_404(email_id)
    return jsonify(email.to_dict())


@bp.route('/api/emails/<int:email_id>/open', methods=['POST'])
def api_open(email_id):
    email = Email.query.get_or_404(email_id)
    token = extract_token(request) or (request.get_json() or {}).get('token')
    user_id = get_user_id_from_token(token)
    db.session.add(UserAction(email_id=email_id, action='opened', user_id=user_id))
    update_campaign_target(email_id, 'opened')
    db.session.commit()
    return jsonify(email.to_dict())


@bp.route('/api/emails/<int:email_id>/click', methods=['POST'])
def api_click(email_id):
    email = Email.query.get_or_404(email_id)
    token = extract_token(request) or (request.get_json() or {}).get('token')
    user_id = get_user_id_from_token(token)
    time_to_action_seconds = compute_email_time_to_action_seconds(email_id, user_id)
    db.session.add(UserAction(email_id=email_id, action='clicked', user_id=user_id, time_to_action_seconds=time_to_action_seconds))
    update_campaign_target(email_id, 'clicked')
    db.session.commit()

    if email.is_phishing:
        return jsonify({
            'correct': False,
            'message': 'You clicked a phishing link. In real life this could steal credentials or install malware.',
            'tip': email.feedback or 'Check the sender and hover over links before clicking.',
            'time_to_action_seconds': time_to_action_seconds
        })
    return jsonify({
        'correct': True,
        'message': 'You clicked a legitimate link. Good job staying calm and checking context.',
        'tip': email.feedback or 'Still verify domains and requests even if it looks normal.',
        'time_to_action_seconds': time_to_action_seconds
    })


@bp.route('/api/emails/<int:email_id>/report', methods=['POST'])
def api_report(email_id):
    email = Email.query.get_or_404(email_id)
    token = extract_token(request) or (request.get_json() or {}).get('token')
    user_id = get_user_id_from_token(token)
    time_to_action_seconds = compute_email_time_to_action_seconds(email_id, user_id)
    db.session.add(UserAction(email_id=email_id, action='reported', user_id=user_id, time_to_action_seconds=time_to_action_seconds))
    update_campaign_target(email_id, 'reported')
    db.session.commit()

    if email.is_phishing:
        return jsonify({
            'correct': True,
            'message': 'Correct! You reported a phishing email.',
            'tip': email.feedback or 'Reporting suspicious emails helps protect others.',
            'time_to_action_seconds': time_to_action_seconds
        })
    return jsonify({
        'correct': False,
        'message': 'This email was legitimate, so reporting it was not needed.',
        'tip': 'Check for urgency, mismatched domains, and requests for credentials before reporting.',
        'time_to_action_seconds': time_to_action_seconds
    })


@bp.route('/click/<int:email_id>')
def click_email(email_id):
    email = Email.query.get_or_404(email_id)
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


@bp.route('/report/<int:email_id>')
def report_email(email_id):
    email = Email.query.get_or_404(email_id)
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


@bp.route('/email/<int:email_id>')
def view_email(email_id):
    email = Email.query.get_or_404(email_id)
    db.session.add(UserAction(email_id=email_id, action="opened"))
    update_campaign_target(email_id, 'opened')
    db.session.commit()
    return render_template("email.html", email=email)
