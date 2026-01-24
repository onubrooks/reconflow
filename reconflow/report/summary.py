"""Run summary generation."""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


@dataclass
class RunSummary:
    """Summary of a reconciliation run."""

    run_id: str
    pipeline_name: str
    executed_at: str
    totals: dict[str, int]
    metrics: dict[str, float]
    paths: dict[str, str]


def _utc_now_id() -> str:
    """Generate a UTC timestamp-based run ID."""
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def write_run_artifacts(
    run_dir: str,
    pipeline_name: str,
    matched: pd.DataFrame,
    missing_in_target: pd.DataFrame,
    missing_in_source: pd.DataFrame,
    amount_mismatches: pd.DataFrame,
) -> RunSummary:
    """
    Write run artifacts to disk.

    Args:
        run_dir: Base directory for runs
        pipeline_name: Name of the pipeline
        matched: Matched records DataFrame
        missing_in_target: Records missing in target
        missing_in_source: Records missing in source
        amount_mismatches: Records with amount mismatches

    Returns:
        RunSummary with paths and metrics
    """
    run_id = _utc_now_id()
    out_dir = Path(run_dir) / pipeline_name / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    matched.to_csv(out_dir / "matched.csv", index=False)
    missing_in_target.to_csv(out_dir / "missing_in_target.csv", index=False)
    missing_in_source.to_csv(out_dir / "missing_in_source.csv", index=False)
    amount_mismatches.to_csv(out_dir / "amount_mismatches.csv", index=False)

    total_source = len(matched) + len(missing_in_target) + len(amount_mismatches)
    pool_match_pct = (len(matched) / total_source * 100) if total_source > 0 else 0.0

    totals = {
        "matched": len(matched),
        "missing_in_target": len(missing_in_target),
        "missing_in_source": len(missing_in_source),
        "amount_mismatches": len(amount_mismatches),
        "total_source": total_source,
    }

    metrics = {
        "pool_match_pct": round(pool_match_pct, 2),
    }

    paths = {
        "dir": str(out_dir),
        "matched": str(out_dir / "matched.csv"),
        "missing_in_target": str(out_dir / "missing_in_target.csv"),
        "missing_in_source": str(out_dir / "missing_in_source.csv"),
        "amount_mismatches": str(out_dir / "amount_mismatches.csv"),
    }

    summary = RunSummary(
        run_id=run_id,
        pipeline_name=pipeline_name,
        executed_at=dt.datetime.now(dt.UTC).isoformat(),
        totals=totals,
        metrics=metrics,
        paths=paths,
    )

    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(asdict(summary), f, indent=2)

    latest_file = Path(run_dir) / pipeline_name / "latest.txt"
    latest_file.parent.mkdir(parents=True, exist_ok=True)
    latest_file.write_text(run_id, encoding="utf-8")

    return summary
