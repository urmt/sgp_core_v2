# RD-WELL.5C — Cross-Pattern Coupling Audit

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Does strong coupling survive independent worlds?"  
**Status:** COMPLETE

---

## Question

Does the strong coupling between C and stabilization metrics observed in bubbles survive across independent Gray-Scott regimes?

This directly attacks SR-30 (program dependence).

---

## Method

Repeat the exact same analysis (C vs S₁, S₂, S₃) on multiple Gray-Scott patterns:
- bubbles
- maze
- spirals
- spots (failed to download)
- worms (failed to download)
- gliders (failed to download)

---

## Results

| Pattern | S₁ (Spectral) | S₂ (Derivative) | S₃ (Morphology) |
|---------|---------------|------------------|------------------|
| bubbles | -0.9283 | -0.9500 | -0.9128 |
| maze | -0.9383 | -0.7560 | -0.7373 |
| spirals | -0.6977 | -0.4904 | -0.0980 |

---

## Analysis

**Strong coupling (|r| > 0.8):**

| Metric | Patterns with strong coupling |
|--------|------------------------------|
| S₁ | 2/3 (bubbles, maze) |
| S₂ | 1/3 (bubbles) |
| S₃ | 1/3 (bubbles) |

**Coupling strength varies across patterns:**

- **bubbles:** All three metrics strongly coupled
- **maze:** S₁ strongly coupled, S₂/S₃ moderately coupled
- **spirals:** S₁ moderately coupled, S₂/S₃ weakly coupled

---

## What This Means

The coupling between C and stabilization metrics is **NOT universal** across all Gray-Scott regimes.

This suggests:
1. The coupling is **regime-dependent**
2. Different patterns exhibit **different coupling geometries**
3. This is **Outcome C** from the Research Director's framework

---

## Implications

1. **The coupling is not a universal property of the Gray-Scott system**
2. **Bubbles was special, not representative**
3. **Cross-domain validation has revealed regime-dependence**

---

## Status

- **RD-WELL.5:** PROVISIONAL — Stabilization operationalization failed independence test
- **RD-WELL.5B:** PROVISIONAL — Alternative metrics coupled to C in bubbles
- **RD-WELL.5C:** PROVISIONAL — Coupling varies across patterns

No temporal ordering claims are supported.

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5c/cross_pattern_coupling.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well5c/run_cross_pattern_coupling.py`
