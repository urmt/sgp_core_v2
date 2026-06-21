# RD-WELL.5A — Threshold Sensitivity Audit

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Test threshold dependence"  
**Status:** COMPLETE

---

## Question

Is the temporal ordering (C vs stabilization) stable across different threshold choices?

## Method

Tested stabilization time across thresholds:

| Threshold (θ) | Status | Stab. A | Stab. B | C before | C after | C increases? |
|-------------|--------|---------|---------|---------|---------|-------------|
| 0.001 | VALID | t=15 | t=13 | 0.332076 | 0.688862 | YES |
| 0.005 | NOT FOUND | — | — | — | — | — |
| 0.01 | NOT FOUND | — | — | — | — | — |
| 0.02 | NOT FOUND | — | — | — | — | — |
| 0.05 | NOT FOUND | — | — | — | — | — |

---

## Critical Finding

**Only threshold θ=0.001 produced a detectable stabilization event.**

For all higher thresholds (0.005–0.05), the frame-to-frame variance never dropped below the threshold within the first 200 time steps.

---

## What This Means

1. **Stabilization detection is highly sensitive to threshold choice**
2. **The operational definition may fail for reasonable thresholds**
3. **The temporal ordering claim is only supported at one extreme threshold**

---

## Implications for RD-WELL.5

Theurally, the result is **weaker than initially reported**:

- C increases after stabilization in **one regime** (bubbles)
- At **one extreme threshold** (θ=0.001)
- Using **one stabilization metric** (frame-to-frame variance)

This falls far below the standard for cross-domain validation.

---

## Recommendation

The Research Director's concerns are validated:

> **RD-WELL.5 is PROVISIONAL and may be artifactual.**

Before proceeding, we need:

1. **A more robust stabilization metric** (spectral entropy, derivative norm)
2. **Multiple thresholds tested per metric**
3. **Multiple regimes tested per metric**
4. **A metric that works across reasonable thresholds**

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5a/threshold_sensitivity_audit.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well5a/run_threshold_sensitivity_audit.py`
