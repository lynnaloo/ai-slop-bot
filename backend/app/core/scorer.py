from app.models.rubric import InputType, RubricCategory


def applicable_categories(
    categories: list[RubricCategory], input_type: InputType
) -> list[RubricCategory]:
    return [c for c in categories if input_type in c.applies_to]


def compute(
    raw_scores: dict[str, int],
    categories: list[RubricCategory],
    input_type: InputType,
) -> tuple[int, dict[str, float]]:
    """
    Returns (composite_score_0_to_100, {category_id: weighted_score}).
    Renormalizes weights to only the applicable categories for this input type.
    """
    applicable = applicable_categories(categories, input_type)
    total_weight = sum(c.weight for c in applicable)

    weighted: dict[str, float] = {}
    composite = 0.0

    for cat in applicable:
        raw = raw_scores.get(cat.id, 0)
        normalized_weight = cat.weight / total_weight
        ws = raw * normalized_weight
        weighted[cat.id] = round(ws, 2)
        composite += ws

    # raw scores are 0–10, weights sum to 1.0 after normalization → composite 0–10, scale to 0–100
    return round(composite * 10), weighted
