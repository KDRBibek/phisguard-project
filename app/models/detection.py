import json
from app.extensions import db


class DetectionResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(10), nullable=False)  # email | sms
    message_ref_id = db.Column(db.Integer, nullable=True)
    sender = db.Column(db.String(255), nullable=True)
    subject = db.Column(db.String(255), nullable=True)
    body = db.Column(db.Text, nullable=False)
    link_url = db.Column(db.String(500), nullable=True)
    risk_score = db.Column(db.Integer, nullable=False)
    verdict = db.Column(db.String(20), nullable=False)
    reasons = db.Column(db.Text, nullable=False, default='[]')
    user_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        try:
            reason_list = json.loads(self.reasons or '[]')
            if not isinstance(reason_list, list):
                reason_list = []
        except Exception:
            reason_list = []

        return {
            'id': self.id,
            'channel': self.channel,
            'message_ref_id': self.message_ref_id,
            'sender': self.sender,
            'subject': self.subject,
            'body': self.body,
            'link_url': self.link_url,
            'risk_score': int(self.risk_score or 0),
            'verdict': self.verdict,
            'reasons': reason_list,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
