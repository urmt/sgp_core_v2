# RELATIONAL FAILURE MAP — SECTION 9

**Date:** 2025-05-13

---

## Adversarial Attack Results

| System | Fragmentation | vs Hier (0.06) | Fooled? |
|--------|---------------|-----------------|---------|
| random_gaussian | 0.140 | +0.080 | NO |
| hierarchical | 0.060 | baseline | NO |
| fake_low_fragmentation | 0.180 | +0.120 | NO |
| multi_scale_camouflage | 0.200 | +0.140 | NO |
| graph_motif_injection | 0.180 | +0.120 | NO |

---

## Key Finding

**Graph fragmentation RESISTED adversarial attacks.**

All adversarial systems had fragmentation 0.18-0.20, much higher than hierarchical 0.06.

---

## Failure Zones

- None found for fragmentation metric
- Ensemble consensus still not discriminating
- Scale-transition not fully tested
- Temporal not tested

---

## Status

**HARDENING SUCCESS** - Graph metrics survived adversarial attack.