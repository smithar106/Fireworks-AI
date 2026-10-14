"""Fireworks AI — Northstar Retail Group take-home assessment.

A single Streamlit application with two strictly separated audience views
selected via a top tab bar:

  1. Internal Fireworks QBR (account management, engineering, executives)
  2. Customer-facing Northstar account health (VP CX, VP Engineering)

Run:
    streamlit run app.py

NOTE: the tab selector is for DEMONSTRATION ONLY. It is not an authentication
or security boundary — both views run in the same process and the internal view
must never be exposed to a real customer. See README.md.
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
# Sidebar: date filter (view selection lives in the top tabs)
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("#### Date range")
    min_date = df[config.DATE_COL].min().date()
    max_date = df[config.DATE_COL].max().date()
    start, end = st.date_input(
        "Filter window",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    ui.footnote(
        "The Internal / Customer tabs are a local demonstration control — not an "
        "authentication or security boundary."
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

ui.header(
    "Northstar Retail Group — Fireworks AI",
    f"Deployment `northstar-flagship-support-ft-v1` · {summary['start_date']} to {summary['end_date']} · {summary['days']} days",
)

# ---------------------------------------------------------------------------
# Top-level audience tabs
# ---------------------------------------------------------------------------

internal_tab, customer_tab = st.tabs(
    ["Internal Fireworks QBR", "Customer — Northstar account health"]
)

with internal_tab:
    internal.render(summary, score, filtered)

with customer_tab:
    customer.render(summary, filtered)
