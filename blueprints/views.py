import os
from flask import Blueprint, render_template, send_from_directory
from models import Email

bp = Blueprint('views', __name__)


@bp.route('/inbox')
def inbox():
    emails = Email.query.order_by(Email.id).all()
    return render_template("inbox.html", emails=emails)


@bp.route('/')
def root():
    dist_index = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist', 'index.html')
    dist_index = os.path.abspath(dist_index)
    if os.path.exists(dist_index):
        return send_from_directory(os.path.dirname(dist_index), 'index.html')
    return inbox()


@bp.route('/<path:filename>')
def frontend_static(filename):
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
    static_dir = os.path.abspath(static_dir)
    path = os.path.join(static_dir, filename)
    if os.path.exists(path):
        return send_from_directory(static_dir, filename)
    return inbox()
