import re
from urllib.parse import urlparse

URGENT_PATTERNS = [
    r'urgent',
    r'immediately',
    r'within\s+\d+\s*(hour|hours|minute|minutes)',
    r'action required',
    r'due today',
    r'expired',
    r'suspend',
    r'locked',
]

CREDENTIAL_PATTERNS = [
    r'password',
    r'otp',
    r'pin',
    r'verify\s+account',
    r'bank\s+details',
    r'login',
    r'credential',
]

THREAT_PATTERNS = [
    r'late fee',
    r'penalty',
    r'account limited',
    r'security alert',
    r'unusual sign-?in',
    r'reset immediately',
]

URL_SHORTENER_HOSTS = {
    'bit.ly',
    'tinyurl.com',
    't.co',
    'rb.gy',
    'is.gd',
}

SUSPICIOUS_TLDS = {
    'zip',
    'click',
    'top',
    'xyz',
    'work',
    'gq',
}


EMAIL_IN_ANGLE_RE = re.compile(r'<([^>]+)>')
NON_ASCII_RE = re.compile(r'[^\x00-\x7f]')


def _extract_sender_domain(sender):
    if not sender:
        return ''
    match = EMAIL_IN_ANGLE_RE.search(sender)
    email_value = match.group(1) if match else sender
    if '@' not in email_value:
        return ''
    return email_value.split('@', 1)[1].strip().lower()


def _extract_link_host(link_url):
    if not link_url:
        return ''
    try:
        parsed = urlparse(link_url)
        return (parsed.netloc or '').lower().strip()
    except Exception:
        return ''


def _has_pattern(text, patterns):
    haystack = (text or '').lower()
    return any(re.search(p, haystack) for p in patterns)


def _looks_like_domain_mismatch(sender_domain, link_host):
    if not sender_domain or not link_host:
        return False
    # Common case: sender domain should appear in destination host for trusted links.
    return sender_domain not in link_host and link_host not in sender_domain


def analyze_message(*, channel, sender='', subject='', body='', link_url=''):
    score = 0
    reasons = []

    combined_text = ' '.join(filter(None, [subject, body]))
    sender_domain = _extract_sender_domain(sender)
    link_host = _extract_link_host(link_url)

    if _has_pattern(combined_text, URGENT_PATTERNS):
        score += 20
        reasons.append('Uses urgency or deadline language to pressure fast action.')

    if _has_pattern(combined_text, CREDENTIAL_PATTERNS):
        score += 25
        reasons.append('Requests login, password, OTP, or other sensitive account details.')

    if _has_pattern(combined_text, THREAT_PATTERNS):
        score += 15
        reasons.append('Contains threat or fear-based account language.')

    if link_url:
        if link_url.lower().startswith('http://'):
            score += 15
            reasons.append('Uses an insecure http link instead of https.')

        if link_host in URL_SHORTENER_HOSTS:
            score += 20
            reasons.append('Uses a shortened URL that hides the final destination.')

        if link_host and '.' in link_host:
            tld = link_host.rsplit('.', 1)[-1]
            if tld in SUSPICIOUS_TLDS:
                score += 10
                reasons.append('Uses an uncommon top-level domain often seen in phishing.')

        if NON_ASCII_RE.search(link_url):
            score += 20
            reasons.append('Link contains non-ASCII characters that can mimic trusted domains.')

    if NON_ASCII_RE.search(sender or ''):
        score += 10
        reasons.append('Sender text contains unusual characters that may indicate spoofing.')

    if _looks_like_domain_mismatch(sender_domain, link_host):
        score += 15
        reasons.append('Sender domain does not match the linked destination domain.')

    if channel == 'sms' and link_url:
        score += 5
        reasons.append('SMS messages with links require extra caution.')

    if score <= 15:
        reasons.append('No strong phishing indicators detected from current message content.')

    score = max(0, min(100, int(score)))
    if score >= 70:
        verdict = 'phishing'
    elif score >= 40:
        verdict = 'suspicious'
    else:
        verdict = 'safe'

    return {
        'risk_score': score,
        'verdict': verdict,
        'reasons': reasons,
    }


def analyze_email(*, sender='', subject='', body='', link_url=''):
    return analyze_message(channel='email', sender=sender, subject=subject, body=body, link_url=link_url)


def analyze_sms(*, sender='', body='', link_url=''):
    return analyze_message(channel='sms', sender=sender, subject='SMS', body=body, link_url=link_url)
