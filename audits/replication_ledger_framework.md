# Replication Ledger Framework

**Source:** Research Director (P1 authorization)
**Status:** ACTIVE FRAMEWORK
**Date:** 2026-06-17

## Purpose

The Replication Ledger is a structured record of every measurement, its provenance, and its metadata. It ensures that every estimate is traceable and that sources of variation can be identified.

## Required Metadata

For every measurement, record:

| Field | Description |
|-------|-------------|
| trajectory_id | exact source trajectory |
| frame_index | exact temporal location |
| transform | original, rank, z-score, etc. |
| dimensional_reduction | slice, projection, volume proxy |
| compute_C_version | exact implementation used |
| audit_provenance | originating audit |

## Output Tables

### Table A — Trajectory Replication

Raw measurements for each trajectory and frame.

| trajectory | frame | ΔC_rank |
|------------|-------|---------|

### Table B — Within-Trajectory Spread

Temporal variability within each trajectory.

| trajectory | min | max | mean | spread |
|------------|-----|-----|------|--------|

### Table C — Between-Trajectory Spread

Replication variability across trajectories at fixed frame locations.

| frame_location | mean ΔC_rank | SD |
|----------------|--------------|-----|

### Table D — Provenance Ledger

Complete provenance for every estimate.

| estimate_id | trajectory | frame | transform | dimensional_reduction | compute_C_version | audit_provenance |
|-------------|------------|-------|-----------|----------------------|-------------------|------------------|

## Interpretation

The goal is to determine which source of variation dominates:

1. **Trajectory dominates:** Different trajectories give very different ΔC_rank values.
2. **Time dominates:** Different frames within the same trajectory give very different ΔC_rank values.
3. **Protocol dominates:** Different transforms or implementations give very different ΔC_rank values.
4. **Interactions dominate:** The effect of one source depends on the level of another.

All outcomes are scientifically useful.

## Success Criterion

The goal is **not** to obtain a single GS number.

The goal is to estimate:

```text
ΔC_rank(GS | trajectory, time, protocol)
```

and determine which source of variation dominates.
