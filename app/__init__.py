import os
from dotenv import load_dotenv
from flask import Flask
from app.config import Config
from app.extensions import db, login_manager
from app.models import Email, User
from app.blueprints.auth.routes import bp as auth_bp
from app.blueprints.simulate.routes import bp as simulate_bp
from app.blueprints.admin.routes import bp as admin_bp
from app.blueprints.views import bp as views_bp
from app.blueprints.simulate.services import (
    seed_emails,
    ensure_user_action_user_id_column,
    ensure_user_action_time_to_action_column,
    ensure_email_campaign_columns,
    ensure_email_difficulty_column,
    ensure_template_difficulty_column,
    ensure_target_role_column,
    ensure_campaign_extended_columns,
)


def create_app(config_class=Config):
    load_dotenv()
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_dir = os.path.join(base_dir, 'templates')

    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(config_class)


    db.init_app(app)
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, user_id)

    app.register_blueprint(auth_bp)
    app.register_blueprint(simulate_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(views_bp)

    with app.app_context():
        db.create_all()
        try:
            if Email.query.count() == 0:
                seed_emails()
        except Exception:
            pass
        ensure_user_action_user_id_column()
        ensure_user_action_time_to_action_column()
        ensure_email_campaign_columns()
        ensure_email_difficulty_column()
        ensure_template_difficulty_column()
        ensure_target_role_column()
        ensure_campaign_extended_columns()

    return app
