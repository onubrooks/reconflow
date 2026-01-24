"""Tests for matching engine."""

import pandas as pd

from reconflow.matching import match_records


def test_exact_match():
    """Test exact matching with identical records."""
    source = pd.DataFrame({
        "reference": ["REF001", "REF002", "REF003"],
        "amount": ["100.00", "200.00", "300.00"],
    })
    target = pd.DataFrame({
        "reference": ["REF001", "REF002", "REF003"],
        "amount": ["100.00", "200.00", "300.00"],
    })

    result = match_records(source, target)

    assert len(result.matched) == 3
    assert len(result.missing_in_target) == 0
    assert len(result.missing_in_source) == 0
    assert len(result.amount_mismatches) == 0


def test_missing_in_target():
    """Test detection of records missing in target."""
    source = pd.DataFrame({
        "reference": ["REF001", "REF002"],
        "amount": ["100.00", "200.00"],
    })
    target = pd.DataFrame({
        "reference": ["REF001"],
        "amount": ["100.00"],
    })

    result = match_records(source, target)

    assert len(result.matched) == 1
    assert len(result.missing_in_target) == 1


def test_amount_mismatch():
    """Test detection of amount mismatches."""
    source = pd.DataFrame({
        "reference": ["REF001"],
        "amount": ["100.00"],
    })
    target = pd.DataFrame({
        "reference": ["REF001"],
        "amount": ["100.05"],
    })

    result = match_records(source, target, tolerance=0.01)

    assert len(result.matched) == 0
    assert len(result.amount_mismatches) == 1


def test_amount_within_tolerance():
    """Test amounts within tolerance are matched."""
    source = pd.DataFrame({
        "reference": ["REF001"],
        "amount": ["100.007"],
    })
    target = pd.DataFrame({
        "reference": ["REF001"],
        "amount": ["100.01"],
    })

    result = match_records(source, target, tolerance=0.01)

    assert len(result.matched) == 1
    assert len(result.amount_mismatches) == 0


def test_case_insensitive_reference():
    """Test that reference matching is case-insensitive."""
    source = pd.DataFrame({
        "reference": ["trf|abc|123"],
        "amount": ["100.00"],
    })
    target = pd.DataFrame({
        "reference": ["TRF|ABC|123"],
        "amount": ["100.00"],
    })

    result = match_records(source, target, normalize_refs=True)

    assert len(result.matched) == 1


def test_pool_match_percentage():
    """Test pool match percentage calculation."""
    source = pd.DataFrame({
        "reference": ["REF001", "REF002", "REF003", "REF004"],
        "amount": ["100.00", "200.00", "300.00", "400.00"],
    })
    target = pd.DataFrame({
        "reference": ["REF001", "REF002"],
        "amount": ["100.00", "200.00"],
    })

    result = match_records(source, target)

    assert result.pool_match_pct == 50.0
