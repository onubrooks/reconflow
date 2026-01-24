"""Decimal standardization utilities.

This module contains the MOST CRITICAL function in ReconFlow.
Decimal precision mismatches cause 80% of reconciliation failures.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def standardize_decimal(
    value: str | float | int | Decimal | None,
    precision: int = 2,
) -> float | None:
    """
    Standardize a numeric value to consistent decimal precision.

    This function solves the #1 cause of reconciliation mismatches:
    - Product computes: 10.007 → displays as 10.01
    - CBA records: 10.01
    - Naive comparison: 10.007 != 10.01 → MISMATCH (wrong!)
    - With standardization: 10.01 == 10.01 → MATCH (correct!)

    Args:
        value: The numeric value to standardize. Can be string, float, int, or Decimal.
        precision: Number of decimal places (default 2 for currency).

    Returns:
        Standardized float value, or None if input is None.

    Examples:
        >>> standardize_decimal(10.007, 2)
        10.01
        >>> standardize_decimal(10.994, 2)
        10.99
        >>> standardize_decimal("10.005", 2)
        10.01
        >>> standardize_decimal(None)
        None
    """
    if value is None:
        return None

    d = Decimal(str(value))

    quantize_str = "0." + "0" * precision

    result = d.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)

    return float(result)


def amounts_match(
    amount1: str | float | int | Decimal | None,
    amount2: str | float | int | Decimal | None,
    precision: int = 2,
    tolerance: float = 0.0,
) -> bool:
    """
    Check if two amounts match within tolerance after standardization.

    Args:
        amount1: First amount to compare
        amount2: Second amount to compare
        precision: Decimal precision for standardization
        tolerance: Absolute tolerance for matching (default 0 = exact match)

    Returns:
        True if amounts match within tolerance, False otherwise
    """
    std1 = standardize_decimal(amount1, precision)
    std2 = standardize_decimal(amount2, precision)

    if std1 is None or std2 is None:
        return std1 is None and std2 is None

    return abs(std1 - std2) <= tolerance
