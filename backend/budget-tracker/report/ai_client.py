"""
AI client — takes pre-computed scorer + recommender output and asks the LLM
only to write compelling narratives and a brief verdict paragraph.

The model is never asked to analyse raw data or invent numbers.
It receives deterministic facts and makes them readable.
"""

import json
import os
from typing import Optional

import pandas as pd

from .scorer import ScoreResult
from .recommender import RecommendationResult, Recommendation


def _make_client():
    api_key  = os.environ.get("API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("BASE_URL", "").strip() or None
    if not api_key:
        return None, None
    from openai import OpenAI
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    model = os.environ.get("MODEL", "gpt-4o-mini").strip()
    return OpenAI(**kwargs), model


def _build_prompt(score: ScoreResult, result: RecommendationResult) -> str:
    """
    We give the AI the pre-computed facts.
    It only needs to write the human-readable narrative — no analysis.
    """
    lines = [
        "You are a personal finance advisor reviewing a client's spending report.",
        "",
        "I have already analysed the data and found these specific issues.",
        "Your job: for each finding, write ONE compelling 2-sentence narrative.",
        "Be direct. Reference the exact amounts. Use an encouraging but honest tone.",
        "",
        f"FINANCIAL HEALTH SCORE: {score.total}/100 (Grade {score.grade})",
        f"HEADLINE: {score.headline}",
        "",
        "SCORE COMPONENTS:",
    ]
    for c in score.components:
        lines.append(f"  [{c.score}/{c.max_score}] {c.label}: {c.detail}")

    lines += ["", "PRE-COMPUTED RECOMMENDATIONS (enhance these with a narrative):"]
    for r in result.recommendations:
        lines.append(f"  ID={r.id} | {r.title} | Impact={r.impact}")
        lines.append(f"    Data: {r.specifics}")
        lines.append(f"    Action: {r.action}")
        if r.monthly_impact > 0:
            lines.append(f"    Potential saving: Rs.{r.monthly_impact:,.0f}/month")
        lines.append("")

    lines += [
        "Return ONLY valid JSON, no markdown:",
        "{",
        '  "score_verdict": "<2-sentence verdict on the overall financial health score>",',
        '  "narratives": [',
        '    {"id": <rec_id>, "narrative": "<2 sentences, specific amounts, actionable>"},',
        '    ...',
        '  ]',
        "}",
    ]
    return "\n".join(lines)


def enhance(score: ScoreResult, result: RecommendationResult) -> Optional[dict]:
    """
    Calls the LLM to add narrative text to pre-computed recommendations.
    Returns None if the API is unavailable or fails.
    """
    client, model = _make_client()
    if client is None:
        return None

    prompt = _build_prompt(score, result)

    try:
        resp = client.chat.completions.create(
            model=model,
            temperature=0.4,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a personal finance advisor. "
                        "Return only valid JSON matching the requested schema."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        data = json.loads(resp.choices[0].message.content)
        return data
    except Exception as e:
        print(f"  [AI] Enhancement unavailable: {e}")
        return None


def apply_narratives(result: RecommendationResult, ai_data: Optional[dict]) -> None:
    """Mutates result.recommendations in-place with AI narratives if available."""
    if not ai_data:
        return
    narratives = {n["id"]: n["narrative"] for n in ai_data.get("narratives", [])}
    for rec in result.recommendations:
        if rec.id in narratives:
            rec.narrative = narratives[rec.id]
