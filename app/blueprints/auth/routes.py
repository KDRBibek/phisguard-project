import uuid
from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user
from app.extensions import db
from app.models import User
from app.services.auth_store import ADMIN_PASSWORD, USER_PASSWORD, extract_token, issue_token, revoke_token

bp = Blueprint('auth', __name__)


def _normalize_name(value):
    name = (value or '').strip()
    if not name:
        return ''
    return ''.join(ch for ch in name if ch.isalnum() or ch in ('-', '_', ' ')).strip()


def _get_or_create_user(role, name=None):
    safe_name = _normalize_name(name)
    _ = safe_name  # Name is validated but not persisted in identifiers.
    user_id = f"{role}-{str(uuid.uuid4())[:8]}"
    user = User(id=user_id, role=role)
    db.session.add(user)
    db.session.commit()
    return user


@bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    pwd = data.get('password', '')
    role = data.get('role', 'user')
    name = (data.get('name') or '').strip()
    if role == 'admin':
        if pwd == ADMIN_PASSWORD:
            user = _get_or_create_user('admin')
            login_user(user)
            token = issue_token('admin', user.id)
            return jsonify({'ok': True, 'token': token, 'role': 'admin', 'user_id': user.id})
        return jsonify({'ok': False, 'error': 'invalid admin password'}), 403

    if not name:
        return jsonify({'ok': False, 'error': 'name is required'}), 400

    if pwd == USER_PASSWORD:
        user = _get_or_create_user('user', name=name)
        login_user(user)
        token = issue_token('user', user.id)
        return jsonify({'ok': True, 'token': token, 'role': 'user', 'user_id': user.id})
    return jsonify({'ok': False, 'error': 'invalid user password'}), 403


@bp.route('/api/logout', methods=['POST'])
def api_logout():
    data = request.get_json() or {}
    token = data.get('token') or extract_token(request)
    revoke_token(token)
    logout_user()
    return jsonify({'ok': True})
