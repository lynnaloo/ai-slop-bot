# AI Slop Bot — Project Plan

Detect AI-generated "slop" in images, URLs, and text. Returns a 0–100 slop score with a per-category breakdown driven by a customizable YAML rubric.

## What It Does

- **Web app**: Paste a URL, upload an image, or paste text → get a slop score + breakdown
- **Slack bot**: `/slopcheck`, `@slop-bot`, or auto-scan configured channels
- **Customizable rubric**: Edit `backend/rubric.yaml` to add/remove/weight detection categories without code changes

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.12, FastAPI |
| AI | Google Gemini `gemini-2.5-flash` (configurable via `GEMINI_MODEL`) |
| Frontend | React 18 + TypeScript, Vite, TanStack Query |
| Auth | Firebase Auth (Google Sign-In, restricted to `@salesforce.com`) |
| Proxy | Firebase Function forwards Firebase tokens as OIDC tokens to Cloud Run |
| Slack | `slack-bolt` async, HTTP mode mounted on FastAPI |
| Deployment | Google Cloud Run (API), Firebase Hosting + Functions (frontend) |
| Rubric | `backend/rubric.yaml`, versioned in repo, hot-reloadable |

## Repository Layout

```
ai-slop-bot/
├── plans/project-plan.md
├── .env.example
├── firebase.json
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── rubric.yaml
│   └── app/
│       ├── main.py                 FastAPI app + Slack mount
│       ├── config.py               all settings (reads .env)
│       ├── core/
│       │   ├── analyzer.py         main pipeline (shared by API + Slack)
│       │   ├── gemini_client.py    Gemini API wrapper
│       │   ├── rubric_loader.py    loads/validates/hot-reloads rubric
│       │   ├── scorer.py           weighted score math
│       │   └── fetcher.py          URL fetch + Playwright screenshot
│       ├── models/
│       ├── routers/
│       └── slack/
│           ├── bot.py              Slack Bolt handlers
│           └── formatters.py       AnalysisResult → Block Kit card
├── functions/
│   └── index.js                    Firebase Function proxy
└── frontend/
    └── src/
        ├── firebase.ts             Firebase Auth setup
        ├── hooks/useAuth.ts        auth state
        ├── api/client.ts           attaches Firebase token to requests
        └── components/
```

## Rubric (`backend/rubric.yaml`)

**Tier 1: Polished but Hollow**

| Category | Weight | Detects |
|---|---|---|
| No Signs of Human Iteration | 20% | Frictionless output, no pivots, no "why" |
| No Real Problem Being Solved | 20% | Demos that exist to showcase tech, not solve a need |
| Absent Engineering Voice | 10% | Blandest-default decisions with no tradeoffs visible |

**Tier 2: Generated and Abandoned**

| Category | Weight | Detects |
|---|---|---|
| Broken or Incomplete Implementation | 20% | Missing imports, unwired handlers |
| Placeholder & Fake Data | 15% | Lorem ipsum, John Doe, YOUR_API_KEY_HERE |
| Cosmetic Error Handling | 15% | `catch (e) {}`, spinners that never resolve |

Weights auto-normalize if they don't sum to 1.0. Categories not applicable to the input type are skipped and the score is renormalized. Hot-reload via `POST /api/rubric/reload`.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/analyze` | POST multipart | Analyze a URL, image, or text |
| `/api/rubric` | GET | View current rubric |
| `/api/rubric/reload` | POST | Hot-reload rubric from disk |
| `/health` | GET | Cloud Run healthcheck |
| `/slack/events` | POST | Slack event webhook |

## Auth Architecture

The Salesforce GCP org blocks unauthenticated Cloud Run access (`allUsers` invoker is disallowed by org policy). The workaround:

1. User signs in via Firebase Auth (Google, restricted to `@salesforce.com`)
2. Frontend attaches the Firebase ID token to every API request
3. Firebase Function (`functions/index.js`) verifies the Firebase token, then calls Cloud Run using a Google OIDC token scoped to the Cloud Run service URL
4. Cloud Run accepts the OIDC token because the Function's service account has `roles/run.invoker`

