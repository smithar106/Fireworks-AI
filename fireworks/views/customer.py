"""Customer-facing view: Northstar account health (VP Customer Experience,
VP Engineering).

Deliberately restricted to operational, quality, adoption, and joint next-step
content. No competitive intelligence, margins, unit economics, staffing, or
internal commercial sentiment. `content()` returns a plain structure so tests
can assert no internal-only term appears here.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from fireworks import assumptions, charts, config, ui


def _hero(summary: dict[str, Any]) -> str:
    o = assumptions.PROVIDED_OUTCOMES
    return (
        "One month in, the flagship support agent is delivering — "
        f"<span class=\"accent\">{o['automation']['value']} of Tier-1 automated</span>, "
        f"{summary['latest']['availability_pct']:.1f}% available, and CSAT climbing."
    )


def _outcome_takeaways(summary: dict[str, Any]) -> list[dict[str, str]]:
    o = assumptions.PROVIDED_OUTCOMES
    return [
        {"text": f"**{o['automation']['value']}** of Tier-1 automated (weighted monthly {summary['weighted_automation_pct']:.1f}%).", "tone": "good"},
        {"text": f"**{o['handle_time']['value']}** handle time and **{o['csat']['value']}** CSAT vs. pre-launch baseline.", "tone": "good"},
        {"text": f"In August: CSAT {summary['first']['csat_score']:.1f} → {summary['latest']['csat_score']:.1f}; handle time {summary['first']['avg_handle_time_min']:.2f} → {summary['latest']['avg_handle_time_min']:.2f} min.", "tone": "neutral"},
    ]


def content(summary: dict[str, Any]) -> list[dict[str, Any]]:
    latest = summary["latest"]
    return [
        {
            "heading": "Executive summary",
            "kpis": [
                {"label": "Tier-1 automation", "value": ui.fmt_pct(summary["weighted_automation_pct"]), "sub": "Aug 31: 70.8%", "tone": "good"},
                {"label": "Availability", "value": ui.fmt_pct(latest["availability_pct"], 1), "sub": "≥99.8% all month", "tone": "good"},
                {"label": "CSAT", "value": f"{latest['csat_score']:.1f}", "sub": f"+{summary['csat_point_change']:.1f} pts in Aug", "tone": "good"},
            ],
            "blocks": [],
        },
        {
            "heading": "Usage & spend",
            "subheading": "Adoption climbed ~64% through August with stable spend efficiency.",
            "kpis": [
                {"label": "Requests", "value": ui.fmt_int(summary["total_requests"]), "sub": "inference calls", "tone": "neutral"},
                {"label": "Tokens", "value": ui.fmt_number(summary["total_tokens"] / 1e9, 2) + "B", "sub": "input + output", "tone": "neutral"},
                {"label": "Spend", "value": ui.fmt_usd(summary["total_spend"]), "sub": "inference only", "tone": "neutral"},
                {"label": "Blended $/M tokens", "value": f"${summary['spend_per_million_tokens']:.2f}", "sub": "input + output", "tone": "neutral"},
            ],
            "blocks": [],
        },
        {
            "heading": "Reliability",
            "subheading": "Availability held ≥99.8%; errors fell from 1.34% to 0.66%.",
            "kpis": [
                {"label": "Error rate", "value": ui.fmt_pct(latest["error_rate_pct"], 2), "sub": "1.34% → 0.66%", "tone": "good"},
                {"label": "P50 latency", "value": ui.fmt_ms(latest["p50_latency_ms"]), "sub": "latest day", "tone": "neutral"},
                {"label": "P95 latency", "value": ui.fmt_ms(latest["p95_latency_ms"]), "sub": "daily reported", "tone": "neutral"},
            ],
            "blocks": [],
        },
        {
            "heading": "Quality",
            "subheading": "Grounding and eval pass rates are 96%+ and still improving.",
            "kpis": [
                {"label": "Grounded answers", "value": ui.fmt_pct(latest["grounded_answer_rate_pct"]), "sub": "latest day", "tone": "good"},
                {"label": "Quality eval pass", "value": ui.fmt_pct(latest["quality_eval_pass_rate_pct"]), "sub": "latest day", "tone": "good"},
                {"label": "Escalations", "value": ui.fmt_pct(latest["escalation_rate_pct"]), "sub": "14.6% → 11.2%", "tone": "good"},
            ],
            "blocks": [],
        },
        {
            "heading": "Incidents",
            "blocks": [
                "Three events were disclosed and resolved same-day: catalog sync (Aug 9), "
                "promotional traffic burst (Aug 21), RAG index refresh (Aug 24).",
            ],
        },
        {
            "heading": "Recommendations",
            "blocks": [
                "Agree a second-brand pilot, tie autoscaling to the promotion calendar, "
                "and expand coverage to the top unresolved intents.",
            ],
        },
    ]


def render(summary: dict[str, Any], df: pd.DataFrame) -> None:
    ui.hero(_hero(summary))
    sections = content(summary)

    for s in sections:
        with st.container(border=True):
            ui.section(s["heading"], s.get("subheading"))
            if s.get("kpis"):
                ui.kpi_row(s["kpis"])
            for b in s["blocks"]:
                st.markdown(b)

            heading = s["heading"]
            if heading == "Executive summary":
                ui.takeaways(_outcome_takeaways(summary))
            elif heading == "Usage & spend":
                c1, c2 = st.columns(2)
                with c1:
                    ui.chart(charts.line(df, ["requests"], ["Requests"], "Requests per day", digits=0))
                with c2:
                    ui.chart(charts.line(df, ["spend_usd"], ["Spend"], "Spend per day (USD)", colors=[config.ACCENT], digits=2))
            elif heading == "Reliability":
                ui.chart(
                    charts.line(
                        df, ["p50_latency_ms", "p95_latency_ms"], ["P50", "P95 (daily)"],
                        "Latency — falling through August",
                        colors=[config.ACCENT, config.WARN], digits=0,
                    )
                )
                ui.chart(charts.line(df, ["error_rate_pct"], ["Error rate"], "Error rate — 1.34% → 0.66%", colors=[config.BAD], digits=2))
            elif heading == "Quality":
                ui.chart(
                    charts.line(
                        df, ["grounded_answer_rate_pct", "quality_eval_pass_rate_pct"],
                        ["Grounded answers", "Quality eval pass"], "Answer quality",
                        colors=[config.GOOD, config.ACCENT],
                    )
                )
