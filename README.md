# Fireworks AI — Northstar Retail Group Take-Home Assessment

A production-style demonstration that turns one dataset into **three coordinated
deliverables**:

1. **Internal Fireworks QBR dashboard** — account management, engineering,
   executives.
2. **Customer-facing account-health dashboard** — Northstar VP Customer
   Experience & VP Engineering.
3. **Executive EBR** (`EBR.md`) — an executive brief with the results, expansion
   recommendation, scaling plan, pilot, budget, talking points, and top risk.

The application is fully local, needs **no API keys or paid services**, and runs
on the supplied 31-day CSV.

---

## Data

- **File:** `data/northstar_flagship_30_day_metrics.csv`
- **Rows:** 31 daily rows, `2026-08-01` through `2026-08-31`
- **Deployment:** `northstar-flagship-support-ft-v1`

### Columns

| Column | Type | Meaning |
| --- | --- | --- |
| `date` | date | Report day |
| `deployment` | str | Model/deployment id |
| `requests` | int | Inference calls (not tickets) |
| `input_tokens` / `output_tokens` / `total_tokens` | int | Token counts |
| `spend_usd` | float | Recorded inference spend |
| `p50_latency_ms` / `p95_latency_ms` | int | Daily reported latencies |
| `error_rate_pct` | float | Error rate % |
| `availability_pct` | float | Availability % |
| `tier1_tickets` / `automated_tier1_tickets` | int | Tier-1 ticket counts |
| `automation_rate_pct` | float | Daily automation % |
| `avg_handle_time_min` | float | Average handle time (min) |
| `csat_score` | float | CSAT score |
| `grounded_answer_rate_pct` / `quality_eval_pass_rate_pct` | float | Quality % |
| `escalation_rate_pct` | float | Escalation % |
| `operational_note` | str (optional) | Free-text event note |

---

## Installation

Requires **Python 3.11+** (developed and tested on Python 3.14).

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Pinned dependencies (also listed verbatim in `requirements.txt`):

| Package | Version |
| --- | --- |
| numpy | 2.5.4 |
| pandas | 3.0.6 |
| plotly | 7.1.0 |
| streamlit | 1.65.0 |
| pytest | 9.1.1 |

## Run

```bash
streamlit run app.py
```

Then open the printed local URL (default `http://localhost:8501`).

## Navigation

- The **sidebar** has the audience selector and a date-range filter.
- Selecting **Internal Fireworks QBR** renders the internal view.
- Selecting **Customer — Northstar account health** renders the customer view.
- The date filter recalculates every metric (totals, weighted automation, and
  the health score) over the selected window.

> **The view selector is a local demonstration control only.** It is **not** an
> authentication or security boundary — both views run in the same process and
> the internal view must never be exposed to a real customer. See `DESIGN.md`.

## Environment variables

**None.** The application reads only the bundled CSV and requires no secrets,
API keys, or network access.

## Tests

```bash
.venv/bin/python -m pytest -q
```

Coverage: metric reconciliation (totals, weighted automation, tokens, spend per
million tokens, date filtering), data validation (schema, types, ranges,
consistency), scoring (piecewise thresholds, weights, range), and
audience-separation (the customer view never contains internal-only terms).

---

## Architecture

```
app.py                     Streamlit entry point + sidebar + routing
fireworks/
  config.py                paths, column names, types, chart palette
  assumptions.py           ALL assumed/provided/proposed values in one place
  data.py                  CSV loading (cached) + validation
  metrics.py               pure metric calculations
  scoring.py               0–100 account-health scoring
  charts.py                Plotly chart builders
  ui.py                    shared UI helpers + stylesheet
  views/
    internal.py            Internal QBR view
    customer.py            Customer-facing view
data/
  northstar_flagship_30_day_metrics.csv
tests/
  test_metrics.py          reconciliation + filtering
  test_validation.py       schema/type/range checks
  test_scoring.py          scoring framework
  test_separation.py       internal/customer separation
```

