from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.gemini_client import GeminiClient
from app.core.rubric_loader import RubricStore
from app.routers import analyze, rubric


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rubric_store = RubricStore(settings.rubric_path)
    app.state.rubric_store.load()
    app.state.gemini = GeminiClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    )

    if settings.slack_bot_token and settings.slack_signing_secret:
        from app.slack.bot import create_slack_handler
        app.state.slack_handler = create_slack_handler(app)
    else:
        app.state.slack_handler = None

    yield


app = FastAPI(title="AI Slop Bot", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(rubric.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "model": settings.gemini_model}


@app.post("/slack/events")
async def slack_events(request):
    from fastapi import Request
    if app.state.slack_handler is None:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "Slack not configured"}, status_code=503)
    return await app.state.slack_handler.handle(request)
