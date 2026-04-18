# PHISGUARD: Phishing Awareness Simulation Platform

A web-based phishing awareness training platform that simulates realistic phishing attacks via email and SMS to assess and improve user security awareness.

## Overview

PHISGUARD enables organizations to conduct controlled phishing simulations targeting their users. The platform tracks which users fall for simulations, reports their actions with metrics, and provides immediate feedback to help users recognize phishing attacks in real-world scenarios.

**Target Users:** Security teams and HR personnel managing company-wide security awareness programs.

---

## Technology Stack

### Backend
- **Framework:** Flask 3.1+ (Python web framework)
- **Database:** SQLAlchemy ORM with SQLite (default)
- **Authentication:** Token-based (24-hour expiration with rate limiting)
- **Database Migrations:** Alembic
- **Testing:** pytest 7.0+ with pytest-flask

### Frontend
- **Framework:** React 18.2 (JavaScript UI library)
- **Build Tool:** Vite 6.4
- **Routing:** React Router v6
- **Styling:** Tailwind CSS 3.4
- **Deployment Build:** Node.js / npm

### Security
- Rate limiting: 5 failed login attempts → 15-minute lockout
- Environment-based credentials (no hardcoded defaults)
- Token expiration (24 hours)
- CSRF protection available via Flask-Login

---

## Key Features Implemented

### For Users
- ✅ Email phishing simulation scenarios (click/report actions)
- ✅ SMS phishing simulation scenarios (click/report actions)
- ✅ Immediate feedback on actions taken (correct/incorrect assessment)
- ✅ Personal awareness dashboard (accuracy percentage, action history)
- ✅ Difficulty rating per scenario (easy, medium, hard)

### For Administrators
- ✅ Create and manage email templates
- ✅ Create and manage SMS templates
- ✅ Add simulation targets (users by name, email, department, role)
- ✅ Campaign creation with manual state transitions (draft → scheduled → active → completed/archived)
- ✅ On-demand analytics dashboard (computed when requested)
- ✅ Per-user performance reports (accuracy, response times, action history)
- ✅ Campaign metrics (open rate, click rate, report rate, time-to-action)

### Technical
- ✅ 49 automated unit tests (auth, simulations, admin)
- ✅ Role-based access control (user/admin)
- ✅ Persistent session tracking with token expiration
- ✅ Database migration support via Alembic

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 16+ (for frontend build)
- Git

### Backend Setup

```bash
# 1. Clone and navigate
git clone <repository-url>
cd phisguard

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and set ADMIN_PASSWORD, USER_PASSWORD, SECRET_KEY

# 5. Initialize database
python create_db.py

# 6. Run backend server
python run.py
# Backend runs on: http://127.0.0.1:5000
```

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
# Frontend runs on: http://127.0.0.1:5173 (dev proxy to backend)

# 4. Build for production (optional)
npm run build
# Output: frontend/dist/
```

### Important: Configure .env

Create a `.env` file from `.env.example` and set:
```env
ADMIN_PASSWORD=<strong_password>
USER_PASSWORD=<strong_password>
SECRET_KEY=<random_secret>
```

The application **will not start** without these environment variables.

---

## Database Architecture

This project uses a **hybrid initialization strategy** combining SQLAlchemy ORM with optional Alembic migrations:

**How it works:**
1. **SQLAlchemy models** (app/models/*.py) define the schema as the source of truth
2. **db.create_all()** (called on startup) creates all tables from model definitions
3. **Alembic migration** (migrations/versions/bb87c67e8f62_initial.py) exists for reference but is **not auto-applied**
4. **Schema repair helpers** (ensure_*_column functions) gracefully patch any schema gaps on startup

**Why this approach?**
- Models-first is simpler for a development/academic project
- db.create_all() works reliably for clean database initialization
- Schema repair helpers provide flexibility if the codebase evolves during development
- Alembic migration is available for production deployments that need versioned schema control

**For this submission:**
- Simply run the application; no manual migration steps are needed
- Database is created automatically in `instance/app.db`
- Tests use in-memory SQLite (instant, isolated)

**Database Location:**
- Development: `instance/app.db` (SQLite file, created on first run)
- Testing: In-memory SQLite (config: `app/test_config.py`)

---

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
# Output: 49 passing tests in ~1.3 seconds
```

### Run Specific Test Suite
```bash
pytest tests/test_auth.py -v          # Authentication tests
pytest tests/test_simulate.py -v      # Simulation tests
pytest tests/test_admin.py -v         # Admin feature tests
```

### Run with Coverage (optional)
```bash
pip install coverage
pytest tests/ --cov=app --cov-report=html
# Opens: htmlcov/index.html
```

**Test Coverage:**
- 14 Authentication tests (login, rate limiting, tokens, logout)
- 18 Simulation tests (email/SMS scenarios, actions, awareness, feedback)
- 17 Admin tests (authorization, templates, targets, campaigns, analytics)

---

## Project Limitations

### By Design
1. **Single Shared Password:** All regular users share one password. No individual user registration or multi-factor authentication.
2. **In-Memory Rate Limiting:** Failed login attempts tracked in-memory; resets on server restart (lockout data is not persistent).
3. **Email Delivery:** SMTP configuration optional. Without SMTP, campaigns run in-app only (no external emails sent to targets).
4. **Static Email/SMS Scenarios:** Phishing scenarios are pre-seeded on app startup (~10 email + ~8 SMS); no dynamic scenario generation.
5. **On-Demand Analytics:** Metrics are computed dynamically when requested (not logged or cached); no background dashboards.
6. **Manual Campaign Transitions:** Campaign state changes (scheduled → active, active → completed, etc.) require manual admin API calls; no background scheduler.

### Known Constraints
1. **Database:** SQLite (suitable for SMB/testing; scale to PostgreSQL for production at scale).
2. **Frontend Build:** Client-side routing; no Server-Side Rendering.
3. **Manual Theming:** No built-in theme editor; styling changes require direct Tailwind CSS edits.
4. **No Scheduling System:** No background job processor; campaign auto-activation requires manual admin action or polling.

---

## Ethical & Safety Boundaries

### How This Platform is Intended to be Used
✅ **Legitimate Uses:**
- Internal security awareness training with explicit employee consent
- Measuring organizational phishing resilience
- Controlled educational environment for security training
- Authorized red-team / penetration testing exercises

### Strict Prohibitions
❌ **Not Permitted:**
- Phishing real users without informed consent
- Using this platform for social engineering outside a legitimate company context
- Deploying simulations against external users or organizations
- Impersonating authority figures to coerce users
- Capturing user credentials for malicious purposes
- Using SMTP configuration to spam external recipients

### Data Protection
✅ **What the Platform Does:**
- Records only: user ID, action taken, timestamp, whether assessment was correct
- Stores no personal data beyond what users provide
- Does not capture email passwords, card numbers, or sensitive PII beyond simulation context

✅ **Admin Responsibilities:**
- Inform employees in writing that phishing simulations will occur
- Use results only for training, not disciplinary action
- Securely manage `.env` credentials
- Comply with local data protection laws (GDPR, CCPA, etc.)

---

## Project Structure

```
phisguard/
├── app/                    # Flask application (backend)
│   ├── blueprints/        # Route handlers (auth, admin, simulate, views)
│   ├── models/            # SQLAlchemy ORM models
│   ├── services/          # Business logic (auth, email, detector)
│   └── config.py          # Flask configuration
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── styles/        # Tailwind CSS
│   └── vite.config.js     # Vite build config
├── migrations/            # Alembic database migrations
├── templates/             # HTML templates (email, feedback, inbox)
├── tests/                 # pytest test suite (49 tests)
├── requirements.txt       # Python dependencies
├── package.json           # Node.js dependencies (frontend)
├── run.py                 # Backend entry point
└── README.md             # This file
```

---

## API Endpoints (Summary)

### Authentication
- `POST /api/login` — Login with password and role
- `POST /api/logout` — Logout and revoke token

### User Endpoints
- `GET /api/emails` — List phishing scenarios (email)
- `POST /api/emails/<id>/open` — Record email open
- `POST /api/emails/<id>/click` — Record email click (with feedback)
- `POST /api/emails/<id>/report` — Report email as phishing (with feedback)
- `GET /api/sms` — List phishing scenarios (SMS)
- `GET /api/awareness` — Get user awareness metrics
- `GET /api/feedback` — Get user action history with feedback

### Admin Endpoints (require admin token)
- `GET /api/templates` — List email templates
- `POST /api/templates` — Create email template
- `POST /api/targets` — Create simulation targets (users)
- `POST /api/campaigns` — Create campaign (in draft or active state)
- `POST /api/campaigns/<id>/schedule` — Transition campaign from draft to scheduled
- `POST /api/campaigns/<id>/activate` — Transition campaign from scheduled to active
- `POST /api/campaigns/<id>/complete` — Mark campaign as completed
- `POST /api/campaigns/auto_activate` — Transition all due scheduled campaigns to active
- `GET /api/analytics` — Get advanced campaign and user analytics

---

## Troubleshooting

### Backend won't start: "Authentication credentials missing"
**Solution:** Create `.env` file with `ADMIN_PASSWORD`, `USER_PASSWORD`, and `SECRET_KEY`.

### Frontend can't reach backend
**Solution:** Ensure backend runs on `http://127.0.0.1:5000` and frontend dev server has proxy configured in `vite.config.js`.

### Tests fail with database errors
**Solution:** Tests use in-memory SQLite. Run `pytest tests/ -v` with a clean Python environment.

### SMTP emails not sending
**Solution:** Configure SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD in `.env` and restart backend.

---

## Possible Future Enhancements

- [ ] Individual user accounts with password hashing + MFA
- [ ] JWT token refresh / longer-lived sessions
- [ ] Background scheduler (APScheduler/Celery) for automatic campaign transitions
- [ ] LDAP/Active Directory integration for enterprise user import
- [ ] Real-time metrics caching (Redis) for faster analytics
- [ ] Multi-language template support
- [ ] Mobile app for SMS- and email-based simulations
- [ ] Webhook integrations for SOAR platforms (Splunk, Palo Alto)
- [ ] Campaign pause/resume functionality

---

## Academic Context

This project is developed as a **final-year computer science project** focusing on:
- Secure authentication and session management
- Full-stack web application architecture (Flask + React)
- Database design and migrations
- Automated testing (pytest)
- Security awareness and ethical software development

---

## License

This project is provided **for educational and authorized organizational use only**. Use of this platform for unauthorized phishing attacks violates computer fraud laws in most jurisdictions.

---

## Disclaimer

This platform is designed to **simulate phishing attacks with explicit user consent**. The developers assume no liability for misuse, unauthorized deployment, or violations of local laws. Organizations using this platform are solely responsible for:
- Obtaining informed written consent from all targets
- Complying with data protection regulations
- Using results ethically and responsibly
- Protecting credentials and sensitive configuration

---

## Support

For issues or questions, refer to:
- [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) — Deployment checklist
- [tests/README.md](tests/README.md) — Testing guide
- [frontend/README_FRONTEND.md](frontend/README_FRONTEND.md) — Frontend-specific documentation
