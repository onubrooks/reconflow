"""Command-line interface for ReconFlow."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from reconflow import __version__
from reconflow.config import load_config
from reconflow.io import coerce_amount, read_csv
from reconflow.matching import match_records
from reconflow.report import write_run_artifacts

app = typer.Typer(
    name="reconflow",
    help="Config-driven reconciliation framework for fintech",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def _print_summary(summary_path: Path) -> None:
    """Print a run summary in a formatted table."""
    data = json.loads(summary_path.read_text(encoding="utf-8"))

    table = Table(title=f"ReconFlow Run: {data['pipeline_name']} / {data['run_id']}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    for key, value in data["totals"].items():
        table.add_row(key, str(value))

    table.add_row("---", "---")

    for key, value in data["metrics"].items():
        table.add_row(key, f"{value}%")

    console.print(table)
    console.print(f"\n[bold]Artifacts:[/bold] {data['paths']['dir']}")


@app.command()
def version() -> None:
    """Show ReconFlow version."""
    console.print(f"ReconFlow v{__version__}")


@app.command()
def validate(
    config_path: str = typer.Argument(..., help="Path to reconflow.yaml"),
) -> None:
    """Validate a configuration file."""
    try:
        config = load_config(config_path)

        errors = []
        if not Path(config.product.path).exists():
            errors.append(f"Product file not found: {config.product.path}")
        if not Path(config.cba.path).exists():
            errors.append(f"CBA file not found: {config.cba.path}")

        if errors:
            for error in errors:
                console.print(f"[red]✗[/red] {error}")
            raise typer.Exit(1)

        console.print("[green]✓[/green] Configuration is valid")
        console.print(f"  Pipeline: {config.pipeline_name}")
        console.print(f"  Strategy: {config.matching.strategy}")

    except Exception as e:
        console.print(f"[red]✗[/red] Validation failed: {e}")
        raise typer.Exit(1) from e


@app.command()
def run(
    config_path: str = typer.Argument(..., help="Path to reconflow.yaml"),
) -> None:
    """Run a reconciliation pipeline."""
    try:
        config = load_config(config_path)
        console.print(f"[cyan]Running pipeline:[/cyan] {config.pipeline_name}")

        console.print("  Loading product data...")
        product = read_csv(config.product.path)
        console.print(f"    {len(product)} records")

        console.print("  Loading CBA data...")
        cba = read_csv(config.cba.path)
        console.print(f"    {len(cba)} records")

        product[config.product.amount_field] = coerce_amount(product[config.product.amount_field])
        cba[config.cba.amount_field] = coerce_amount(cba[config.cba.amount_field])

        console.print("  Matching records...")
        result = match_records(
            source=product,
            target=cba,
            strategy=config.matching.strategy,
            source_ref_col=config.product.reference_field,
            target_ref_col=config.cba.reference_field,
            source_amt_col=config.product.amount_field,
            target_amt_col=config.cba.amount_field,
            tolerance=config.matching.amount_tolerance_abs,
            normalize_refs=config.matching.normalize_reference,
            decimal_precision=config.pricing.decimal_precision,
        )

        console.print("  Writing results...")
        summary = write_run_artifacts(
            run_dir=config.output.run_dir,
            pipeline_name=config.pipeline_name,
            matched=result.matched,
            missing_in_target=result.missing_in_target,
            missing_in_source=result.missing_in_source,
            amount_mismatches=result.amount_mismatches,
        )

        console.print()
        _print_summary(Path(summary.paths["dir"]) / "summary.json")

    except Exception as e:
        console.print(f"[red]✗[/red] Run failed: {e}")
        raise typer.Exit(1) from e


@app.command()
def explain(
    latest: bool = typer.Option(
        True,
        "--latest/--no-latest",
        help="Explain the latest run",
    ),
    run_id: str | None = typer.Option(None, "--run-id", help="Explain a specific run"),
    pipeline_name: str = typer.Option("quickstart", help="Pipeline name"),
    run_dir: str = typer.Option(".reconflow/runs", help="Runs directory"),
) -> None:
    """Explain reconciliation results."""
    try:
        base = Path(run_dir) / pipeline_name

        if run_id is None:
            if not latest:
                console.print("[red]✗[/red] Provide --run-id or use --latest")
                raise typer.Exit(1)

            latest_file = base / "latest.txt"
            if not latest_file.exists():
                console.print("[red]✗[/red] No runs found. Run: reconflow run <config>")
                raise typer.Exit(1)

            run_id = latest_file.read_text(encoding="utf-8").strip()

        summary_path = base / run_id / "summary.json"
        if not summary_path.exists():
            console.print(f"[red]✗[/red] Run not found: {run_id}")
            raise typer.Exit(1)

        data = json.loads(summary_path.read_text(encoding="utf-8"))

        console.print("\n[bold]What happened?[/bold]")
        console.print("• Product records matched against CBA records by normalized reference")
        console.print("• Amounts matched if difference ≤ tolerance")

        console.print("\n[bold]Results breakdown:[/bold]")
        console.print(f"• [green]Matched:[/green] {data['totals']['matched']} records")
        console.print(
            f"• [yellow]Missing in CBA:[/yellow] {data['totals']['missing_in_target']} records"
        )
        console.print(
            f"• [yellow]Missing in Product:[/yellow] {data['totals']['missing_in_source']} records"
        )
        console.print(
            f"• [red]Amount mismatches:[/red] {data['totals']['amount_mismatches']} records"
        )

        console.print("\n[bold]Where to look next:[/bold]")
        console.print(f"• Matched: {data['paths']['matched']}")
        console.print(f"• Missing in CBA: {data['paths']['missing_in_target']}")
        console.print(f"• Missing in Product: {data['paths']['missing_in_source']}")
        console.print(f"• Amount mismatches: {data['paths']['amount_mismatches']}")

        console.print()
        _print_summary(summary_path)

    except Exception as e:
        console.print(f"[red]✗[/red] Explain failed: {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
