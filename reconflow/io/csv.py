"""CSV reading and writing utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_csv(
    path: str | Path,
    dtype: dict | None = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Read a CSV file into a DataFrame.

    By default, reads all columns as strings to preserve data integrity
    (e.g., leading zeros in references).

    Args:
        path: Path to the CSV file
        dtype: Column data types (default: all strings)
        **kwargs: Additional arguments passed to pd.read_csv

    Returns:
        DataFrame with CSV contents
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    if dtype is None:
        dtype = str

    return pd.read_csv(path, dtype=dtype, **kwargs)


def write_csv(
    df: pd.DataFrame,
    path: str | Path,
    index: bool = False,
    **kwargs,
) -> None:
    """
    Write a DataFrame to a CSV file.

    Args:
        df: DataFrame to write
        path: Output path
        index: Whether to write row index (default False)
        **kwargs: Additional arguments passed to df.to_csv
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index, **kwargs)
