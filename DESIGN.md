# Dashboard Design Document

## Screenshots

No screenshot tooling is available in this environment, so no screenshots are
included and none are claimed. To capture them for submission:

1. `streamlit run app.py`
2. In the sidebar, select **Internal Fireworks QBR** and capture the page.
3. Select **Customer — Northstar account health** and capture the page.
4. Use the browser's full-page screenshot (e.g. DevTools → "Capture full size
   screenshot", or `Cmd/Ctrl+Shift+S`).

## Intended audiences

| View | Audience | Goals |
| --- | --- | --- |
| Internal Fireworks QBR | Account manager, Forward Deployed Engineer, Applied Data Scientist, Solutions Architect, executive sponsor | Defend the account, surface risk, plan expansion, drive decisions |
| Customer — account health | VP Customer Experience, VP Engineering | Confirm value, understand operations and quality, plan next steps |

## Design principles

1. **One dataset, two lenses.** Both views read the same validated CSV, but the
   content and framing are built from separate modules (`views/internal.py`,
   `views/customer.py`).
2. **Accuracy over flash.** Metrics are recomputed from source data with correct
   weighting; averages are labelled; unobserved dimensions are never estimated.
3. **Transparent assumptions.** Every non-observed value lives in
   `assumptions.py` and is labelled in the UI.
4. **Executive readability.** KPI cards for the top line, interactive charts for
   the detail, footnotes for the fine print.

## Visualizations

- **KPI cards** — headline numbers (score, weighted automation, spend, requests,
  availability, latency, quality).
- **Line charts** — daily series for requests, tokens, spend, automation,
  latency (P50/P95), error rate, availability, grounding, eval, escalations, CSAT.
- **Horizontal bar chart** — dimension sub-scores in the health framework.
- **Tables** — scoring breakdown, incidents, risks, brand pipeline, action tracker.

## Account health score

A transparent 0–100 score, weighted across eight *scored* dimensions (see
`assumptions.SCORING_DIMENSIONS`). Each dimension maps an observed metric to a
sub-score via piecewise-linear thresholds, and the weighted average is taken over
scored dimensions only. Relationship, commercial, and competitive dimensions are
listed but never scored. The score is intentionally presented as **operational**
health, with explicit sensitivity/limitation notes.

## Content separation

- The two views are **separate Streamlit pages** (`st.navigation`), so only the
  selected view's code executes on any given render.
- The customer view contains **only** operational, quality, adoption, and joint
  next-step content.
- Internal-only content (competitive risk, relationship coverage, staffing,
  unit economics, margins, account blockers, expansion confidence) is rendered
  **only** in the internal view.
- `assumptions.INTERNAL_ONLY_TERMS` enumerates the forbidden vocabulary, and
  `tests/test_separation.py` verifies the customer view never contains it.

## Exclusions (from the customer view)

Competitive intelligence, commercial/margin analysis, staffing and headcount,
unit economics, expansion confidence, account blockers, and renewal/churn
sentiment.

## Tradeoffs

- **Scoring simplicity vs. richness:** piecewise-linear thresholds are easy to
  audit but coarse; they are chosen over a fitted model for transparency.
- **Point-in-time vs. period metrics:** automation uses the weighted period rate;
  latency/quality use the latest-day value; both are labelled.
- **Single-file demo vs. production auth:** the navigation selector is a
  convenience control, explicitly documented as not a security boundary.

## Caveats

- Daily P95 is not a monthly P95 (raw distribution unavailable).
- Spend is inference-only, not fully loaded cost.
- Provided outcomes (35% handle-time, +12 CSAT) lack an in-data baseline.
- Brand pipeline and qualitative internal assessments are illustrative.

## Assumptions

All assumptions are centralized in `fireworks/assumptions.py` and labelled in
the UI: the four-brand expansion profiles, top-risk owners/targets, the action
tracker, and every "illustrative" internal assessment.
