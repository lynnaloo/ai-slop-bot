import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from app.models.rubric import Rubric

logger = logging.getLogger(__name__)


class RubricStore:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._rubric: Rubric | None = None

    def load(self) -> Rubric:
        raw = yaml.safe_load(self._path.read_text())
        try:
            rubric = Rubric.model_validate(raw)
        except ValidationError as e:
            raise ValueError(f"Invalid rubric at {self._path}: {e}") from e

        total_weight = sum(c.weight for c in rubric.categories)
        if abs(total_weight - 1.0) > 0.001:
            logger.warning(
                "Rubric weights sum to %.4f (not 1.0) — normalizing automatically", total_weight
            )
            for cat in rubric.categories:
                cat.weight = cat.weight / total_weight

        self._rubric = rubric
        logger.info("Loaded rubric v%s with %d categories", rubric.version, len(rubric.categories))
        return rubric

    def reload(self) -> Rubric:
        return self.load()

    @property
    def rubric(self) -> Rubric:
        if self._rubric is None:
            return self.load()
        return self._rubric
