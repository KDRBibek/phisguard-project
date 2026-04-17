# PHISGUARD API Specification

This document describes the JSON API endpoints used by the PHISGUARD React frontend.

Base URL (development): `http://127.0.0.1:5000`

## Authentication
- User login: POST /api/login (role user/admin) returns token.
- Admin endpoints require X-Admin-Token or Authorization: Bearer <token>.
- User-scoped endpoints (for simulation history) accept X-Token or Authorization: Bearer <token>.

## Endpoints

### GET /api/emails
Returns list of available email scenarios.

Response: 200 OK

[
  {
    "id": 1,
    "sender": "PayPal Billing Team",
    "subject": "Action Required: Account Limited",
    "body": "...",
    "is_phishing": true,
    "link_text": "Verify now",
    "link_url": "http://example.com/simulated-phish",
    "feedback": "Phishing often uses urgency..."
  }
]

### GET /api/emails/:id
Returns detail for an email scenario.

Response: 200 OK (object above)

### POST /api/emails
Create a new email scenario (admin).

Request JSON:
{
  "sender": "string",
  "subject": "string",
  "body": "string",
  "is_phishing": true|false,
  "link_text": "string",
  "link_url": "string",
  "feedback": "string"
}

Response: 201 Created
{ "id": <new id>, ... }

### POST /api/emails/:id/click
Records a click action and returns feedback JSON.

Response: 200 OK
{
  "correct": false,
  "message": "You clicked a phishing link...",
  "tip": "..."
}

### POST /api/emails/:id/report
Records a report action and returns feedback JSON.

Response: 200 OK

### GET /api/feedback
Returns the logged-in user's combined feedback history (email + SMS), newest first.

Headers:
- X-Token: <user token>

Response: 200 OK
[
  {
    "item_id": 1,
    "channel": "email",
    "subject": "Action Required: ...",
    "sender": "Security Team",
    "action": "click",
    "correct": false,
    "message": "You clicked a phishing link...",
    "tip": "Check sender and links...",
    "time_to_action_seconds": 8.2,
    "created_at": "2026-04-17T10:30:00"
  }
]

Response: 401 Unauthorized
{ "error": "unauthorized" }

### POST /api/feedback/reset
Clears the logged-in user's simulation actions/feedback history.

Headers:
- X-Token: <user token>

Response: 200 OK
{ "ok": true }

Response: 401 Unauthorized
{ "error": "unauthorized" }

### GET /api/awareness
Returns awareness accuracy for the logged-in user only.

Headers:
- X-Token: <user token>

Response: 200 OK
{
  "total_checked": 12,
  "correct": 9,
  "accuracy_percent": 75.0
}

### GET /api/actions
List recorded `UserAction` events (admin).

Response: 200 OK
[
  { "id": 1, "email_id": 2, "action": "clicked", "created_at": "..." }
]

### GET /api/metrics
Basic aggregated metrics per email id: counts of opened/clicked/reported.

Response: 200 OK
[
  { "email_id": 1, "clicks": 2, "reports": 1, "opens": 5 }
]

### POST /api/emails/:id/open
Records that the user opened/viewed the email (useful for tracking opens/views).

Response: 200 OK
{ /* email object */ }

### POST /api/detector/analyze-email
Runs detector analysis for an email scenario or raw email content.

Request JSON (scenario):
{
  "email_id": 1
}

Request JSON (raw content):
{
  "sender": "Security Team <alerts@example.com>",
  "subject": "Action required",
  "body": "...",
  "link_url": "https://example.com/login"
}

Response: 200 OK
{
  "analysis_id": 42,
  "message_ref_id": 1,
  "risk_score": 78,
  "verdict": "phishing",
  "reasons": [
    "Uses urgency or deadline language to pressure fast action.",
    "Sender domain does not match the linked destination domain."
  ]
}

### POST /api/detector/analyze-sms
Runs detector analysis for an SMS scenario or raw SMS content.

Request JSON (scenario):
{
  "message_id": 3
}

Request JSON (raw content):
{
  "sender": "Bank Alerts",
  "body": "Alert: verify now...",
  "link_url": "http://example.invalid/verify"
}

