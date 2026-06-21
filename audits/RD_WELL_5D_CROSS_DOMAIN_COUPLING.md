# RD-WELL.5D — Cross-Domain Coupling Audit

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Which classes of observables maintain coupling to C across independent worlds?"  
**Status:** PARTIAL (Gray-Scott complete, other domains failed to download)

---

## Question

Which classes of observables maintain coupling to C across independent worlds?

This directly attacks SR-30 (program dependence).

---

## Method

Compute correlations between C and stabilization metrics (S₁, S₂, S₃) on multiple domains.

---

## Results

### Gray-Scott Patterns

| Domain | S₁ (Spectral) | S₂ (Derivative) | S₃ (Morphology) |
|--------|---------------|------------------|------------------|
| bubbles | -0.9773 | -0.9456 | -0.9152 |
| maze | -0.7766 | -0.7281 | -0.7446 |
| spirals | -0.7947 | -0.4882 | -0.1235 |

### Other Domains

| Domain | Status |
|--------|--------|
| Rayleigh-Bénard | Failed to download |
| Active Matter | Failed to download |

---

## Analysis

**Coupling geometry varies across Gray-Scott regimes:**

- **bubbles:** All three metrics strongly coupled (|r| > 0.9)
- **maze:** All three metrics moderately coupled (|r| ~ 0.73-0.78)
- **spirals:** S₁ moderately coupled, S₂ weakly coupled, S₃ nearly uncoupled

**S₁ (Spectral) maintains coupling across all three patterns:**
- bubbles: r = -0.98
- maze: r = -0.78
- spirals: r = -0.79

**S₃ (Morphology) coupling degrades substantially:**
- bubbles: r = -0.92
- maze: r = -0.74
- spirals: r = -0.12

---

## Implications

1. **Spectral organization (S₁) maintains coupling across Gray-Scott regimes**
2. **Morphology-based organization (S₃) is regime-dependent**
3. **The coupling geometry itself is the observable**
4. **Different classes of observables have different cross-domain stability**

---

## Status

- **RD-WELL.5:** PROVISIONAL
- **RD-WELL.5B:** PROVISIONAL
- **RD-WELL.5C:** PROVISIONAL — Coupling varies across patterns
- **RD-WELL.5D:** PARTIAL — Gray-Scott complete, other domains pending

---

## Next Steps

1. Download Rayleigh-Bénard and Active Matter datasets
2. Repeat analysis on those domains
3. Construct full coupling geometry table across domains

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5d/cross_domain_coupling.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well5d/run_cross_domain_coupling.py`
