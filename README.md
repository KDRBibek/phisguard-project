# PHISGUARD

PHISGUARD is a web-based phishing simulation and awareness tool. It provides safe, controlled email and SMS simulations plus an awareness program and feedback tracking.

Project Structure (high-level)
- run.py: starts the Flask backend (app factory).
- app/: Flask app package (blueprints, models, services).
- frontend/: React + Vite UI.
- instance/: SQLite database (runtime data).
- templates/: Flask-rendered fallback pages.

How It Works (backend)
- On startup, the app factory seeds three phishing emails and serves three phishing SMS messages.
- User actions (open/click/report) are stored in the database.
- Admin endpoints manage templates, targets, campaigns, and metrics.

How It Works (frontend)
- Home: overview + feedback summary gating.
- Simulation: two tabs (Email and SMS) with separate inboxes and tips.
- Awareness: structured awareness program (modules + timeline).
- Feedback: user’s past results loaded from backend per logged-in user.

Email vs SMS
- Email simulation data comes from seeded email records in the database.
- SMS simulation data is served by /api/sms from static scenarios.

Key User Flows
1) User logs in → Simulation → opens a message → clicks/report.
2) Feedback is stored by user ID in the backend and shown in Feedback page.
3) After all Email + SMS are tested, summary unlocks on Home.

Admin Flow
- Login as admin → Admin dashboard → create templates, targets, campaigns → view metrics.

Quick start (development)

1. Activate Python environment (from project root):

```powershell
.\venv\Scripts\Activate
pip install -r requirements.txt
```

2. Configure environment variables (optional but recommended):

Copy `.env.example` to `.env` and set strong values for `SECRET_KEY`, `ADMIN_PASSWORD`, and `USER_PASSWORD`.

3. Start backend (in one terminal):

```powershell
# run Flask app
python run.py
```

4. Start frontend dev server (in a second terminal):

```powershell
cd frontend
npm install
npm run dev
```

Open the frontend at http://localhost:5173 — the frontend proxies `/api` to `http://127.0.0.1:5000`.

PowerShell Run Guide (Teacher Demo)

Use two PowerShell terminals.

Terminal 1: Backend (Flask)

```powershell
Set-Location "c:\Users\luhag\phisguard project"
.\.venv\Scripts\Activate
python run.py
```

Expected:
- Backend starts on `http://127.0.0.1:5000`

Terminal 2: Frontend (React + Vite)

```powershell
Set-Location "c:\Users\luhag\phisguard project\frontend"
npm install
npm run dev
```

Expected:
- Frontend starts on `http://localhost:5173`

Open in browser:
- Main app for demo: `http://localhost:5173`

Login credentials for demonstration:
- User password: `user` (name can be any non-empty value)
- Admin password: `admin`

If .env is configured, those values override defaults.

Quick troubleshooting:
- If backend fails to import app modules, make sure Terminal 1 is in `c:\Users\luhag\phisguard project`.
- If frontend cannot load data, check Terminal 1 is running and reachable at `127.0.0.1:5000`.
- If you see `401 unauthorized` after code changes, the backend may have auto-restarted (tokens are in-memory). Log in again.
- If `npm run dev` exits, port `5173` may already be in use. Try `npm run dev -- --port 5174`.

Build for production (so Flask can serve static files):

```powershell
cd frontend
npm run build
# then start backend
python run.py
# open http://127.0.0.1:5000
```

Notes
- Feedback Summary: http://localhost:5173/feedback
- API spec: docs/API_SPEC.md.

Docker (local deployment)

1. Create `.env` from `.env.example` and set secrets.

2. Build and run:

```powershell
docker compose up --build
```

3. Open the app at http://localhost:5173

Notes:
- The backend runs on http://localhost:5000
- The frontend preview server proxies `/api` to the backend inside Docker.

Assumptions & Limits
- This is a safe simulation tool; it does not send real emails or SMS.
- Local development only; no production hardening (rate limits, hardened auth) is included.
- Tokens are in-memory for local development; restarting the backend resets active sessions.

Outbound Email (optional)

PHISGUARD can optionally send real outbound simulation emails via SMTP when dispatching campaigns.

Set these environment variables:
- SMTP_HOST
- SMTP_PORT (use `587` for STARTTLS, `465` for implicit TLS)
- SMTP_USERNAME (optional)
- SMTP_PASSWORD (optional)
- SMTP_FROM_EMAIL

Behavior:
- Subjects are prefixed with `[SIMULATION]`.
- Links in outbound emails are safe and point back to the app (e.g. `/l/<email_id>`), which records a click and redirects to `/phished` or `/safe-link`.
- If SMTP is not configured (or sending fails), campaigns still run as in-app simulations and tracking continues.

Resources / Environment
- Python 3.10+ with Flask + SQLAlchemy
- Node.js 18+ for the React frontend
- SQLite database for local development

Evaluation Metrics (suggested targets)
- Detection accuracy improves by >=20% after training
- False positives (reporting legitimate messages) reduced by >=10%
- User-reported confidence improves by >=1 point on a 5-point Likert scale

Alternatives Considered
- GoPhish (feature-rich but heavy for coursework and focused on real email delivery)
- Custom simulator (chosen to keep simulations ethical and fully controlled)