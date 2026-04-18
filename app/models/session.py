from datetime import datetime, timedelta
from app.extensions import db


class Session(db.Model):
    """Persistent authentication session with expiration."""
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    user_id = db.Column(db.String(100), db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def is_valid(self):
        """Check if session token is still valid (not expired)."""
        return datetime.utcnow() < self.expires_at
    
    def is_admin(self):
        """Check if this is an admin session."""
        return self.role == 'admin'
