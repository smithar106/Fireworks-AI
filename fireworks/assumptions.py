"""Central, readable configuration of every *assumed*, *provided*, and *proposed*
value in the application.

This file exists so a reviewer can audit every non-observed number in one place.
Nothing here is loaded from a database or computed on the fly — every entry is
either (a) a scenario-provided outcome, (b) a documented assumption, or (c) a
proposal clearly labelled as such.
"""

from __future__ import annotations

from typing import Literal

# ---------------------------------------------------------------------------
# Scenario-provided business outcomes
#
# These come from the assignment brief, NOT from the CSV. The 30-day dataset
# shows the *current* state and the trajectory, but it does NOT contain the
# pre-Fireworks baselines these outcomes are measured against. We therefore
# report them as provided and never invent a baseline.
# ---------------------------------------------------------------------------

PROVIDED_OUTCOMES: dict[str, dict[str, str]] = {
    "automation": {
        "label": "Automation",
        "value": "70%",
        "footnote": (
            "Scenario-provided outcome. Consistent with the dataset: weighted "
            "monthly automation is 67.97% and the Aug 31 daily rate is 70.8%."
        ),
    },
    "handle_time": {
        "label": "Handle-time reduction",
        "value": "35%",
        "footnote": (
            "Scenario-provided outcome vs. a pre-Fireworks baseline that is NOT "
            "in this dataset. The observed 30-day trend is a reduction in "
            "avg_handle_time_min from 8.15 to 7.35 min (~10%)."
        ),
    },
    "csat": {
        "label": "CSAT improvement",
        "value": "+12 points",
        "footnote": (
            "Scenario-provided outcome vs. a pre-Fireworks baseline that is NOT "
            "in this dataset. The observed 30-day trend is csat_score 80.6 to "
            "84.2 (+3.6 points)."
        ),
    },
}

# ---------------------------------------------------------------------------
# Account health scoring framework
#
# Each dimension maps an *observed* metric (from the CSV) to a 0–100 sub-score
# using piecewise-linear thresholds, then a weighted average is taken over the
# SCORED dimensions only. Unobserved dimensions (relationship, commercial,
# competitive) are listed separately and explicitly NOT scored.
#
# `source` declares how the observed value is computed from the filtered frame:
#   ("weighted", None)      -> weighted monthly automation (sum/ sum)
#   ("latest", <column>)    -> latest day's value in the filtered range
# `direction` is informational ("higher" = higher value is better).
# `thresholds` are (metric_value, sub_score) points sorted ascending by value;
#   the scorer interpolates linearly between them and clamps to [0, 100].
# ---------------------------------------------------------------------------

ScoringSource = tuple[Literal["weighted", "latest"], str | None]

SCORING_DIMENSIONS: list[dict] = [
    {
        "key": "automation",
        "name": "Automation",
        "weight": 0.20,
        "direction": "higher",
        "source": ("weighted", None),
        "thresholds": [(50.0, 0.0), (60.0, 55.0), (65.0, 75.0), (70.0, 90.0), (80.0, 100.0)],
        "description": "Weighted monthly Tier-1 automation (sum automated / sum Tier-1).",
    },
    {
        "key": "grounded_answer_rate",
        "name": "Grounded answer rate",
        "weight": 0.15,
        "direction": "higher",
        "source": ("latest", "grounded_answer_rate_pct"),
        "thresholds": [(85.0, 0.0), (90.0, 60.0), (93.0, 80.0), (96.0, 100.0)],
        "description": "Share of answers that passed grounding checks (latest day).",
    },
    {
        "key": "quality_eval_pass_rate",
        "name": "Quality eval pass rate",
        "weight": 0.10,
        "direction": "higher",
        "source": ("latest", "quality_eval_pass_rate_pct"),
        "thresholds": [(85.0, 0.0), (90.0, 60.0), (93.0, 80.0), (96.0, 100.0)],
        "description": "Share of evaluated responses passing quality checks (latest day).",
    },
    {
        "key": "availability",
        "name": "Availability",
        "weight": 0.10,
        "direction": "higher",
        "source": ("latest", "availability_pct"),
        "thresholds": [(99.0, 0.0), (99.5, 60.0), (99.9, 100.0)],
        "description": "Reported availability percentage (latest day).",
    },
    {
        "key": "error_rate",
        "name": "Error rate",
        "weight": 0.10,
        "direction": "lower",
        "source": ("latest", "error_rate_pct"),
        "thresholds": [(0.5, 100.0), (1.0, 90.0), (2.0, 70.0), (5.0, 0.0)],
        "description": "Reported error rate percentage (latest day); lower is better.",
    },
    {
        "key": "p95_latency",
        "name": "P95 latency",
        "weight": 0.10,
        "direction": "lower",
        "source": ("latest", "p95_latency_ms"),
        "thresholds": [(1000.0, 100.0), (1500.0, 85.0), (2000.0, 60.0), (3000.0, 0.0)],
        "description": "Daily reported P95 latency in ms (latest day); lower is better.",
    },
    {
        "key": "csat",
        "name": "CSAT",
        "weight": 0.15,
        "direction": "higher",
        "source": ("latest", "csat_score"),
        "thresholds": [(75.0, 0.0), (80.0, 75.0), (85.0, 100.0)],
        "description": "Customer satisfaction score (latest day).",
    },
    {
        "key": "escalation_rate",
        "name": "Escalation rate",
        "weight": 0.10,
        "direction": "lower",
        "source": ("latest", "escalation_rate_pct"),
        "thresholds": [(10.0, 100.0), (12.0, 80.0), (15.0, 60.0), (20.0, 0.0)],
        "description": "Share of Tier-1 tickets escalated (latest day); lower is better.",
    },
]

