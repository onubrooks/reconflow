"""Reference normalization utilities."""

from __future__ import annotations

import re

_TRF_PATTERN = re.compile(r"\b(TRF\|[^\s|]+(?:\|[^\s|]+)*)\b", re.IGNORECASE)

_GENERIC_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[|/_-][A-Za-z0-9]+)*")


def normalize_reference(ref: str | None, extract_trf: bool = True) -> str:
    """
    Normalize a transaction reference for consistent matching.

    Handles common inconsistencies between systems:
    - Case differences: "TRF|ABC" vs "trf|abc"
    - Whitespace: "TRF | ABC" vs "TRF|ABC"
    - Embedded references: "Payment: TRF|ABC|123" → "TRF|ABC|123"

    Args:
        ref: Raw reference string from source system
        extract_trf: Whether to extract TRF patterns from longer strings

    Returns:
        Normalized uppercase reference, empty string if None

    Examples:
        >>> normalize_reference("TRF|MONIEPOINT|123456|NGN")
        'TRF|MONIEPOINT|123456|NGN'
        >>> normalize_reference("  trf|abc|123  ")
        'TRF|ABC|123'
        >>> normalize_reference("Payment ref: TRF|ABC|123 confirmed")
        'TRF|ABC|123'
        >>> normalize_reference(None)
        ''
    """
    if ref is None:
        return ""

    ref = str(ref).strip()

    if not ref:
        return ""

    if extract_trf:
        match = _TRF_PATTERN.search(ref)
        if match:
            ref = match.group(1)

    ref = ref.upper()
    ref = re.sub(r"\s+", " ", ref)

    return ref


def extract_reference_parts(ref: str) -> list[str]:
    """
    Extract parts from a pipe-separated reference.

    Args:
        ref: Reference string (normalized or raw)

    Returns:
        List of reference parts

    Examples:
        >>> extract_reference_parts("TRF|MONIEPOINT|123456|NGN")
        ['TRF', 'MONIEPOINT', '123456', 'NGN']
    """
    normalized = normalize_reference(ref)
    if not normalized:
        return []
    return [part.strip() for part in normalized.split("|") if part.strip()]
