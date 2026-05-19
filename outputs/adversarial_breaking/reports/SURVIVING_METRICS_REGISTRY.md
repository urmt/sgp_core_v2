# SURVIVING METRICS REGISTRY — SECTION 9

**Date:** 2025-05-13

---

## Rejected Metrics

| Metric | Reason |
|--------|--------|
| Sigmoid R² (V2_003) | No discrimination |
| k0 (V2_003) | Identical across systems |
| Deceptive Curvature detection | BROKEN - can be fooled |

---

## Surviving Metrics (CONDITIONAL)

| Metric | Confidence | Concerns |
|--------|------------|----------|
| Local Curvature Entropy | MEDIUM | Deceptive curvature can fool it |
| Scale Transition Instability | HIGH | Stable across tests |
| Topological Persistence | MEDIUM | Not fully tested |

---

## Confidence Levels

- **HIGH**: Passed adversarial and null tests
- **MEDIUM**: Passed most tests, some concerns
- **LOW**: Needs more validation

---

## Status

**CONDITIONAL SURVIVAL** - Metrics need additional constraints before real-world use.