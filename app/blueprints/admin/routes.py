from datetime import datetime
import os
import logging

from flask import Blueprint, jsonify, request
from sqlalchemy import and_

from app.blueprints.admin.services import (
    compute_advanced_metrics,
    compute_email_metrics,
    compute_sms_metrics,
    compute_sms_user_reports,
    compute_user_reports,
)
from app.blueprints.simulate.services import infer_difficulty, render_template_text
from app.extensions import db
from app.models import Campaign, CampaignTarget, Email, SmsAction, Target, Template, UserAction
from app.services.auth_store import extract_token, is_admin_token
from app.services.mailer import send_smtp_email, smtp_is_configured

bp = Blueprint('admin', __name__)

logger = logging.getLogger(__name__)

ALLOWED_CAMPAIGN_STATES = {'draft', 'scheduled', 'active', 'completed', 'archived'}


def require_admin(f):
    def wrapper(*args, **kwargs):
        token = extract_token(request)
        if not token or not is_admin_token(token):
            return jsonify({'error': 'unauthorized'}), 401
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


def _parse_iso_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        return None


def _resolve_campaign_targets(target_ids, department_filter, role_filter):
    if target_ids:
        return Target.query.filter(Target.id.in_(target_ids)).all()

    q = Target.query
    if department_filter:
        q = q.filter(Target.department == department_filter)
    if role_filter:
        q = q.filter(Target.role == role_filter)
    return q.all()


def _dispatch_campaign(campaign, targets, base_url=None):
    existing = CampaignTarget.query.filter_by(campaign_id=campaign.id).count()
    if existing > 0:
        return

    base_url = (base_url or '').rstrip('/')
    if not base_url:
        base_url = (os.getenv('FLASK_BASE_URL') or '').rstrip('/')

    smtp_enabled = smtp_is_configured()
    if not smtp_enabled:
        logger.info('SMTP not configured; campaign will run in-app only')

    for target in targets:
        subject = render_template_text(campaign.snapshot_subject or '', target)
        if not subject.startswith('[SIMULATION]'):
            subject = f"[SIMULATION] {subject}".strip()
        body = render_template_text(campaign.snapshot_body or '', target)
        link_text = render_template_text(campaign.snapshot_link_text or 'Open link', target)
        link_url = render_template_text(campaign.snapshot_link_url or '#', target)
        feedback = render_template_text(campaign.snapshot_feedback or '', target)

        email = Email(
            sender=campaign.snapshot_sender or 'security@company.com',
            subject=subject,
            body=body,
            is_phishing=bool(campaign.snapshot_is_phishing),
            difficulty=campaign.snapshot_difficulty
            or infer_difficulty(subject, body, bool(campaign.snapshot_is_phishing)),
            link_text=link_text,
            link_url=link_url,
            feedback=feedback,
            campaign_id=campaign.id,
            target_id=target.id,
        )
        db.session.add(email)
        db.session.flush()

        tracking_url = f"{base_url}/l/{email.id}" if base_url else None

        if smtp_enabled and tracking_url and target.email:
            text_body = (
                f"{body}\n\n"
                f"{link_text}: {tracking_url}\n"
            )
            html_body = (
                "<html><body>"
                f"<p style='white-space:pre-wrap'>{body}</p>"
                f"<p><a href='{tracking_url}'>{link_text}</a></p>"
                "</body></html>"
            )
            try:
                sent = send_smtp_email(
                    to_email=target.email,
                    subject=subject,
                    text_body=text_body,
                    html_body=html_body,
                )
                if sent:
                    logger.info('SMTP sent simulation email_id=%s to=%s', email.id, target.email)
                else:
                    logger.warning('SMTP send skipped (missing config) email_id=%s to=%s', email.id, target.email)
            except Exception:
                # Never break simulation persistence/tracking if SMTP fails.
                logger.exception('SMTP send failed email_id=%s to=%s', email.id, target.email)

        db.session.add(
            CampaignTarget(
                campaign_id=campaign.id,
                target_id=target.id,
                email_id=email.id,
                status='sent',
            )
        )


def _recent_email_actions(limit=100):
    actions = UserAction.query.order_by(UserAction.created_at.desc()).limit(limit).all()
    return [a.to_dict() for a in actions]


def _recent_sms_actions(limit=100):
    actions = SmsAction.query.order_by(SmsAction.created_at.desc()).limit(limit).all()
    return [a.to_dict() for a in actions]


def _clear_user_actions(user_id):
    if not user_id:
        return False
    UserAction.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return True


