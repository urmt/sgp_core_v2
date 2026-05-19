# SECTION 9: WHY METRICS FAILED (OR SUCCEEDED) — V2_004

**Date:** 2025-05-13

---

## Result: NEW METRICS SHOW DISCRIMINATION

Contrary to V2_003, the new metric redesign SUCCEEDED:

### What Worked

1. **Local Curvature Entropy**
   - Random: 0.000002
   - Hierarchical: 0.000088 (44x difference!)
   - Effect vs null: 17-57x

2. **Scale Transition Instability**
   - Random: 0.0013
   - Hierarchical: 0.0065 (5x difference)

3. **Topological Persistence**
   - Random: 0.55
   - Hierarchical: 0.99 (near 2x)

---

## Why Old Metrics Failed

The D(k) + sigmoid approach failed because:
1. D(k) measures GLOBAL dimension, not LOCAL structure
2. Sigmoid fits ANY monotonic curve (including linear)
3. k0 and R² are invariant across different data structures
4. Null destruction doesn't affect global averages

---

## Why New Metrics Succeeded

1. **Curvature measures LOCAL variation** - Captures transitions in D(k)
2. **Instability measures SCALE changes** - Different scales respond differently
3. **Persistence measures STRUCTURE survival** - Cluster continuity

These metrics capture properties that D(k) + sigmoid misses.

---

## Status

**SUCCESS** - Discrimination achieved with new metrics.