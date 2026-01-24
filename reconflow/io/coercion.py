"""Type coercion utilities for data loading."""

from __future__ import annotations

import pandas as pd


def coerce_amount(series: pd.Series) -> pd.Series:
    """
    Coerce a series to numeric values.

    Invalid values become NaN rather than raising errors.

    Args:
        series: Series containing amount values (possibly strings)

    Returns:
        Series with numeric values
    """
    return pd.to_numeric(series, errors="coerce")


def coerce_date(
    series: pd.Series,
    utc: bool = True,
    format: str | None = None,
) -> pd.Series:
    """
    Coerce a series to datetime values.

    Invalid values become NaT rather than raising errors.

    Args:
        series: Series containing date values (possibly strings)
        utc: Whether to convert to UTC (default True)
        format: Date format string (optional)

    Returns:
        Series with datetime values
    """
    return pd.to_datetime(series, errors="coerce", utc=utc, format=format)
