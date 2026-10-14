"""Metric tests — recompute the expected reconciliation independently."""

from __future__ import annotations

import math

import pytest

from fireworks import metrics
from fireworks.data import load_dataframe


@pytest.fixture(scope="module")
def df():
    return load_dataframe()


def test_reconciliation_totals(df):
    s = metrics.compute_summary(df)
    assert s["total_requests"] == 789_563
    assert math.isclose(s["total_spend"], 1213.12, abs_tol=0.01)
    assert s["total_tier1"] == 143_430
    assert s["total_automated_tier1"] == 97_488


def test_total_tokens(df):
    s = metrics.compute_summary(df)
    assert s["total_tokens"] == 1_086_535_740


def test_weighted_automation(df):
    # Weighted = sum(automated) / sum(tier1), NOT mean of daily rates.
    assert math.isclose(metrics.weighted_automation_pct(df), 67.97, abs_tol=0.01)


def test_weighted_automation_equals_ratio(df):
    assert math.isclose(
        metrics.weighted_automation_pct(df),
        df["automated_tier1_tickets"].sum() / df["tier1_tickets"].sum() * 100,
    )


def test_unweighted_is_simple_mean(df):
    # The unweighted daily average is exactly the mean of the daily rate column.
    u = metrics.unweighted_daily_average(df, "automation_rate_pct")
    assert math.isclose(u, df["automation_rate_pct"].mean())


def test_weighted_is_not_the_simple_mean(df):
    # Weighted (sum/sum) is a different formula from the naive daily mean; in this
    # dataset they are close but not identical.
    w = metrics.weighted_automation_pct(df)
    assert not math.isclose(w, df["automation_rate_pct"].mean(), abs_tol=1e-9)


def test_spend_per_million_tokens(df):
    assert math.isclose(
        metrics.spend_per_million_tokens(df),
        1213.12 / (1_086_535_740 / 1e6),
        rel_tol=1e-6,
    )


def test_filter_recalculates(df):
    sub = metrics.filter_by_date(df, "2026-08-01", "2026-08-15")
    s = metrics.compute_summary(sub)
    assert s["days"] == 15
    # Weighted automation is recomputed over the window, not the full month.
    assert math.isclose(
        s["weighted_automation_pct"],
        sub["automated_tier1_tickets"].sum() / sub["tier1_tickets"].sum() * 100,
    )
    assert s["total_requests"] == int(sub["requests"].sum())
