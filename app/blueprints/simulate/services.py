import csv
import os
import random
from datetime import datetime, timezone
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
    ct.last_action_at = _utcnow_like(ct.last_action_at)


def _utcnow_like(value):
    if value is None or value.tzinfo is None:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    return datetime.now(timezone.utc)


def compute_email_time_to_action_seconds(email_id, user_id):
    if not user_id:
        return None
    last_open = UserAction.query.filter_by(email_id=email_id, user_id=user_id, action='opened').order_by(UserAction.created_at.desc()).first()
    if not last_open or not last_open.created_at:
        return None
    return max(0, (_utcnow_like(last_open.created_at) - last_open.created_at).total_seconds())


def compute_sms_time_to_action_seconds(message_id, user_id):
    if not user_id:
        return None
    last_open = SmsAction.query.filter_by(message_id=message_id, user_id=user_id, action='opened').order_by(SmsAction.created_at.desc()).first()
    if not last_open or not last_open.created_at:
        return None
    return max(0, (_utcnow_like(last_open.created_at) - last_open.created_at).total_seconds())


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
        {
            'id': 4,
            'sender': 'University Library',
            'body': 'Reminder: your borrowed item "Network Security Essentials" is due on Friday. Renew or return through the official library portal.',
            'is_phishing': False,
            'link_text': 'Open library portal',
            'link_url': 'https://library.greenwich.ac.uk/account',
            'feedback': 'Legitimate context: routine due-date reminder and known service. Still prefer using your saved portal bookmark.',
        },
        {
            'id': 5,
            'sender': 'Campus IT Service',
            'body': 'Planned maintenance tonight 11:00 PM-1:00 AM may affect Wi-Fi login. Service status is available on the official IT status page.',
            'is_phishing': False,
            'link_text': 'View service status',
            'link_url': 'https://status.it.greenwich.ac.uk',
            'feedback': 'Legitimate message: informational maintenance notice with no request for passwords or urgent action.',
        },
        {
            'id': 6,
            'sender': 'Courier Updates',
            'body': 'Your parcel is out for delivery today between 2:00 PM and 4:00 PM. Track updates in the official courier app.',
            'is_phishing': False,
            'link_text': 'Track delivery',
            'link_url': 'https://www.dhl.com/global-en/home/tracking.html',
            'feedback': 'Legitimate delivery update with no credential request. Verify directly in the courier app if uncertain.',
        },
        {
            'id': 7,
            'sender': 'Coinbase Alert',
            'body': "Withdrawal successful. Wasn't you? Visit coinbạse.com/disable",
            'is_phishing': True,
            'link_text': 'Secure account',
            'link_url': 'http://coinbase-security-example.invalid/disable',
            'feedback': 'Red flags: look-alike domain using altered characters, urgency after a fake withdrawal alert, and a pushed link in SMS.',
        },
        {
            'id': 8,
            'sender': 'Voicemail Service',
            'body': 'mldrarp You mave a misseh call. Cadlor left you a message: http://regalappstechnology.com/w.php?4e04in7',
            'is_phishing': True,
            'link_text': 'Play voicemail',
            'link_url': 'http://regalappstechnology.com/w.php?4e04in7',
            'feedback': 'Red flags: heavy spelling mistakes, unknown sender context, and insecure http link to an unrelated domain.',
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
        Email(
            sender="University Registrar <registrar@greenwich.ac.uk>",
            subject="Semester enrollment confirmation and timetable availability",
            body=(
                "Hello Bibek,\n"
                "Your enrollment for Semester 2 has been confirmed successfully.\n"
                "Your updated timetable is now available in the official student portal.\n\n"
                "View timetable: https://portal.gre.ac.uk/student/timetable\n\n"
                "Regards,\n"
                "Registry Services"
            ),
            is_phishing=False,
            difficulty=infer_difficulty(
                "Semester enrollment confirmation and timetable availability",
                "Your enrollment for Semester 2 has been confirmed successfully.",
                False
            ),
            link_text="View timetable",
            link_url="https://portal.gre.ac.uk/student/timetable",
            feedback="Legitimate message: expected academic update from an official university domain with no request for sensitive credentials."
        ),
        Email(
            sender="Course Team <noreply@learn.gre.ac.uk>",
            subject="New COMP1682 workshop materials uploaded",
            body=(
                "Hi,\n"
                "New workshop slides and lab instructions for COMP1682 are now available on the learning platform.\n"
                "Please review before the next class.\n\n"
                "Open module page: https://learn.gre.ac.uk/course/comp1682\n\n"
                "Thanks,\n"
                "COMP1682 Teaching Team"
            ),
            is_phishing=False,
            difficulty=infer_difficulty(
                "New COMP1682 workshop materials uploaded",
                "New workshop slides and lab instructions are now available.",
                False
            ),
            link_text="Open module page",
            link_url="https://learn.gre.ac.uk/course/comp1682",
            feedback="Legitimate learning-platform notice: routine course communication and no pressure for immediate sensitive action."
        ),
        Email(
            sender="Finance Office <finance@greenwich.ac.uk>",
            subject="Tuition payment receipt for February",
            body=(
                "Hello,\n"
                "This is confirmation that your tuition installment payment dated 14 February has been received.\n"
                "You can view or download your receipt from the official finance portal.\n\n"
                "Finance portal: https://portal.gre.ac.uk/finance/receipts\n\n"
                "Kind regards,\n"
                "University Finance Office"
            ),
            is_phishing=False,
            difficulty=infer_difficulty(
                "Tuition payment receipt for February",
                "This is confirmation that your tuition installment payment has been received.",
                False
            ),
            link_text="Open finance portal",
            link_url="https://portal.gre.ac.uk/finance/receipts",
            feedback="Legitimate finance confirmation: informational receipt notice, no threat language, and no request to submit credentials by email."
        ),
        Email(
            sender="App Store <billingservice-info0033@refundsubsweb.com>",
            subject="Re: [ Statement Activity ] : Confirmation Order Product From mobile legend Full Payment Dispatched",
            body=(
                "Dear Customer,\n\n"
                "This is the details of your activity:\n"
                "Item: 3.750 Diamonds (Mobile Legend App)\n"
                "Date: Sunday, December 9, 2018\n"
                "Location: Singapore\n\n"
                "For more information about your order, please open the attached PDF file.\n"
                "Attachment: Invoice.pdf"
            ),
            is_phishing=True,
            difficulty=infer_difficulty(
                "Re: [ Statement Activity ] : Confirmation Order Product From mobile legend Full Payment Dispatched",
                "For more information about your order, please open the attached PDF file.",
                True
            ),
            link_text="Open invoice",
            link_url="http://apple-billing-example.invalid/invoice",
            feedback="Red flags: sender domain does not match Apple, unusual wording, and pressure to open a suspicious attachment.",
        ),
        Email(
            sender="IT STAFF <alerts@microsoft-security-notice.invalid>",
            subject="Your Password for sean@sean-wright.com has expired",
            body=(
                "Dear sean,\n\n"
                "Your Password for sean@sean-wright.com has expired.\n"
                "Dated: Wed, 04 Aug 2021 21:10:48 +0000\n\n"
                "Keep Same Password"
            ),
            is_phishing=True,
            difficulty=infer_difficulty(
                "Your Password for sean@sean-wright.com has expired",
                "Keep Same Password",
                True
            ),
            link_text="Keep Same Password",
            link_url="http://microsoft-reset-example.invalid/session",
            feedback="Red flags: impersonated Microsoft branding, unusual CTA text, and suspicious non-official reset domain.",
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


def ensure_target_role_column():
    try:
        rows = db.session.execute(text("PRAGMA table_info(target)")).fetchall()
        cols = {r[1] for r in rows}
        if 'role' not in cols:
            db.session.execute(text("ALTER TABLE target ADD COLUMN role VARCHAR(100)"))
        db.session.commit()
    except Exception:
        db.session.rollback()


def ensure_campaign_extended_columns():
    try:
        rows = db.session.execute(text("PRAGMA table_info(campaign)")).fetchall()
        cols = {r[1] for r in rows}
        if 'segment_department' not in cols:
            db.session.execute(text("ALTER TABLE campaign ADD COLUMN segment_department VARCHAR(120)"))
        if 'segment_role' not in cols:
            db.session.execute(text("ALTER TABLE campaign ADD COLUMN segment_role VARCHAR(120)"))
        if 'snapshot_sender' not in cols:
            db.session.execute(text("ALTER TABLE campaign ADD COLUMN snapshot_sender VARCHAR(100)"))
        if 'snapshot_subject' not in cols:
            db.session.execute(text("ALTER TABLE campaign ADD COLUMN snapshot_subject VARCHAR(200)"))
        if 'snapshot_body' not in cols:
            db.session.execute(text("ALTER TABLE campaign ADD COLUMN snapshot_body TEXT"))
        if 'snapshot_link_text' not in cols:
            db.session.execute(text("ALTER TABLE campaign ADD COLUMN snapshot_link_text VARCHAR(100)"))
        if 'snapshot_link_url' not in cols:
            db.session.execute(text("ALTER TABLE campaign ADD COLUMN snapshot_link_url VARCHAR(200)"))
        if 'snapshot_feedback' not in cols:
            db.session.execute(text("ALTER TABLE campaign ADD COLUMN snapshot_feedback TEXT"))
        if 'snapshot_is_phishing' not in cols:
            db.session.execute(text("ALTER TABLE campaign ADD COLUMN snapshot_is_phishing BOOLEAN"))
        if 'snapshot_difficulty' not in cols:
            db.session.execute(text("ALTER TABLE campaign ADD COLUMN snapshot_difficulty VARCHAR(20)"))
        db.session.commit()
    except Exception:
        db.session.rollback()
