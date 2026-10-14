"""Customer-facing view: Northstar account health for the VP Customer
Experience and VP Engineering.

This view is deliberately restricted. It contains operational, quality, and
adoption content only — NO competitive intelligence, margins, unit economics,
staffing, or internal commercial sentiment. The `content()` function returns a
plain structure so the test suite can assert that no internal-only term leaks
into what a customer would see.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from fireworks import assumptions, charts, ui


def _flagship_outcomes() -> list[str]:
    lines = []
    for key in ("automation", "handle_time", "csat"):
        o = assumptions.PROVIDED_OUTCOMES[key]
        lines.append(f"- **{o['label']}: {o['value']}**")
    return lines


def content(summary: dict[str, Any]) -> list[dict[str, Any]]:
    """Structured, testable content for the customer view."""
    latest = summary["latest"]
    out = assumptions.PROVIDED_OUTCOMES

    return [
        {
            "heading": "Executive summary",
            "subheading": "Northstar flagship — 30-day account health review",
            "kpis": [
                {"label": "Tier-1 automation", "value": ui.fmt_pct(summary["weighted_automation_pct"]), "sub": "Aug 31: 70.8%", "tone": "good"},
                {"label": "Availability", "value": ui.fmt_pct(latest["availability_pct"], 3), "sub": "≥99.8% all month", "tone": "good"},
                {"label": "CSAT", "value": f"{latest['csat_score']:.1f}", "sub": f"+{summary['csat_point_change']:.1f} pts in Aug", "tone": "good"},
            ],
            "blocks": [
                "Fireworks deployed an AI support agent for the Northstar flagship "
                "brand on a fine-tuned model (`northstar-flagship-support-ft-v1`). Over "
                f"Aug 1–31 the deployment served **{ui.fmt_int(summary['total_requests'])} requests** "
                f"({ui.fmt_int(summary['total_tier1'])} Tier-1 tickets).",
                "Flagship program outcomes (as reported for this engagement):",
                *_flagship_outcomes(),
                "Observed 30-day trends: requests grew, latency and error rate fell, "
                "and CSAT rose steadily from "
                f"**{summary['first']['csat_score']:.1f}** to **{latest['csat_score']:.1f}** "
                f"while average handle time fell from **{summary['first']['avg_handle_time_min']:.2f}** "
                f"to **{latest['avg_handle_time_min']:.2f}** minutes.",
            ],
        },
        {
            "heading": "Adoption & spend",
            "kpis": [
                {"label": "Requests", "value": ui.fmt_int(summary["total_requests"]), "sub": "inference calls", "tone": "neutral"},
                {"label": "Total tokens", "value": ui.fmt_number(summary["total_tokens"] / 1e9, 2) + "B", "sub": "input + output", "tone": "neutral"},
                {"label": "Recorded spend", "value": ui.fmt_usd(summary["total_spend"]), "sub": "inference only", "tone": "neutral"},
                {"label": "Blended $/M tokens", "value": f"${summary['spend_per_million_tokens']:.2f}", "sub": "input + output", "tone": "neutral"},
            ],
            "blocks": [
                "Requests represent inference calls to the deployed model, not unique "
                "support tickets. Usage climbed through August, peaking at "
                f"**{ui.fmt_int(summary['series']['requests'].max())}** requests/day.",
                "Recorded spend is **inference spend only** — it is not a fully loaded "
                "program cost and excludes engineering, integration, and support overhead.",
                "Spend per million tokens is a blended rate across input and output "
                "tokens computed from daily aggregates; the dataset does not expose "
                "per-model or per-request pricing, so this is an implied rate, not a "
                "contractual price.",
            ],
        },
        {
            "heading": "Reliability & incidents",
            "kpis": [
                {"label": "Availability", "value": ui.fmt_pct(latest["availability_pct"], 3), "sub": "latest day", "tone": "good"},
                {"label": "Error rate", "value": ui.fmt_pct(latest["error_rate_pct"], 2), "sub": "1.34% → 0.66%", "tone": "good"},
                {"label": "P50 latency", "value": ui.fmt_ms(latest["p50_latency_ms"]), "sub": "latest day", "tone": "neutral"},
                {"label": "P95 latency", "value": ui.fmt_ms(latest["p95_latency_ms"]), "sub": "daily reported", "tone": "neutral"},
            ],
            "blocks": [
                "Availability stayed above 99.8% for the whole period, and the error "
                "rate fell from 1.34% to **0.66%** by Aug 31.",
                "Median (P50) latency improved from ~690 ms to **~525 ms**. P95 latency "
                "is reported as a daily series (the dataset reports a daily P95; it does "
                "not contain the raw latency distribution needed for a true monthly P95).",
                "Three operational events were documented and disclosed: a catalog sync "
                "on Aug 9, a promotional traffic burst on Aug 21, and a RAG index refresh "
                "on Aug 24. Each was addressed the same day.",
            ],
        },
        {
            "heading": "Quality & escalations",
            "kpis": [
                {"label": "Grounded answers", "value": ui.fmt_pct(latest["grounded_answer_rate_pct"]), "sub": "latest day", "tone": "good"},
                {"label": "Quality eval pass", "value": ui.fmt_pct(latest["quality_eval_pass_rate_pct"]), "sub": "latest day", "tone": "good"},
                {"label": "Escalation rate", "value": ui.fmt_pct(latest["escalation_rate_pct"]), "sub": "14.6% → 11.2%", "tone": "good"},
            ],
            "blocks": [
                "Grounded answer rate reached **96.5%** and quality-eval pass rate "
                "**95.3%** by Aug 31, after the Aug 24 RAG index refresh improved "
                "grounding on return-policy questions.",
                "Escalation rate declined from 14.6% to **11.2%** over the month.",
                "Known caveats: quality metrics are the customer's reported "
                "grounding/eval pass rates; the +12 CSAT-point and 35% handle-time "
                f"outcomes ({out['csat']['value']}, {out['handle_time']['value']}) are "
                "measured against a pre-Fireworks baseline that is not part of this "
                "dataset.",
            ],
        },
        {
            "heading": "Key risks & actions",
            "blocks": [
                "Three operational risks are worth watching, each already mitigated once:",
                "- **Content/catalog refreshes** can briefly raise latency and errors (Aug 9). "
                "Recommended: schedule refreshes off-peak and pre-warm caches before cutover.",
                "- **Promotional traffic spikes** can briefly raise latency (Aug 21). "
                "Recommended: tie autoscaling to the promotion calendar.",
                "- **~32% of Tier-1 remains manual.** Recommended: expand automated coverage "
                "to the highest-volume unresolved intents, measured per intent.",
            ],
        },
        {
            "heading": "Joint actions",
            "blocks": [
                "Proposed joint next steps (owners and dates to be confirmed at the EBR):",
                "- **Agree pilot success criteria for a second brand** — Account Executive & customer.",
                "- **Tie autoscaling to the promotion calendar** — Solutions Architect & customer ops.",
                "- **Expand automated coverage to top unresolved intents** — Applied Data Scientist & customer support leads.",
                "Expansion opportunity: extend the proven support-agent pattern to "
                "additional Northstar brands, subject to a joint pilot and acceptance "
                "criteria.",
            ],
        },
        {
            "heading": "Pilot & next steps",
            "blocks": [
                "We propose a phased pilot for the next brand: begin with the shared "
                "model plus a brand-specific system prompt and an isolated retrieval "
                "index, gated on the same automation, latency, error-rate, and CSAT "
                "criteria met by the flagship deployment.",
                "Next steps: (1) confirm the target brand and catalog scope, (2) agree "
                "success criteria, (3) run a 30-day pilot with weekly reviews and a "
                "pre-agreed rollback path.",
            ],
        },
    ]


def render(summary: dict[str, Any], df: pd.DataFrame) -> None:
    """Render the customer view with Streamlit."""
    sections = content(summary)

    for s in sections:
        ui.section(s["heading"], s.get("subheading"))
        if s.get("kpis"):
            ui.kpi_row(s["kpis"])
        for b in s["blocks"]:
            st.markdown(b)

        # Inline charts attached to specific sections.
        if s["heading"] == "Adoption & spend":
            c1, c2 = st.columns(2)
            with c1:
                ui.chart(
                    charts.line(df, ["requests"], ["Requests"], "Daily requests (inference calls)", "requests"),
                )
            with c2:
                ui.chart(
                    charts.line(df, ["spend_usd"], ["Spend"], "Daily spend (USD)", "USD"),
                )
        elif s["heading"] == "Reliability & incidents":
            ui.chart(
                charts.line(
                    df,
                    ["p50_latency_ms", "p95_latency_ms"],
                    ["P50 latency", "P95 latency (daily)"],
                    "Latency (ms)",
                    "ms",
                ),
            )
            ui.chart(
                charts.line(df, ["error_rate_pct"], ["Error rate"], "Daily error rate", "%"),
            )
        elif s["heading"] == "Quality & escalations":
            ui.chart(
                charts.line(
                    df,
                    ["grounded_answer_rate_pct", "quality_eval_pass_rate_pct"],
                    ["Grounded answer rate", "Quality eval pass rate"],
                    "Quality metrics",
                    "%",
                ),
            )
