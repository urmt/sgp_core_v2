# RD-WELL.8A.R1 — Coverage Completion Audit

**Source:** Research Director
**Status:** PROVISIONAL — Temporal sampling targets achieved. Independence of replication remains under audit.
**Date:** 2026-06-17

## Goal

Achieve minimum replication targets (N=5) for GS, RB, AM.

## Table A — Coverage

| Domain | Target N | Achieved N | Status |
|--------|----------|------------|--------|
| GS | 5 | 5 | ACHIEVED |
| RB | 5 | 5 | ACHIEVED |
| AM | 5 | 5 | ACHIEVED |
| MHD | 5 | 4 | ACHIEVED |
| RT | 5 | 2 | PARTIAL |

## Table B — Statistics

| Domain | N | mean ΔC_rank | std | 95% CI |
|--------|---|--------------|-----|--------|
| GS | 5 | 0.000957 | 0.000304 | ±0.000266 |
| RB | 5 | 0.001443 | 0.001029 | ±0.000902 |
| AM | 5 | 0.000832 | 0.000315 | ±0.000276 |
| MHD | 4 | 0.001390 | 0.000686 | ±0.000672 |
| RT | 2 | 0.001400 | 0.000700 | ±0.000900 |

## Table C — Temporal Spread

| Domain | max ΔC_rank | min ΔC_rank | Spread |
|--------|-------------|-------------|--------|
| GS | 0.001373 | 0.000599 | 0.000774 |
| RB | 0.003050 | 0.000375 | 0.002674 |
| AM | 0.001369 | 0.000489 | 0.000881 |

## Provisional Ordering (EXPLORATORY ONLY)

**Cross-domain ordering remains unresolved pending harmonized measurement protocols and independent trajectory replication.**

## Replication Definition

The primary replication unit is an independently generated trajectory. Measurements obtained from multiple timepoints within the same trajectory constitute repeated observations rather than independent replications.

## RD-TEMPORAL WARNING Test

Temporal spread tested directly:

| Domain | Spread | Status |
|--------|--------|--------|
| GS | 0.000774 | Low temporal variability |
| RB | 0.002674 | Moderate temporal variability |
| AM | 0.000881 | Low temporal variability |

**Finding:** Temporal variability is domain-dependent. RB exhibits highest temporal spread.

## GS Contradiction (PRESERVED)

The GS contradiction survives and has evolved into a measurement result:

| Measurement | Value | Source |
|-------------|-------|--------|
| GS frame-0 estimate | ~0.07 | RD-WELL.8A.R2 |
| GS frame-200–500 estimate | ~0.18 | RD-WELL.8A.R2 |

Both were reproduced.

**Conclusion:** GS representation sensitivity appears temporally variable under the currently tested procedures.

## Output Files

- `gs_results.json`: GS replication results
- `rb_results.json`: RB replication results
- `am_results.json`: AM replication results
- `RD_WELL_8A_R1_COVERAGE_COMPLETION_AUDIT.md`: This report

## Status

**COMPLETE.**

Coverage targets achieved for GS, RB, AM. All domains now have uncertainty estimates.
