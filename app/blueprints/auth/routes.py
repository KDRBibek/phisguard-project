import re
from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user
from app.extensions import db
from app.models import User
from app.services.auth_store import (
    ADMIN_PASSWORD, USER_PASSWORD, extract_token, issue_token, revoke_token,
    _get_client_ip, _is_client_locked, _record_failed_attempt, _clear_failed_attempts
)

bp = Blueprint('auth', __name__)


def _normalize_name(value):
    name = (value or '').strip()
    if not name:
        return ''
    return ''.join(ch for ch in name if ch.isalnum() or ch in ('-', '_', ' ')).strip()


def _slugify_name(value):
    cleaned = _normalize_name(value).lower()
    slug = re.sub(r'\s+', '-', cleaned)
    slug = re.sub(r'[^a-z0-9_-]', '', slug)
    slug = slug.strip('-_')
    return slug or 'user'


def _get_or_create_user(role, name=None):
    if role == 'admin':
        user_id = 'admin'
    else:
        safe_name = _normalize_name(name)
        user_id = f"user-{_slugify_name(safe_name)}"

    existing = db.session.get(User, user_id)
    if existing:
        return existing

    user = User(id=user_id, role=role)
    db.session.add(user)
    db.session.commit()
    return user


@bp.route('/api/login', methods=['POST'])
def api_login():
    """
    Rate-limited login endpoint with token expiration.
    Returns token valid for 24 hours.
    """
    client_ip = _get_client_ip(request)
    
    # Check rate limiting
    if _is_client_locked(client_ip):
        return jsonify({'ok': False, 'error': 'too many failed attempts; try again later'}), 429
    
    data = request.get_json() or {}
    pwd = data.get('password', '')
    role = data.get('role', 'user')
    name = (data.get('name') or '').strip()
    
    if role == 'admin':
        if pwd == ADMIN_PASSWORD:
            user = _get_or_create_user('admin')
            login_user(user)
            token = issue_token('admin', user.id)
            _clear_failed_attempts(client_ip)
            print(f"✓ Admin login successful: user={user.id}, token={token[:10]}...")
            return jsonify({'ok': True, 'token': token, 'role': 'admin', 'user_id': user.id})
        _record_failed_attempt(client_ip)
        print(f"✗ Admin login failed: wrong password from {client_ip}")
        return jsonify({'ok': False, 'error': 'invalid admin password'}), 403

    if not name:
        return jsonify({'ok': False, 'error': 'name is required'}), 400

    if pwd == USER_PASSWORD:
        user = _get_or_create_user('user', name=name)
        login_user(user)
        token = issue_token('user', user.id)
        _clear_failed_attempts(client_ip)
        return jsonify({'ok': True, 'token': token, 'role': 'user', 'user_id': user.id})
    
    _record_failed_attempt(client_ip)
    return jsonify({'ok': False, 'error': 'invalid user password'}), 403


@bp.route('/api/logout', methods=['POST'])
def api_logout():
    """Revoke token and logout session."""
    data = request.get_json() or {}
    token = data.get('token') or extract_token(request)
    revoke_token(token)
    logout_user()
    return jsonify({'ok': True})
