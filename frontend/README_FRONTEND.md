Frontend (Vite + React + Tailwind)

Setup

1. From project root, open a terminal and run:

```powershell
cd frontend
npm install
```

2. Development server:

```powershell
npm run dev
```

The Vite dev server proxies `/api` to the Flask backend (configured to `http://127.0.0.1:5000`).

3. Build for production:

```powershell
npm run build

# to preview the built site on port 5001
npm run preview
```

Notes
- This scaffold uses Tailwind CSS. To add `shadcn/ui` components you can run their setup inside this folder and wire components into `src/components`.
- After building, the static files will appear in `frontend/dist` and `app.py` serves them at `/`.

Feature Overview
- Home: overview and feedback summary gating
- Simulation: Email and SMS tabs with tips and safe feedback
- Feedback: user feedback history (stored in browser localStorage)
