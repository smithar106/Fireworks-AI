"""Metric calculations.

All functions are pure and operate on an already-filtered DataFrame, so the
date-range filter and the tests exercise identical code. Units are documented
in each docstring; percentages are floats (e.g. 67.97 means 67.97%).
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from fireworks import config


def filter_by_date(df: pd.DataFrame, start, end) -> pd.DataFrame:
    """Return rows where ``date`` is within [start, end] (inclusive)."""
    mask = (df[config.DATE_COL] >= pd.Timestamp(start)) & (df[config.DATE_COL] <= pd.Timestamp(end))
    return df.loc[mask]


def totals(df: pd.DataFrame) -> dict[str, int | float]:
    """Period sums. Tokens/requests are summed; returns raw numbers."""
    return {
        "requests": int(df["requests"].sum()),
        "input_tokens": int(df["input_tokens"].sum()),
        "output_tokens": int(df["output_tokens"].sum()),
        "total_tokens": int(df["total_tokens"].sum()),
        "spend_usd": float(df["spend_usd"].sum()),
        "tier1_tickets": int(df["tier1_tickets"].sum()),
        "automated_tier1_tickets": int(df["automated_tier1_tickets"].sum()),
    }


def weighted_automation_pct(df: pd.DataFrame) -> float:
    """Weighted monthly automation = SUM(automated) / SUM(tier1) * 100.

    This is the ONLY correct period automation rate; it is NOT the average of
    the daily ``automation_rate_pct`` column.
    """
    t = df["tier1_tickets"].sum()
    if t == 0:
        return float("nan")
    return df["automated_tier1_tickets"].sum() / t * 100


def unweighted_daily_average(df: pd.DataFrame, column: str) -> float:
    """Simple mean of a daily column (an *unweighted daily average*).

    Only used where the daily column is already a rate/percentage. It is not a
    substitute for a properly weighted period rate.
    """
    return float(df[column].mean())


def spend_per_million_tokens(df: pd.DataFrame) -> float:
    """Blended USD per million tokens (total spend / total tokens * 1e6)."""
    tok = df["total_tokens"].sum()
    if tok == 0:
        return float("nan")
    return float(df["spend_usd"].sum()) / (tok / 1e6)


def _pct_change(first: float, last: float) -> float:
    if first == 0:
        return float("nan")
    return (last - first) / first * 100


def compute_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Compute the full KPI summary consumed by both views.

    ``df`` is assumed to already be filtered to the desired date range.
    """
    if df.empty:
        return {"empty": True}

    tot = totals(df)
    first = df.iloc[0]
    last = df.iloc[-1]

    manual_tier1 = tot["tier1_tickets"] - tot["automated_tier1_tickets"]

    return {
        "empty": False,
        "start_date": df[config.DATE_COL].min().date(),
        "end_date": df[config.DATE_COL].max().date(),
        "days": int(len(df)),
        # Totals
        "total_requests": tot["requests"],
        "total_input_tokens": tot["input_tokens"],
        "total_output_tokens": tot["output_tokens"],
        "total_tokens": tot["total_tokens"],
        "total_spend": tot["spend_usd"],
        "total_tier1": tot["tier1_tickets"],
        "total_automated_tier1": tot["automated_tier1_tickets"],
        "manual_tier1": int(manual_tier1),
        # Automation (correct weighting vs. the daily-column average)
        "weighted_automation_pct": weighted_automation_pct(df),
        "unweighted_automation_pct": unweighted_daily_average(df, "automation_rate_pct"),
        # Spend efficiency
        "spend_per_million_tokens": spend_per_million_tokens(df),
        # Latency (label as average-of-daily, NOT a monthly P95)
        "avg_daily_p50_ms": unweighted_daily_average(df, "p50_latency_ms"),
        "avg_daily_p95_ms": unweighted_daily_average(df, "p95_latency_ms"),
        "max_daily_p95_ms": float(df["p95_latency_ms"].max()),
        "min_daily_p95_ms": float(df["p95_latency_ms"].min()),
        # Latest-day point-in-time values
        "latest": {
            "automation_rate_pct": float(last["automation_rate_pct"]),
            "error_rate_pct": float(last["error_rate_pct"]),
            "availability_pct": float(last["availability_pct"]),
            "p50_latency_ms": float(last["p50_latency_ms"]),
            "p95_latency_ms": float(last["p95_latency_ms"]),
            "grounded_answer_rate_pct": float(last["grounded_answer_rate_pct"]),
            "quality_eval_pass_rate_pct": float(last["quality_eval_pass_rate_pct"]),
            "escalation_rate_pct": float(last["escalation_rate_pct"]),
            "csat_score": float(last["csat_score"]),
            "avg_handle_time_min": float(last["avg_handle_time_min"]),
        },
        "first": {
            "csat_score": float(first["csat_score"]),
            "avg_handle_time_min": float(first["avg_handle_time_min"]),
        },
        # Provided-outcome trend context (observed, no invented baseline)
        "handle_time_pct_change": _pct_change(
            float(first["avg_handle_time_min"]), float(last["avg_handle_time_min"])
        ),
        "csat_point_change": float(last["csat_score"]) - float(first["csat_score"]),
        # Daily series for charts
        "series": {
            "date": df[config.DATE_COL],
            "requests": df["requests"],
            "total_tokens": df["total_tokens"],
            "spend_usd": df["spend_usd"],
            "automation_rate_pct": df["automation_rate_pct"],
            "p50_latency_ms": df["p50_latency_ms"],
            "p95_latency_ms": df["p95_latency_ms"],
            "error_rate_pct": df["error_rate_pct"],
            "availability_pct": df["availability_pct"],
            "grounded_answer_rate_pct": df["grounded_answer_rate_pct"],
            "quality_eval_pass_rate_pct": df["quality_eval_pass_rate_pct"],
            "escalation_rate_pct": df["escalation_rate_pct"],
            "csat_score": df["csat_score"],
        },
    }
