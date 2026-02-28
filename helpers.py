from app.blueprints.simulate.services import *
import csv
import os
import random
from datetime import datetime
from sqlalchemy import text
from models import db, Email, UserAction, Template, Target, CampaignTarget, SmsAction


def render_template_text(text_value, target):
    if not text_value:
        return text_value
    replacements = {
        '{{name}}': target.name if target else '',
        '{{email}}': target.email if target else '',
        '{{department}}': target.department if target and target.department else '',
    }
    for key, value in replacements.items():
        text_value = text_value.replace(key, value)
    return text_value


def infer_difficulty(subject, body, is_phishing):
    text = f"{subject or ''} {body or ''}".strip()
    length = len(text)
    if is_phishing and length < 140:
        return "hard"
    if length > 300:
        return "easy"
    return "medium"


def update_campaign_target(email_id, action):
    ct = CampaignTarget.query.filter_by(email_id=email_id).first()
    if not ct:
        return
    ct.status = action
    ct.last_action_at = datetime.utcnow()


def compute_email_time_to_action_seconds(email_id, user_id):
    if not user_id:
        return None
    last_open = UserAction.query.filter_by(email_id=email_id, user_id=user_id, action='opened').order_by(UserAction.created_at.desc()).first()
    if not last_open or not last_open.created_at:
        return None
    return max(0, (datetime.utcnow() - last_open.created_at).total_seconds())


def compute_sms_time_to_action_seconds(message_id, user_id):
    if not user_id:
        return None
    last_open = SmsAction.query.filter_by(message_id=message_id, user_id=user_id, action='opened').order_by(SmsAction.created_at.desc()).first()
    if not last_open or not last_open.created_at:
        return None
    return max(0, (datetime.utcnow() - last_open.created_at).total_seconds())


def load_sms_messages():
    dataset_path = os.path.join(os.path.dirname(__file__), 'data', 'cleaned_sms.csv')
    messages = []
    if not os.path.exists(dataset_path):
        return messages

    rows = []
    try:
        with open(dataset_path, 'r', encoding='utf-8', errors='replace', newline='') as f:
            csv.field_size_limit(2 ** 20)
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('body') and row.get('label'):
                    rows.append(row)
    except Exception:
        rows = []

    sampled = rows[:7] if len(rows) >= 7 else rows

    for idx, r in enumerate(sampled, start=1):
        is_phishing = str(r.get('label', '')).strip().lower() == 'phishing'
        feedback = (
            "Phishing signs: urgency, suspicious links, or requests for credentials. Verify via official channels."
            if is_phishing
            else "Legitimate-looking message, but still verify the sender and avoid sharing sensitive data."
        )
        body = r.get('body') or ''
        difficulty = infer_difficulty('SMS', body, is_phishing)
        messages.append({
            'id': idx,
            'sender': r.get('sender') or 'SMS Sender',
            'body': body,
            'is_phishing': is_phishing,
            'link_text': 'Open link',
            'link_url': '#',
            'feedback': feedback,
            'difficulty': difficulty,
        })

    return messages


def ensure_user_action_user_id_column():
    try:
        rows = db.session.execute(text("PRAGMA table_info(user_action)")).fetchall()
        cols = {r[1] for r in rows}
        if 'user_id' not in cols:
            db.session.execute(text("ALTER TABLE user_action ADD COLUMN user_id VARCHAR(100)"))
            db.session.commit()
    except Exception:
        db.session.rollback()


def ensure_user_action_time_to_action_column():
    try:
        rows = db.session.execute(text("PRAGMA table_info(user_action)")).fetchall()
        cols = {r[1] for r in rows}
        if 'time_to_action_seconds' not in cols:
            db.session.execute(text("ALTER TABLE user_action ADD COLUMN time_to_action_seconds FLOAT"))
            db.session.commit()
    except Exception:
        db.session.rollback()


