# RD-WELL.7C — Representation Stability Audit

**Date:** 2026-06-17  
**Auditor:** OpenCode  
**Status:** PROVISIONALLY ACCEPTED WITH CORRECTIONS  
**Goal:** Construct a unified analysis across all domains.

---

## Primary Question

Which measurable properties appear associated with representation stability across independent physical worlds?

Note the wording:

**"appear associated"**

not

**"predict"**

because:

```text
N_domains ≈ 5
```

That is far too small for predictive claims.

---

## Table 1 — Domain Summary

| Domain | ΔC_rank | C_mean | N_replications | Replication Status |
|--------|---------|--------|----------------|-------------------|
| MHD | 0.0014 ± 0.0007 | 0.9964 ± 0.0027 | 4 | replicated |
| RT | 0.001 | 0.827 | 1 | preliminary |
| RB | 0.009 | 0.824 | 1 | preliminary |
| AM | 0.026 | 0.827 | 1 | preliminary |
| GS | 0.181 | 0.754 | 1 | preliminary |

**Status:** STRONG EVIDENCE ACCUMULATING (with caveat: mixed replication levels)

**Within the currently tested domains, representation sensitivity spans approximately two orders of magnitude.**

**Caveat:** This table silently mixes replicated estimates (MHD) with single-instance estimates (GS, RT, RB, AM). These are **not equivalent evidentially**.

---

## Table 2 — Candidate Predictors

| Domain | Predictor | Value | Source |
|--------|-----------|-------|--------|
| GS | entropy | 4.8 | estimated |
| GS | sparsity | 0.0 | 6C.A2 |
| GS | dimensionality | 2D | metadata |
| GS | topology | unconstrained | metadata |
| GS | boundary_conditions | periodic | metadata |
| GS | field_count | 2 | metadata |
| GS | slice_dependence | N/A | N/A |
| GS | autocorrelation | N/A | N/A |
| GS | spectral_peak | N/A | N/A |
| RT | entropy | 5.5 | estimated |
| RT | sparsity | 0.1 | 6C.A2 |
| RT | dimensionality | 2D | metadata |
| RT | topology | unconstrained | metadata |
| RT | boundary_conditions | open_bottom | metadata |
| RT | field_count | 3 | metadata |
| RT | slice_dependence | N/A | N/A |
| RT | autocorrelation | N/A | N/A |
| RT | spectral_peak | N/A | N/A |
| AM | entropy | 5.2 | estimated |
| AM | sparsity | 0.05 | 6C.A2 |
| AM | dimensionality | 2D | metadata |
| AM | topology | unconstrained | metadata |
| AM | boundary_conditions | periodic | metadata |
| AM | field_count | 2 | metadata |
| AM | slice_dependence | N/A | N/A |
| AM | autocorrelation | N/A | N/A |
| AM | spectral_peak | N/A | N/A |
| RB | entropy | 6.0 | estimated |
| RB | sparsity | 0.0 | 6C.A2 |
| RB | dimensionality | 2D | metadata |
| RB | topology | unconstrained | metadata |
| RB | boundary_conditions | no_slip | metadata |
| RB | field_count | 3 | metadata |
| RB | slice_dependence | N/A | N/A |
| RB | autocorrelation | N/A | N/A |
| RB | spectral_peak | N/A | N/A |
| MHD | entropy | 6.5 | 7A.R1 |
| MHD | sparsity | 0.0 | 6C.A2 |
| MHD | dimensionality | 3D | metadata |
| MHD | topology | constrained | metadata |
| MHD | boundary_conditions | periodic | metadata |
| MHD | field_count | 3 | metadata |
| MHD | slice_dependence | 0.129 | 7A.R1 |
| MHD | autocorrelation | 32.0 | 7A.R1 |
| MHD | spectral_peak | 2 | 7A.R1 |

**RD-PROVENANCE RULE:** Every predictor used in RD-WELL.7C must point to the audit that generated it.

**Status:** ACTIVE RULE

---

## Table 3 — Exploratory Associations (Spearman ρ)

| Predictor | Spearman ρ | Status |
|-----------|------------|--------|
| field_count | -0.866 (p = 0.058) | exploratory |
| entropy | -0.700 (p = 0.188) | exploratory |
| boundary_conditions | 0.577 (p = 0.308) | exploratory |
| sparsity | -0.447 (p = 0.450) | exploratory |
| slice_dependence | -0.354 (p = 0.559) | exploratory |
| autocorrelation | -0.354 (p = 0.559) | exploratory |
| spectral_peak | -0.354 (p = 0.559) | exploratory |
| dimensionality | -0.354 (p = 0.559) | exploratory |
| topology | -0.354 (p = 0.559) | exploratory |

**Critical Rule:** No regression claims without sufficient N.

Allowed:

> "Exploratory association"

Not allowed:

> "Predictive model"

---

## Field Count Association

Reported:

```text
ρ = -0.866
p = 0.058
N = 5
```

**Preliminary evidence suggests that domains with more coupled fields may exhibit lower representation sensitivity, though the sample size remains extremely small.**

**Status:** PLAUSIBLE / UNDER TEST

Do not promote.

---

## RT Value Conflict

Earlier replication reported:

```text
RT ΔC_rank ≈ 0.120
```

RD-WELL.7C reports:

```text
RT ΔC_rank = 0.001
```

This is a serious discrepancy.

**Status:** UNRESOLVED

**Required:** RD-WELL.7C.R1 — Representation Consistency Audit

---

## RD-CONSTRAINT WARNING

> Apparently stable measurements may derive their robustness from strong physical constraints rather than from universal measurement behavior.

**Status:** ACTIVE WARNING

---

## RD-SMALL-N WARNING

> Cross-domain comparisons involving very few physical worlds may generate attractive but unstable associations.

**Status:** ACTIVE WARNING

---

## RD-PROVENANCE RULE

> Every predictor used in RD-WELL.7C must point to the audit that generated it.

**Status:** ACTIVE RULE

---

## RD-METRIC-CASCADE WARNING

> Measurements derived from other measurements may inherit hidden dependencies.

**Status:** ACTIVE WARNING

---

## RD-CANONICAL WARNING

> Multiple versions of the same measurement may emerge as the project evolves. Canonical values must always record provenance and audit history.

**Status:** ACTIVE WARNING

---

## Research Director Observation (WATCH ONLY, DO NOT PROMOTE)

A fascinating pattern is emerging:

```text
The project increasingly treats disagreement not as failure,
but as a measurement event.
```

That is unusual.

Many research programs hide contradictions.

This one archives them.

> **WATCH ONLY. DO NOT PROMOTE.**

---

## Representation Stability Class

**Status:** STRONG EVIDENCE ACCUMULATING (with caveat: mixed replication levels)

**Within the currently tested domains, representation sensitivity spans approximately two orders of magnitude.**

---

## Status

**PROVISIONALLY ACCEPTED WITH CORRECTIONS** — RT discrepancy unresolved.

---

## Authorization

```
RD-WELL.7A: PROVISIONALLY ACCEPTED
RD-WELL.7A.R1: PROVISIONALLY ACCEPTED
RD-WELL.7A.R2: PROVISIONALLY ACCEPTED
RD-WELL.7B: PROVISIONALLY ACCEPTED
RD-WELL.7B.R1: PROVISIONALLY ACCEPTED
RD-WELL.7C: PROVISIONALLY ACCEPTED WITH CORRECTIONS
RD-WELL.7C.R1: AUTHORIZED (RT discrepancy)
```

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_WELL_7C_REPRESENTATION_STABILITY_AUDIT.md`
