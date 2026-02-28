from flask import Blueprint, jsonify, request
from auth_store import extract_token, get_user_id_from_token
from helpers import load_sms_messages, compute_sms_time_to_action_seconds
from models import db, SmsAction

bp = Blueprint('sms', __name__)


@bp.route('/api/sms')
def api_sms():
    messages = load_sms_messages()
    return jsonify(messages)


def _get_message_or_404(message_id):
    messages = load_sms_messages()
    message = next((m for m in messages if m['id'] == message_id), None)
    return message


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
    correct = not message['is_phishing']
    result = {
        'correct': correct,
        'message': 'Correct. This SMS appears legitimate.' if correct else 'Incorrect. This was a phishing SMS.',
        'tip': message.get('feedback') or '',
        'time_to_action_seconds': time_to_action_seconds
    }
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
    correct = message['is_phishing']
    result = {
        'correct': correct,
        'message': 'Correct. You reported a phishing SMS.' if correct else 'Incorrect. This SMS appears legitimate.',
        'tip': message.get('feedback') or '',
        'time_to_action_seconds': time_to_action_seconds
    }
    return jsonify(result)
