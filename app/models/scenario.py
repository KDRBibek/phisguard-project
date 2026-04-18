from app.extensions import db


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)

    is_phishing = db.Column(db.Boolean, default=False)
    difficulty = db.Column(db.String(20), default="medium")
    link_text = db.Column(db.String(100), default="Open link")
    link_url = db.Column(db.String(200), default="#")
    feedback = db.Column(db.Text, default="")
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=True)
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "subject": self.subject,
            "body": self.body,
            "is_phishing": bool(self.is_phishing),
            "difficulty": self.difficulty,
            "link_text": self.link_text,
            "link_url": self.link_url,
            "feedback": self.feedback,
            "campaign_id": self.campaign_id,
            "target_id": self.target_id,
        }


class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    sender = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_phishing = db.Column(db.Boolean, default=False)
    difficulty = db.Column(db.String(20), default="medium")
    link_text = db.Column(db.String(100), default="Open link")
    link_url = db.Column(db.String(200), default="#")
    feedback = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sender": self.sender,
            "subject": self.subject,
            "body": self.body,
            "is_phishing": bool(self.is_phishing),
            "difficulty": self.difficulty,
            "link_text": self.link_text,
            "link_url": self.link_url,
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