def ensure_email_campaign_columns():
    try:
        rows = db.session.execute(text("PRAGMA table_info(email)")).fetchall()
        cols = {r[1] for r in rows}
        if 'campaign_id' not in cols:
            db.session.execute(text("ALTER TABLE email ADD COLUMN campaign_id INTEGER"))
        if 'target_id' not in cols:
            db.session.execute(text("ALTER TABLE email ADD COLUMN target_id INTEGER"))
        db.session.commit()
    except Exception:
        db.session.rollback()


def ensure_email_difficulty_column():
    try:
        rows = db.session.execute(text("PRAGMA table_info(email)")).fetchall()
        cols = {r[1] for r in rows}
        if 'difficulty' not in cols:
            db.session.execute(text("ALTER TABLE email ADD COLUMN difficulty VARCHAR(20)"))
        db.session.commit()
    except Exception:
        db.session.rollback()


def ensure_template_difficulty_column():
    try:
        rows = db.session.execute(text("PRAGMA table_info(template)")).fetchall()
        cols = {r[1] for r in rows}
        if 'difficulty' not in cols:
            db.session.execute(text("ALTER TABLE template ADD COLUMN difficulty VARCHAR(20)"))
        db.session.commit()
    except Exception:
        db.session.rollback()


def seed_emails():
    UserAction.query.delete()
    try:
        CampaignTarget.query.delete()
    except Exception:
        pass
    Email.query.delete()

    dataset_path = os.path.join(os.path.dirname(__file__), 'data', 'cleaned_emails.csv')
    if os.path.exists(dataset_path):
        rows = []
        try:
            with open(dataset_path, 'r', encoding='utf-8', errors='replace', newline='') as f:
                csv.field_size_limit(2 ** 20)
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('body') and row.get('label'):
                        rows.append(row)
        except Exception:
            rows = []

        if len(rows) >= 7:
            sampled = rows[:7]
            emails = []
            for r in sampled:
                is_phishing = str(r.get('label', '')).strip().lower() == 'phishing'
                feedback = (
                    "Phishing signs: urgency, suspicious links, or requests for credentials. Verify via official channels."
                    if is_phishing
                    else "Legitimate-looking message, but still verify the sender and access services through official sites."
                )
                emails.append(Email(
                    sender=r.get('sender') or 'Dataset Source',
                    subject=r.get('subject') or 'Message update',
                    body=r.get('body') or '',
                    is_phishing=is_phishing,
                    difficulty=infer_difficulty(r.get('subject'), r.get('body'), is_phishing),
                    link_text='Open link',
                    link_url='#',
                    feedback=feedback
                ))
            db.session.add_all(emails)
            db.session.commit()
            return

    emails = [
        Email(
            sender="University IT Support",
            subject="Password Expiry Notice",
            body="Your password will expire in 2 days. Please update it using the official portal.",
            is_phishing=False,
            difficulty=infer_difficulty("Password Expiry Notice", "Your password will expire in 2 days. Please update it using the official portal.", False),
            link_text="Go to password portal",
            link_url="https://example.com/official-portal",
            feedback="Legitimate email: The request is routine and points to an official portal. Still verify the sender domain and navigate directly to the portal rather than clicking links."
        ),
        Email(
            sender="PayPal Billing Team",
            subject="Action Required: Account Limited",
            body="We noticed unusual activity. Verify your account immediately to avoid suspension.",
            is_phishing=True,
            difficulty=infer_difficulty("Action Required: Account Limited", "We noticed unusual activity. Verify your account immediately to avoid suspension.", True),
            link_text="Verify now",
            link_url="http://example.com/simulated-phish",
            feedback="Phishing signs: urgent threat (account limited) and a generic link. Always check the sender domain and avoid logging in from email links."
        ),
        Email(
            sender="HR Department",
            subject="Updated Payroll Details Needed",
            body="Your payroll details are incomplete. Please confirm your bank info by end of day.",
            is_phishing=True,
            difficulty=infer_difficulty("Updated Payroll Details Needed", "Your payroll details are incomplete. Please confirm your bank info by end of day.", True),
            link_text="Update payroll",
            link_url="http://example.com/payroll-update",
            feedback="Phishing signs: request for sensitive financial info, time pressure, and a non-company link. HR should never ask for bank details via email links."
        ),
        Email(
            sender="Company Travel Desk",
            subject="Travel Itinerary Confirmation",
            body="Your upcoming travel itinerary is attached. No action is required unless details are incorrect.",
            is_phishing=False,
            difficulty=infer_difficulty("Travel Itinerary Confirmation", "Your upcoming travel itinerary is attached. No action is required unless details are incorrect.", False),
            link_text="View itinerary",
            link_url="https://example.com/travel-portal",
            feedback="Legitimate email: no urgent pressure and no request for credentials. Still verify the sender and access the portal via a trusted bookmark."
        ),
        Email(
            sender="Security Alert",
            subject="Unusual Login Attempt Detected",
            body="We detected a login attempt from a new device. Confirm it was you to secure your account.",
            is_phishing=True,
            difficulty=infer_difficulty("Unusual Login Attempt Detected", "We detected a login attempt from a new device. Confirm it was you to secure your account.", True),
            link_text="Confirm login",
            link_url="http://example.com/confirm-login",
            feedback="Phishing signs: fear-based messaging and a generic confirmation link. Use the official site or app to review security alerts."
        ),
        Email(
            sender="Online Store",
            subject="Your Order Has Shipped",
            body="Good news! Your order has shipped. Track your package using the link below.",
            is_phishing=False,
            difficulty=infer_difficulty("Your Order Has Shipped", "Good news! Your order has shipped. Track your package using the link below.", False),
            link_text="Track package",
            link_url="https://example.com/order-tracking",
            feedback="Legitimate email: informational update with no sensitive requests. Still verify the domain and avoid entering credentials on unexpected links."
        ),
        Email(
            sender="Finance Team",
            subject="Urgent: Invoice Overdue",
            body="Your invoice is overdue. Please review and pay immediately to avoid penalties.",
            is_phishing=True,
            difficulty=infer_difficulty("Urgent: Invoice Overdue", "Your invoice is overdue. Please review and pay immediately to avoid penalties.", True),
            link_text="Pay invoice",
            link_url="http://example.com/pay-invoice",
            feedback="Phishing signs: urgency and payment demand. Verify with finance through official channels and never pay from an email link."
        ),
    ]
    db.session.add_all(emails)
    db.session.commit()


