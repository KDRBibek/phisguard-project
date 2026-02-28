import csv
import os
import random
from datetime import datetime
from sqlalchemy import text
from app.extensions import db
from app.models import Email, UserAction, CampaignTarget, SmsAction


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
    messages = [
        {
            'id': 1,
            'sender': 'Delivery Service',
            'body': 'Parcel held: address incomplete. Update within 2 hours to avoid return: https://track-example.invalid/confirm',
            'is_phishing': True,
            'link_text': 'Update address',
            'link_url': 'https://track-example.invalid/confirm',
            'feedback': 'Red flags: urgency and a link inside the SMS. Verify delivery issues by checking the official courier app or website directly.',
        },
        {
            'id': 2,
            'sender': 'Bank Alerts',
            'body': 'Alert: Your card is temporarily locked due to a suspicious purchase. Verify now: https://banking-example.invalid/secure',
            'is_phishing': True,
            'link_text': 'Verify card',
            'link_url': 'https://banking-example.invalid/secure',
            'feedback': 'Red flags: fear trigger and a link push. Banks ask you to log in via the official app or website, not via SMS links.',
        },
        {
            'id': 3,
            'sender': 'Account Security',
            'body': 'Your verification code is 839144. If you did not request this, reset immediately: https://account-example.invalid/reset',
            'is_phishing': True,
            'link_text': 'Reset account',
            'link_url': 'https://account-example.invalid/reset',
            'feedback': 'Red flags: tries to rush a reset after an OTP. Do not click; open the app directly and check recent activity.',
        },
    ]

    for msg in messages:
        msg['difficulty'] = infer_difficulty('SMS', msg['body'], msg['is_phishing'])

    return messages


def seed_emails():
    UserAction.query.delete()
    try:
        CampaignTarget.query.delete()
    except Exception:
        pass
    Email.query.delete()

    emails = [
        Email(
            sender="Account Security Team <security@notify-example.invalid>",
            subject="Action Required: Unusual sign-in detected on your account",
            body=(
                "Hello,\n"
                "We detected a sign-in attempt from a new device (Windows PC) near Kuala Lumpur at 10:12 AM.\n\n"
                "If this was you, no action is needed. If you do not recognize this activity, secure your account immediately to prevent suspension.\n\n"
                "Review activity: https://login.company-example.invalid/security-review\n\n"
                "Thanks,\n"
                "Account Security Team\n"
                "--\n"
                "This is an automated message. Please do not reply."
            ),
            is_phishing=True,
            difficulty=infer_difficulty(
                "Action Required: Unusual sign-in detected on your account",
                "We detected a sign-in attempt from a new device near Kuala Lumpur.",
                True
            ),
            link_text="Review activity",
            link_url="https://login.company-example.invalid/security-review",
            feedback="Red flags: urgency and suspension threat, look-alike domain, and generic greeting. Verify via your official portal or IT helpdesk."
        ),
        Email(
            sender="HR Operations <hr-ops@payroll-example.invalid>",
            subject="Required: Verify payroll details for March processing",
            body=(
                "Hi,\n"
                "We are updating payroll records due to a compliance audit. Please confirm your details today so your salary is not delayed.\n\n"
                "Complete verification: https://forms.company-example.invalid/payroll-verify\n\n"
                "Required fields include: full name, staff ID, bank name, and last 4 digits of account number.\n\n"
                "Regards,\n"
                "HR Operations"
            ),
            is_phishing=True,
            difficulty=infer_difficulty(
                "Required: Verify payroll details for March processing",
                "We are updating payroll records due to a compliance audit.",
                True
            ),
            link_text="Complete verification",
            link_url="https://forms.company-example.invalid/payroll-verify",
            feedback="Red flags: requests sensitive banking info, audit pressure, and non-HR domain. HR should use official internal systems."
        ),
        Email(
            sender="Accounts Payable <ap@vendor-example.invalid>",
            subject="Updated bank details for Invoice INV-10488 (Due Today)",
            body=(
                "Hello Finance Team,\n"
                "Following our bank's migration, please use the updated account details for INV-10488.\n\n"
                "To avoid late fees, confirm the change and proceed with payment today.\n\n"
                "View remittance update: https://secure.vendor-example.invalid/remittance/INV-10488\n\n"
                "Kind regards,\n"
                "A. Rahman\n"
                "Accounts Department"
            ),
            is_phishing=True,
            difficulty=infer_difficulty(
                "Updated bank details for Invoice INV-10488 (Due Today)",
                "Following our bank's migration, please use the updated account details.",
                True
            ),
            link_text="View remittance update",
            link_url="https://secure.vendor-example.invalid/remittance/INV-10488",
            feedback="Red flags: bank detail change request, due-today pressure, and external link. Verify out-of-band using known vendor contacts."
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
