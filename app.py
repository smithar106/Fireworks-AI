"""Fireworks AI — Northstar Retail Group take-home assessment.

A single Streamlit application with two strictly separated audience views:

  1. Internal Fireworks QBR (account management, engineering, executives)
  2. Customer-facing Northstar account health (VP CX, VP Engineering)

Run:
    streamlit run app.py

NOTE: the view selector in the sidebar is for DEMONSTRATION ONLY. It is not an
authentication or security boundary — both views render in the same process and
the internal view is never exposed to a real customer. See README.md.
"""

from __future__ import annotations

import streamlit as st

from fireworks import config, metrics, scoring, ui
from fireworks.data import load_dataframe, validate_dataframe
from fireworks.views import customer, internal

st.set_page_config(
    page_title="Northstar — Fireworks AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.inject_css()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

df = load_dataframe()
report = validate_dataframe(df)

# ---------------------------------------------------------------------------
# Sidebar: audience selector + date filter
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### Audience view")
    view = st.radio(
        "Select a view (demo only)",
        options=("Internal Fireworks QBR", "Customer — Northstar account health"),
        index=0,
    )
    st.markdown(
        '<div class="fw-footnote">The view selector is a local demonstration control, '
        "not an authentication or security boundary. Both views run in the same "
        "process.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("### Date range")
    min_date = df[config.DATE_COL].min().date()
    max_date = df[config.DATE_COL].max().date()
    start, end = st.date_input(
        "Filter window",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

ui.render_validation_banner(report)

# ---------------------------------------------------------------------------
# Compute filtered metrics + score (correctly recalculated per filter)
# ---------------------------------------------------------------------------

filtered = metrics.filter_by_date(df, start, end)
if filtered.empty:
    st.warning("No data in the selected date range.")
    st.stop()

summary = metrics.compute_summary(filtered)
score = scoring.compute_health_score(filtered)

st.title("Northstar Retail Group — Fireworks AI")
st.caption(
    f"Deployment: `northstar-flagship-support-ft-v1` · "
    f"{summary['start_date']} to {summary['end_date']} · {summary['days']} days"
)

if view == "Internal Fireworks QBR":
    internal.render(summary, score, filtered)
else:
    customer.render(summary, filtered)

ui.footnote(
    "Metric notes: requests are inference calls, not tickets. Weighted automation = "
    "sum(automated) / sum(Tier-1). 'P95 latency' is the daily reported P95 (a true "
    "monthly P95 requires the raw distribution, which is not provided). Recorded spend "
    "is inference spend only."
)
