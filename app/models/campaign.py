from app.extensions import db
from app.security import EncryptedString


class Target(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(EncryptedString(255), nullable=False)
    email = db.Column(EncryptedString(255), nullable=False)
    department = db.Column(EncryptedString(255), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), nullable=False)
    status = db.Column(db.String(50), default="active")
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "template_id": self.template_id,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CampaignTarget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'), nullable=False)
    email_id = db.Column(db.Integer, db.ForeignKey('email.id'), nullable=False)
    status = db.Column(db.String(50), default="sent")
    last_action_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "target_id": self.target_id,
            "email_id": self.email_id,
            "status": self.status,
            "last_action_at": self.last_action_at.isoformat() if self.last_action_at else None,
        }
