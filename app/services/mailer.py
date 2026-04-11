import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional


def _get_env(name: str) -> Optional[str]:
    value = os.getenv(name)
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def smtp_is_configured() -> bool:
    return bool(_get_env('SMTP_HOST') and _get_env('SMTP_PORT') and _get_env('SMTP_FROM_EMAIL'))


def send_smtp_email(*, to_email: str, subject: str, text_body: str, html_body: Optional[str] = None) -> bool:
    """Send an email via SMTP using environment variables.

    Required env vars:
      - SMTP_HOST
      - SMTP_PORT
      - SMTP_FROM_EMAIL

    Optional env vars:
      - SMTP_USERNAME
      - SMTP_PASSWORD

    Behavior:
      - Port 465 uses implicit TLS (SMTP_SSL)
      - Other ports use STARTTLS
      - If username/password are not set, sends without auth

    Returns True if a send was attempted and succeeded; False otherwise.
    """

    smtp_host = _get_env('SMTP_HOST')
    smtp_port_raw = _get_env('SMTP_PORT')
    from_email = _get_env('SMTP_FROM_EMAIL')
    smtp_username = _get_env('SMTP_USERNAME')
    smtp_password = _get_env('SMTP_PASSWORD')

    if not smtp_host or not smtp_port_raw or not from_email:
        return False

    try:
        smtp_port = int(smtp_port_raw)
    except Exception:
        return False

    msg = EmailMessage()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(text_body or '')
    if html_body:
        msg.add_alternative(html_body, subtype='html')

    context = ssl.create_default_context()

    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=20) as server:
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.send_message(msg)
        return True

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.ehlo()
        # Safe default: require encrypted transport on non-465 ports.
        server.starttls(context=context)
        server.ehlo()
        if smtp_username and smtp_password:
            server.login(smtp_username, smtp_password)
        server.send_message(msg)

    return True
