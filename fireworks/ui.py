"""Shared UI helpers: styling, KPI cards, sections, footnotes, and formatting."""

from __future__ import annotations

from typing import Any

import streamlit as st

from fireworks import config

# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def fmt_int(n: int | float) -> str:
    return f"{int(n):,}"


def fmt_usd(x: float) -> str:
    return f"${x:,.2f}"


def fmt_pct(x: float, decimals: int = 1) -> str:
    return f"{x:.{decimals}f}%"


def fmt_number(x: float, decimals: int = 2) -> str:
    return f"{x:,.{decimals}f}"


def fmt_ms(x: float) -> str:
    return f"{x:,.0f} ms"


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------


def inject_css() -> None:
    """Inject a restrained enterprise SaaS stylesheet."""
    st.markdown(
        """
        <style>
        :root {
            --ink: #14161A;
            --muted: #5C6470;
            --line: #E7E5DF;
            --accent: #3457D5;
        }
        .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1160px; }
        h1, h2, h3 { color: var(--ink); letter-spacing: -0.01em; }
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 0.9rem;
            padding: 1rem 1.1rem;
            box-shadow: 0 1px 1px rgba(20,22,26,0.04), 0 10px 26px -20px rgba(20,22,26,0.16);
        }
        div[data-testid="stMetricValue"] { font-size: 1.5rem; font-weight: 650; }
        div[data-testid="stMetricLabel"] { color: var(--muted); }
        .fw-footnote {
            color: #9299A4; font-size: 0.78rem; line-height: 1.45;
            border-top: 1px solid var(--line); margin-top: 0.4rem; padding-top: 0.4rem;
        }
        .fw-eyebrow {
            font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase;
            color: #9299A4; font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------


def section(title: str, subtitle: str | None = None, eyebrow: str | None = None) -> None:
    if eyebrow:
        st.markdown(f'<div class="fw-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f'<p style="color:{config.MUTED};margin-top:-0.5rem;">{subtitle}</p>', unsafe_allow_html=True)


def kpi(label: str, value: str, delta: str | None = None, delta_color: str = "normal", help: str | None = None) -> None:
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color, help=help)


def pill(text: str, tone: str = "muted") -> None:
    tones = {
        "muted": ("#F1F0EB", "#5C6470"),
        "good": ("#E8F8F0", "#0A5C3F"),
        "warn": ("#FBF1E1", "#8A5208"),
        "bad": ("#FBEDEA", "#8A3324"),
        "accent": ("#ECF0FD", "#16286B"),
    }
    bg, fg = tones.get(tone, tones["muted"])
    st.markdown(
        f'<span style="display:inline-block;background:{bg};color:{fg};'
        f'border-radius:999px;padding:0.15rem 0.65rem;font-size:0.75rem;font-weight:600;">{text}</span>',
        unsafe_allow_html=True,
    )


def footnote(text: str) -> None:
    st.markdown(f'<div class="fw-footnote">{text}</div>', unsafe_allow_html=True)


def disclaimer(text: str) -> None:
    st.info(text)


def render_validation_banner(report: dict[str, Any]) -> None:
    """Show a validation status banner; does not block rendering on warnings."""
    if report["ok"]:
        if report.get("warnings"):
            st.warning("Data validation: " + "; ".join(report["warnings"]))
    else:
        st.error("Data validation errors: " + "; ".join(report["errors"]))
        st.stop()
