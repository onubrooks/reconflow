"""Matching strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pandas as pd

from reconflow.normalize import normalize_reference, standardize_decimal


@dataclass
class MatchResult:
    """Result of a matching operation."""

    matched: pd.DataFrame = field(default_factory=pd.DataFrame)
    missing_in_target: pd.DataFrame = field(default_factory=pd.DataFrame)
    missing_in_source: pd.DataFrame = field(default_factory=pd.DataFrame)
    amount_mismatches: pd.DataFrame = field(default_factory=pd.DataFrame)

    @property
    def total_source(self) -> int:
        return len(self.matched) + len(self.missing_in_target) + len(self.amount_mismatches)

    @property
    def pool_match_pct(self) -> float:
        if self.total_source == 0:
            return 0.0
        return (len(self.matched) / self.total_source) * 100


class MatchingStrategy(ABC):
    """Base class for matching strategies."""

    name: str = "base"

    @abstractmethod
    def match(
        self,
        source: pd.DataFrame,
        target: pd.DataFrame,
        source_ref_col: str,
        target_ref_col: str,
        source_amt_col: str,
        target_amt_col: str,
        tolerance: float = 0.01,
        normalize_refs: bool = True,
        decimal_precision: int = 2,
    ) -> MatchResult:
        """Execute matching logic."""
        raise NotImplementedError


class ExactReferenceStrategy(MatchingStrategy):
    """
    Exact reference matching strategy (1:1).

    Matches records where:
    1. Normalized references are identical
    2. Standardized amounts are within tolerance
    """

    name: str = "exact_reference"

    def match(
        self,
        source: pd.DataFrame,
        target: pd.DataFrame,
        source_ref_col: str,
        target_ref_col: str,
        source_amt_col: str,
        target_amt_col: str,
        tolerance: float = 0.01,
        normalize_refs: bool = True,
        decimal_precision: int = 2,
    ) -> MatchResult:
        """
        Match source to target using exact reference matching.

        Args:
            source: Source DataFrame (e.g., product transactions)
            target: Target DataFrame (e.g., CBA ledger)
            source_ref_col: Reference column name in source
            target_ref_col: Reference column name in target
            source_amt_col: Amount column name in source
            target_amt_col: Amount column name in target
            tolerance: Amount tolerance for matching
            normalize_refs: Whether to normalize references
            decimal_precision: Decimal places for amount standardization

        Returns:
            MatchResult with matched and unmatched records
        """
        src = source.copy()
        tgt = target.copy()

        if normalize_refs:
            src["_norm_ref"] = src[source_ref_col].apply(normalize_reference)
            tgt["_norm_ref"] = tgt[target_ref_col].apply(normalize_reference)
            merge_col_src = "_norm_ref"
            merge_col_tgt = "_norm_ref"
        else:
            merge_col_src = source_ref_col
            merge_col_tgt = target_ref_col

        src["_std_amt"] = src[source_amt_col].apply(
            lambda x: standardize_decimal(x, decimal_precision)
        )
        tgt["_std_amt"] = tgt[target_amt_col].apply(
            lambda x: standardize_decimal(x, decimal_precision)
        )

        merged = src.merge(
            tgt,
            left_on=merge_col_src,
            right_on=merge_col_tgt,
            how="outer",
            suffixes=("_source", "_target"),
            indicator=True,
        )

        merged["_amt_diff"] = abs(
            merged["_std_amt_source"].fillna(0) - merged["_std_amt_target"].fillna(0)
        )

        both_mask = merged["_merge"] == "both"
        left_only_mask = merged["_merge"] == "left_only"
        right_only_mask = merged["_merge"] == "right_only"

        amount_match_mask = merged["_amt_diff"] <= tolerance

        matched = merged[both_mask & amount_match_mask].copy()
        amount_mismatches = merged[both_mask & ~amount_match_mask].copy()
        missing_in_target = merged[left_only_mask].copy()
        missing_in_source = merged[right_only_mask].copy()

        return MatchResult(
            matched=matched,
            missing_in_target=missing_in_target,
            missing_in_source=missing_in_source,
            amount_mismatches=amount_mismatches,
        )
