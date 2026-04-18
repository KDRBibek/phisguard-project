# PHISGUARD — How to Run (Tutor)

This project has two parts:
- Backend: Flask API (Python)
- Frontend: React app (Vite)

You run them in **two terminals**.

## Requirements

- Windows + PowerShell
- Python 3.10+ (recommended: 3.11+)
- Node.js 18+ (npm included)

## 1) Backend (Flask)

Open PowerShell in the project root (same folder as `run.py`).

If the virtual environment already exists:

```powershell
Set-Location "c:\Users\luhag\phisguard project"
.\.venv\Scripts\Activate
pip install -r requirements.txt
python run.py
```

If `.venv` does NOT exist yet:

```powershell
Set-Location "c:\Users\luhag\phisguard project"
py -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
python run.py
```

Expected:
- Backend runs on `http://127.0.0.1:5000`

## 2) Frontend (React + Vite)

Open a second PowerShell terminal:

```powershell
Set-Location "c:\Users\luhag\phisguard project\frontend"
npm install
npm run dev
```

Expected:
- Frontend runs on `http://localhost:5173`
- The frontend proxies `/api` calls to the backend (so backend must be running).

## Login (for marking/demo)

- User login:
  - Name: any non-empty name
  - Password: `user` (or `USER_PASSWORD` if set in `.env`)
- Admin login:
  - Password: `admin` (or `ADMIN_PASSWORD` if set in `.env`)

## Quick troubleshooting

- Backend import errors (example: `No module named 'app'`):
  - Make sure the backend terminal is in the project root: `c:\Users\luhag\phisguard project`
- Frontend shows empty data / API errors:
  - Confirm backend is running at `127.0.0.1:5000`
- `401 unauthorized` after backend code changes:
  - Flask auto-restart clears in-memory tokens; just log in again.
- `npm run dev` exits immediately:
  - Port `5173` might be busy → try: `npm run dev -- --port 5174`
