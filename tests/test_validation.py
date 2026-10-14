"""Data validation tests — schema, types, ranges, and consistency."""

from __future__ import annotations

import pandas as pd
import pytest

from fireworks import config
from fireworks.data import load_dataframe, validate_dataframe


@pytest.fixture(scope="module")
def df():
    return load_dataframe()


def test_real_data_validates(df):
    report = validate_dataframe(df)
    assert report["ok"], report["errors"]


def test_missing_column_fails(df):
    bad = df.drop(columns=["spend_usd"])
    report = validate_dataframe(bad)
    assert not report["ok"]
    assert any("spend_usd" in e for e in report["errors"])


def test_duplicate_dates_fail(df):
    bad = df.copy()
    bad.loc[bad.index[1], "date"] = bad.loc[bad.index[0], "date"]
    report = validate_dataframe(bad)
    assert not report["ok"]


def test_percentage_out_of_range_fails(df):
    bad = df.copy()
    bad.loc[bad.index[0], "automation_rate_pct"] = 150.0
    report = validate_dataframe(bad)
    assert not report["ok"]
    assert any("automation_rate_pct" in e for e in report["errors"])


def test_negative_value_fails(df):
    bad = df.copy()
    bad.loc[bad.index[0], "requests"] = -1
    report = validate_dataframe(bad)
    assert not report["ok"]


def test_automated_greater_than_tier1_fails(df):
    bad = df.copy()
    bad.loc[bad.index[0], "automated_tier1_tickets"] = bad.loc[bad.index[0], "tier1_tickets"] + 10
    report = validate_dataframe(bad)
    assert not report["ok"]
    assert any("automated_tier1_tickets" in e for e in report["errors"])


def test_row_count_asserted(df):
    bad = df.iloc[:30]
    report = validate_dataframe(bad)
    assert not report["ok"]
    assert any("31" in e for e in report["errors"])


def test_missing_numeric_value_fails(df):
    bad = df.copy()
    bad.loc[bad.index[5], "csat_score"] = float("nan")
    report = validate_dataframe(bad)
    assert not report["ok"]
    assert any("csat_score" in e for e in report["errors"])