# Dimensions the dataset cannot support. Shown for transparency, never scored.
UNSCORED_DIMENSIONS: list[dict] = [
    {"name": "Relationship health", "reason": "No relationship/coverage data in dataset."},
    {"name": "Commercial / contract posture", "reason": "No contract or renewal data in dataset."},
    {"name": "Competitive position", "reason": "No competitive intelligence in dataset."},
]

# Human-readable tiers for the overall score.
SCORE_TIERS: list[dict] = [
    {"min": 85, "label": "Healthy", "tone": "good"},
    {"min": 70, "label": "Stable", "tone": "ok"},
    {"min": 50, "label": "Watch", "tone": "warn"},
    {"min": 0, "label": "At risk", "tone": "bad"},
]

# ---------------------------------------------------------------------------
# Operational event timeline (from the CSV `operational_note` column)
# ---------------------------------------------------------------------------

OPERATIONAL_EVENTS: list[dict] = [
    {
        "date": "2026-08-09",
        "kind": "incident",
        "title": "Catalog sync latency & error spike",
        "detail": "Catalog sync caused a latency and error spike; mitigated the same day.",
        "observed": "p95 latency 2,168 ms (vs ~1,600–1,800 ms nearby), error rate 2.18%, availability 99.695%.",
    },
    {
        "date": "2026-08-21",
        "kind": "incident",
        "title": "Promotional traffic burst",
        "detail": "Traffic burst during promotion; autoscaling threshold adjusted.",
        "observed": "p95 latency 1,794 ms, error rate 1.41%, availability 99.803%.",
    },
    {
        "date": "2026-08-24",
        "kind": "improvement",
        "title": "RAG index refresh",
        "detail": "RAG index refresh improved grounding on return-policy questions.",
        "observed": "Grounding 94.6% → 95.7% on Aug 24.",
    },
]

# ---------------------------------------------------------------------------
# Top three prioritized risks (internal view)
#
# `impact`, `evidence`, and `mitigation` are grounded in the observed data where
# possible; `owner_role` and `target_date` are proposed.
# ---------------------------------------------------------------------------

TOP_RISKS: list[dict] = [
    {
        "title": "Content-refresh events degrade latency and errors",
        "impact": "High — a catalog/index refresh (Aug 9) drove p95 to 2,168 ms and error rate to 2.18%.",
        "evidence": "Aug 9 operational note + p95/error/availability series.",
        "mitigation": "Staged index swaps, prefix-cache warming before cutover, and a rollback gate.",
        "owner_role": "Forward Deployed Engineer",
        "target_date": "2026-09-30",
    },
    {
        "title": "Promotional traffic bursts outpace autoscaling",
        "impact": "Medium — a promotion (Aug 21) drove p95 to 1,794 ms and error rate to 1.41%.",
        "evidence": "Aug 21 operational note + latency/error series.",
        "mitigation": "Predictive autoscaling keyed to promotion calendar; graceful load shedding.",
        "owner_role": "Solutions Architect",
        "target_date": "2026-10-15",
    },
    {
        "title": "~30% of Tier-1 remains manual",
        "impact": "Medium — 45,942 of 143,430 Tier-1 tickets were not automated in August.",
        "evidence": "Weighted monthly automation 67.97% (sum automated / sum Tier-1).",
        "mitigation": "Expand automated coverage to the highest-volume unresolved intents; measure per-intent.",
        "owner_role": "Applied Data Scientist",
        "target_date": "2026-10-31",
    },
]

# ---------------------------------------------------------------------------
# Action tracker (internal view). owner_role/priority/target_date/dependencies
# are proposed; status reflects a live demo placeholder.
# ---------------------------------------------------------------------------

ACTIONS: list[dict] = [
    {
        "action": "Instrument per-intent automation coverage",
        "owner_role": "Applied Data Scientist",
        "priority": "High",
        "target_date": "2026-09-18",
        "dependencies": "None",
        "status": "In progress",
    },
    {
        "action": "Add pre-cutover cache warming for catalog/index refreshes",
        "owner_role": "Forward Deployed Engineer",
        "priority": "High",
        "target_date": "2026-09-30",
        "dependencies": "Engineering capacity",
        "status": "Proposed",
    },
    {
        "action": "Tie autoscaling to the promotion calendar",
        "owner_role": "Solutions Architect",
        "priority": "Medium",
        "target_date": "2026-10-15",
        "dependencies": "Promotion calendar from Northstar",
        "status": "Proposed",
    },
    {
        "action": "Agree pilot success criteria for a second brand",
        "owner_role": "Account Executive",
        "priority": "Medium",
        "target_date": "2026-10-01",
        "dependencies": "Customer EBR",
        "status": "Proposed",
    },
    {
        "action": "Document RAG index refresh runbook",
        "owner_role": "Forward Deployed Engineer",
        "priority": "Low",
        "target_date": "2026-09-15",
        "dependencies": "None",
        "status": "Done",
    },
]

