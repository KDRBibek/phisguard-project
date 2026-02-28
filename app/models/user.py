from flask_login import UserMixin
from app.extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.String(100), primary_key=True)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def get_id(self):
        return self.id
