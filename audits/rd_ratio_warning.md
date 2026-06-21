# RD-RATIO WARNING

**Date:** 2026-06-17  
**Status:** ACTIVE WARNING  
**Source:** P2 (RB Independent Trajectory Replication)

## Candidate Wording

> Similar variance ratios may conceal large differences in absolute measurement scale.

## Evidence

GS and RB:

| Domain | Within-Trajectory | Between-Trajectory | Ratio | Mean ΔC_rank |
|--------|-------------------|--------------------|-------|--------------|
| GS | 0.004087 | 0.003936 | 1.04x | 0.1610 |
| RB | 0.000015 | 0.000014 | 1.05x | 0.0075 |

Nearly identical ratios (~1.04x vs ~1.05x).

Approximately twenty-fold difference in mean ΔC_rank.

## Implication

A shared ratio does **not** imply shared behavior.

The system may have:

- similar variance structure
- radically different sensitivity scale

These are different questions. Keep them separate.

## Required Protocol

Future trajectory audits must include:

### Table E — Variance Decomposition

| Domain | Within | Between | Ratio | Mean ΔC_rank |
|--------|--------|---------|-------|--------------|

This prevents readers from focusing only on the ratio.

## Interpretation Constraint

The following statement is acceptable:

> Temporal variation exceeded trajectory variation in both GS and RB under the present measurement procedures.

The following statement is **not** acceptable:

> Temporal variation generally exceeds trajectory variation.

The sample remains too small.
