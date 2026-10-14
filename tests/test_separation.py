"""Audience-separation tests.

Verifies that the customer-facing view never contains internal-only labels or
fields (competitive, commercial, margin, staffing, etc.), and that the internal
view does contain them (sanity check that the check is not vacuous).
"""

from __future__ import annotations

import pytest

from fireworks import assumptions
from fireworks.data import load_dataframe
from fireworks.metrics import compute_summary
from fireworks.scoring import compute_health_score
from fireworks.views import customer, flatten, internal


@pytest.fixture(scope="module")
def df():
    return load_dataframe()


@pytest.fixture(scope="module")
def summary(df):
    return compute_summary(df)


@pytest.fixture(scope="module")
def score(df):
    return compute_health_score(df)


def _lower(texts):
    return "\n".join(texts).lower()


def test_customer_view_has_no_internal_terms(summary):
    texts = flatten(customer.content(summary))
    lower = _lower(texts)
    for term in assumptions.INTERNAL_ONLY_TERMS:
        assert term not in lower, f"customer view leaks internal term: {term!r}"


def test_customer_view_no_commercial_language(summary):
    texts = flatten(customer.content(summary))
    lower = _lower(texts)
    for bad in ("margin", "unit economics", "competitive", "staffing", "churn", "renewal"):
        assert bad not in lower


def test_internal_view_contains_internal_terms(summary, score):
    texts = flatten(internal.content(summary, score))
    lower = _lower(texts)
    # Sanity check: the internal view is expected to use internal vocabulary.
    assert "competitive risk" in lower
    assert "unit economics" in lower


def test_customer_content_nonempty(summary):
    texts = flatten(customer.content(summary))
    assert len(texts) > 0
