import os
import uuid

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')
USER_PASSWORD = os.getenv('USER_PASSWORD', 'user')

_admin_tokens = set()
_user_tokens = set()
_admin_sessions = {}
_user_sessions = {}


def extract_token(req):
    token = req.headers.get('X-Admin-Token') or req.headers.get('X-Token') or req.headers.get('Authorization')
    if token and token.lower().startswith('bearer '):
        token = token[7:].strip()
    return token


def issue_token(role, user_id):
    token = str(uuid.uuid4())
    if role == 'admin':
        _admin_tokens.add(token)
        _admin_sessions[token] = user_id
    else:
        _user_tokens.add(token)
        _user_sessions[token] = user_id
    return token


def revoke_token(token):
    if not token:
        return
    if token in _admin_tokens:
        _admin_tokens.discard(token)
        _admin_sessions.pop(token, None)
    if token in _user_tokens:
        _user_tokens.discard(token)
        _user_sessions.pop(token, None)


def get_user_id_from_token(token):
    if not token:
        return None
    return _user_sessions.get(token) or _admin_sessions.get(token)


def is_admin_token(token):
    return token in _admin_tokens
