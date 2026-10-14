"""Internal Fireworks QBR view: account management, engineering, executives.

Contains the full picture including the transparent health score, competitive
risk, relationship coverage, support burden, staffing, unit economics, account
blockers, and the expansion pipeline. This content must NEVER be shown in the
customer-facing view.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from fireworks import assumptions, charts, ui


def _score_block(score: dict[str, Any]) -> list[str]:
    dims = []
    for d in score["dimensions"]:
        dims.append(
            f"- **{d['name']}** — weight {d['weight']:.0%}, {d['direction']} is better: "
            f"observed **{d['observed_value']:,.2f}{d['unit']}** → sub-score **{d['sub_score']}/100**."
        )
    return dims


def content(summary: dict[str, Any], score: dict[str, Any]) -> list[dict[str, Any]]:
    """Structured content for the internal QBR view."""
    latest = summary["latest"]
    tier = score["tier"]
    out = assumptions.PROVIDED_OUTCOMES

    return [
        {
            "heading": "Account overview",
            "subheading": "Northstar Retail Group — flagship deployment",
            "kpis": [
                {"label": "Account health score", "value": f"{score['overall_score']:.0f}", "sub": f"/ 100 · {tier['label']}", "tone": "accent"},
                {"label": "Weighted automation", "value": ui.fmt_pct(summary["weighted_automation_pct"]), "sub": "Aug 31: 70.8%", "tone": "good"},
                {"label": "Recorded spend", "value": ui.fmt_usd(summary["total_spend"]), "sub": "inference only", "tone": "neutral"},
                {"label": "Requests", "value": ui.fmt_int(summary["total_requests"]), "sub": "inference calls", "tone": "neutral"},
            ],
            "blocks": [
                f"**Status: {tier['label']}** ({score['overall_score']:.1f}/100) — see the scoring "
                "framework below for the exact dimensions and weights.",
                "Observed 30-day performance: availability ≥99.8% throughout; error rate "
                f"1.34% → **{latest['error_rate_pct']:.2f}%**; P95 (daily) ending at "
                f"**{latest['p95_latency_ms']:.0f} ms**; CSAT {summary['first']['csat_score']:.1f} → "
                f"**{latest['csat_score']:.1f}**; escalation 14.6% → **{latest['escalation_rate_pct']:.1f}%**.",
                "Key decisions to make: (1) green-light a second-brand pilot, (2) approve "
                "autoscaling/cache-warming hardening, (3) scope the next automation-coverage "
                "sprint for the remaining ~30% manual Tier-1.",
            ],
        },
        {
            "heading": "Account health score",
            "subheading": "Transparent 0–100 score with explicit dimensions and weights",
            "blocks": [
                "Each dimension maps an observed metric to a 0–100 sub-score via "
                "piecewise-linear thresholds, then a weighted average is taken over the "
                "**scored** dimensions only.",
                *_score_block(score),
                "**Unscored dimensions** (dataset does not support them, shown for "
                "transparency and never scored): "
                + ", ".join(f"{u['name']} ({u['reason']})" for u in score["unscored"]) + ".",
                "**Sensitivity & limitations:** the score is only as strong as its inputs. "
                "Automation uses the correct weighted rate (sum automated / sum Tier-1), not "
                "a mean of daily rates. P95 uses the daily reported value, not a computed "
                "monthly P95 (the raw distribution is unavailable). Relationship and "
                "commercial dimensions are excluded rather than estimated, so the score "
                "reflects *operational* health, not full account health.",
            ],
        },
        {
            "heading": "Incident timeline",
            "blocks": [],
        },
        {
            "heading": "Top risks",
            "blocks": [],
        },
        {
            "heading": "Expansion pipeline",
            "subheading": "Hypothetical profiles — every field is an assumption",
            "blocks": [
                "The profiles below are illustrative. Support volumes, catalog complexity, "
                "tone, policy complexity, maturity, and readiness are **assumptions**, not "
                "customer-provided facts.",
            ],
        },
        {
            "heading": "Scaling architecture",
            "subheading": "How to extend to multiple brands — cost, latency, and policy tradeoffs",
            "blocks": [
                "Three options are evaluated below. The recommendation: start every brand "
                "on a **shared base model + brand-specific system prompt + isolated "
                "retrieval index**, and fine-tune only where a measured behavior gap "
                "proves it necessary.",
                "Key principles: separate models/GPUs do **not** automatically guarantee "
                "data privacy (isolation is enforced at the retrieval, prompt, and access "
                "layers), and fine-tuning is **not** required to use private enterprise "
                "knowledge — retrieval with a good base model is usually sufficient.",
                "Recommended phased pilot: (1) shared model + brand prompt + isolated "
                "index; (2) 30-day pilot; (3) acceptance gates — weighted automation ≥65%, "
                "error rate <1%, P95 (daily) <1,500 ms, grounded answer ≥95%, no regression "
                "in CSAT; (4) rollback to the previous configuration if any gate fails for "
                "two consecutive weeks.",
            ],
        },
        {
            "heading": "Internal assessments",
            "subheading": "Illustrative — competitive, commercial, and coverage views",
            "blocks": [
                "- **Competitive risk:** *Illustrative.* No competitive intelligence is in the "
                "dataset; flag for account-team input.",
                "- **Relationship coverage:** *Illustrative.* Executive sponsor coverage and "
                "champion depth are not tracked in the dataset and require a manual review.",
                "- **Support burden:** Observed — 45,942 manual Tier-1 tickets remain in "
                "August (32% of Tier-1).",
                "- **Staffing:** *Illustrative.* Required FDE/data-science allocation is not "
                "derivable from the dataset; proposed staffing is a planning assumption.",
                "- **Unit economics:** Observed inference spend is $1,213.12 for ~1.09B "
                "tokens (~$1.12/M blended). This is inference spend only, not fully loaded "
                "program cost; gross margin and cost-per-ticket are not computable from this "
                "dataset.",
                "- **Expansion confidence:** *Illustrative.* Confidence to expand is rated "
                "medium-high based on operational health (score 92.8) and the mitigation of "
                "both August incidents, but is an internal judgment, not a customer fact.",
                "- **Account blockers:** None observed; the two operational incidents were "
                "mitigated same-day. Watch content-refresh and promo-traffic recurrence.",
                "- **Decisions required:** pilot green-light, hardening approval, coverage-sprint scope.",
            ],
        },
        {
            "heading": "Action tracker",
            "blocks": [],
        },
    ]


def render(summary: dict[str, Any], score: dict[str, Any], df: pd.DataFrame) -> None:
    """Render the internal QBR view with Streamlit."""
    sections = content(summary, score)

    for s in sections:
        ui.section(s["heading"], s.get("subheading"))
        if s.get("kpis"):
            ui.kpi_row(s["kpis"])
        for b in s["blocks"]:
            st.markdown(b)

        heading = s["heading"]
        if heading == "Account health score":
            _render_scoring_table(score)
        elif heading == "Incident timeline":
            _render_incidents()
        elif heading == "Top risks":
            _render_risks()
        elif heading == "Expansion pipeline":
            _render_brands()
        elif heading == "Scaling architecture":
            _render_architecture()
        elif heading == "Action tracker":
            _render_actions()
        elif heading == "Account overview":
            _render_trends(df)


def _render_trends(df: pd.DataFrame) -> None:
    ui.chart(
        charts.line(df, ["requests"], ["Requests"], "Daily requests", "requests"),
    )
    c1, c2 = st.columns(2)
    with c1:
        ui.chart(
            charts.line(df, ["total_tokens"], ["Tokens"], "Daily total tokens", "tokens"),
        )
    with c2:
        ui.chart(
            charts.line(df, ["spend_usd"], ["Spend"], "Daily spend (USD)", "USD"),
        )
    ui.chart(
        charts.line(df, ["automation_rate_pct"], ["Automation"], "Daily automation rate", "%"),
    )
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
    ui.chart(
        charts.line(df, ["availability_pct"], ["Availability"], "Daily availability", "%"),
    )
    c1, c2 = st.columns(2)
    with c1:
        ui.chart(
            charts.line(
                df,
                ["grounded_answer_rate_pct", "quality_eval_pass_rate_pct"],
                ["Grounded answer rate", "Quality eval pass rate"],
                "Quality metrics",
                "%",
            ),
        )
    with c2:
        ui.chart(
            charts.line(
                df,
                ["escalation_rate_pct", "csat_score"],
                ["Escalation rate", "CSAT"],
                "Escalations & CSAT",
                "value",
            ),
        )


def _render_scoring_table(score: dict[str, Any]) -> None:
    rows = [
        {
            "Dimension": d["name"],
            "Weight": f"{d['weight']:.0%}",
            "Observed": f"{d['observed_value']:,.2f}{d['unit']}",
            "Sub-score": f"{d['sub_score']:.1f}",
            "Direction": d["direction"],
        }
        for d in score["dimensions"]
    ]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    ui.chart(
        charts.bars(
            [d["name"] for d in score["dimensions"]],
            [d["sub_score"] for d in score["dimensions"]],
            title="Dimension sub-scores (0–100)",
            x_title="sub-score",
            color="#3457D5",
        ),
    )


def _render_incidents() -> None:
    for e in assumptions.OPERATIONAL_EVENTS:
        tone = "warn" if e["kind"] == "incident" else "good"
        label = "Incident" if e["kind"] == "incident" else "Improvement"
        st.markdown(f"**{e['date']}** — {e['title']}")
        ui.pill(label, tone)
        st.markdown(f"- {e['detail']}\n- Observed: {e['observed']}")


def _render_risks() -> None:
    for r in assumptions.TOP_RISKS:
        st.markdown(f"**{r['title']}**")
        st.markdown(
            f"- **Impact:** {r['impact']}\n- **Evidence:** {r['evidence']}\n"
            f"- **Mitigation:** {r['mitigation']}\n"
            f"- **Owner:** {r['owner_role']} · **Target:** {r['target_date']}"
        )


def _render_brands() -> None:
    cols = [
        "Brand",
        "Positioning",
        "Support volume",
        "Catalog complexity",
        "Brand tone",
        "Return policy",
        "Team maturity",
        "Technical readiness",
        "Dependencies",
        "Pilot priority",
    ]
    rows = [
        [
            b["name"],
            b["positioning"],
            b["support_volume"],
            b["catalog_complexity"],
            b["brand_tone"],
            b["return_policy_complexity"],
            b["team_maturity"],
            b["technical_readiness"],
            b["expected_dependencies"],
            b["pilot_priority"],
        ]
        for b in assumptions.BRAND_PIPELINE
    ]
    st.dataframe(pd.DataFrame(rows, columns=cols), width="stretch", hide_index=True)


def _render_actions() -> None:
    rows = [
        {
            "Action": a["action"],
            "Owner role": a["owner_role"],
            "Priority": a["priority"],
            "Target date": a["target_date"],
            "Dependencies": a["dependencies"],
            "Status": a["status"],
        }
        for a in assumptions.ACTIONS
    ]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def _render_architecture() -> None:
    for opt in assumptions.ARCHITECTURE_OPTIONS:
        st.markdown(f"**{opt['name']}**")
        st.markdown(
            "- **Pros:** " + "; ".join(opt["pros"]) + "\n"
            "- **Cons:** " + "; ".join(opt["cons"]) + "\n"
            f"- **Assessment:** {opt['assessment']}"
        )
