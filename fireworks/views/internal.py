"""Internal Fireworks QBR view: account management, engineering, executives.

Contains the full picture (health score, risks, expansion pipeline, competitive
risk, unit economics, staffing). This content must NEVER appear in the
customer-facing view.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from fireworks import assumptions, charts, config, ui


def _overview_takeaways(summary: dict[str, Any], score: dict[str, Any]) -> list[dict[str, str]]:
    latest = summary["latest"]
    return [
        {"text": f"Status **{score['tier']['label']}** ({score['overall_score']:.0f}/100) — operational health, not full account health.", "tone": "accent"},
        {"text": f"Error rate 1.34% → {latest['error_rate_pct']:.2f}%, escalation 14.6% → {latest['escalation_rate_pct']:.1f}%.", "tone": "good"},
        {"text": f"~{ui.fmt_int(summary['manual_tier1'])} Tier-1 tickets (~{100 - summary['weighted_automation_pct']:.0f}%) still manual.", "tone": "warn"},
    ]


def _hero(summary: dict[str, Any], score: dict[str, Any]) -> str:
    return (
        f"Account health <span class=\"accent\">{score['overall_score']:.0f}/100</span> — {score['tier']['label'].lower()}, "
        "with two same-day-resolved incidents and a credible path to four more brands."
    )


def content(summary: dict[str, Any], score: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "heading": "Account overview",
            "kpis": [
                {"label": "Account health score", "value": f"{score['overall_score']:.0f}", "sub": f"/ 100 · {score['tier']['label']}", "tone": "accent"},
                {"label": "Weighted automation", "value": ui.fmt_pct(summary["weighted_automation_pct"]), "sub": "Aug 31: 70.8%", "tone": "good"},
                {"label": "Recorded spend", "value": ui.fmt_usd(summary["total_spend"]), "sub": "inference only", "tone": "neutral"},
                {"label": "Requests", "value": ui.fmt_int(summary["total_requests"]), "sub": "inference calls", "tone": "neutral"},
            ],
            "blocks": [],
        },
        {
            "heading": "Account health score",
            "subheading": "Transparent 0–100 weighted score across eight operational dimensions.",
            "blocks": [],
        },
        {"heading": "Trends", "subheading": "Every key metric moved the right way through August.", "blocks": []},
        {"heading": "Incidents", "subheading": "Two incidents, both resolved same-day; one improvement.", "blocks": []},
        {"heading": "Top risks", "subheading": "Content-refresh resilience, promo autoscaling, and remaining manual Tier-1.", "blocks": []},
        {
            "heading": "Expansion pipeline",
            "subheading": "Four hypothetical brands — every field is an assumption.",
            "blocks": [],
        },
        {
            "heading": "Scaling architecture",
            "subheading": "Start shared; fine-tune only where behavior gaps are proven.",
            "blocks": [],
        },
        {
            "heading": "Internal assessments",
            "blocks": [
                "- **Competitive risk:** *Illustrative* — no competitive data; flag for account team.",
                "- **Relationship coverage:** *Illustrative* — sponsor/champion depth not tracked in data.",
                "- **Support burden:** " + ui.fmt_int(summary["manual_tier1"]) + " manual Tier-1 tickets remain (~32%).",
                "- **Staffing:** *Illustrative* — FDE/DS allocation not derivable from data.",
                "- **Unit economics:** $" + f"{summary['spend_per_million_tokens']:.2f}" + "/M blended (inference only); margin not computable.",
                "- **Expansion confidence:** *Illustrative* — medium-high given health score 92.8 and incident mitigation.",
                "- **Blockers:** none observed; watch content-refresh and promo-traffic recurrence.",
            ],
        },
        {"heading": "Action tracker", "blocks": []},
    ]


def render(summary: dict[str, Any], score: dict[str, Any], df: pd.DataFrame) -> None:
    ui.hero(_hero(summary, score))
    sections = content(summary, score)

    for s in sections:
        with st.container(border=True):
            ui.section(s["heading"], s.get("subheading"))
            if s.get("kpis"):
                ui.kpi_row(s["kpis"])
            for b in s["blocks"]:
                st.markdown(b)

            heading = s["heading"]
            if heading == "Account overview":
                ui.takeaways(_overview_takeaways(summary, score))
            elif heading == "Account health score":
                _render_scoring(score)
            elif heading == "Trends":
                _render_trends(df)
            elif heading == "Incidents":
                _render_incidents()
            elif heading == "Top risks":
                _render_risks()
            elif heading == "Expansion pipeline":
                _render_brands()
            elif heading == "Scaling architecture":
                _render_architecture()
            elif heading == "Action tracker":
                _render_actions()


def _render_scoring(score: dict[str, Any]) -> None:
    ui.chart(
        charts.bars(
            [d["name"] for d in score["dimensions"]],
            [d["sub_score"] for d in score["dimensions"]],
            title="Dimension sub-scores (0–100)",
        )
    )
    rows = [
        {"Dimension": d["name"], "Weight": f"{d['weight']:.0%}", "Observed": f"{d['observed_value']:,.2f}{d['unit']}", "Sub-score": f"{d['sub_score']:.1f}"}
        for d in score["dimensions"]
    ]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    ui.footnote("Unscored: " + ", ".join(u["name"] for u in score["unscored"]) + ".")


def _render_trends(df: pd.DataFrame) -> None:
    c1, c2 = st.columns(2)
    with c1:
        ui.chart(charts.line(df, ["requests"], ["Requests"], "Daily requests", digits=0))
    with c2:
        ui.chart(charts.line(df, ["total_tokens"], ["Tokens"], "Daily total tokens", colors=[config.GOOD], digits=0))
    c1, c2 = st.columns(2)
    with c1:
        ui.chart(charts.line(df, ["spend_usd"], ["Spend"], "Daily spend (USD)", colors=[config.ACCENT], digits=2))
    with c2:
        ui.chart(charts.line(df, ["automation_rate_pct"], ["Automation"], "Automation — 65% → 70.8%", colors=[config.GOOD]))
    c1, c2 = st.columns(2)
    with c1:
        ui.chart(
            charts.line(
                df, ["p50_latency_ms", "p95_latency_ms"], ["P50", "P95 (daily)"],
                "Latency — falling through August", colors=[config.ACCENT, config.WARN], digits=0,
            )
        )
    with c2:
        ui.chart(charts.line(df, ["error_rate_pct"], ["Error rate"], "Error rate — 1.34% → 0.66%", colors=[config.BAD], digits=2))
    c1, c2 = st.columns(2)
    with c1:
        ui.chart(charts.line(df, ["availability_pct"], ["Availability"], "Daily availability", colors=[config.GOOD], digits=3))
    with c2:
        ui.chart(
            charts.line(
                df, ["grounded_answer_rate_pct", "quality_eval_pass_rate_pct"],
                ["Grounded answers", "Quality eval pass"], "Answer quality",
                colors=[config.GOOD, config.ACCENT],
            )
        )
    c1, c2 = st.columns(2)
    with c1:
        ui.chart(charts.line(df, ["escalation_rate_pct"], ["Escalation rate"], "Daily escalation rate", colors=[config.BAD]))
    with c2:
        ui.chart(charts.line(df, ["csat_score"], ["CSAT"], "Daily CSAT", colors=[config.ACCENT]))


def _render_incidents() -> None:
    for e in assumptions.OPERATIONAL_EVENTS:
        tone = "warn" if e["kind"] == "incident" else "good"
        label = "Incident" if e["kind"] == "incident" else "Improvement"
        st.markdown(f"**{e['date']}** — {e['title']} · {e['detail']}")
        ui.pill(label, tone)
        ui.footnote(f"Observed: {e['observed']}")


def _render_risks() -> None:
    for r in assumptions.TOP_RISKS:
        st.markdown(f"**{r['title']}**")
        ui.takeaways(
            [
                {"text": f"Impact: {r['impact']}", "tone": "warn"},
                {"text": f"Mitigation: {r['mitigation']}", "tone": "neutral"},
                {"text": f"Owner: {r['owner_role']} · Target: {r['target_date']}", "tone": "neutral"},
            ]
        )


def _render_brands() -> None:
    cols = ["Brand", "Positioning", "Volume", "Catalog", "Tone", "Returns", "Maturity", "Deps", "Priority"]
    rows = [
        [b["name"], b["positioning"], b["support_volume"], b["catalog_complexity"], b["brand_tone"],
         b["return_policy_complexity"], b["team_maturity"], b["expected_dependencies"], b["pilot_priority"]]
        for b in assumptions.BRAND_PIPELINE
    ]
    st.dataframe(pd.DataFrame(rows, columns=cols), width="stretch", hide_index=True)


def _render_architecture() -> None:
    for opt in assumptions.ARCHITECTURE_OPTIONS:
        st.markdown(f"**{opt['name']}** — {opt['assessment']}")
        ui.takeaways(
            [
                {"text": "Pros: " + "; ".join(opt["pros"]), "tone": "good"},
                {"text": "Cons: " + "; ".join(opt["cons"]), "tone": "warn"},
            ]
        )
    ui.footnote(
        "Separate models/GPUs do not guarantee privacy; isolation is enforced at the "
        "retrieval, prompt, and access layers. Fine-tuning is not required to use private knowledge."
    )


def _render_actions() -> None:
    rows = [
        {"Action": a["action"], "Owner": a["owner_role"], "Priority": a["priority"],
         "Target": a["target_date"], "Status": a["status"]}
        for a in assumptions.ACTIONS
    ]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
