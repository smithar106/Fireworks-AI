"""Plotly chart builders with a clean, professional style (reference-dashboard
inspired: muted axes, light grid, colored lines, no chart chrome).
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from fireworks import config

_AXIS_FONT = dict(size=11, color=config.MUTED)
_TICK_FONT = dict(size=11, color=config.MUTED)


def _style(fig: go.Figure, title: str, y_title: str, height: int = 280) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=config.INK), x=0.01, xanchor="left"),
        height=height,
        margin=dict(l=8, r=8, t=40, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color=config.INK),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", bordercolor=config.BORDER, font=dict(color=config.INK, size=12)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=11, color=config.MUTED)),
        showlegend=True,
    )
    fig.update_xaxes(
        showline=True,
        linecolor=config.BORDER,
        linewidth=1,
        showgrid=False,
        zeroline=False,
        tickfont=_TICK_FONT,
        tickformat="%b %d",
        nticks=7,
        title_font=_AXIS_FONT,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#F0F0F3",
        gridwidth=1,
        zeroline=False,
        tickfont=_TICK_FONT,
        title_font=_AXIS_FONT,
        title_standoff=8,
    )
    if y_title:
        fig.update_yaxes(title_text=y_title)
    return fig


def line(
    df: pd.DataFrame,
    columns: list[str],
    labels: list[str] | None = None,
    title: str = "",
    y_title: str = "",
    height: int = 280,
    colors: list[str] | None = None,
) -> go.Figure:
    """One or more daily line series against date."""
    labels = labels or columns
    colors = colors or [config.PALETTE[i % len(config.PALETTE)] for i in range(len(columns))]
    fig = go.Figure()
    for i, col in enumerate(columns):
        fig.add_trace(
            go.Scatter(
                x=df[config.DATE_COL],
                y=df[col],
                mode="lines",
                name=labels[i],
                line=dict(width=2.4, color=colors[i], shape="spline", smoothing=0.6),
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
    height: int = 280,
) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=values,
            y=categories,
            orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            hovertemplate="%{y}: %{x:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=config.INK), x=0.01, xanchor="left"),
        height=height,
        margin=dict(l=8, r=8, t=40, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color=config.INK),
    )
    fig.update_xaxes(
        showline=True, linecolor=config.BORDER, linewidth=1, showgrid=False,
        zeroline=False, tickfont=_TICK_FONT, title_font=_AXIS_FONT,
    )
    fig.update_yaxes(
        autorange="reversed", showgrid=False, zeroline=False,
        tickfont=_TICK_FONT, title_font=_AXIS_FONT,
    )
    if x_title:
        fig.update_xaxes(title_text=x_title)
    return fig
