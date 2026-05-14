from typing import Literal
from pydantic import BaseModel, field_validator


InputType = Literal["text", "url", "image"]


class RubricCategory(BaseModel):
    id: str
    label: str
    group: str | None = None
    weight: float
    applies_to: list[InputType]
    prompt: str

    @field_validator("weight")
    @classmethod
    def weight_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("weight must be > 0")
        return v


class Rubric(BaseModel):
    version: str
    description: str = ""
    categories: list[RubricCategory]

    @field_validator("categories")
    @classmethod
    def categories_not_empty(cls, v: list[RubricCategory]) -> list[RubricCategory]:
        if not v:
            raise ValueError("rubric must have at least one category")
        return v
