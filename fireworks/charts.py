"""Plotly chart builders with a clean, professional style (reference-dashboard
inspired: muted axes, light grid, colored lines, no redundant labels).
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from fireworks import config

_TICK_FONT = dict(size=11, color=config.MUTED)


def _style(fig: go.Figure, title: str, height: int, showlegend: bool) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=config.INK), x=0.01, xanchor="left"),
        height=height,
        margin=dict(l=8, r=8, t=40, b=30 if showlegend else 8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color=config.INK),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", bordercolor=config.BORDER, font=dict(color=config.INK, size=12)),
        showlegend=showlegend,
    )
    if showlegend:
        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="top", y=-0.12, x=0.5, xanchor="center",
                font=dict(size=11, color=config.MUTED),
            ),
        )
    fig.update_xaxes(
        showline=True, linecolor=config.BORDER, linewidth=1,
        showgrid=False, zeroline=False, tickfont=_TICK_FONT,
        tickformat="%b %d", nticks=7,
    )
    fig.update_yaxes(
        showgrid=True, gridcolor="#F0F0F3", gridwidth=1,
        zeroline=False, tickfont=_TICK_FONT,
    )
    return fig


def line(
    df: pd.DataFrame,
    columns: list[str],
    labels: list[str] | None = None,
    title: str = "",
    height: int = 280,
    colors: list[str] | None = None,
    digits: int = 1,
) -> go.Figure:
    """One or more daily line series against date (no redundant axis/legend text)."""
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
                line=dict(width=2.4, color=colors[i]),
                hovertemplate=f"{labels[i]}: %{{y:,.{digits}f}}<extra></extra>",
            )
        )
    return _style(fig, title, height, showlegend=len(columns) > 1)


def bars(
    categories: list[str],
    values: list[float],
    title: str = "",
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
        showlegend=False,
    )
    fig.update_xaxes(
        showline=True, linecolor=config.BORDER, linewidth=1, showgrid=False,
        zeroline=False, tickfont=_TICK_FONT,
    )
    fig.update_yaxes(autorange="reversed", showgrid=False, zeroline=False, tickfont=_TICK_FONT)
    return fig
