"""Scoring tests — piecewise interpolation, weights, and framework shape."""

from __future__ import annotations

import math

import pytest

from fireworks import assumptions
from fireworks.data import load_dataframe
from fireworks.scoring import compute_health_score, piecewise_score


def test_piecewise_clamps_low():
    assert piecewise_score(0, [(10, 50), (20, 100)]) == 50.0


def test_piecewise_clamps_high():
    assert piecewise_score(30, [(10, 50), (20, 100)]) == 100.0


def test_piecewise_interpolates():
    # midpoint of (0,0)->(100,100) is 50
    assert math.isclose(piecewise_score(50, [(0, 0), (100, 100)]), 50.0, abs_tol=1e-6)


def test_piecewise_nonlinear_thresholds():
    # 67.5 sits halfway between the (65, 75) and (70, 90) knots -> 82.5.
    assert math.isclose(piecewise_score(67.5, [(50, 0), (60, 55), (65, 75), (70, 90), (80, 100)]), 82.5, abs_tol=1e-6)


def test_weights_sum_to_one():
    total = sum(d["weight"] for d in assumptions.SCORING_DIMENSIONS)
    assert math.isclose(total, 1.0, abs_tol=1e-9)


def test_score_in_range():
    df = load_dataframe()
    score = compute_health_score(df)
    assert 0 <= score["overall_score"] <= 100


def test_score_dimensions_present():
    df = load_dataframe()
    score = compute_health_score(df)
    keys = {d["key"] for d in score["dimensions"]}
    assert "automation" in keys
    assert "csat" in keys
    # every scored dimension has a finite sub-score
    for d in score["dimensions"]:
        assert math.isfinite(d["sub_score"])


def test_unscored_dimensions_listed():
    df = load_dataframe()
    score = compute_health_score(df)
    assert len(score["unscored"]) > 0


def test_score_respects_filter():
    df = load_dataframe()
    full = compute_health_score(df)
    sub = compute_health_score(df.iloc[-10:])
    assert math.isfinite(full["overall_score"])
    assert math.isfinite(sub["overall_score"])
