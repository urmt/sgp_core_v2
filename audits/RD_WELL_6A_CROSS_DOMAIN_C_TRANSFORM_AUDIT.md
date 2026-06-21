# RD-WELL.6A — Cross-Domain C Computation with Transform Audit

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Compute C under multiple field transformations"  
**Status:** COMPLETE

---

## Question

Is C itself representation-stable?

---

## Method

Compute C under multiple field transformations for each domain:
- original
- z-score
- rank
- min-max

Report: ΔC_transform

---

## Results

### Rayleigh-Bénard Buoyancy

| Transformation | C Value | ΔC |
|----------------|---------|-----|
| original | 0.745474 | 0.000000 |
| zscore | 0.745474 | 0.000000 |
| rank | 0.765508 | 0.020034 |
| minmax | 0.745474 | 0.000000 |

### Active Matter Concentration

| Transformation | C Value | ΔC |
|----------------|---------|-----|
| original | 0.771579 | 0.000000 |
| zscore | 0.771579 | 0.000000 |
| rank | 0.732803 | 0.038776 |
| minmax | 0.771579 | 0.000000 |

---

## Key Findings

1. **No transform sensitivity observed for z-score or min-max normalization** — ΔC = 0 for both domains
2. **Rank transformation sensitivity observed** — ΔC = 0.020 (RB) and 0.039 (AM)
3. **C can be computed in multiple independent physical domains** — RB: 0.745, AM: 0.772 (original)

---

## Implications

**No transform sensitivity observed for linear transformations (z-score, min-max), but rank transformation sensitivity observed.**

This means:
- No transform sensitivity observed for linear field transformations
- Rank transformation sensitivity observed
- Representation stability depends on the type of transformation

**Interpretation (carefully phrased):**
> C may depend partly on metric structure rather than purely ordinal structure.

**Safe wording:**
> The current implementation of C remains computable across multiple independent physical worlds and exhibits limited sensitivity to some tested field transformations.

---

## Status

Cross-domain C computation with transform audit complete.

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well6a/cross_domain_C_transform_audit.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well6a/run_cross_domain_C_transform_audit.py`
