"""Matching engine orchestrator."""

from __future__ import annotations

import pandas as pd

from reconflow.matching.strategies import (
    ExactReferenceStrategy,
    MatchingStrategy,
    MatchResult,
)

_STRATEGIES: dict[str, MatchingStrategy] = {
    "exact_reference": ExactReferenceStrategy(),
}


def get_strategy(name: str) -> MatchingStrategy:
    """Get a matching strategy by name."""
    if name not in _STRATEGIES:
        raise ValueError(f"Unknown matching strategy: {name}")
    return _STRATEGIES[name]


def match_records(
    source: pd.DataFrame,
    target: pd.DataFrame,
    strategy: str = "exact_reference",
    source_ref_col: str = "reference",
    target_ref_col: str = "reference",
    source_amt_col: str = "amount",
    target_amt_col: str = "amount",
    tolerance: float = 0.01,
    normalize_refs: bool = True,
    decimal_precision: int = 2,
) -> MatchResult:
    """
    Match records between source and target DataFrames.

    Args:
        source: Source DataFrame
        target: Target DataFrame
        strategy: Matching strategy name
        source_ref_col: Reference column in source
        target_ref_col: Reference column in target
        source_amt_col: Amount column in source
        target_amt_col: Amount column in target
        tolerance: Amount tolerance
        normalize_refs: Whether to normalize references
        decimal_precision: Decimal precision

    Returns:
        MatchResult with categorized records
    """
    matcher = get_strategy(strategy)

    return matcher.match(
        source=source,
        target=target,
        source_ref_col=source_ref_col,
        target_ref_col=target_ref_col,
        source_amt_col=source_amt_col,
        target_amt_col=target_amt_col,
        tolerance=tolerance,
        normalize_refs=normalize_refs,
        decimal_precision=decimal_precision,
    )
