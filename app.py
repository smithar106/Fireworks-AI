"""Fireworks AI — Northstar Retail Group take-home assessment.

A single Streamlit application with two strictly separated audience views,
selected via the left navigation:

  1. Internal Fireworks QBR (account management, engineering, executives)
  2. Customer-facing Northstar account health (VP CX, VP Engineering)

The two views are implemented as separate `st.Page`s, so only the selected
view's code executes on any given render — the customer view never renders the
internal view's content (and vice versa).

Run:
    streamlit run app.py

NOTE: the navigation selector is a local demonstration control, not an
authentication or security boundary. See README.md.
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
# Data + validation (shared across pages; loading is cached)
# ---------------------------------------------------------------------------

df = load_dataframe()
report = validate_dataframe(df)

# ---------------------------------------------------------------------------
# Shared sidebar: date filter (view selection lives in the left navigation)
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
        "The Internal / Customer navigation is a local demonstration control — "
        "not an authentication or security boundary."
    )

ui.render_validation_banner(report)

filtered = metrics.filter_by_date(df, start, end)
if filtered.empty:
    st.warning("No data in the selected date range.")
    st.stop()

summary = metrics.compute_summary(filtered)
score = scoring.compute_health_score(filtered)


def _header(summary) -> None:
    ui.header(
        "Northstar Retail Group — Fireworks AI",
        f"Deployment `northstar-flagship-support-ft-v1` · "
        f"{summary['start_date']} to {summary['end_date']} · {summary['days']} days",
    )


def internal_page() -> None:
    _header(summary)
    internal.render(summary, score, filtered)


def customer_page() -> None:
    _header(summary)
    customer.render(summary, filtered)


# ---------------------------------------------------------------------------
# Separate pages for true audience isolation (only the selected page renders)
# ---------------------------------------------------------------------------

pg = st.navigation(
    [
        st.Page(internal_page, title="Internal Fireworks QBR", default=True),
        st.Page(customer_page, title="Customer — Northstar account health"),
    ]
)
pg.run()
