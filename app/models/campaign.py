from app.extensions import db
from app.security import EncryptedString


class Target(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(EncryptedString(255), nullable=False)
    email = db.Column(EncryptedString(255), nullable=False)
    department = db.Column(EncryptedString(255), nullable=True)
    role = db.Column(EncryptedString(255), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), nullable=False)

    # New lifecycle fields
    state = db.Column(db.String(32), nullable=False, server_default='draft')  # draft, scheduled, active, completed, archived
    scheduled_at = db.Column(db.DateTime, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    archived_at = db.Column(db.DateTime, nullable=True)
    segment_department = db.Column(db.String(120), nullable=True)
    segment_role = db.Column(db.String(120), nullable=True)
    snapshot_sender = db.Column(db.String(100), nullable=True)
    snapshot_subject = db.Column(db.String(200), nullable=True)
    snapshot_body = db.Column(db.Text, nullable=True)
    snapshot_link_text = db.Column(db.String(100), nullable=True)
    snapshot_link_url = db.Column(db.String(200), nullable=True)
    snapshot_feedback = db.Column(db.Text, nullable=True)
    snapshot_is_phishing = db.Column(db.Boolean, nullable=True)
    snapshot_difficulty = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(50), default="active")  # Deprecated, for migration only
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "template_id": self.template_id,
            "state": self.state,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "segment_department": self.segment_department,
            "segment_role": self.segment_role,
            "snapshot_sender": self.snapshot_sender,
            "snapshot_subject": self.snapshot_subject,
            "snapshot_body": self.snapshot_body,
            "snapshot_link_text": self.snapshot_link_text,
            "snapshot_link_url": self.snapshot_link_url,
            "snapshot_feedback": self.snapshot_feedback,
            "snapshot_is_phishing": self.snapshot_is_phishing,
            "snapshot_difficulty": self.snapshot_difficulty,
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
