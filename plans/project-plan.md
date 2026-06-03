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
| AI | Google Gemini `gemini-2.5-flash` (configurable via `GEMINI_MODEL` env var) |
| Frontend | React 18 + TypeScript, Vite, TanStack Query, Recharts |
| Slack | `slack-bolt` (async), HTTP mode mounted on FastAPI |
| Deployment | Google Cloud Run (API), Firebase Hosting (frontend) |
| Rubric | `backend/rubric.yaml` — versioned in repo, hot-reloadable |

---

## Repository Layout

```
ai-slop-bot/
├── plans/project-plan.md           ← you are here
├── .env.example                    ← copy to .env and fill in secrets
├── .gitignore
├── firebase.json                   ← Firebase Hosting + Cloud Run rewrites
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

The rubric drives all detection. Tuned for evaluating demos and sample apps. Two failure tiers:

**Tier 1 — Polished but Hollow** (well-prompted, functional, unmodified)

| Category | Weight | What It Detects |
|---|---|---|
| No Signs of Human Iteration | 20% | Frictionless output — no pivots, no "why", identical depth everywhere |
| No Real Problem Being Solved | 20% | Todo/weather/blog apps that demo a tech, not solve a real need |
| Absent Engineering Voice | 10% | Every decision is the blandest default; no opinions or tradeoffs |

**Tier 2 — Generated and Abandoned** (shipped without review)

| Category | Weight | What It Detects |
|---|---|---|
| Broken or Incomplete Implementation | 20% | Missing imports, unwired handlers, non-existent endpoints |
| Placeholder & Fake Data | 15% | Lorem ipsum, John Doe, YOUR_API_KEY_HERE left in |
| Cosmetic Error Handling | 15% | `catch (e) {}`, spinners that never resolve, silent failures |

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
| `/health` | GET | Healthcheck for Cloud Run |
| `/slack/events` | POST | Slack event webhook |

---

## Score Thresholds

| Score | Verdict | Gauge color |
|---|---|---|
| 0–30 | Probably Human | Green |
| 31–60 | Uncertain | Amber |
| 61–100 | Likely AI Slop | Red |

---

## Environment Variables

```bash
# Required
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

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
cp .env.example .env   # fill in GEMINI_API_KEY

cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
# → http://localhost:5173
```

---

## Deployment

### Backend — Google Cloud Run ✅ DONE
- Project: `ehc-c-buskey-506b97`
- Service: `ai-slop-api`
- Region: `us-central1`
- URL: `https://ai-slop-api-lxxfdfgvoq-uc.a.run.app`
- Secrets in GCP Secret Manager: `gemini-api-key`

To redeploy after code changes:
```bash
gcloud run deploy ai-slop-api \
  --source ./backend \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --min-instances 1 \
  --memory 2Gi \
  --set-env-vars GEMINI_MODEL=gemini-2.5-flash \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --project ehc-c-buskey-506b97
```

### Frontend — Firebase Hosting ✅ DONE
- Site: `ai-slop-detector`
- URL: `https://ai-slop-detector.web.app`
- `/api/**` rewrites automatically proxied to Cloud Run (see `firebase.json`)

To redeploy after frontend changes:
```bash
cd frontend && npm run build && cd ..
firebase deploy --only hosting:ai-slop-detector
```

---

## Implementation Phases

- [x] Core pipeline: rubric → Gemini → scorer → analyzer
- [x] FastAPI routes (`/api/analyze`, `/api/rubric`, `/health`)
- [x] React frontend (SubmitForm, ScoreGauge, CategoryBreakdown, ResultCard)
- [x] Backend deployed to Cloud Run
- [x] Frontend deployed to Firebase Hosting (`https://ai-slop-detector.web.app`)
- [ ] **Slack bot** — see details below
- [ ] Smoke test (`backend/scripts/test_analysis.py`)

---

## Slack Bot — TODO

The code is written (`backend/app/slack/bot.py`, `backend/app/slack/formatters.py`) and wired into the FastAPI app. It activates automatically when `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` are set. What still needs to be done:

### Step 1 — Create a Slack App
1. Go to **https://api.slack.com/apps** → **Create New App** → **From scratch**
2. Name it `slop-bot`, select your workspace
3. Under **OAuth & Permissions → Scopes**, add these **Bot Token Scopes**:
   - `app_mentions:read` — receive @mentions
   - `chat:write` — post messages
   - `commands` — receive slash commands
   - `channels:history` — read messages for auto-scan
   - `groups:history` — read messages in private channels (if needed)
4. Click **Install to Workspace** → copy the **Bot User OAuth Token** (`xoxb-...`)

### Step 2 — Configure Event Subscriptions
1. Under **Event Subscriptions** → enable events
2. Set the **Request URL** to:
   ```
   https://ai-slop-api-lxxfdfgvoq-uc.a.run.app/slack/events
   ```
   Slack will send a challenge request — the app handles it automatically.
3. Under **Subscribe to bot events** add:
   - `app_mention`
   - `message.channels` (for auto-scan)

### Step 3 — Add the Slash Command
1. Under **Slash Commands** → **Create New Command**
2. Command: `/slopcheck`
3. Request URL: `https://ai-slop-api-lxxfdfgvoq-uc.a.run.app/slack/events`
4. Short description: `Check content for AI slop`
5. Usage hint: `<url or text>`

### Step 4 — Get the Signing Secret
1. Under **Basic Information → App Credentials** → copy the **Signing Secret**

### Step 5 — Add Secrets to GCP and Redeploy
```bash
# Add the secrets
echo -n "xoxb-your-bot-token" | gcloud secrets create slack-bot-token --data-file=- --project ehc-c-buskey-506b97
echo -n "your-signing-secret" | gcloud secrets create slack-signing-secret --data-file=- --project ehc-c-buskey-506b97

# Redeploy with Slack secrets wired in
gcloud run deploy ai-slop-api \
  --source ./backend \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --min-instances 1 \
  --memory 2Gi \
  --set-env-vars GEMINI_MODEL=gemini-2.5-flash \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest,SLACK_BOT_TOKEN=slack-bot-token:latest,SLACK_SIGNING_SECRET=slack-signing-secret:latest \
  --project ehc-c-buskey-506b97
```

### Step 6 — Configure Auto-Scan Channels (optional)
Set `SLACK_AUTO_SCAN_CHANNELS` to a comma-separated list of channel IDs where the bot should silently monitor for URLs and flag anything scoring ≥ 70:
```bash
gcloud run services update ai-slop-api \
  --region us-central1 \
  --update-env-vars SLACK_AUTO_SCAN_CHANNELS=C1234567,C7654321 \
  --project ehc-c-buskey-506b97
```

### Step 7 — Test
```
/slopcheck https://some-demo-app.com
@slop-bot check this text for slop
```

---

## Key Design Decisions

**Single Gemini call per analysis** — all applicable rubric categories bundled into one prompt with structured JSON output. ~10× cheaper and ~5× faster than one call per category.

**Shared analyzer core** — the Slack bot and web API both call `analyzer.analyze()`. No duplicated detection logic.

**Playwright for URL screenshots** — full-page screenshots let Gemini evaluate visual AI image artifacts on web pages, not just text.
