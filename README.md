# ReconFlow

> **The open-source reconciliation & assurance framework for fintech.**

[![CI](https://github.com/YOUR_USERNAME/reconflow/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/reconflow/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

ReconFlow helps data and finance teams **reconcile, validate, and audit financial data** without rewriting the same pipelines over and over again.

## Why ReconFlow?

Every fintech eventually builds:
- Revenue assurance pipelines
- Expense reconciliation systems
- Settlement matching logic
- Audit evidence generation

And every fintech:
- Rewrites the same SQL patterns
- Copies the same DAG structures
- Debugs the same decimal precision bugs

**ReconFlow makes reconciliation infrastructure, not tribal knowledge.**

## Quick Start

```bash
# Install
pip install reconflow

# Initialize (interactive wizard)
reconflow init

# Validate configuration
reconflow validate reconflow.yaml

# Run reconciliation
reconflow run reconflow.yaml

# Explain results
reconflow explain --latest
```

## Features

- ⚡ **YAML-driven pipelines** - 50 lines of config replaces 500 lines of SQL
- 💸 **Pricing engine** - Percentage, flat, tiered strategies built-in
- 🔍 **Deterministic matching** - Exact reference, with tolerance support
- ✅ **Audit trail** - Every run produces explainable, verifiable evidence
- 🔓 **Open source** - Apache 2.0 license, no vendor lock-in

## Documentation

- [Quickstart Guide](examples/quickstart/README.md)
- [Configuration Reference](docs/configuration.md)
- [Contributing](CONTRIBUTING.md)

## Built From Real Production

ReconFlow is born from production systems at Moniepoint, Africa's leading fintech unicorn, processing millions of transactions daily.

## License

Apache 2.0 — Built by engineers who've lost sleep over reconciliation.
