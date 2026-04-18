import os
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import jsonify, request

# Load passwords from environment (REQUIRED - no fallback defaults)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
USER_PASSWORD = os.getenv('USER_PASSWORD')

# Validate credentials are provided
if not ADMIN_PASSWORD or not USER_PASSWORD:
    raise ValueError(
        'Authentication credentials missing. '
        'Set ADMIN_PASSWORD and USER_PASSWORD in .env file. '
        'See .env.example for details.'
    )

# Token configuration
TOKEN_TTL_HOURS = 24
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

# In-memory rate limiting (tracks failed login attempts)
_failed_attempts = {}  # {ip: (count, locked_until_timestamp)}


def _get_client_ip(req):
    """Extract client IP from request."""
    return req.remote_addr or req.headers.get('X-Forwarded-For', '').split(',')[0].strip()


def _is_client_locked(ip):
    """Check if client is rate-limited."""
    if ip not in _failed_attempts:
        return False
    count, locked_until = _failed_attempts[ip]
    # Only check time if locked_until is in the future (not the current time)
    if locked_until and datetime.utcnow() > locked_until:
        del _failed_attempts[ip]
        return False
    # Return True only if we've reached the threshold AND have a valid lockout time
    return count >= MAX_LOGIN_ATTEMPTS and locked_until


def _record_failed_attempt(ip):
    """Track failed login attempt for rate limiting."""
    if ip not in _failed_attempts:
        # First attempt: record count but no lockout yet
        _failed_attempts[ip] = (1, None)
    else:
        count, locked_until = _failed_attempts[ip]
        if count >= MAX_LOGIN_ATTEMPTS:
            # Already locked out, extend the lockout time
            locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
            _failed_attempts[ip] = (count + 1, locked_until)
        elif count + 1 >= MAX_LOGIN_ATTEMPTS:
            # This is the attempt that triggers lockout
            locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
            _failed_attempts[ip] = (count + 1, locked_until)
        else:
            # Still below threshold, just increment count
            _failed_attempts[ip] = (count + 1, None)


def _clear_failed_attempts(ip):
    """Clear failed attempts after successful login."""
    _failed_attempts.pop(ip, None)


def extract_token(req):
    """Extract token from request headers."""
    token = req.headers.get('X-Admin-Token') or req.headers.get('X-Token') or req.headers.get('Authorization')
    if token and token.lower().startswith('bearer '):
        token = token[7:].strip()
    return token


def issue_token(role, user_id):
    """
    Create a new session token with expiration.
    Uses database for persistence; in-memory fallback for performance.
    """
    from app.models import Session
    from app.extensions import db
    
    token_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS)
    
    try:
        session = Session(id=token_id, user_id=user_id, role=role, expires_at=expires_at)
        db.session.add(session)
        db.session.commit()
        print(f"✓ Session created: token={token_id[:10]}..., role={role}, user={user_id}")
    except Exception as e:
        print(f"✗ Error storing session in database: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
    
    return token_id


def revoke_token(token):
    """Revoke/delete an authentication token."""
    if not token:
        return
    
    from app.models import Session
    from app.extensions import db
    
    try:
        session = db.session.query(Session).filter_by(id=token).first()
        if session:
            db.session.delete(session)
            db.session.commit()
    except Exception as e:
        print(f"Warning: Could not revoke session: {e}")
        db.session.rollback()


def get_user_id_from_token(token):
    """
    Validate token and return associated user ID.
    Returns None if token is invalid or expired.
    """
    if not token:
        return None
    
    from app.models import Session
    from app.extensions import db
    
    try:
        session = db.session.query(Session).filter_by(id=token).first()
        if session and session.is_valid():
            return session.user_id
    except Exception as e:
        print(f"Warning: Could not retrieve session: {e}")
    
    return None


def is_admin_token(token):
    """Check if token belongs to an admin user."""
    if not token:
        return False
    
    from app.models import Session
    from app.extensions import db
    
    try:
        session = db.session.query(Session).filter_by(id=token).first()
        if not session:
            print(f"Session not found for token: {token[:10]}...")
            return False
        
        if not session.is_valid():
            print(f"Session expired for token: {token[:10]}...")
            return False
            
        is_admin = session.is_admin()
        print(f"Token is_admin check: {is_admin}, role: {session.role}")
        return is_admin
    except Exception as e:
        print(f"Error validating admin token: {e}")
        import traceback
        traceback.print_exc()
        return False


def require_token(f):
    """Decorator: Require valid authentication token."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = extract_token(request)
        user_id = get_user_id_from_token(token)
        if not user_id:
            return jsonify({'error': 'unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapper


def require_admin(f):
    """Decorator: Require valid admin authentication token."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = extract_token(request)
        if not token or not is_admin_token(token):
            return jsonify({'error': 'unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapper
