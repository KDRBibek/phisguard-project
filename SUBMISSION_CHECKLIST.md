# Academic Submission Checklist

## Pre-Submission Cleanup

Before submitting your repository, ensure the following items are excluded from the final ZIP file.

---

## ❌ EXCLUDE FROM SUBMISSION

### Environment & Dependencies (Do NOT include)
- `.venv/` — Virtual environment directory (user will recreate with `pip install -r requirements.txt`)
- `venv/` — Alternative venv directory
- `frontend/node_modules/` — Node packages (user will run `npm install`)

### Build Artifacts (Do NOT include)
- `__pycache__/` — Python bytecode cache
- `.pytest_cache/` — Pytest cache files
- `frontend/dist/` — Built frontend (user will rebuild with `npm run build`)
- `frontend/.vite/` — Vite cache
- `build/` — Any Python build artifacts
- `dist/` — Any Python distribution files
- `*.egg-info/` — Package metadata

### Database Files (Do NOT include)
- `instance/app.db` — SQLite database file
- `instance/database.db` — Another SQLite database file
- `.db`, `.sqlite`, `.sqlite3` — Any database files
  - User can initialize fresh database using provided scripts

### Environment Secrets (NEVER include)
- `.env` — Local environment variables with credentials
  - Keep only `.env.example` as template
- `*.pem`, `*.key`, `*.p12`, `*.pfx` — Certificate/key files
- Any files in `secrets/` directory

### Version Control (Do NOT include)
- `.git/` — Git history directory
  - Repository will be submitted as ZIP without git history
  - Tutor will only see final code, not commit history

### System Files (Do NOT include)
- `.DS_Store` — macOS metadata
- `Thumbs.db` — Windows thumbnails
- `.vscode/` — VSCode workspace settings (optional - up to you)

### Logs (Do NOT include)
- `*.log` files in any directory
- `logs/` directory

### Temporary Files (Do NOT include)
- `*.pyc` — Compiled Python files
- `.mypy_cache/`, `.ruff_cache/` — Linter caches
- `.ipynb_checkpoints/` — Jupyter checkpoints (if any)

---

## ✅ INCLUDE IN SUBMISSION

### Source Code (MUST include)
```
app/
├── __init__.py
├── config.py
├── extensions.py
├── security.py
├── blueprints/
│   ├── __init__.py
│   ├── views.py
│   ├── admin/
│   ├── api/
│   ├── auth/
│   └── simulate/
├── models/
│   ├── __init__.py
│   ├── attempt.py
│   ├── campaign.py
│   ├── detection.py
│   ├── event.py
│   ├── feedback.py
│   ├── scenario.py
│   ├── session.py
│   └── user.py
└── services/
    ├── __init__.py
    ├── auth_store.py
    ├── detector.py
    └── mailer.py
```

### Configuration Files (MUST include)
- `requirements.txt` — Python dependencies
- `alembic.ini` — Database migration config
- `.env.example` — Template for environment variables (with NO secrets)
- `.gitignore` — Git ignore rules

### Database Migrations (MUST include)
```
migrations/
├── env.py
├── script.py.mako
└── versions/
    └── *.py
```

### Frontend Code (MUST include)
```
frontend/
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── components/
│   ├── pages/
│   ├── styles/
│   ├── data/
│   └── assets/
├── package.json
├── package-lock.json
├── vite.config.js
├── tailwind.config.cjs
├── postcss.config.cjs
├── index.html
└── README_FRONTEND.md
```

### Templates (MUST include)
```
templates/
├── email.html
├── feedback.html
└── inbox.html
```

### Documentation (MUST include)
- `README.md` — Main project README
- `docs/` — API documentation, reports, etc.
- `tests/README.md` — Testing documentation

### Test Suite (MUST include)
```
tests/
├── conftest.py
├── test_auth.py
├── test_admin.py
├── test_simulate.py
├── __init__.py
└── README.md
```

### Root Files (MUST include)
- `run.py` — Application entry point
- `app.py` — Alternative entry point

### Migration Tools (MUST include)
- `alembic.ini` — Alembic config for database migrations

---

## 📋 Quick Cleanup Commands

### For ZIP Submission (Windows PowerShell)

```powershell
# Remove environment
Remove-Item -Recurse -Force .venv
Remove-Item -Recurse -Force venv

# Remove caches
Remove-Item -Recurse -Force __pycache__
Remove-Item -Recurse -Force .pytest_cache
Remove-Item -Recurse -Force frontend/node_modules
Remove-Item -Recurse -Force frontend/dist
Remove-Item -Recurse -Force .vscode

# Remove database files
Remove-Item -Force instance/*.db
Remove-Item -Force instance/*.sqlite*

# Remove local .env (keep .env.example)
Remove-Item -Force .env

# Verify git history isn't included
Remove-Item -Recurse -Force .git
```

### For ZIP Submission (Linux/macOS)

```bash
# Remove environment
rm -rf .venv venv

# Remove caches
rm -rf __pycache__ .pytest_cache
rm -rf frontend/node_modules frontend/dist
rm -rf .vscode

# Remove database files
rm -f instance/*.db instance/*.sqlite*

# Remove local .env (keep .env.example)
rm -f .env

# Remove git history
rm -rf .git
```

---

## 🎯 Submission Structure

**Ideal submission ZIP should contain:**

```
phisguard-submission/
├── app/                          (All source code)
├── frontend/                     (All frontend code, NO node_modules)
├── migrations/                   (Database migrations)
├── templates/                    (HTML templates)
├── tests/                        (Test suite)
├── docs/                         (Documentation)
├── requirements.txt              (Python dependencies)
├── .env.example                  (Template only, NO secrets)
├── .gitignore                    (For reference)
├── alembic.ini
├── run.py
├── app.py
└── README.md
```

**ZIP Size Target:** ~2-5 MB (without node_modules and venv)

---

## ✓ Final Pre-Submission Checklist

- [ ] Removed `.venv/` and `venv/` directories
- [ ] Removed `frontend/node_modules/` directory
- [ ] Removed `frontend/dist/` and `.pytest_cache/` directories
- [ ] Removed all `__pycache__/` directories
- [ ] Removed local `.env` file (keep `.env.example`)
- [ ] Removed database files from `instance/` directory
- [ ] Verified `.env.example` contains NO real credentials
- [ ] Verified `requirements.txt` is complete and accurate
- [ ] Verified test suite runs successfully: `pytest tests/`
- [ ] Verified README files are present and readable
- [ ] Verified source code has no debug/print statements
- [ ] Confirmed `.gitignore` excludes all unwanted files
- [ ] Ready to create ZIP file for submission

---

## 📝 Student Running Your Code

After unzipping, they should simply:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env
# Edit .env with their own credentials

# 3. Initialize database
python create_db.py

# 4. Run the application
python run.py
```

They should NOT need to:
- Recreate venv/virtualenv (pip install handles this)
- Rebuild frontend (next step will handle this)
- Worry about missing dependencies

---

## 📚 References

- **Size Check:** Use `7-Zip` or `WinRAR` to verify ZIP is ~2-5 MB
- **Integrity Check:** Extract ZIP to a fresh folder and verify it opens
- **Run Test:** Ensure tutor can run `pytest tests/` after fresh extraction
