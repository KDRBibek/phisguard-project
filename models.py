from app.extensions import db
from app.models import (
    User,
    Email,
    Template,
    Target,
    Campaign,
    CampaignTarget,
    UserAction,
    SmsAction,
    DetectionResult,
)

__all__ = [
    'db',
    'User',
    'Email',
    'Template',
    'Target',
    'Campaign',
    'CampaignTarget',
    'UserAction',
    'SmsAction',
    'DetectionResult',
]
