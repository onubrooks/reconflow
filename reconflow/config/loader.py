"""Configuration loading and validation."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

from reconflow.config.models import ReconFlowConfig


def _interpolate_env_vars(data: Any) -> Any:
    """Recursively interpolate ${VAR} patterns with environment variables."""
    if isinstance(data, str):
        pattern = re.compile(r"\$\{([^}]+)\}")

        def replacer(match: re.Match) -> str:
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))

        return pattern.sub(replacer, data)
    if isinstance(data, dict):
        return {k: _interpolate_env_vars(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_interpolate_env_vars(item) for item in data]
    return data


def load_config(path: str | Path) -> ReconFlowConfig:
    """
    Load and validate a ReconFlow configuration file.

    Args:
        path: Path to the YAML configuration file

    Returns:
        Validated ReconFlowConfig object

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValidationError: If config is invalid
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)

    if raw_data is None:
        raw_data = {}

    data = _interpolate_env_vars(raw_data)

    return ReconFlowConfig.model_validate(data)
