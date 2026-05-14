"""
Quick CLI smoke test. Run from backend/ with:
  GEMINI_API_KEY=... python scripts/test_analysis.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.analyzer import AnalysisInput, analyze
from app.core.gemini_client import GeminiClient
from app.core.rubric_loader import RubricStore

SLOP_TEXT = (
    "In today's fast-paced world, it's more important than ever to leverage synergistic "
    "solutions that empower stakeholders to unlock their full potential. Our holistic approach "
    "to thought leadership enables seamless value proposition delivery across all touchpoints. "
    "It's worth noting that results may vary. That said, our robust ecosystem of innovative "
    "solutions is a true game-changer for forward-thinking organizations."
)

HUMAN_TEXT = (
    "I've been making bread for about three years now. My first loaves were dense bricks — "
    "I overworked the dough every time because I was nervous it wasn't developed enough. "
    "The thing that actually helped was stopping trying to follow a strict recipe and just "
    "learning what the dough should feel like. Sticky but not wet. Alive, almost."
)


async def main():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("Set GEMINI_API_KEY env var")
        sys.exit(1)

    model = os.environ.get("GEMINI_MODEL", "gemini-3.1-pro-preview")
    gemini = GeminiClient(api_key=api_key, model=model)
    store = RubricStore("rubric.yaml")

    print("Analyzing slop text...")
    slop_result = await analyze(AnalysisInput(input_type="text", text=SLOP_TEXT), gemini, store)
    print(f"  Slop score:  {slop_result.score}/100 — {slop_result.verdict}")

    print("Analyzing human text...")
    human_result = await analyze(AnalysisInput(input_type="text", text=HUMAN_TEXT), gemini, store)
    print(f"  Human score: {human_result.score}/100 — {human_result.verdict}")

    diff = slop_result.score - human_result.score
    print(f"\nScore difference: {diff} points")
    if diff >= 30:
        print("PASS — slop score is at least 30 points higher than human score")
    else:
        print("WARN — difference less than 30 points, consider tuning the rubric")


asyncio.run(main())