@bp.route('/api/analytics', methods=['GET'])
@require_admin
def api_analytics():
    return jsonify(compute_advanced_metrics())


@bp.route('/api/admin/analytics/overview', methods=['GET'])
@require_admin
def api_admin_analytics_overview():
    return jsonify(compute_advanced_metrics())


@bp.route('/api/admin/analytics/email', methods=['GET'])
@require_admin
def api_admin_analytics_email():
    return jsonify(compute_email_metrics())


@bp.route('/api/admin/analytics/sms', methods=['GET'])
@require_admin
def api_admin_analytics_sms():
    return jsonify(compute_sms_metrics())


@bp.route('/api/admin/analytics/users/email', methods=['GET'])
@require_admin
def api_admin_analytics_users_email():
    return jsonify(compute_user_reports())


@bp.route('/api/admin/analytics/users/sms', methods=['GET'])
@require_admin
def api_admin_analytics_users_sms():
    return jsonify(compute_sms_user_reports())


@bp.route('/api/admin/activity/email-actions', methods=['GET'])
@require_admin
def api_admin_activity_email_actions():
    return jsonify(_recent_email_actions())


@bp.route('/api/admin/activity/sms-actions', methods=['GET'])
@require_admin
def api_admin_activity_sms_actions():
    return jsonify(_recent_sms_actions())


@bp.route('/api/admin/activity/clear-user', methods=['POST'])
@require_admin
def api_admin_activity_clear_user():
    data = request.get_json() or {}
    if _clear_user_actions(data.get('user_id')):
        return jsonify({'ok': True})
    return jsonify({'error': 'missing user_id'}), 400


@bp.route('/api/emails', methods=['POST'])
@require_admin
def api_create_email():
    data = request.get_json() or {}
    required = ['sender', 'subject', 'body']
    for r in required:
        if not data.get(r):
            return jsonify({'error': f'missing {r}'}), 400

    email = Email(
        sender=data.get('sender'),
        subject=data.get('subject'),
        body=data.get('body'),
        is_phishing=bool(data.get('is_phishing', False)),
        difficulty=data.get('difficulty')
        or infer_difficulty(
            data.get('subject'), data.get('body'), bool(data.get('is_phishing', False))
        ),
        link_text=data.get('link_text') or 'Open link',
        link_url=data.get('link_url') or '#',
        feedback=data.get('feedback') or '',
    )
    db.session.add(email)
    db.session.commit()
    return jsonify(email.to_dict()), 201


@bp.route('/api/emails/<int:email_id>', methods=['DELETE'])
@require_admin
def api_delete_email(email_id):
    email = db.get_or_404(Email, email_id)
    UserAction.query.filter_by(email_id=email_id).delete()
    db.session.delete(email)
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/api/templates', methods=['GET', 'POST'])
@require_admin
def api_templates():
    if request.method == 'GET':
        templates = Template.query.order_by(Template.created_at.desc()).all()
        return jsonify([t.to_dict() for t in templates])

    data = request.get_json() or {}
    required = ['name', 'sender', 'subject', 'body']
    for r in required:
        if not data.get(r):
            return jsonify({'error': f'missing {r}'}), 400

    t = Template(
        name=data.get('name'),
        sender=data.get('sender'),
        subject=data.get('subject'),
        body=data.get('body'),
        is_phishing=bool(data.get('is_phishing', False)),
        difficulty=data.get('difficulty')
        or infer_difficulty(
            data.get('subject'), data.get('body'), bool(data.get('is_phishing', False))
        ),
        link_text=data.get('link_text') or 'Open link',
        link_url=data.get('link_url') or '#',
        feedback=data.get('feedback') or '',
    )
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201


