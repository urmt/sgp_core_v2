# METRIC REDESIGN INIT — SECTION 1

**Date:** 2025-05-13  
**Status:** COMPLETE

---

## Purpose

Following failed V2_003 discrimination phase, redesign metrics to actually distinguish organized from random systems.

## Relation to Failed V2_003

**V2_003 Findings:**
- Sigmoid R² > 0.99 on ALL systems (random, hierarchical, sparse, oscillator)
- k0 ~5.8 for ALL systems (no discrimination)
- Topology destruction Δk0 < 0.1, ΔR² < 0.001
- Multi-seed convergence to identical parameters

**Conclusion:** D(k) + sigmoid approach fundamentally failed.

## Directory Structure

```
/sgp_core_v2/scripts/core/metric_redesign/
├── new_metrics.py           # Candidate metrics
├── adversarial_metric_test.py  # Test harness
├── evaluation.py             # Success criteria evaluation
└── __init__.py

/home/student/sgp_core_v2/outputs/metric_redesign/
├── figures/                 # Generated plots
├── reports/                 # Validation reports
└── logs/                    # Runtime logs
```

## New Metric Design

5 candidate approaches:
1. Local Curvature Entropy
2. Scale Transition Instability
3. Multi-scale Spectral Drift
4. Topological Persistence Proxy
5. Temporal Stability Index

---

## Status

**INIT COMPLETE**  
Next: Section 2 — Document failure of old metric