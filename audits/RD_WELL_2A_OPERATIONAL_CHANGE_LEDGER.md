# RD-WELL.2A — Operational Change Ledger

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "describe before explaining"  
**Status:** COMPLETE

---

## Method

For each dataset, record only:
- What appears
- What disappears
- What repeats
- What stabilizes

**Forbidden words:** coherence, persistence, emergence, interaction, observer, sentience, hierarchy, intelligence

---

## Gray-Scott Bubbles (F=0.098, k=0.057)

| Interval | Appears | Disappears | Repeats | Stabilizes |
|----------|---------|------------|---------|------------|
| t0→t100 | B local maxima increased (30 → 3758), A local maxima increased (94 → 3073) | none | none | A variance decreased (0.021282 → 0.013986), B variance decreased (0.016389 → 0.007277) |
| t100→t500 | none | none | A mean stable (~0.9695), B mean stable (~0.0193) | none |
| t500→t1000 | none | none | A mean stable (~0.9696), B mean stable (~0.0192) | none |

---

## Gray-Scott Maze (F=0.029, k=0.057)

| Interval | Appears | Disappears | Repeats | Stabilizes |
|----------|---------|------------|---------|------------|
| t0→t100 | B local maxima increased (100 → 557), A local maxima increased (107 → 199) | none | none | none |
| t100→t500 | A local maxima increased (199 → 485) | none | none | A variance decreased (0.048657 → 0.021312), B variance decreased (0.012316 → 0.009468) |
| t500→t1000 | none | none | A mean stable (~0.5139), B mean stable (~0.1639) | none |

---

## Gray-Scott Spirals (F=0.018, k=0.051)

| Interval | Appears | Disappears | Repeats | Stabilizes |
|----------|---------|------------|---------|------------|
| t0→t100 | B local maxima increased (30 → 520) | none | none | B variance decreased (0.016389 → 0.011092) |
| t100→t500 | none | none | none | none |
| t500→t1000 | none | none | none | none |

---

## Key Observations

1. **All patterns show rapid change in first 100 time steps**
2. **Local maxima increase dramatically in early intervals**
3. **Variance decreases (stabilizes) in early intervals**
4. **Mean values stabilize in later intervals**
5. **No pattern shows disappearance of features**

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well2a/operational_change_ledger.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well2a/run_operational_change_ledger.py`