# ---------------------------------------------------------------------------
# Four-brand expansion pipeline (internal view)
#
# Every field here is a HYPOTHETICAL illustration and is labelled an assumption
# in the UI. No real customer data is implied.
# ---------------------------------------------------------------------------

BRAND_PIPELINE: list[dict] = [
    {
        "name": "Brand B — Home & Living",
        "positioning": "Premium home furnishings and decor",
        "support_volume": "~15k tickets/mo (assumed)",
        "catalog_complexity": "High — large SKU count, seasonal",
        "brand_tone": "Warm, detailed",
        "return_policy_complexity": "High — furniture/oversized exceptions",
        "team_maturity": "Medium — established in-house help desk",
        "technical_readiness": "Medium — existing help desk, no LLM",
        "expected_dependencies": "Product catalog sync, return-policy retrieval index",
        "pilot_priority": 1,
    },
    {
        "name": "Brand C — Beauty & Personal Care",
        "positioning": "Clean, accessible beauty",
        "support_volume": "~8k tickets/mo (assumed)",
        "catalog_complexity": "Medium — ingredients, usage guidance",
        "brand_tone": "Polished, safety-conscious",
        "return_policy_complexity": "Medium — hygiene-item restrictions",
        "team_maturity": "Low — outsourced contact center",
        "technical_readiness": "Low — outsourced contact center",
        "expected_dependencies": "Ingredient/safety knowledge base, policy isolation",
        "pilot_priority": 2,
    },
    {
        "name": "Brand D — Electronics & Accessories",
        "positioning": "Value consumer electronics",
        "support_volume": "~20k tickets/mo (assumed)",
        "catalog_complexity": "High — specs, compatibility",
        "brand_tone": "Technical, concise",
        "return_policy_complexity": "High — warranty + serial tracking",
        "team_maturity": "High — mature internal ops",
        "technical_readiness": "High — existing API integrations",
        "expected_dependencies": "Spec DB, warranty lookup, serialized returns",
        "pilot_priority": 3,
    },
    {
        "name": "Brand E — Outdoor & Apparel",
        "positioning": "Casual outdoor lifestyle",
        "support_volume": "~6k tickets/mo (assumed)",
        "catalog_complexity": "Low — sizing, care instructions",
        "brand_tone": "Casual, quick",
        "return_policy_complexity": "Low — 30-day standard",
        "team_maturity": "Low — small team",
        "technical_readiness": "Low — minimal tooling",
        "expected_dependencies": "Size guide + order status APIs",
        "pilot_priority": 4,
    },
]

# ---------------------------------------------------------------------------
# Architectural proposal (evaluated in the internal view)
# ---------------------------------------------------------------------------

ARCHITECTURE_OPTIONS: list[dict] = [
    {
        "name": "Shared base model + brand system prompts + isolated retrieval indexes",
        "pros": [
            "Lowest compute cost (one model, high KV/prefix-cache reuse)",
            "Lowest operational complexity — one serving path to maintain",
            "Best latency/throughput via shared prefix caching",
            "Policy isolation enforced at the retrieval + prompt layer",
        ],
        "cons": [
            "Brand-specific behavior is bounded by prompt quality",
            "One model's regression affects every brand",
            "Retrieval isolation must be enforced rigorously (index-per-brand)",
        ],
        "assessment": "Recommended default — cheapest and simplest, sufficient for most brands.",
    },
    {
        "name": "Separate fine-tuned models per brand",
        "pros": [
            "Strongest brand-specific tone/behavior control",
            "Independent release cadence and rollback per brand",
        ],
        "cons": [
            "Highest cost (N serving workloads, no shared prefix cache)",
            "Highest operational + evaluation burden",
            "Fine-tuning is usually unnecessary to use private enterprise knowledge",
        ],
        "assessment": "Reserve for proven behavior gaps the shared model cannot close.",
    },
    {
        "name": "Hybrid: fine-tune only where behavior gaps are proven",
        "pros": [
            "Targets spend at genuine quality gaps",
            "Keeps shared-model cost benefits for everyone else",
        ],
        "cons": [
            "Requires a measurable, gate-driven fine-tuning workflow",
        ],
        "assessment": "Recommended path — start shared, fine-tune only on measured failure.",
    },
]

# ---------------------------------------------------------------------------
# Internal-only terms (MUST NOT appear in the customer view)
# ---------------------------------------------------------------------------

INTERNAL_ONLY_TERMS: tuple[str, ...] = (
    "competitive risk",
    "competitor",
    "margin",
    "unit economics",
    "expansion confidence",
    "account blocker",
    "staffing",
    "headcount",
    "relationship coverage",
    "renewal risk",
    "churn",
    "win rate",
)
