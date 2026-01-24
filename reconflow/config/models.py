"""Pydantic models for ReconFlow configuration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CSVSource(BaseModel):
    """Configuration for a CSV data source."""

    path: str = Field(..., description="Path to CSV file")
    date_field: str = Field(default="date", description="Column name for date")
    reference_field: str = Field(default="reference", description="Column name for reference")
    amount_field: str = Field(default="amount", description="Column name for amount")


class PricingConfig(BaseModel):
    """Configuration for pricing calculations."""

    strategy: Literal["percentage", "flat", "tiered"] = Field(
        default="percentage",
        description="Pricing strategy to use",
    )
    rate: float = Field(default=0.0, description="Rate for percentage pricing")
    flat_fee: float = Field(default=0.0, description="Flat fee amount")
    cap: float | None = Field(default=None, description="Maximum fee cap")
    decimal_precision: int = Field(default=2, description="Decimal places for amounts")

    @field_validator("rate")
    @classmethod
    def rate_must_be_valid(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("Rate must be between 0 and 1")
        return v


class MatchingConfig(BaseModel):
    """Configuration for matching logic."""

    strategy: Literal["exact_reference", "group_sum"] = Field(
        default="exact_reference",
        description="Matching strategy to use",
    )
    amount_tolerance_abs: float = Field(
        default=0.01,
        description="Absolute tolerance for amount matching",
    )
    normalize_reference: bool = Field(
        default=True,
        description="Whether to normalize references before matching",
    )


class QualityConfig(BaseModel):
    """Configuration for data quality checks."""

    min_record_count: int = Field(default=0, description="Minimum expected records")
    max_duplicate_pct: float = Field(default=0.01, description="Maximum duplicate percentage")
    required_fields: list[str] = Field(
        default_factory=lambda: ["date", "reference", "amount"],
        description="Fields that must be present",
    )


class AssuranceControl(BaseModel):
    """Definition of an assurance control."""

    id: str = Field(..., description="Unique control identifier")
    name: str = Field(..., description="Human-readable control name")
    rule: str = Field(..., description="Control evaluation rule")
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = Field(default="HIGH")


class AssuranceConfig(BaseModel):
    """Configuration for assurance controls."""

    controls: list[AssuranceControl] = Field(default_factory=list)


class OutputConfig(BaseModel):
    """Configuration for output settings."""

    run_dir: str = Field(default=".reconflow/runs", description="Directory for run outputs")
    format: Literal["csv", "json"] = Field(default="csv", description="Output format")


class ReconFlowConfig(BaseModel):
    """Root configuration for a ReconFlow pipeline."""

    version: str = Field(default="1", description="Config schema version")
    pipeline_name: str = Field(default="default", description="Pipeline name")

    product: CSVSource = Field(..., description="Product data source")
    cba: CSVSource = Field(..., description="CBA/ledger data source")

    pricing: PricingConfig = Field(default_factory=PricingConfig)
    matching: MatchingConfig = Field(default_factory=MatchingConfig)
    quality: QualityConfig = Field(default_factory=QualityConfig)
    assurance: AssuranceConfig = Field(default_factory=AssuranceConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
