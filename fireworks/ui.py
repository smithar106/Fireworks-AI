"""Shared UI helpers: styling, KPI cards, sections, footnotes, and formatting.

The design language mirrors the reference dashboard: a restrained light theme,
uppercase KPI labels over large values, and bordered white cards.
"""

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


_TONE_COLORS = {
    "neutral": config.INK,
    "good": config.GOOD_TEXT,
    "bad": config.BAD,
    "warn": config.WARN_TEXT,
    "accent": config.ACCENT_DARK,
}

# Monotonic key generator for charts (charts hold no widget state, so a
# run-scoped counter guarantees unique Streamlit element ids without callers
# having to thread keys everywhere).
_chart_seq = 0


def chart(fig, use_container_width: bool = True) -> None:
    global _chart_seq
    _chart_seq += 1
    st.plotly_chart(fig, width="stretch", key=f"fw_chart_{_chart_seq}")


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1180px; }
        h1, h2, h3 { color: #19191F; letter-spacing: -0.01em; }

        .fw-header { border-bottom: 1px solid #E6E6EA; padding-bottom: 1rem; margin-bottom: 0.25rem; }
        .fw-header h1 { font-size: 1.5rem; font-weight: 800; margin: 0; color: #19191F; }
        .fw-header p { margin: 0.25rem 0 0; color: #6B6B75; font-size: 0.9rem; }

        .fw-kpi-row {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 0.75rem; margin: 0.6rem 0 0.6rem;
        }
        .fw-kpi {
            background: #FFFFFF; border: 1px solid #E6E6EA; border-radius: 0.75rem;
            padding: 1rem 1.1rem; box-shadow: 0 1px 2px rgba(25,25,31,0.04);
        }
        .fw-kpi-label {
            font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em;
            text-transform: uppercase; color: #6B6B75;
        }
        .fw-kpi-value { font-size: 1.6rem; font-weight: 800; margin-top: 0.25rem; color: #19191F; line-height: 1.1; }
        .fw-kpi-sub { font-size: 0.78rem; color: #6B6B75; margin-top: 0.25rem; }

        .fw-section { margin: 0 0 0.6rem; }
        .fw-section h3 { font-size: 1rem; font-weight: 800; margin: 0; color: #19191F; }
        .fw-subtitle { color: #6B6B75; font-size: 0.85rem; margin: 0.15rem 0 0; }
        .fw-eyebrow { font-size: 0.7rem; letter-spacing: 0.14em; text-transform: uppercase; color: #8A8A94; font-weight: 700; }

        .fw-hero {
            font-size: 1.15rem; font-weight: 700; color: #19191F; line-height: 1.35;
            letter-spacing: -0.01em; margin: 0.4rem 0 1rem; max-width: 900px;
        }
        .fw-hero .accent { color: #2563EB; }

        .fw-footnote { color: #8A8A94; font-size: 0.76rem; line-height: 1.45;
            border-top: 1px solid #E6E6EA; margin-top: 0.4rem; padding-top: 0.4rem; }

        /* Uniform spacing between bordered section cards */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 0.75rem;
        }
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 1rem 1.1rem;
        }

        /* Prominent top view selector (segmented control) */
        [data-testid="stButtonGroup"] { margin: 0.4rem 0 1rem 0; }
        [data-testid="stButtonGroup"] [data-variant="segmented_control"] {
            font-size: 1rem !important;
            padding: 0.55rem 1.75rem !important;
            border-radius: 0.7rem !important;
        }
        [data-testid="stButtonGroup"] [data-variant="segmented_control"]:has([data-selected="true"]),
        [data-testid="stButtonGroup"] [data-selected="true"] {
            background-color: #2563EB !important;
            border-color: #2563EB !important;
        }
        [data-testid="stButtonGroup"] [data-variant="segmented_control"]:has([data-selected="true"]) *,
        [data-testid="stButtonGroup"] [data-selected="true"] * {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------


def header(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="fw-header"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def hero(text: str) -> None:
    """Render the executive one-liner that opens each view."""
    st.markdown(f'<div class="fw-hero">{text}</div>', unsafe_allow_html=True)


def kpi_row(items: list[dict[str, Any]]) -> None:
    """Render a responsive row of KPI cards.

    Each item: {"label": str, "value": str, "sub": str | None, "tone": str}.
    """
    cards = []
    for it in items:
        color = _TONE_COLORS.get(it.get("tone", "neutral"), config.INK)
        sub = f'<div class="fw-kpi-sub">{it["sub"]}</div>' if it.get("sub") else ""
        cards.append(
            f'<div class="fw-kpi"><div class="fw-kpi-label">{it["label"]}</div>'
            f'<div class="fw-kpi-value" style="color:{color}">{it["value"]}</div>{sub}</div>'
        )
    st.markdown(f'<div class="fw-kpi-row">{"".join(cards)}</div>', unsafe_allow_html=True)


def section(title: str, subtitle: str | None = None, eyebrow: str | None = None) -> None:
    parts = []
    if eyebrow:
        parts.append(f'<div class="fw-eyebrow">{eyebrow}</div>')
    parts.append(f"<h3>{title}</h3>")
    if subtitle:
        parts.append(f'<div class="fw-subtitle">{subtitle}</div>')
    st.markdown(f'<div class="fw-section">{"".join(parts)}</div>', unsafe_allow_html=True)


def pill(text: str, tone: str = "muted") -> None:
    tones = {
        "muted": ("#F1F0EB", "#5C6470"),
        "good": ("#EAF7EE", config.GOOD_TEXT),
        "warn": ("#FDF3E3", config.WARN_TEXT),
        "bad": ("#FDECEA", "#8A1C0D"),
        "accent": ("#EDF2FF", config.ACCENT_DARK),
    }
    bg, fg = tones.get(tone, tones["muted"])
    st.markdown(
        f'<span style="display:inline-block;background:{bg};color:{fg};'
        f'border-radius:999px;padding:0.12rem 0.6rem;font-size:0.74rem;font-weight:700;">{text}</span>',
        unsafe_allow_html=True,
    )


def footnote(text: str) -> None:
    st.markdown(f'<div class="fw-footnote">{text}</div>', unsafe_allow_html=True)


def takeaways(items: list[dict[str, Any]]) -> None:
    """Render a compact list of one-line takeaways (colored dot + text)."""
    color = {"good": config.GOOD, "bad": config.BAD, "warn": config.WARN, "neutral": config.MUTED}
    rows = []
    for it in items:
        tone = it.get("tone", "neutral")
        dot = color.get(tone, config.MUTED)
        rows.append(
            f'<li style="display:flex;gap:0.5rem;align-items:baseline;margin-bottom:0.35rem;'
            f'font-size:0.85rem;color:{config.INK};">'
            f'<span style="width:7px;height:7px;border-radius:999px;background:{dot};'
            f'flex:0 0 auto;transform:translateY(-1px);"></span>'
            f'<span>{it["text"]}</span></li>'
        )
    st.markdown(f'<ul style="list-style:none;margin:0;padding:0;">{"".join(rows)}</ul>', unsafe_allow_html=True)


def disclaimer(text: str) -> None:
    st.info(text)


def render_validation_banner(report: dict[str, Any]) -> None:
    if report["ok"]:
        if report.get("warnings"):
            st.warning("Data validation: " + "; ".join(report["warnings"]))
    else:
        st.error("Data validation errors: " + "; ".join(report["errors"]))
        st.stop()
