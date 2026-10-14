"""Transparent 0–100 account-health scoring.

The score is a weighted average over *scored* dimensions only. Each dimension
maps an observed metric to a 0–100 sub-score via piecewise-linear thresholds
(defined centrally in ``fireworks.assumptions.SCORING_DIMENSIONS``). Dimensions
that the dataset cannot support are reported separately and never scored.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from fireworks import assumptions, metrics

# Human-readable units per dimension (for the UI).
_DIMENSION_UNITS: dict[str, str] = {
    "automation": "%",
    "grounded_answer_rate": "%",
    "quality_eval_pass_rate": "%",
    "availability": "%",
    "error_rate": "%",
    "p95_latency": "ms",
    "csat": "pts",
    "escalation_rate": "%",
}


def piecewise_score(value: float, thresholds: list[tuple[float, float]]) -> float:
    """Linearly interpolate `value` against (x, y) thresholds; clamp to [0,100]."""
    if thresholds is None or len(thresholds) == 0:
        return float("nan")
    xs = [t[0] for t in thresholds]
    ys = [t[1] for t in thresholds]
    if value <= xs[0]:
        return float(ys[0])
    if value >= xs[-1]:
        return float(ys[-1])
    for i in range(len(thresholds) - 1):
        x0, y0 = thresholds[i]
        x1, y1 = thresholds[i + 1]
        if x0 <= value <= x1:
            t = (value - x0) / (x1 - x0)
            return max(0.0, min(100.0, y0 + t * (y1 - y0)))
    return float("nan")


def _observed_value(df: pd.DataFrame, source: tuple[str, str | None]) -> float:
    kind, col = source
    if kind == "weighted":
        return metrics.weighted_automation_pct(df)
    if kind == "latest":
        return float(df[col].iloc[-1])
    raise ValueError(f"unknown scoring source: {source}")


def _tier_for(score: float) -> dict[str, str]:
    for tier in assumptions.SCORE_TIERS:
        if score >= tier["min"]:
            return {"label": tier["label"], "tone": tier["tone"]}
    return {"label": "At risk", "tone": "bad"}


def compute_health_score(df: pd.DataFrame) -> dict[str, Any]:
    """Compute the account health score and per-dimension breakdown."""
    if df.empty:
        return {"overall_score": float("nan"), "dimensions": [], "unscored": assumptions.UNSCORED_DIMENSIONS}

    dimension_results: list[dict[str, Any]] = []
    weighted_sum = 0.0
    weight_total = 0.0

    for dim in assumptions.SCORING_DIMENSIONS:
        value = _observed_value(df, dim["source"])
        sub = piecewise_score(value, dim["thresholds"])
        dimension_results.append(
            {
                "key": dim["key"],
                "name": dim["name"],
                "weight": dim["weight"],
                "direction": dim["direction"],
                "unit": _DIMENSION_UNITS.get(dim["key"], ""),
                "observed_value": round(value, 2),
                "sub_score": round(sub, 1),
                "description": dim["description"],
            }
        )
        weighted_sum += dim["weight"] * sub
        weight_total += dim["weight"]

    overall = weighted_sum / weight_total if weight_total else float("nan")

    return {
        "overall_score": round(overall, 1),
        "tier": _tier_for(overall),
        "dimensions": dimension_results,
        "unscored": assumptions.UNSCORED_DIMENSIONS,
    }
