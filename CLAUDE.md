# AI Slop Bot

Python (FastAPI) backend, React + TypeScript frontend, Slack bot via `slack-bolt`.

## Stack
- **AI**: Google Gemini `gemini-3.1-pro-preview` (model configurable via `GEMINI_MODEL` env var)
- **Rubric**: `backend/rubric.yaml` — edit categories/weights here, hot-reload via `POST /api/rubric/reload`
- **Scoring**: single Gemini call returns all category scores as JSON; `scorer.py` applies weights

## Running locally
```bash
cp .env.example .env  # fill in GEMINI_API_KEY
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
```

## Key files
- `backend/rubric.yaml` — rubric categories and weights
- `backend/app/core/analyzer.py` — shared analysis pipeline (API + Slack)
- `backend/app/core/gemini_client.py` — Gemini prompt construction
- `backend/app/slack/bot.py` — Slack event handlers
