# AI Slop Bot

Python (FastAPI) backend, React + TypeScript frontend, Slack bot via `slack-bolt`. Auth via Firebase (Google Sign-In), proxied through a Firebase Function to Cloud Run.

## Stack
- **AI**: Google Gemini `gemini-2.5-flash` (configurable via `GEMINI_MODEL` env var)
- **Rubric**: `backend/rubric.yaml` — edit categories/weights here, hot-reload via `POST /api/rubric/reload`
- **Scoring**: single Gemini call returns all category scores as JSON; `scorer.py` applies weights
- **Auth**: Firebase Auth (Google Sign-In) + Firebase Function proxy to Cloud Run

## Running locally
```bash
cp .env.example .env
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
```

## Key files
- `backend/rubric.yaml` — rubric categories and weights
- `backend/app/core/analyzer.py` — shared analysis pipeline (API + Slack)
- `backend/app/core/gemini_client.py` — Gemini prompt construction
- `backend/app/slack/bot.py` — Slack event handlers
- `functions/index.js` — Firebase Function proxy (verifies Firebase token, calls Cloud Run with OIDC token)
- `frontend/src/firebase.ts` — Firebase Auth setup
