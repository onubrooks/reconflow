"""Tests for configuration loading and validation."""

import pytest
import tempfile
from pathlib import Path

from reconflow.config import load_config, ReconFlowConfig


def test_load_minimal_config():
    """Test loading a minimal valid configuration."""
    config_yaml = """
version: "1"
pipeline_name: "test"
product:
  path: "data/product.csv"
cba:
  path: "data/cba.csv"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_yaml)
        f.flush()

        config = load_config(f.name)

        assert config.pipeline_name == "test"
        assert config.product.path == "data/product.csv"
        assert config.cba.path == "data/cba.csv"
        assert config.matching.strategy == "exact_reference"


def test_config_defaults():
    """Test that defaults are applied correctly."""
    config_yaml = """
product:
  path: "product.csv"
cba:
  path: "cba.csv"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_yaml)
        f.flush()

        config = load_config(f.name)

        assert config.version == "1"
        assert config.pipeline_name == "default"
        assert config.matching.amount_tolerance_abs == 0.01
        assert config.pricing.decimal_precision == 2


def test_missing_required_field():
    """Test that missing required fields raise errors."""
    config_yaml = """
pipeline_name: "test"
cba:
  path: "cba.csv"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_yaml)
        f.flush()

        with pytest.raises(Exception):  # ValidationError
            load_config(f.name)


def test_file_not_found():
    """Test that missing config file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.yaml")
