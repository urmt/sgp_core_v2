# RELATIONAL QUICK VALIDATION — SECTION 6

**Date:** 2025-05-13

---

## Graph Metrics Results

| System | Edges | Fragmentation |
|--------|-------|---------------|
| random_gaussian | 290 | 0.140 |
| hierarchical | 298 | 0.060 |

---

## Key Finding

Hierarchical has:
- MORE edges (298 vs 290) - 2.8% more connectivity
- LOWER fragmentation (0.06 vs 0.14) - 57% less fragmented

**DISCRIMINATION FOUND**

---

## Relational Ensemble Results

| System | Ensemble Mean | Verdict |
|--------|---------------|---------|
| random_gaussian | ~0.5 | REJECT |
| hierarchical | ~0.5 | REJECT |

Note: Ensemble showing low discrimination - needs tuning.

---

## Status

**PARTIAL SUCCESS** - Graph metrics show discrimination but ensemble needs work.