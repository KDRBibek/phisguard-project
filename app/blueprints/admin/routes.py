from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Email, UserAction, Template, Target, Campaign, CampaignTarget, SmsAction
from app.services.auth_store import extract_token, is_admin_token
from app.blueprints.simulate.services import render_template_text, infer_difficulty
from app.blueprints.admin.services import (
    compute_email_metrics,
    compute_sms_metrics,
    compute_user_reports,
    compute_sms_user_reports,
)

bp = Blueprint('admin', __name__)


def require_admin(f):
    def wrapper(*args, **kwargs):
        token = extract_token(request)
        if not token or not is_admin_token(token):
            return jsonify({'error': 'unauthorized'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


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
        difficulty=data.get('difficulty') or infer_difficulty(data.get('subject'), data.get('body'), bool(data.get('is_phishing', False))),
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
        difficulty=data.get('difficulty') or infer_difficulty(data.get('subject'), data.get('body'), bool(data.get('is_phishing', False))),
        link_text=data.get('link_text') or 'Open link',
        link_url=data.get('link_url') or '#',
        feedback=data.get('feedback') or ''
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
            department=t.get('department')
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
            results.append({
                **c.to_dict(),
                'total_targets': total,
                'opened': opened,
                'clicked': clicked,
                'reported': reported,
            })
        return jsonify(results)

    data = request.get_json() or {}
    name = data.get('name')
    template_id = data.get('template_id')
    target_ids = data.get('target_ids') or []
    status = data.get('status') or 'active'
    notes = data.get('notes') or ''

    try:
        template_id = int(template_id)
    except Exception:
        template_id = None

    if not name or not template_id or not isinstance(target_ids, list) or not target_ids:
        return jsonify({'error': 'missing name, template_id or target_ids'}), 400

    try:
        target_ids = [int(tid) for tid in target_ids]
    except Exception:
        return jsonify({'error': 'invalid target_ids'}), 400

    template = db.session.get(Template, template_id)
    if not template:
        return jsonify({'error': 'template not found'}), 404

    targets = Target.query.filter(Target.id.in_(target_ids)).all()
    if not targets:
        return jsonify({'error': 'no valid targets'}), 400

    campaign = Campaign(name=name, template_id=template_id, status=status, notes=notes)
    db.session.add(campaign)
    db.session.flush()

    for target in targets:
        subject = render_template_text(template.subject, target)
        body = render_template_text(template.body, target)
        link_text = render_template_text(template.link_text, target)
        link_url = render_template_text(template.link_url, target)
        feedback = render_template_text(template.feedback, target)
        email = Email(
            sender=template.sender,
            subject=subject,
            body=body,
            is_phishing=bool(template.is_phishing),
            difficulty=template.difficulty or infer_difficulty(subject, body, bool(template.is_phishing)),
            link_text=link_text,
            link_url=link_url,
            feedback=feedback,
            campaign_id=campaign.id,
            target_id=target.id
        )
        db.session.add(email)
        db.session.flush()
        db.session.add(CampaignTarget(
            campaign_id=campaign.id,
            target_id=target.id,
            email_id=email.id,
            status='sent'
        ))

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
    return jsonify({
        'campaign_id': campaign_id,
        'total_targets': total,
        'opened': opened,
        'clicked': clicked,
        'reported': reported,
    })


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
    actions = UserAction.query.order_by(UserAction.created_at.desc()).limit(100).all()
    return jsonify([a.to_dict() for a in actions])


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
    user_id = data.get('user_id')
    if user_id:
        UserAction.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({'ok': True})
    return jsonify({'error': 'missing user_id'}), 400


@bp.route('/api/metrics')
@require_admin
def api_metrics():
    return jsonify(compute_email_metrics())


@bp.route('/api/sms/actions')
@require_admin
def api_sms_actions():
    actions = SmsAction.query.order_by(SmsAction.created_at.desc()).limit(100).all()
    return jsonify([a.to_dict() for a in actions])


@bp.route('/api/sms/metrics')
@require_admin
def api_sms_metrics():
    return jsonify(compute_sms_metrics())


@bp.route('/api/sms/user_reports')
@require_admin
def api_sms_user_reports():
    return jsonify(compute_sms_user_reports())


@bp.route('/api/sms/actions/clear_user', methods=['POST'])
@require_admin
def api_sms_clear_user_actions():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if user_id:
        SmsAction.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({'ok': True})
    return jsonify({'error': 'missing user_id'}), 400