def generate_dummy_emails(count=10):
    senders = [
        'University IT Support', 'PayPal Billing Team', 'HR Department', 'Security Alert',
        'Customer Service', 'Noreply', 'Billing', 'Online Store'
    ]
    subjects_phish = [
        'Action Required: Account Limited', 'Verify your account now', 'Reset your password immediately',
        'Unusual login attempt detected', 'Confirm your payment details'
    ]
    subjects_legit = [
        'Your monthly statement', 'Welcome to our service', 'Event invitation', 'Password change confirmation', 'Order shipped'
    ]
    bodies = [
        'We noticed unusual activity on your account. Please verify to continue access.',
        'Dear user, your payment could not be processed. Please update your billing information.',
        'This is a notification about your recent request. If you did not request this, contact support.',
        'Hello, here is your weekly update and recommendations.'
    ]

    created = []
    for _ in range(count):
        is_phish = random.random() < 0.5
        body = random.choice(bodies)
        if is_phish:
            subject = random.choice(subjects_phish)
            link_url = f"http://phish{random.randint(1,99)}.example.com/login"
            feedback = "Phishing often uses urgency and unfamiliar domains. Hover links before clicking."
        else:
            subject = random.choice(subjects_legit)
            link_url = f"https://service{random.randint(1,99)}.example.com/dashboard"
            feedback = "Legitimate messages usually reference your account and use official domains."

        email = Email(
            sender=random.choice(senders),
            subject=subject,
            body=body,
            is_phishing=is_phish,
            difficulty=infer_difficulty(subject, body, is_phish),
            link_text='Open link',
            link_url=link_url,
            feedback=feedback
        )
        db.session.add(email)
        created.append(email)

    db.session.commit()
    return created
