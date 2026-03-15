# PHISGUARD API Specification

This document describes the JSON API endpoints used by the PHISGUARD React frontend.

Base URL (development): `http://127.0.0.1:5000`

## Authentication
- User login: POST /api/login (role user/admin) returns token.
- Admin endpoints require X-Admin-Token or Authorization: Bearer <token>.

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

---

## Admin: Targets (Simulated Users)

### GET /api/targets
List targets.

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
Create a campaign and generate simulated emails for each target.

Request JSON:
{
  "name": "string",
  "template_id": 1,
  "target_ids": [1,2,3],
  "status": "active",
  "notes": "string"
}

### GET /api/campaigns/:id/metrics
Campaign-level metrics.

### DELETE /api/campaigns/:id
Delete campaign and related simulated emails.
