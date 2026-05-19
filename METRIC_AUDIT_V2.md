# METRIC AUDIT V2 — SGP-CORE V2

**Date:** 2025-05-13

---

## Prior Metrics Classification

### Robust Metrics (✓)

| Metric | Classification | Status |
|--------|---------------|--------|
| Participation Ratio D(k) | ROBUST | Keep, use |
| k0 (sigmoid inflection) | ROBUST | Keep, use |
| R² (model fit) | ROBUST | Keep, use |
| AIC/BIC | ROBUST | Keep, use |
| Bootstrap CV | ROBUST | Keep, use |

### Unstable Metrics (⚠️)

| Metric | Classification | Status |
|--------|---------------|--------|
| tau (relaxation time) | UNSTABLE | Refine or remove |
| Kc (critical point) | UNSTABLE | Not use for claims |
| Gamma (scaling) | UNSTABLE | Domain-sensitive |

### Noise-Sensitive (⚠️)

| Metric | Classification | Status |
|--------|---------------|--------|
| Binder minimum depth | NOISE-SENSITIVE | Document limitation |
| Loop area (hysteresis) | NOISE-SENSITIVE | Needs larger trials |

### Domain-Sensitive (⚠️)

| Metric | Classification | Status |
|--------|---------------|--------|
| Gamma exponent | DOMAIN-SENSITIVE | Cannot claim universal |
| Kc estimation | DOMAIN-SENSITIVE | No single value |

---

## New Metrics for V2

### Addition: Persistence Metrics

| Metric | Purpose |
|--------|---------|
| τ_persistence | Attractor lifetime |
| M_metastability | Dwell time variance |
| t_recovery | Perturbation resilience |

### Addition: Dynamical Metrics

| Metric | Purpose |
|--------|---------|
| D(k,t) | Temporal dimensionality |
| k0(t) | Inflection trajectory |
| stability_index | Temporal consistency |

---

## Null Comparison Required

Every metric MUST be compared against:
1. Random baseline
2. Shuffled topology
3. Noise control

No metric claim passes without null comparison.

---

## Status

**AUDIT COMPLETE**  
Keep: D(k), k0, R², AIC/BIC, bootstrap, persistence  
Refine: tau, Kc, gamma  
Remove: Unfixable noise-sensitive metrics