Response: 200 OK
{
  "analysis_id": 43,
  "message_ref_id": 3,
  "risk_score": 84,
  "verdict": "phishing",
  "reasons": [
    "Requests login, password, OTP, or other sensitive account details.",
    "Uses an insecure http link instead of https."
  ]
}

---

Notes
- All endpoints return JSON. Errors use appropriate HTTP status codes and a JSON body with `error`.
- For production, add stronger authentication, rate limiting, and validation.

---

## Admin: Templates (Email Blueprints)

### GET /api/templates
List templates.

### POST /api/templates
Create template.

Request JSON:
{
  "name": "string",
  "sender": "string",
  "subject": "string",
  "body": "string",
  "is_phishing": true|false,
  "link_text": "string",
  "link_url": "string",
  "feedback": "string"
}

### DELETE /api/templates/:id
Delete template.

### GET /api/analytics
Legacy analytics overview endpoint (admin).

Response: 200 OK
{ ...advanced metrics... }

### GET /api/admin/analytics/overview
Structured analytics overview endpoint (admin).

### GET /api/admin/analytics/email
Structured email analytics metrics (admin).

### GET /api/admin/analytics/sms
Structured SMS analytics metrics (admin).

### GET /api/admin/analytics/users/email
Structured per-user email performance report (admin).

### GET /api/admin/analytics/users/sms
Structured per-user SMS performance report (admin).

### GET /api/admin/activity/email-actions
Structured recent email action feed (admin).

### GET /api/admin/activity/sms-actions
Structured recent SMS action feed (admin).

### POST /api/admin/activity/clear-user
Structured endpoint to clear user email actions (admin).

Request JSON:
{
  "user_id": "string"
}

Response: 200 OK
{ "ok": true }

Response: 400 Bad Request
{ "error": "missing user_id" }

---

Legacy compatibility:
- GET /api/analytics maps to overview analytics.

### GET /api/actions
Legacy endpoint remains supported and maps to email activity feed.

### GET /api/sms/actions
Legacy endpoint remains supported and maps to SMS activity feed.

### POST /api/actions/clear_user
Legacy endpoint remains supported and maps to clear-user activity action.

---

## Admin: Targets (Simulated Users)

### GET /api/targets
    {"name": "string", "email": "string", "department": "string", "role": "string"}

### POST /api/targets
Create one or many targets.

Request JSON:
{
  "targets": [
    {"name": "string", "email": "string", "department": "string"}
  ]
}

### DELETE /api/targets/:id
Delete target.

---

## Admin: Campaigns

### GET /api/campaigns
List campaigns with summary counts.

### POST /api/campaigns
Create a campaign in one of these states: `draft`, `scheduled`, `active`.

Behavior:
- `draft`: campaign is created, no emails dispatched yet.
- `scheduled`: campaign is created for future dispatch (`scheduled_at` required).
- `active`: campaign dispatches immediately.
- If a scheduled time is already in the past, the campaign is activated immediately.

Target selection behavior:
- Use explicit `target_ids`, or
- Use segmentation filters: `segment_department` and/or `segment_role`.

Historical preservation behavior:
- The campaign stores a template content snapshot at creation.
- Later changes to the original template do not affect existing campaign email content.

Request JSON:
{
  "name": "string",
  "template_id": 1,
  "target_ids": [1,2,3],
  "state": "draft|scheduled|active",
  "scheduled_at": "2026-04-11T18:30:00",
  "segment_department": "Finance",
  "segment_role": "Manager",
  "notes": "string"
}

### GET /api/campaigns/:id/metrics
Campaign-level metrics.

### POST /api/campaigns/:id/schedule
Set/Update schedule and move campaign to `scheduled` (or auto-activate if schedule is now/past).

Request JSON:
{
  "scheduled_at": "2026-04-12T09:00:00"
}

### POST /api/campaigns/:id/activate
Transition campaign to `active` and dispatch if not already dispatched.

### POST /api/campaigns/:id/complete
Transition campaign to `completed`.

### POST /api/campaigns/:id/archive
Transition campaign to `archived`.

### POST /api/campaigns/auto_activate
Activate all scheduled campaigns whose schedule time has passed.

### DELETE /api/campaigns/:id
Delete campaign and related simulated emails.
