# AI Slop Bot

Detects AI-generated "slop" in text, URLs, and images. Returns a 0–100 score with a per-category breakdown powered by Google Gemini.

Available as a **web app** and a **Slack bot** (`/slopcheck`, `@slop-bot`, or auto-scan channels).

## Default Rubric

Tuned for evaluating demos and sample apps across two failure tiers.

**Tier 1 — Polished but Hollow** (well-prompted, functional, but unmodified)

| Category | Weight | What It Detects |
|---|---|---|
| No Signs of Human Iteration | 20% | Suspiciously frictionless — no commented-out code, no pivots, no "why" anywhere |
| No Real Problem Being Solved | 20% | Todo/weather/blog apps that exist to demo a tech, not solve a need |
| Absent Engineering Voice | 10% | Every decision is the blandest default; no opinions or tradeoffs visible |

**Tier 2 — Generated and Abandoned** (shipped without review or testing)

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

## Setup

```bash
cp .env.example .env  # add your GEMINI_API_KEY
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

See [plans/project-plan.md](plans/project-plan.md) for full architecture details.
