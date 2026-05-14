import json
import logging
from dataclasses import dataclass

from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

from app.models.rubric import InputType, RubricCategory

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are an expert AI content detector. Your job is to objectively analyze content \
and score it for signs of AI-generated "slop" — low-quality, generic, or formulaic \
machine-generated content.

Score each category on a scale of 0–10:
  0 = no evidence of AI slop for this category
  10 = strong evidence of AI slop for this category

Be objective and specific in your reasoning. Quote or describe concrete examples from \
the content when justifying a score above 3."""


def _build_prompt(
    categories: list[RubricCategory],
    text: str | None,
    has_image: bool,
) -> str:
    lines = [
        "Analyze the content provided and return scores for each category below.",
        "",
        "Return ONLY a JSON object with this exact structure (no markdown, no explanation):",
        '{ "scores": { "<category_id>": { "score": <int 0-10>, "reasoning": "<1-2 sentences>" } } }',
        "",
        "=== CATEGORIES TO EVALUATE ===",
    ]
    for cat in categories:
        lines.append(f"\n[{cat.id}] {cat.label}")
        lines.append(cat.prompt.strip())

    lines.append("\n=== CONTENT TO ANALYZE ===")
    if text:
        lines.append(text[:6000])
    if has_image:
        lines.append("[An image is also attached above — evaluate it for applicable image categories.]")

    return "\n".join(lines)


@dataclass
class GeminiScores:
    raw: dict[str, int]
    reasoning: dict[str, str]


class GeminiClient:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def analyze(
        self,
        categories: list[RubricCategory],
        input_type: InputType,
        text: str | None = None,
        image_bytes: bytes | None = None,
    ) -> GeminiScores:
        applicable = [c for c in categories if input_type in c.applies_to]
        prompt_text = _build_prompt(applicable, text, image_bytes is not None)

        contents: list = [prompt_text]
        if image_bytes:
            contents.insert(
                0,
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            )

        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )

        data = json.loads(response.text)
        scores = data.get("scores", {})

        raw: dict[str, int] = {}
        reasoning: dict[str, str] = {}
        for cat in applicable:
            entry = scores.get(cat.id, {})
            raw[cat.id] = max(0, min(10, int(entry.get("score", 0))))
            reasoning[cat.id] = entry.get("reasoning", "")

        return GeminiScores(raw=raw, reasoning=reasoning)
