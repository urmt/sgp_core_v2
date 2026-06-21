# RD-WELL.7C.R1 — Representation Consistency Audit

**Date:** 2026-06-17  
**Auditor:** OpenCode  
**Status:** AUTHORIZED  
**Goal:** Resolve RT value discrepancy.

---

## Question

Which RT estimate is canonical, and why do they differ?

---

## Discrepancy

Earlier replication reported:

```text
RT ΔC_rank ≈ 0.120
```

RD-WELL.7C reports:

```text
RT ΔC_rank = 0.001
```

This is a serious discrepancy.

---

## Possible Causes

1. Different trajectory
2. Different timestep
3. Different slicing
4. Different transform implementation
5. Averaging procedures

---

## Required Tasks

### A. Identify Source of Each Value

- **Value 1 (ΔC_rank ≈ 0.120):** From RD-WELL.6C.R1 replication audit
- **Value 2 (ΔC_rank = 0.001):** From RD-WELL.7C domain expansion audit

### B. Compare Implementation Details

- Trajectory selection
- Timestep selection
- Slicing method
- Transform implementation
- Averaging procedures

### C. Determine Canonical Value

- Which value is correct?
- Why do they differ?
- What does this mean for the Representation Stability Class?

---

## RD-CANONICAL WARNING

> Multiple versions of the same measurement may emerge as the project evolves. Canonical values must always record provenance and audit history.

**Status:** ACTIVE WARNING

---

## Status

**AUTHORIZED** — Ready for RT consistency audit.

---

## Authorization

```
RD-WELL.7A: PROVISIONALLY ACCEPTED
RD-WELL.7A.R1: PROVISIONALLY ACCEPTED
RD-WELL.7A.R2: PROVISIONALLY ACCEPTED
RD-WELL.7B: PROVISIONALLY ACCEPTED
RD-WELL.7B.R1: PROVISIONALLY ACCEPTED
RD-WELL.7C: PROVISIONALLY ACCEPTED WITH CORRECTIONS
RD-WELL.7C.R1: AUTHORIZED
```

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_WELL_7C_R1_REPRESENTATION_CONSISTENCY_AUDIT.md`
