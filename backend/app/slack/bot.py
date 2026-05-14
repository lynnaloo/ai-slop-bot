import logging
import re

from fastapi import FastAPI
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

from app.config import settings
from app.core.analyzer import AnalysisInput, analyze
from app.slack.formatters import build_score_card

logger = logging.getLogger(__name__)

_URL_RE = re.compile(r"https?://\S+")


def _extract_url_or_text(text: str) -> tuple[str | None, str | None]:
    """Returns (url, text) — one will be None."""
    match = _URL_RE.search(text)
    if match:
        return match.group(0).rstrip(".,>"), None
    cleaned = text.strip()
    return None, cleaned if cleaned else None


async def _run_and_post(app: FastAPI, say, input: AnalysisInput, thread_ts: str | None = None) -> None:
    try:
        result = await analyze(input, app.state.gemini, app.state.rubric_store)
        blocks = build_score_card(result)
        kwargs = {"blocks": blocks, "text": f"Slop score: {result.score}/100 — {result.verdict}"}
        if thread_ts:
            kwargs["thread_ts"] = thread_ts
        await say(**kwargs)
    except Exception:
        logger.exception("Analysis failed")
        await say("Sorry, analysis failed. Check the logs.")


def create_slack_handler(app: FastAPI) -> AsyncSlackRequestHandler:
    bolt = AsyncApp(
        token=settings.slack_bot_token,
        signing_secret=settings.slack_signing_secret,
    )

    @bolt.command("/slopcheck")
    async def slopcheck_command(ack, command, say):
        await ack()
        raw = command.get("text", "").strip()
        if not raw:
            await say("Usage: `/slopcheck <url or text>`")
            return
        url, text = _extract_url_or_text(raw)
        input_type = "url" if url else "text"
        await _run_and_post(app, say, AnalysisInput(input_type=input_type, url=url, text=text))

    @bolt.event("app_mention")
    async def on_mention(event, say):
        raw = re.sub(r"<@[A-Z0-9]+>", "", event.get("text", "")).strip()
        if not raw:
            await say("Mention me with a URL or text to check for slop!")
            return
        url, text = _extract_url_or_text(raw)
        input_type = "url" if url else "text"
        await _run_and_post(
            app, say,
            AnalysisInput(input_type=input_type, url=url, text=text),
            thread_ts=event.get("ts"),
        )

    @bolt.event("message")
    async def on_message(event, say):
        channel = event.get("channel", "")
        if channel not in settings.auto_scan_channel_list:
            return
        if event.get("subtype"):  # skip edits, bot messages, etc.
            return

        raw = event.get("text", "")
        url, _ = _extract_url_or_text(raw)
        if not url:
            return

        from app.core.analyzer import analyze as _analyze
        from app.core.analyzer import AnalysisInput as _Input
        try:
            result = await _analyze(
                _Input(input_type="url", url=url),
                app.state.gemini,
                app.state.rubric_store,
            )
            if result.score >= settings.auto_scan_threshold:
                blocks = build_score_card(result)
                await say(
                    blocks=blocks,
                    text=f"High slop score detected: {result.score}/100",
                    thread_ts=event.get("ts"),
                )
        except Exception:
            logger.exception("Auto-scan analysis failed for %s", url)

    return AsyncSlackRequestHandler(bolt)
