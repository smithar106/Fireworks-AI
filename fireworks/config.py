"""Central configuration: paths, column names, types, and shared constants.

Keeping column names and schema metadata in one place means the data layer,
metrics layer, and views all agree on the dataset's shape.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_FILE = DATA_DIR / "northstar_flagship_30_day_metrics.csv"

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

DATE_COL = "date"
DEPLOYMENT_COL = "deployment"

# Columns that must be present and numeric (inferred at load time).
NUMERIC_COLUMNS: tuple[str, ...] = (
    "requests",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "spend_usd",
    "p50_latency_ms",
    "p95_latency_ms",
    "error_rate_pct",
    "availability_pct",
    "tier1_tickets",
    "automated_tier1_tickets",
    "automation_rate_pct",
    "avg_handle_time_min",
    "csat_score",
    "grounded_answer_rate_pct",
    "quality_eval_pass_rate_pct",
    "escalation_rate_pct",
)

REQUIRED_COLUMNS: tuple[str, ...] = (DATE_COL, DEPLOYMENT_COL, *NUMERIC_COLUMNS, "operational_note")

# Columns that represent a percentage in [0, 100].
PERCENTAGE_COLUMNS: tuple[str, ...] = (
    "error_rate_pct",
    "availability_pct",
    "automation_rate_pct",
    "grounded_answer_rate_pct",
    "quality_eval_pass_rate_pct",
    "escalation_rate_pct",
)

# Columns that must be non-negative integers.
INTEGER_COLUMNS: tuple[str, ...] = (
    "requests",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "tier1_tickets",
    "automated_tier1_tickets",
)

# Columns that must be non-negative floats.
NON_NEGATIVE_FLOAT_COLUMNS: tuple[str, ...] = (
    "spend_usd",
    "p50_latency_ms",
    "p95_latency_ms",
    "avg_handle_time_min",
)

# Optional free-text column (empty values are expected and allowed).
OPTIONAL_TEXT_COLUMNS: tuple[str, ...] = ("operational_note",)

# The dataset covers one continuous month. Encode the expectation so validation
# can assert it independently of hard-coded metric values.
EXPECTED_ROW_COUNT = 31
EXPECTED_DATE_RANGE = ("2026-08-01", "2026-08-31")

# ---------------------------------------------------------------------------
# Chart palette (consistent across both views)
# ---------------------------------------------------------------------------

INK = "#14161A"
MUTED = "#5C6470"
GRID = "#E7E5DF"
ACCENT = "#3457D5"  # primary blue
ACCENT_2 = "#0E9384"  # teal (secondary)
GOOD = "#0F9D58"
WARN = "#C77B16"
BAD = "#C0392B"

PALETTE = [ACCENT, ACCENT_2, "#6D4BC0", "#C77B16", "#0F9D58", "#8E3B2B"]
