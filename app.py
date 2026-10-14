"""Fireworks AI — Northstar Retail Group take-home assessment.

A single Streamlit application with two strictly separated audience views,
selected via a top segmented control (no sidebar):

  1. Internal Fireworks QBR (account management, engineering, executives)
  2. Customer-facing Northstar account health (VP CX, VP Engineering)

Only the selected view renders (the other view's code never runs), so the
customer page never renders internal content.

Run:
    streamlit run app.py

NOTE: the view selector is a local demonstration control, not an authentication
or security boundary. See README.md.
"""

from __future__ import annotations

import streamlit as st

from fireworks import metrics, scoring, ui
from fireworks.data import load_dataframe, validate_dataframe
from fireworks.views import customer, internal

st.set_page_config(
    page_title="Northstar — Fireworks AI",
    page_icon="✦",
    layout="wide",
)

ui.inject_css()

# ---------------------------------------------------------------------------
# Data + validation (loading is cached)
# ---------------------------------------------------------------------------

df = load_dataframe()
report = validate_dataframe(df)
ui.render_validation_banner(report)

# ---------------------------------------------------------------------------
# Top header + view selector (no sidebar, no date filter)
# ---------------------------------------------------------------------------

ui.header(
    "Northstar Retail Group — Fireworks AI",
    "Northstar flagship support agent · one month in production",
)

view = st.segmented_control(
    "View",
    options=["Internal Fireworks QBR", "Customer — Northstar account health"],
    default="Internal Fireworks QBR",
)

summary = metrics.compute_summary(df)
score = scoring.compute_health_score(df)

# ---------------------------------------------------------------------------
# Render only the selected view (true audience isolation)
# ---------------------------------------------------------------------------

if view == "Customer — Northstar account health":
    customer.render(summary, df)
else:
    internal.render(summary, score, df)

ui.footnote(
    "The view selector is a local demonstration control, not an authentication or "
    "security boundary. Metric notes: requests are inference calls; weighted "
    "automation = sum(automated) / sum(Tier-1); P95 latency is the daily reported value."
)