## Deployment

### Backend (Cloud Run) ✅

Service: `ai-slop-api` / Region: `us-central1`
URL: `https://ai-slop-api-lxxfdfgvoq-uc.a.run.app`

```bash
gcloud run deploy ai-slop-api \
  --source ./backend \
  --region us-central1 \
  --platform managed \
  --min-instances 1 \
  --memory 2Gi \
  --set-env-vars GEMINI_MODEL=gemini-2.5-flash \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --project ehc-c-buskey-506b97
```

### Frontend + Functions (Firebase) ✅

Site: `https://ai-slop-detector.web.app`

```bash
cd functions && npm install && cd ..
cd frontend && npm run build && cd ..
firebase deploy --only functions,hosting:ai-slop-detector
```

## Implementation Status

- [x] Core pipeline: rubric → Gemini → scorer → analyzer
- [x] FastAPI routes
- [x] React frontend with Google Sign-In
- [x] Firebase Function proxy
- [x] Backend deployed to Cloud Run
- [x] Frontend + Functions deployed to Firebase
- [ ] Slack bot (see below)
- [ ] Smoke test (`backend/scripts/test_analysis.py`)

## Slack Bot Setup (TODO)

Code is written in `backend/app/slack/`. Activates automatically when `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` are present.

**Step 1: Create a Slack App**
1. Go to https://api.slack.com/apps → Create New App → From scratch
2. Name it `slop-bot`, select your workspace
3. Under OAuth & Permissions → Bot Token Scopes, add:
   - `app_mentions:read`
   - `chat:write`
   - `commands`
   - `channels:history`
4. Install to Workspace, copy the Bot User OAuth Token (`xoxb-...`)

**Step 2: Configure Event Subscriptions**
1. Enable events, set Request URL to `https://ai-slop-api-lxxfdfgvoq-uc.a.run.app/slack/events`
2. Subscribe to bot events: `app_mention`, `message.channels`

**Step 3: Add Slash Command**
1. Slash Commands → Create New Command
2. Command: `/slopcheck`, Request URL: `https://ai-slop-api-lxxfdfgvoq-uc.a.run.app/slack/events`

**Step 4: Get the Signing Secret**

Basic Information → App Credentials → copy Signing Secret

**Step 5: Add Secrets and Redeploy**

```bash
echo -n "xoxb-..." | gcloud secrets create slack-bot-token --data-file=- --project ehc-c-buskey-506b97
echo -n "your-signing-secret" | gcloud secrets create slack-signing-secret --data-file=- --project ehc-c-buskey-506b97

gcloud run deploy ai-slop-api \
  --source ./backend \
  --region us-central1 \
  --platform managed \
  --min-instances 1 \
  --memory 2Gi \
  --set-env-vars GEMINI_MODEL=gemini-2.5-flash \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest,SLACK_BOT_TOKEN=slack-bot-token:latest,SLACK_SIGNING_SECRET=slack-signing-secret:latest \
  --project ehc-c-buskey-506b97
```

**Step 6: Optional Auto-Scan**

```bash
gcloud run services update ai-slop-api \
  --region us-central1 \
  --update-env-vars "^:^SLACK_AUTO_SCAN_CHANNELS=C1234567:C7654321" \
  --project ehc-c-buskey-506b97
```

**Step 7: Test**
```
/slopcheck https://some-demo-app.com
@slop-bot check this text for slop
```

## Key Design Decisions

**Single Gemini call per analysis**: all applicable rubric categories are bundled into one prompt with structured JSON output. Cheaper and faster than one call per category.

**Shared analyzer core**: the Slack bot and web API both call `analyzer.analyze()` with no duplicated logic.

**Firebase Function proxy**: required because the Salesforce org policy blocks `allUsers` Cloud Run access. The function bridges Firebase Auth tokens (audience: Firebase project) to OIDC tokens (audience: Cloud Run service URL).
