from app.models.request import AnalysisResult


_VERDICT_EMOJI = {
    "Probably Human": ":white_check_mark:",
    "Uncertain": ":warning:",
    "Likely AI Slop": ":robot_face:",
}


def _bar(score: int, max_score: int = 10, width: int = 10) -> str:
    filled = round(score / max_score * width)
    return "█" * filled + "░" * (width - filled)


def build_score_card(result: AnalysisResult) -> list[dict]:
    verdict_emoji = _VERDICT_EMOJI.get(result.verdict, ":question:")
    header_text = f"{verdict_emoji} *AI Slop Score: {result.score}/100* — {result.verdict}"

    category_lines = []
    for cat in result.categories:
        bar = _bar(cat.raw_score)
        category_lines.append(f"`{cat.label:<32}` {bar}  *{cat.raw_score}/10*")

    categories_text = "\n".join(category_lines)

    footer_parts = []
    if result.source_url:
        footer_parts.append(f"<{result.source_url}|View source>")
    footer_parts.append(f"_{result.model}_ · rubric v{result.rubric_version} · {result.analysis_ms}ms")
    footer_text = "  |  ".join(footer_parts)

    blocks: list[dict] = [
        {"type": "section", "text": {"type": "mrkdwn", "text": header_text}},
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": categories_text}},
    ]

    # Add top reasoning snippet for the highest-scoring category
    if result.categories:
        top = max(result.categories, key=lambda c: c.raw_score)
        if top.reasoning:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":mag: *Top signal ({top.label}):* {top.reasoning}",
                },
            })

    blocks.append({"type": "divider"})
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": footer_text}]})

    return blocks
