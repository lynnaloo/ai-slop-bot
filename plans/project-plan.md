# AI Slop Bot — Project Plan

> Detect AI-generated "slop" in images, URLs, and text. Returns a 0–100 slop score with a per-category breakdown driven by a customizable YAML rubric.

---

## What It Does

- **Web app**: Paste a URL, upload an image, or paste text → get a slop score + breakdown
- **Slack bot**: `/slopcheck <url or text>`, `@slop-bot <content>`, or auto-scan configured channels
- **Customizable rubric**: Edit `backend/rubric.yaml` to add/remove/weight detection categories — no code changes needed

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.12, FastAPI |
| AI | Google Gemini `gemini-3.1-pro-preview` (configurable via `GEMINI_MODEL` env var) |
| Frontend | React 18 + TypeScript, Vite, TanStack Query, Recharts |
| Slack | `slack-bolt` (async), HTTP mode mounted on FastAPI |
| Deployment | Google Cloud Run (API), Firebase Hosting (frontend) |
| Rubric | `backend/rubric.yaml` — versioned in repo, hot-reloadable |

---

## Repository Layout

```
ai-slop-bot/
├── plan.md                         ← you are here
├── .env.example                    ← copy to .env and fill in secrets
├── .gitignore
├── docker-compose.yml              ← local dev
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── rubric.yaml                 ← edit this to customize detection
│   │
│   └── app/
│       ├── main.py                 ← FastAPI app + Slack mount
│       ├── config.py               ← all settings (reads .env)
│       ├── core/
│       │   ├── analyzer.py         ← main pipeline (shared by API + Slack)
│       │   ├── gemini_client.py    ← Gemini API wrapper
│       │   ├── rubric_loader.py    ← loads/validates/hot-reloads rubric
│       │   ├── scorer.py           ← weighted score math
│       │   └── fetcher.py          ← URL fetch + Playwright screenshot
│       ├── models/
│       │   ├── request.py          ← Pydantic request/response models
│       │   └── rubric.py           ← Pydantic rubric schema
│       ├── routers/
│       │   ├── analyze.py          ← POST /api/analyze
│       │   └── rubric.py           ← GET /api/rubric, POST /api/rubric/reload
│       └── slack/
│           ├── bot.py              ← Slack Bolt handlers
│           └── formatters.py       ← AnalysisResult → Block Kit card
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.tsx
│       ├── api/client.ts           ← typed fetch wrapper
│       ├── types/api.ts            ← mirrors of backend Pydantic models
│       ├── hooks/useAnalyze.ts     ← TanStack Query useMutation
│       └── components/
│           ├── SubmitForm/         ← tabs: URL | Image | Text
│           ├── ScoreGauge/         ← SVG arc gauge (green/amber/red)
│           ├── CategoryBreakdown/  ← bar chart + expandable reasoning
│           └── ResultCard/         ← full result container
│
└── deploy/
    ├── cloudbuild.yaml
    └── service-api.yaml            ← Cloud Run service definition
```

---

## Rubric Format (`backend/rubric.yaml`)

The rubric drives all detection. Each category gets scored 0–10 by Gemini; scores are weighted into a 0–100 composite.

```yaml
version: "1.0.0"
categories:
  - id: generic_phrasing
    label: "Generic Phrasing"
    weight: 0.20           # must sum to 1.0 across all categories
    applies_to: [text, url]  # or [image, url], or [text, url, image]
    prompt: |
      Score 0–10: How much does this content use hollow filler language?
      ...
```

**Rules:**
- `applies_to`: categories not applicable to the input type are skipped; score renormalized automatically
- Weights are auto-normalized (with a warning) if they don't sum to 1.0
- Hot-reload: `POST /api/rubric/reload` applies rubric changes without restarting

---

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/analyze` | POST (multipart) | Analyze a URL, image, or text |
| `/api/rubric` | GET | View the current rubric |
| `/api/rubric/reload` | POST | Hot-reload rubric from disk |
| `/health` | GET | Healthcheck (Cloud Run) |
| `/slack/events` | POST | Slack event webhook |

**Analyze request fields:**
- `input_type`: `"url"` \| `"image"` \| `"text"`
- `url` / `text` / `image` (file upload): the content

**Analyze response:**
```json
{
  "score": 73,
  "verdict": "Likely AI Slop",
  "categories": [
    { "id": "generic_phrasing", "label": "Generic Phrasing",
      "raw_score": 8, "weighted_score": 16.0, "weight": 0.20,
      "reasoning": "Multiple instances of filler phrases..." }
  ],
  "rubric_version": "1.0.0",
  "model": "gemini-3.1-pro-preview",
  "analysis_ms": 2341
}
```

---

## Slack Bot

| Trigger | How to use |
|---|---|
| Slash command | `/slopcheck https://example.com/article` |
| App mention | `@slop-bot https://example.com/article` |
| Auto-scan | Set `SLACK_AUTO_SCAN_CHANNELS`; bot flags posts scoring ≥ `AUTO_SCAN_THRESHOLD` (default 70) |

---

## Score Thresholds

| Score | Verdict | Gauge color |
|---|---|---|
| 0–30 | Probably Human | Green |
| 31–60 | Uncertain | Amber |
| 61–100 | Likely AI Slop | Red |

---

## Environment Variables

Copy `.env.example` → `.env` and fill in:

```bash
# Required
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.1-pro-preview

# Slack (optional — only needed for bot)
SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
SLACK_AUTO_SCAN_CHANNELS=C1234,C5678
AUTO_SCAN_THRESHOLD=70

# App
RUBRIC_PATH=rubric.yaml
CORS_ORIGINS=http://localhost:5173
PORT=8080
```

---

## Local Development

```bash
# Copy and fill in secrets
cp .env.example .env

# Start everything
docker-compose up

# Or run individually:
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

---

## Deployment (Google Cloud Run + Firebase Hosting)

1. **Backend** → Cloud Run (single service, `min-instances: 1` for Slack reliability)
2. **Frontend** → Firebase Hosting (static SPA)
3. Secrets in GCP Secret Manager

```bash
# Deploy backend
gcloud run deploy ai-slop-api --source ./backend --region us-central1

# Deploy frontend
cd frontend && npm run build && firebase deploy
```

---

## Implementation Phases

- [x] Plan
- [ ] Core pipeline: rubric → Gemini → scorer → analyzer
- [ ] FastAPI routes
- [ ] React frontend
- [ ] Slack bot
- [ ] Docker + Cloud Run deploy

---

## Key Design Decisions

**Single Gemini call per analysis** — all applicable rubric categories are bundled into one prompt with structured JSON output. ~10× cheaper and ~5× faster than one call per category.

**Shared analyzer core** — the Slack bot and web API both call `analyzer.analyze()`. No duplicated detection logic.

**Playwright for URL screenshots** — full-page screenshots let Gemini evaluate visual AI image artifacts on web pages, not just text. Uses `mcr.microsoft.com/playwright/python` base image to keep Docker layer size reasonable.
