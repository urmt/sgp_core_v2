# RD-WELL.6C.R1 — Cross-Domain Replication Audit

**Date:** 2026-06-17  
**Auditor:** OpenCode  
**Status:** AUTHORIZED  
**Goal:** Replicate C across domains before any further coupling work.

---

## Objective

Estimate the stability of C under:

- multiple trajectories
- multiple time points
- multiple parameter regimes (when available)

Compute confidence intervals.

No new theory.

No survivor promotion.

No coupling.

Replication only.

---

## Domains

### Minimum

#### Gray-Scott

Sample:
- trajectories: 0–9
- timepoints: [100, 300, 500, 700, 900]
- patterns: bubbles, maze, spirals

#### Rayleigh-Bénard

Sample:
- trajectories: 0–9
- timepoints: [20, 60, 100, 140, 180]
- Rayleigh numbers: 1e6, 1e8, 1e10 (if accessible)

#### Active Matter

Sample all trajectories.
- timepoints: [10, 20, 40, 60, 80]
- parameter regimes: α = −1, α = −2, α = −4 (if accessible)

#### Rayleigh-Taylor

High priority.
Sample:
- both trajectories
- multiple timepoints
- several z-slices

This directly tests whether ΔC_rank ≈ 0 survives replication.

Do NOT promote even if replicated.

Status remains: PLAUSIBLE / UNDER TEST

---

## Measurements

For every sample compute:

- C_original
- C_rank
- ΔC_rank = |C_original − C_rank|

Also compute:

- mean
- std
- 95% confidence interval
- N

Store raw JSON.

---

## Required Tables

### Table 1: Cross-Domain Replication

| Domain | N | mean(C) | std(C) | 95% CI | mean(ΔC_rank) |
|--------|---|---------|--------|--------|---------------|

### Table 2: Representation Stability Class (PROVISIONAL)

| Domain | Rank Sensitivity | Classification |
|--------|------------------|----------------|
| Gray-Scott | high | High rank sensitivity |
| Rayleigh-Bénard | low | Low rank sensitivity |
| Active Matter | low | Low rank sensitivity |
| Rayleigh-Taylor | very low | Very low rank sensitivity |

This is descriptive only.

No ontology.

No survivor promotion.

---

## Explicit Warnings

- Replication precedes explanation.
- A stable mean with unstable variance is not stability.
- A replicated effect inside one research program remains vulnerable to SR-30.

---

## New Dashboard Metric

### RD-REPLICATION SCORE

```
replicated_measurements / total_measurements
```

Purpose:

Track whether the program is measuring the world or accumulating single examples.

Not a law.

Not a survivor.

A dashboard indicator only.

---

## Freeze

Until RD-WELL.6C.R1 completes:

- RD-WELL.6B coupling work remains frozen.

Reason:

Relationships should not be studied before measurements themselves are stable.

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_WELL_6C_R1_REPLICATION_AUDIT.md`
