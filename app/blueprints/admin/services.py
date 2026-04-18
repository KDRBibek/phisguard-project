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

def compute_advanced_metrics():
    """
    Returns a dictionary with advanced analytics for the admin dashboard:
    - click-through rate
    - report rate
    - false positive/true positive rates
    - average time to click/report
    - accuracy by user/campaign/difficulty/category
    """
    from app.models import Email, UserAction
    from sqlalchemy import func
    metrics = {}

    # All actions
    actions = UserAction.query.all()
    emails = {e.id: e for e in Email.query.all()}

    # Click-through rate (CTR): clicks / total emails
    total_emails = len(emails)
    total_clicks = sum(1 for a in actions if a.action == 'clicked')
    metrics['click_through_rate'] = total_clicks / total_emails if total_emails else None

    # Report rate: reports / total emails
    total_reports = sum(1 for a in actions if a.action == 'reported')
    metrics['report_rate'] = total_reports / total_emails if total_emails else None

    # True/False positive rates
    tp = fp = tn = fn = 0
    for a in actions:
        email = emails.get(a.email_id)
        if not email:
            continue
        if a.action == 'reported':
            if email.is_phishing:
                tp += 1  # True positive: reported phishing
            else:
                fp += 1  # False positive: reported legit
        elif a.action == 'clicked':
            if email.is_phishing:
                fn += 1  # False negative: clicked phishing
            else:
                tn += 1  # True negative: clicked legit
    metrics['true_positive_rate'] = tp / (tp + fn) if (tp + fn) else None
    metrics['false_positive_rate'] = fp / (fp + tn) if (fp + tn) else None
    metrics['true_positives'] = tp
    metrics['false_positives'] = fp
    metrics['true_negatives'] = tn
    metrics['false_negatives'] = fn

    # Average time to click/report
    click_times = [a.time_to_action_seconds for a in actions if a.action == 'clicked' and a.time_to_action_seconds is not None]
    report_times = [a.time_to_action_seconds for a in actions if a.action == 'reported' and a.time_to_action_seconds is not None]
    metrics['avg_time_to_click'] = sum(click_times) / len(click_times) if click_times else None
    metrics['avg_time_to_report'] = sum(report_times) / len(report_times) if report_times else None

    # Accuracy by user
    user_stats = {}
    for a in actions:
        email = emails.get(a.email_id)
        if not email:
            continue
        user_id = a.user_id or 'unknown'
        stat = user_stats.setdefault(user_id, {'correct': 0, 'total': 0})
        if a.action == 'reported':
            stat['total'] += 1
            if email.is_phishing:
                stat['correct'] += 1
        elif a.action == 'clicked':
            stat['total'] += 1
            if not email.is_phishing:
                stat['correct'] += 1
    metrics['accuracy_by_user'] = {uid: (s['correct'] / s['total'] if s['total'] else None) for uid, s in user_stats.items()}

    # Accuracy by campaign
    campaign_stats = {}
    for a in actions:
        email = emails.get(a.email_id)
        if not email or not email.campaign_id:
            continue
        cid = email.campaign_id
        stat = campaign_stats.setdefault(cid, {'correct': 0, 'total': 0})
        if a.action == 'reported':
            stat['total'] += 1
            if email.is_phishing:
                stat['correct'] += 1
        elif a.action == 'clicked':
            stat['total'] += 1
            if not email.is_phishing:
                stat['correct'] += 1
    metrics['accuracy_by_campaign'] = {cid: (s['correct'] / s['total'] if s['total'] else None) for cid, s in campaign_stats.items()}

    # Accuracy by difficulty
    diff_stats = {}
    for a in actions:
        email = emails.get(a.email_id)
        if not email:
            continue
        diff = email.difficulty or 'unknown'
        stat = diff_stats.setdefault(diff, {'correct': 0, 'total': 0})
        if a.action == 'reported':
            stat['total'] += 1
            if email.is_phishing:
                stat['correct'] += 1
        elif a.action == 'clicked':
            stat['total'] += 1
            if not email.is_phishing:
                stat['correct'] += 1
    metrics['accuracy_by_difficulty'] = {d: (s['correct'] / s['total'] if s['total'] else None) for d, s in diff_stats.items()}

    # Accuracy by scenario category (if available)
    # If Email model has a 'category' field, use it; otherwise, skip or set to None
    cat_stats = {}
    for a in actions:
        email = emails.get(a.email_id)
        if not email or not hasattr(email, 'category'):
            continue
        cat = getattr(email, 'category', 'unknown') or 'unknown'
        stat = cat_stats.setdefault(cat, {'correct': 0, 'total': 0})
        if a.action == 'reported':
            stat['total'] += 1
            if email.is_phishing:
                stat['correct'] += 1
        elif a.action == 'clicked':
            stat['total'] += 1
            if not email.is_phishing:
                stat['correct'] += 1
    metrics['accuracy_by_category'] = {c: (s['correct'] / s['total'] if s['total'] else None) for c, s in cat_stats.items()}

    return metrics
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
