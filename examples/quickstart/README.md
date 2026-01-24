# ReconFlow Quickstart

This example demonstrates basic reconciliation between product transactions and CBA ledger entries.

## Files

- `reconflow.yaml` - Pipeline configuration
- `data/broken_product.csv` - Product transactions with intentional issues
- `data/broken_cba.csv` - CBA ledger with intentional mismatches

## Run the Example

```bash
# From repository root
cd reconflow

# Validate configuration
reconflow validate examples/quickstart/reconflow.yaml

# Run reconciliation
reconflow run examples/quickstart/reconflow.yaml

# Explain results
reconflow explain --latest --pipeline-name quickstart
```

## Expected Results

The broken data files contain intentional issues:

- **Decimal precision**: `1000.007` vs `1000.01`
- **Case differences**: `trf|abc` vs `TRF|ABC`
- **Missing records**: Records in one file but not the other
- **Amount mismatches**: Same reference, different amounts

ReconFlow should:

1. Match records after normalizing references and decimals
2. Identify records missing in each source
3. Flag amount mismatches exceeding tolerance
