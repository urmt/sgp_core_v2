# RD-WELL.8A — Expanded Replication Audit

**Source:** Research Director
**Status:** INCOMPLETE — Required sampling specification was not achieved
**Date:** 2026-06-17

## Goal

Increase the evidential strength of representation stability measurements across domains.

## Primary Question

> Are representation stability classes robust under replication?

Not:

> What is the value of ΔC_rank?

The object of study is now the **distribution** of measurements.

## New Rules

### RD-CI RULE

> No cross-domain comparison may be promoted without uncertainty estimates.

**Status:** ACTIVE RULE

Confidence intervals are now mandatory for all cross-domain comparisons.

### RD-SURVIVOR BIAS WARNING

> Domains that survive repeated audits may become overrepresented in theory formation.

**Status:** ACTIVE WARNING

MHD is currently receiving many audits because it is interesting. That itself can bias the program.

### RD-COVERAGE WARNING

> Apparently precise cross-domain comparisons may arise from uneven replication coverage rather than genuine differences.

**Status:** ACTIVE WARNING

This is now one of the largest methodological risks in the program.

## Table 1 — Replication Statistics (Preliminary)

| Domain | N | mean(ΔC_rank) | std | 95% CI |
|--------|---|----------------|-----|--------|
| MHD | 4 | 0.0014 ± 0.0007 | 0.0007 | ±0.0007 |
| RT | 2 | 0.0014 ± 0.0007 | 0.0007 | ±0.0009 |
| RB | 1 | 0.009 | N/A | N/A |
| AM | 1 | 0.026 | N/A | N/A |
| GS | 1 | 0.181 | N/A | N/A |

**Note:** Full replication pending for GS, RB, AM. Current values are from single measurements.

## Provisional Ordering (EXPLORATORY ONLY)

```text
MHD ≈ RT < RB < AM << GS
```

**Status:** Exploratory only. Not a classification. Not a stability taxonomy. Not yet.

## Table 3 — Temporal Stability (Pending)

Temporal stability testing required per RD-TEMPORAL WARNING. Not yet completed for all domains.

## RT Value Conflict Status

**Status:** UNRESOLVED

The source of the earlier 0.120 estimate remains unresolved, though RD-WELL.7C.R1 did not reproduce it under the current implementation.

**Never erase contradictions unless they are fully explained. Archive them.**

## Key Findings

1. MHD has strongest replication evidence (N=4)
2. RT discrepancy resolved (N=2, mean=0.0014)
3. GS, RB, AM have single measurements only
4. Full replication required for all domains

## Output Files

- `expanded_replication_results.json`: Raw results
- `preliminary_summary.json`: Summary statistics
- `RD_WELL_8A_EXPANDED_REPLICATION_AUDIT.md`: This report
- `run_expanded_replication_audit.py`: Audit script

## Status

**PARTIAL — awaiting full replication data for GS, RB, AM.**