Each view exposes a pure `content(...)` function that returns structured text so
the test suite can assert audience separation without running a browser, and a
`render(...)` function that draws that content with Streamlit.

---

## Metric definitions

| Metric | Definition | Notes |
| --- | --- | --- |
| Total requests | `sum(requests)` | Inference calls, **not** tickets |
| Total tokens | `sum(total_tokens)` | Input + output |
| Recorded spend | `sum(spend_usd)` | Inference spend only |
| **Weighted automation** | `sum(automated_tier1_tickets) / sum(tier1_tickets) × 100` | The only correct period rate; **not** the mean of daily rates |
| Unweighted daily avg | `mean(daily_rate_column)` | Labelled explicitly when used |
| Spend / M tokens | `sum(spend_usd) / (sum(total_tokens) / 1e6)` | Blended rate; dataset lacks per-request pricing |
| P95 latency | daily reported `p95_latency_ms` | **Not** a monthly P95 (raw distribution absent) |
| Automation (Aug 31) | `automation_rate_pct` on Aug 31 | 70.8% |

**Verified reconciliation** (recomputed by `tests/test_metrics.py`):

| Figure | Value |
| --- | --- |
| Total requests | **789,563** |
| Recorded spend | **$1,213.12** |
| Total Tier-1 tickets | **143,430** |
| Automated Tier-1 tickets | **97,488** |
| Weighted monthly automation | **67.97%** |
| Automation on Aug 31 | **70.8%** |
| Total tokens | 1,086,535,740 |
| Spend per M tokens | ~$1.12 |

## Provided vs. observed vs. assumed

- **Provided (scenario):** 70% automation, 35% handle-time reduction, +12 CSAT
  points. These are the assignment's stated business outcomes, measured against
  a pre-Fireworks baseline that is **not** in this dataset. The app reports them
  as provided with explanatory footnotes and never invents the baseline.
- **Observed:** everything computed from the CSV (totals, trends, automation,
  latency, errors, availability, grounding, quality, escalations, CSAT).
- **Assumed:** the four-brand expansion pipeline, top risks' owner/target, the
  action tracker, and all "illustrative" internal assessments. Every such value
  is labelled an assumption in `fireworks/assumptions.py` and in the UI.

## Scoring framework

`fireworks/scoring.py` maps each *scored* dimension to a 0–100 sub-score via
piecewise-linear thresholds (defined in `assumptions.py`), then takes a weighted
average over scored dimensions only:

- Automation (20%), grounded answer rate (15%), CSAT (15%), quality eval (10%),
  availability (10%), error rate (10%), P95 latency (10%), escalation (10%).

Relationship health, commercial posture, and competitive position are **not
scored** (no data) and are shown as unscored. The score is operational health,
not full account health.

## Known limitations

- P95 latency is daily-reported; no raw distribution is available for a true
  monthly P95.
- `spend_usd` is inference spend only, not fully loaded program cost.
- Quality/CSAT/grounding figures are the customer's reported values.
- No pre-Fireworks baseline exists in the data for the 35%/-12-point outcomes.
- The four-brand pipeline and internal qualitative assessments are illustrative
  assumptions, not facts.
- The view selector is a demo control, not an access-control boundary.

## Screenshots

No screenshot tooling is available in this environment, so no screenshots are
claimed. To capture them manually:

1. `streamlit run app.py`
2. For each audience view, select it in the sidebar, then use the browser menu
   or `Cmd/Ctrl+Shift+S` to capture the full page.

## Suggested ZIP structure

Exclude credentials, secrets, virtual environments, and generated artifacts.

```
fireworks-northstar-assessment/
  app.py
  requirements.txt
  README.md
  DESIGN.md
  EBR.md
  railway.json
  conftest.py
  data/northstar_flagship_30_day_metrics.csv
  fireworks/
    __init__.py
    config.py
    assumptions.py
    data.py
    metrics.py
    scoring.py
    charts.py
    ui.py
    views/__init__.py
    views/internal.py
    views/customer.py
  tests/
    test_metrics.py
    test_validation.py
    test_scoring.py
    test_separation.py
```

