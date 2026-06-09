# AI Slop Bot

Detects AI-generated "slop" in text, URLs, and images. Returns a 0–100 score with a per-category breakdown powered by Google Gemini.

Available as a **web app** and a **Slack bot** (`/slopcheck`, `@slop-bot`, or auto-scan channels).

Requires a `@salesforce.com` Google account to sign in.

## Default Rubric

Tuned for evaluating demos and sample apps across two failure tiers.

**Tier 1: Polished but Hollow** (well-prompted, functional, but unmodified)

| Category | Weight | What It Detects |
|---|---|---|
| No Signs of Human Iteration | 20% | Frictionless output with no pivots, no "why", identical depth everywhere |
| No Real Problem Being Solved | 20% | Todo/weather/blog apps that demo a tech, not solve a real need |
| Absent Engineering Voice | 10% | Every decision is the blandest default with no opinions or tradeoffs |

**Tier 2: Generated and Abandoned** (shipped without review or testing)

| Category | Weight | What It Detects |
|---|---|---|
| Broken or Incomplete Implementation | 20% | Missing imports, unwired handlers, references to non-existent endpoints |
| Placeholder & Fake Data | 15% | Lorem ipsum, John Doe, YOUR_API_KEY_HERE left in |
| Cosmetic Error Handling | 15% | `catch (e) {}`, spinners that never resolve, silent failures |

Customize categories and weights in [`backend/rubric.yaml`](backend/rubric.yaml).

## Score Thresholds

| Score | Verdict |
|---|---|
| 0–30 | Probably Human |
| 31–60 | Uncertain |
| 61–100 | Likely AI Slop |

## Local Development

```bash
cp .env.example .env
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
```

Open http://localhost:5173

## Deployment

### Backend (Google Cloud Run)

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

Service URL: `https://ai-slop-api-lxxfdfgvoq-uc.a.run.app`

### Frontend + Functions (Firebase)

```bash
cd functions && npm install && cd ..
cd frontend && npm run build && cd ..
firebase deploy --only functions,hosting:ai-slop-detector
```

Site URL: `https://ai-slop-detector.web.app`

> Requests go: browser → Firebase Function (verifies Firebase token) → Cloud Run (called with OIDC token). This works around the Salesforce org policy that blocks unauthenticated Cloud Run access.

### Adding Slack

See [plans/project-plan.md](plans/project-plan.md) for the full Slack setup walkthrough.

### Rotating the Gemini API Key

```bash
echo -n "your-new-key" | gcloud secrets versions add gemini-api-key --data-file=- --project ehc-c-buskey-506b97
```
