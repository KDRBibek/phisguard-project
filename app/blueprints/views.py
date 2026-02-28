import os
from flask import Blueprint, render_template, send_from_directory
from app.models import Email

bp = Blueprint('views', __name__)


@bp.route('/inbox')
def inbox():
    emails = Email.query.order_by(Email.id).all()
    return render_template("inbox.html", emails=emails)


@bp.route('/')
def root():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dist_index = os.path.join(base_dir, 'frontend', 'dist', 'index.html')
    if os.path.exists(dist_index):
        return send_from_directory(os.path.dirname(dist_index), 'index.html')
    return inbox()


@bp.route('/<path:filename>')
def frontend_static(filename):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    static_dir = os.path.join(base_dir, 'frontend', 'dist')
    path = os.path.join(static_dir, filename)
    if os.path.exists(path):
        return send_from_directory(static_dir, filename)
    return inbox()