@bp.route('/api/templates/<int:template_id>', methods=['DELETE'])
@require_admin
def api_delete_template(template_id):
    t = db.get_or_404(Template, template_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/api/targets', methods=['GET', 'POST'])
@require_admin
def api_targets():
    if request.method == 'GET':
        targets = Target.query.order_by(Target.created_at.desc()).all()
        return jsonify([t.to_dict() for t in targets])

    data = request.get_json() or {}
    created = []
    if isinstance(data.get('targets'), list):
        targets = data.get('targets')
    elif data.get('name') and data.get('email'):
        targets = [data]
    else:
        targets = []

    if not targets:
        return jsonify({'error': 'missing targets'}), 400

    for t in targets:
        if not t.get('name') or not t.get('email'):
            continue
        target = Target(
            name=t.get('name'),
            email=t.get('email'),
            department=t.get('department'),
            role=t.get('role'),
        )
        db.session.add(target)
        created.append(target)

    db.session.commit()
    return jsonify([t.to_dict() for t in created]), 201


@bp.route('/api/targets/<int:target_id>', methods=['DELETE'])
@require_admin
def api_delete_target(target_id):
    t = db.get_or_404(Target, target_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/api/campaigns', methods=['GET', 'POST'])
@require_admin
def api_campaigns():
    if request.method == 'GET':
        campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
        results = []
        for c in campaigns:
            total = CampaignTarget.query.filter_by(campaign_id=c.id).count()
            opened = CampaignTarget.query.filter_by(campaign_id=c.id, status='opened').count()
            clicked = CampaignTarget.query.filter_by(campaign_id=c.id, status='clicked').count()
            reported = CampaignTarget.query.filter_by(campaign_id=c.id, status='reported').count()
            results.append(
                {
                    **c.to_dict(),
                    'total_targets': total,
                    'opened': opened,
                    'clicked': clicked,
                    'reported': reported,
                }
            )
        return jsonify(results)

    data = request.get_json() or {}
    name = data.get('name')
    template_id = data.get('template_id')
    target_ids = data.get('target_ids') or []
    notes = data.get('notes') or ''
    department_filter = data.get('segment_department') or None
    role_filter = data.get('segment_role') or None
    requested_state = data.get('state') or 'draft'
    scheduled_at = _parse_iso_datetime(data.get('scheduled_at'))

    if requested_state not in ALLOWED_CAMPAIGN_STATES:
        return jsonify({'error': 'invalid state'}), 400

    try:
        template_id = int(template_id)
    except Exception:
        template_id = None

    if not name or not template_id:
        return jsonify({'error': 'missing name or template_id'}), 400

    try:
        target_ids = [int(tid) for tid in target_ids]
    except Exception:
        return jsonify({'error': 'invalid target_ids'}), 400

    template = db.session.get(Template, template_id)
    if not template:
        return jsonify({'error': 'template not found'}), 404

    targets = _resolve_campaign_targets(target_ids, department_filter, role_filter)
    if not targets:
        return jsonify({'error': 'no targets matched selection'}), 400

    now = datetime.utcnow()
    state = requested_state
    if state == 'scheduled' and not scheduled_at:
        return jsonify({'error': 'scheduled_at is required for scheduled campaigns'}), 400
    if state == 'scheduled' and scheduled_at and scheduled_at <= now:
        state = 'active'

    campaign = Campaign(
        name=name,
        template_id=template_id,
        state=state,
        scheduled_at=scheduled_at,
        started_at=now if state == 'active' else None,
        notes=notes,
        segment_department=department_filter,
        segment_role=role_filter,
        snapshot_sender=template.sender,
        snapshot_subject=template.subject,
        snapshot_body=template.body,
        snapshot_link_text=template.link_text,
        snapshot_link_url=template.link_url,
        snapshot_feedback=template.feedback,
        snapshot_is_phishing=bool(template.is_phishing),
        snapshot_difficulty=template.difficulty,
    )
    db.session.add(campaign)
    db.session.flush()

    if state == 'active':
        _dispatch_campaign(campaign, targets, base_url=request.host_url)

    db.session.commit()
    return jsonify(campaign.to_dict()), 201


@bp.route('/api/campaigns/<int:campaign_id>/metrics')
@require_admin
def api_campaign_metrics(campaign_id):
    db.get_or_404(Campaign, campaign_id)
    total = CampaignTarget.query.filter_by(campaign_id=campaign_id).count()
    opened = CampaignTarget.query.filter_by(campaign_id=campaign_id, status='opened').count()
    clicked = CampaignTarget.query.filter_by(campaign_id=campaign_id, status='clicked').count()
    reported = CampaignTarget.query.filter_by(campaign_id=campaign_id, status='reported').count()
    return jsonify(
        {
            'campaign_id': campaign_id,
            'total_targets': total,
            'opened': opened,
            'clicked': clicked,
            'reported': reported,
        }
    )


@bp.route('/api/campaigns/<int:campaign_id>/schedule', methods=['POST'])
@require_admin
def api_schedule_campaign(campaign_id):
    campaign = db.get_or_404(Campaign, campaign_id)
    if campaign.state not in ('draft', 'scheduled'):
        return jsonify({'error': 'campaign cannot be scheduled from current state'}), 400

    data = request.get_json() or {}
    scheduled_at = _parse_iso_datetime(data.get('scheduled_at'))
    if not scheduled_at:
        return jsonify({'error': 'invalid scheduled_at'}), 400

    campaign.scheduled_at = scheduled_at
    campaign.state = 'scheduled' if scheduled_at > datetime.utcnow() else 'active'
    if campaign.state == 'active':
        campaign.started_at = datetime.utcnow()
        targets = _resolve_campaign_targets([], campaign.segment_department, campaign.segment_role)
        _dispatch_campaign(campaign, targets, base_url=request.host_url)

    db.session.commit()
    return jsonify(campaign.to_dict())


@bp.route('/api/campaigns/<int:campaign_id>/activate', methods=['POST'])
@require_admin
def api_activate_campaign(campaign_id):
    campaign = db.get_or_404(Campaign, campaign_id)
    if campaign.state not in ('scheduled', 'draft'):
        return jsonify({'error': 'campaign must be draft/scheduled to activate'}), 400

    campaign.state = 'active'
    campaign.started_at = datetime.utcnow()
    targets = _resolve_campaign_targets([], campaign.segment_department, campaign.segment_role)
    _dispatch_campaign(campaign, targets, base_url=request.host_url)
    db.session.commit()
    return jsonify(campaign.to_dict())


@bp.route('/api/campaigns/<int:campaign_id>/complete', methods=['POST'])
@require_admin
def api_complete_campaign(campaign_id):
    campaign = db.get_or_404(Campaign, campaign_id)
    if campaign.state != 'active':
        return jsonify({'error': 'campaign must be active to complete'}), 400

    campaign.state = 'completed'
    campaign.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify(campaign.to_dict())


@bp.route('/api/campaigns/<int:campaign_id>/archive', methods=['POST'])
@require_admin
def api_archive_campaign(campaign_id):
    campaign = db.get_or_404(Campaign, campaign_id)
    if campaign.state not in ('completed', 'active'):
        return jsonify({'error': 'only completed or active campaigns can be archived'}), 400

    campaign.state = 'archived'
    campaign.archived_at = datetime.utcnow()
    db.session.commit()
    return jsonify(campaign.to_dict())


@bp.route('/api/campaigns/auto_activate', methods=['POST'])
@require_admin
def api_auto_activate_campaigns():
    now = datetime.utcnow()
    scheduled = Campaign.query.filter(
        and_(Campaign.state == 'scheduled', Campaign.scheduled_at <= now)
    ).all()
    activated = []

    for campaign in scheduled:
        campaign.state = 'active'
        campaign.started_at = now
        targets = _resolve_campaign_targets([], campaign.segment_department, campaign.segment_role)
        _dispatch_campaign(campaign, targets, base_url=request.host_url)
        activated.append(campaign.id)

    db.session.commit()
    return jsonify({'activated_campaigns': activated})


@bp.route('/api/campaigns/<int:campaign_id>', methods=['DELETE'])
@require_admin
def api_delete_campaign(campaign_id):
    campaign = db.get_or_404(Campaign, campaign_id)
    campaign_targets = CampaignTarget.query.filter_by(campaign_id=campaign_id).all()
    email_ids = [ct.email_id for ct in campaign_targets]
    if email_ids:
        UserAction.query.filter(UserAction.email_id.in_(email_ids)).delete(synchronize_session=False)
        Email.query.filter(Email.id.in_(email_ids)).delete(synchronize_session=False)
    CampaignTarget.query.filter_by(campaign_id=campaign_id).delete(synchronize_session=False)
    db.session.delete(campaign)
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/api/actions')
@require_admin
def api_actions():
    return jsonify(_recent_email_actions())


@bp.route('/api/actions/<int:action_id>', methods=['DELETE'])
@require_admin
def api_delete_action(action_id):
    a = db.get_or_404(UserAction, action_id)
    db.session.delete(a)
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/api/user_reports')
@require_admin
def api_user_reports():
    return jsonify(compute_user_reports())


@bp.route('/api/actions/clear_user', methods=['POST'])
@require_admin
def api_clear_user_actions():
    data = request.get_json() or {}
    if _clear_user_actions(data.get('user_id')):
        return jsonify({'ok': True})
    return jsonify({'error': 'missing user_id'}), 400


@bp.route('/api/metrics')
@require_admin
def api_metrics():
    return jsonify(compute_email_metrics())


@bp.route('/api/sms/actions')
@require_admin
def api_sms_actions():
    return jsonify(_recent_sms_actions())


@bp.route('/api/sms/metrics')
@require_admin
def api_sms_metrics():
    return jsonify(compute_sms_metrics())


@bp.route('/api/sms/user_reports')
@require_admin
def api_sms_user_reports():
    return jsonify(compute_sms_user_reports())
