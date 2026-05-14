from typing import Literal
from pydantic import BaseModel


class CategoryResult(BaseModel):
    id: str
    label: str
    raw_score: int
    weighted_score: float
    weight: float
    reasoning: str


class AnalysisResult(BaseModel):
    score: int
    verdict: Literal["Probably Human", "Uncertain", "Likely AI Slop"]
    categories: list[CategoryResult]
    input_type: Literal["text", "url", "image"]
    source_url: str | None = None
    rubric_version: str
    model: str
    analysis_ms: int


def verdict_for_score(score: int) -> Literal["Probably Human", "Uncertain", "Likely AI Slop"]:
    if score <= 30:
        return "Probably Human"
    if score <= 60:
        return "Uncertain"
    return "Likely AI Slop"
