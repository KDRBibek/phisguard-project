from app.extensions import db


class UserAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('email.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(100), nullable=True)
    time_to_action_seconds = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "email_id": self.email_id,
            "action": self.action,
            "user_id": self.user_id,
            "time_to_action_seconds": self.time_to_action_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SmsAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(100), nullable=True)
    time_to_action_seconds = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "message_id": self.message_id,
            "action": self.action,
            "user_id": self.user_id,
            "time_to_action_seconds": self.time_to_action_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
