from sqlalchemy import func
from app.extensions import db
from app.models import Email, UserAction, SmsAction
from app.blueprints.simulate.services import load_sms_messages


def compute_email_metrics():
    q = db.session.query(
        UserAction.email_id,
        UserAction.action,
        func.count(UserAction.id).label('cnt')
    ).group_by(UserAction.email_id, UserAction.action).all()

    metrics = {}
    for email_id, action, cnt in q:
        m = metrics.setdefault(email_id, {'email_id': email_id, 'clicks': 0, 'reports': 0, 'opens': 0})
        if action == 'clicked':
            m['clicks'] = cnt
        elif action == 'reported':
            m['reports'] = cnt
        elif action == 'opened':
            m['opens'] = cnt

    return list(metrics.values())


def compute_sms_metrics():
    q = db.session.query(
        SmsAction.message_id,
        SmsAction.action,
        func.count(SmsAction.id).label('cnt')
    ).group_by(SmsAction.message_id, SmsAction.action).all()

    metrics = {}
    for message_id, action, cnt in q:
        m = metrics.setdefault(message_id, {'message_id': message_id, 'clicks': 0, 'reports': 0, 'opens': 0})
        if action == 'clicked':
            m['clicks'] = cnt
        elif action == 'reported':
            m['reports'] = cnt
        elif action == 'opened':
            m['opens'] = cnt

    return list(metrics.values())


def compute_user_reports():
    q = db.session.query(UserAction.user_id, UserAction.action, func.count(UserAction.id).label('cnt')).filter(UserAction.action.in_(['clicked','reported'])).group_by(UserAction.user_id, UserAction.action).all()
    reports = {}
    for user_id, action, cnt in q:
        u = reports.setdefault(user_id or 'unknown', {'user_id': user_id or 'unknown', 'checked': 0, 'correct': 0})
        if action in ('reported', 'clicked'):
            u['checked'] += cnt

    for user_key in reports.keys():
        uid = None if user_key == 'unknown' else user_key
        user_actions = UserAction.query.filter_by(user_id=uid).all() if uid else UserAction.query.filter(UserAction.user_id.is_(None)).all()
        correct = 0
        total = 0
        for a in user_actions:
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
        reports[user_key]['checked'] = total
        reports[user_key]['correct'] = correct
        reports[user_key]['accuracy_percent'] = (correct / total * 100) if total > 0 else None

    return list(reports.values())


def compute_sms_user_reports():
    q = db.session.query(SmsAction.user_id, SmsAction.action, func.count(SmsAction.id).label('cnt')).filter(SmsAction.action.in_(['clicked','reported'])).group_by(SmsAction.user_id, SmsAction.action).all()
    reports = {}
    for user_id, action, cnt in q:
        u = reports.setdefault(user_id or 'unknown', {'user_id': user_id or 'unknown', 'checked': 0, 'correct': 0})
        if action in ('reported', 'clicked'):
            u['checked'] += cnt

    messages = load_sms_messages()
    message_map = {m['id']: m for m in messages}

    for user_key in reports.keys():
        uid = None if user_key == 'unknown' else user_key
        user_actions = SmsAction.query.filter_by(user_id=uid).all() if uid else SmsAction.query.filter(SmsAction.user_id.is_(None)).all()
        correct = 0
        total = 0
        for a in user_actions:
            message = message_map.get(a.message_id)
            if not message:
                continue
            if a.action == 'reported':
                total += 1
                if message['is_phishing']:
                    correct += 1
            elif a.action == 'clicked':
                total += 1
                if not message['is_phishing']:
                    correct += 1
        reports[user_key]['checked'] = total
        reports[user_key]['correct'] = correct
        reports[user_key]['accuracy_percent'] = (correct / total * 100) if total > 0 else None

    return list(reports.values())
