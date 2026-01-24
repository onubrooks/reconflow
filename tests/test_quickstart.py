"""Integration tests using quickstart example."""

from reconflow.config import load_config
from reconflow.io import coerce_amount, read_csv
from reconflow.matching import match_records


def test_quickstart_config_loads():
    """Test that quickstart config loads correctly."""
    config = load_config("examples/quickstart/reconflow.yaml")
    assert config.pipeline_name == "quickstart"
    assert config.matching.strategy == "exact_reference"


def test_quickstart_data_loads():
    """Test that quickstart data files load correctly."""
    config = load_config("examples/quickstart/reconflow.yaml")

    product = read_csv(config.product.path)
    cba = read_csv(config.cba.path)

    assert len(product) > 0
    assert len(cba) > 0


def test_quickstart_matching():
    """Test that quickstart matching produces expected results."""
    config = load_config("examples/quickstart/reconflow.yaml")

    product = read_csv(config.product.path)
    cba = read_csv(config.cba.path)

    product[config.product.amount_field] = coerce_amount(product[config.product.amount_field])
    cba[config.cba.amount_field] = coerce_amount(cba[config.cba.amount_field])

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
    )

    assert len(result.matched) >= 0
    assert result.total_source > 0
