# AI Slop Bot

Detects AI-generated "slop" in text, URLs, and images. Returns a 0–100 score with a per-category breakdown powered by Google Gemini.

Available as a **web app** and a **Slack bot** (`/slopcheck`, `@slop-bot`, or auto-scan channels).

## Default Rubric

| Category | Weight | Input |
|---|---|---|
| Generic Phrasing | 20% | text, url |
| Corporate Buzzword Density | 15% | text, url |
| Suspiciously Uniform Structure | 15% | text, url |
| Excessive Hedging | 10% | text, url |
| Grammatically Perfect but Voiceless | 15% | text, url |
| AI Image Artifacts | 15% | image, url |
| Stock Photo / AI Studio Aesthetic | 10% | image, url |

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

See [plan.md](plan.md) for full architecture details.
