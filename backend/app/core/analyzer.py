import time
from dataclasses import dataclass

from app.core import fetcher, scorer
from app.core.gemini_client import GeminiClient
from app.core.rubric_loader import RubricStore
from app.models.request import AnalysisResult, CategoryResult, verdict_for_score
from app.models.rubric import InputType


@dataclass
class AnalysisInput:
    input_type: InputType
    url: str | None = None
    text: str | None = None
    image_bytes: bytes | None = None


async def analyze(
    input: AnalysisInput,
    gemini: GeminiClient,
    rubric_store: RubricStore,
) -> AnalysisResult:
    start = time.monotonic()
    rubric = rubric_store.rubric

    text = input.text
    image_bytes = input.image_bytes
    source_url = input.url

    if input.input_type == "url" and input.url:
        page = await fetcher.fetch(input.url)
        text = page.text
        image_bytes = page.screenshot_bytes

    gemini_scores = await gemini.analyze(
        categories=rubric.categories,
        input_type=input.input_type,
        text=text,
        image_bytes=image_bytes,
    )

    composite, weighted_scores = scorer.compute(
        raw_scores=gemini_scores.raw,
        categories=rubric.categories,
        input_type=input.input_type,
    )

    applicable = scorer.applicable_categories(rubric.categories, input.input_type)
    category_results = [
        CategoryResult(
            id=cat.id,
            label=cat.label,
            raw_score=gemini_scores.raw.get(cat.id, 0),
            weighted_score=weighted_scores.get(cat.id, 0.0),
            weight=cat.weight,
            reasoning=gemini_scores.reasoning.get(cat.id, ""),
        )
        for cat in applicable
    ]

    elapsed_ms = round((time.monotonic() - start) * 1000)

    return AnalysisResult(
        score=composite,
        verdict=verdict_for_score(composite),
        categories=category_results,
        input_type=input.input_type,
        source_url=source_url,
        rubric_version=rubric.version,
        model=gemini._model,
        analysis_ms=elapsed_ms,
    )
