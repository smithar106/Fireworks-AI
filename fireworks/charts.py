"""Plotly chart builders with a consistent, accessible style.

Every figure sets explicit titles, axis units, and hover templates so charts are
legible without relying on Streamlit's defaults.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from fireworks import config


def _style(fig: go.Figure, title: str, y_title: str, height: int = 340) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=config.INK)),
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color=config.INK),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        yaxis=dict(title=y_title, gridcolor=config.GRID, zeroline=False),
        xaxis=dict(gridcolor=config.GRID, zeroline=False),
    )
    return fig


def line(
    df: pd.DataFrame,
    columns: list[str],
    labels: list[str] | None = None,
    title: str = "",
    y_title: str = "",
    height: int = 340,
) -> go.Figure:
    """One or more daily line series against date."""
    labels = labels or columns
    fig = go.Figure()
    for i, col in enumerate(columns):
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
    height: int = 320,
) -> go.Figure:
    """Horizontal bar chart (long labels read better horizontally)."""
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
        title=dict(text=title, font=dict(size=15, color=config.INK)),
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color=config.INK),
        xaxis=dict(title=x_title, gridcolor=config.GRID, zeroline=False),
        yaxis=dict(autorange="reversed", gridcolor=config.GRID),
    )
    return fig
