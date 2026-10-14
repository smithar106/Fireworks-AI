"""Data loading and validation.

Loading is deterministic and cached; validation is a pure function that returns
a structured report so both the Streamlit app and the test suite can exercise
the exact same code path.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import pandas as pd

from fireworks import config


@lru_cache(maxsize=1)
def load_dataframe(path: str | None = None) -> pd.DataFrame:
    """Load the metrics CSV and normalize types.

    Returns a DataFrame with ``date`` as a ``datetime64`` column and all metric
    columns coerced to numeric. Cached so repeated reruns/tests reuse the parse.
    """
    path = path or str(config.DATA_FILE)
    df = pd.read_csv(path, parse_dates=[config.DATE_COL])

    # Coerce every expected numeric column; invalid values become NaN and are
    # surfaced by validate_dataframe rather than silently failing later.
    for col in config.NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def validate_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Validate schema, types, ranges, and internal consistency.

    Returns a dict with ``ok`` (bool), ``errors`` (list[str]), ``warnings``
    (list[str]), and a short ``summary`` string.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # --- Schema ----------------------------------------------------------
    missing_cols = [c for c in config.REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")

    if errors:
        return _report(errors, warnings)

    # --- Row count -------------------------------------------------------
    if len(df) != config.EXPECTED_ROW_COUNT:
        errors.append(
            f"Expected {config.EXPECTED_ROW_COUNT} rows, found {len(df)}."
        )

    # --- Dates -----------------------------------------------------------
    if df[config.DATE_COL].isna().any():
        errors.append("`date` contains missing values.")
    elif not df[config.DATE_COL].is_unique:
        errors.append("`date` contains duplicate values.")
    else:
        dates = df[config.DATE_COL].sort_values()
        expected = pd.date_range(config.EXPECTED_DATE_RANGE[0], config.EXPECTED_DATE_RANGE[1], freq="D")
        if not dates.reset_index(drop=True).equals(pd.Series(expected)):
            errors.append("`date` is not a contiguous daily series for 2026-08-01..2026-08-31.")

    # --- Missing values in required numeric columns ----------------------
    for col in config.NUMERIC_COLUMNS:
        if df[col].isna().any():
            errors.append(f"`{col}` contains missing values.")

    # --- Negative values -------------------------------------------------
    for col in [*config.INTEGER_COLUMNS, *config.NON_NEGATIVE_FLOAT_COLUMNS]:
        if (df[col] < 0).any():
            errors.append(f"`{col}` contains negative values.")

    # --- Integer columns are integral ------------------------------------
    for col in config.INTEGER_COLUMNS:
        vals = df[col].dropna()
        if not (vals == vals.round()).all():
            errors.append(f"`{col}` contains non-integer values.")

    # --- Percentage ranges -----------------------------------------------
    for col in config.PERCENTAGE_COLUMNS:
        if ((df[col] < 0) | (df[col] > 100)).any():
            errors.append(f"`{col}` contains values outside [0, 100].")

    # --- Cross-field consistency -----------------------------------------
    if not (df["automated_tier1_tickets"] <= df["tier1_tickets"]).all():
        errors.append("Some rows have automated_tier1_tickets > tier1_tickets.")

    # automation_rate_pct should equal automated / tier1 * 100 within tolerance.
    calc_rate = df["automated_tier1_tickets"] / df["tier1_tickets"] * 100
    if (calc_rate - df["automation_rate_pct"]).abs().max() > 0.5:
        warnings.append(
            "automation_rate_pct differs from automated_tier1_tickets / tier1_tickets by >0.5pp on some rows."
        )

    # total_tokens should equal input + output.
    calc_total = df["input_tokens"] + df["output_tokens"]
    if (calc_total - df["total_tokens"]).abs().max() > 1:
        warnings.append("total_tokens differs from input_tokens + output_tokens on some rows.")

    # --- Optional text ---------------------------------------------------
    if df["operational_note"].isna().all():
        warnings.append("`operational_note` is entirely empty (no operational events recorded).")

    return _report(errors, warnings)


def _report(errors: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "summary": (
            f"Validation {'passed' if not errors else 'FAILED'}: "
            f"{len(errors)} error(s), {len(warnings)} warning(s)."
        ),
    }


def operational_events(df: pd.DataFrame) -> list[dict[str, str]]:
    """Extract documented operational events from the `operational_note` column."""
    events: list[dict[str, str]] = []
    notes = df[df["operational_note"].notna()]
    for _, row in notes.iterrows():
        events.append(
            {
                "date": row[config.DATE_COL].date().isoformat(),
                "note": str(row["operational_note"]).strip(),
            }
        )
    return events
