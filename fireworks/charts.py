"""Plotly chart builders with a consistent, professional style."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from fireworks import config


def _style(fig: go.Figure, title: str, y_title: str, height: int = 300) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=config.INK), x=0.01, xanchor="left"),
        height=height,
        margin=dict(l=10, r=10, t=42, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color=config.INK),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", bordercolor=config.BORDER, font=dict(color=config.INK, size=12)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=11)),
        yaxis=dict(title=y_title, gridcolor=config.BORDER, zeroline=False, title_font=dict(size=11, color=config.MUTED)),
        xaxis=dict(gridcolor=config.BORDER, zeroline=False, tickformat="%b %d", nticks=8),
    )
    return fig


def _area(df: pd.DataFrame, column: str, label: str, title: str, y_title: str, color: str, height: int = 300) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=df[config.DATE_COL],
            y=df[column],
            mode="lines",
            name=label,
            line=dict(width=2.2, color=color),
            fill="tozeroy",
            fillcolor=_rgba(color, 0.10),
            hovertemplate=f"{label}: %{{y:,.0f}}<extra></extra>",
        )
    )
    return _style(fig, title, y_title, height)


def line(
    df: pd.DataFrame,
    columns: list[str],
    labels: list[str] | None = None,
    title: str = "",
    y_title: str = "",
    height: int = 300,
    area: str | None = None,
) -> go.Figure:
    """One or more daily line series against date.

    If `area` names one of `columns`, that series is rendered as a filled area;
    the rest are plain lines. `labels` are used for legend/hover.
    """
    labels = labels or columns
    fig = go.Figure()
    for i, col in enumerate(columns):
        if area and col == area:
            fig.add_trace(
                go.Scatter(
                    x=df[config.DATE_COL],
                    y=df[col],
                    mode="lines",
                    name=labels[i],
                    line=dict(width=2.2, color=config.PALETTE[i % len(config.PALETTE)]),
                    fill="tozeroy",
                    fillcolor=_rgba(config.PALETTE[i % len(config.PALETTE)], 0.10),
                    hovertemplate=f"{labels[i]}: %{{y:,.2f}}<extra></extra>",
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=df[config.DATE_COL],
                    y=df[col],
                    mode="lines",
                    name=labels[i],
                    line=dict(width=2.2, color=config.PALETTE[i % len(config.PALETTE)]),
                    hovertemplate=f"{labels[i]}: %{{y:,.2f}}<extra></extra>",
                )
            )
    return _style(fig, title, y_title, height)


def bars(
    categories: list[str],
    values: list[float],
    title: str = "",
    x_title: str = "",
    color: str = config.ACCENT,
    height: int = 300,
) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=values,
            y=categories,
            orientation="h",
            marker_color=color,
            hovertemplate="%{y}: %{x:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=config.INK), x=0.01, xanchor="left"),
        height=height,
        margin=dict(l=10, r=10, t=42, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color=config.INK),
        xaxis=dict(title=x_title, gridcolor=config.BORDER, zeroline=False, title_font=dict(size=11, color=config.MUTED)),
        yaxis=dict(autorange="reversed", gridcolor=config.BORDER),
    )
    return fig


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
