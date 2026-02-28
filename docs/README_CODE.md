# PHISGUARD Code Explanation (Demo Guide)

## Recommended Architecture (Simple + Strong for FYP)
**Backend:** Flask + SQLAlchemy + Flask-Login, organized with **Blueprints**
- `run.py` starts the app using `create_app()` from app/__init__.py.
- Blueprints separate concerns: auth, simulate, admin, views.

**Database:** SQLite for development; optional Postgres/MySQL later
- Local dev uses `sqlite:///database.db`.
- The models remain compatible with Postgres/MySQL if you later switch the URI.

**Frontend:** keep existing React + Vite (unchanged)
- The API surface stays the same, so no frontend refactor is required.

## 1) Backend Overview (Flask)
**Entry:** run.py
- Uses `create_app()` from app/__init__.py.
- Initializes extensions, registers blueprints, and seeds data.
- Exposes APIs used by the React frontend.

### Key backend sections
- **Auth**: `/api/login` returns a token for user/admin. Admin endpoints check `X-Admin-Token`.
- **Email actions**:
  - `/api/emails` → list emails
  - `/api/emails/<id>/open` → record “opened”
  - `/api/emails/<id>/click` → record “clicked” + feedback
  - `/api/emails/<id>/report` → record “reported” + feedback
- **SMS endpoint**:
  - `/api/sms` returns three static phishing SMS scenarios.
- **Campaign management** (admin): templates, targets, campaigns, and metrics.

## 2) Data Models (SQLAlchemy)
**File:** models.py
- **Email**: sender, subject, body, link, feedback, phishing flag.
- **UserAction**: records opens/clicks/reports.
- **Template / Target / Campaign / CampaignTarget**: used by admin dashboard to generate and track campaigns.

## 3) Frontend Overview (React + Vite)
**Entry:** frontend/src/App.jsx
- Controls routes and navigation.
- Loads emails and SMS messages.
- Stores user feedback in localStorage.

### Main pages
- **Home**: overview + feedback summary (locked until all Email + SMS are tested).
- **Simulation**: two tabs (Email / SMS) with their own inbox and tips.
- **Awareness**: structured learning program (modules + timeline).
- **Feedback**: user’s history from localStorage.
- **Admin**: templates, targets, campaigns, and metrics.

### Key components
- **EmailList / EmailView**: shows inbox list and email details.
- **SmsList / SmsView**: same for SMS.
- **InboxTips / SmsTips**: quick guidance panels.

## 4) Scenario Flow
- **Email**: seeded in app/blueprints/simulate/services.py (3 phishing emails).
- **SMS**: served by /api/sms in app/blueprints/simulate/services.py (3 phishing SMS).

## 5) Demo Script (talking points)
- **Problem:** phishing is common; users need safe practice.
- **Solution:** PHISGUARD simulates emails and SMS in a controlled environment.
- **Flow:** open message → click/report → feedback → summary.
- **Awareness:** structured program supports learning beyond testing.
- **Admin:** create campaigns, templates, targets, and metrics.

## 6) How to Run (demo)
1. Backend:
  - python run.py
2. Frontend:
   - cd frontend
   - npm run dev

Open http://localhost:5173
