# Phase N — Dynamical Coupling

## Directory Structure
```
phaseN_dynamical_coupling/
├── MANIFEST.md
├── scripts/
│   ├── N1_N2_minimal_coupling.py
│   ├── N3_N4_mutual_stabilization_alignment.py
│   ├── N5_N6_emergent_failure.py
│   ├── N7_N8_taxonomy_dynamical_nulls.py
│   └── N9_synthesis.py
├── outputs/
│   ├── phaseN_minimal_couplings.csv     (365 KB)
│   ├── phaseN_temporal_trajectories.csv (12646 KB)
│   ├── phaseN_transition_geometry.csv   (365 KB)
│   ├── phaseN_mutual_stabilization.csv  (452 KB)
│   ├── phaseN_phase_alignment.csv       (475 KB)
│   ├── phaseN_emergent_coupling.csv     (548 KB)
│   ├── phaseN_failure_modes.csv         (303 KB)
│   ├── phaseN_coupling_taxonomy.csv     (368 KB)
│   └── phaseN_dynamical_nulls.csv       (31 KB)
└── summaries/
    ├── n1_summary.json
    ├── n2_summary.json
    ├── n3_summary.json
    ├── n4_summary.json
    ├── n5_summary.json
    ├── n6_summary.json
    ├── n7_summary.json
    ├── n8_summary.json
    └── n9_synthesis.json
```

## Primary Question
**Can recursive continuity become dynamically co-maintained across separate processes?**

Phase M discovered that static similarity metrics cannot capture intersubjective organization. Phase N implements dynamical coupling — actual temporal interaction between recursively self-maintaining processes — to test whether coupling produces genuine co-maintenance.

## Sub-Phase Summary

| Sub-phase | Title | Key Finding |
|-----------|-------|-------------|
| N1 | Minimal Coupling | Coupled oscillator model produces synchronization (mean=0.873) with coupling strengthening synchronization (r=0.799). |
| N2 | Transition Geometry | Mutual stability index = 0.891. Mutual persistence gain = 0.145. Coupling reduces collapse probability from 0.158 to 0.017. |
| N3 | Mutual Stabilization | Mutual stabilization = 0.901. 37.7% of pairs are mutually self-maintaining. Persistence coupling (r=0.536) and capture probability (r=0.750) predict stabilization. |
| N4 | Phase Alignment | 85.4% converge to phase and frequency synchronization within 100 steps. Mean sync time = 33.3 steps. Coupling strength predicts sync time (r=-0.642). |
| N5 | Emergent Coupled Identities | Emergent sync bonus = 0.032. Collective closure = 0.622. Co-continuity = 0.873. Higher-order continuity correlates with final synchronization (r=0.981). |
| N6 | Coupling Failure Modes | Extremely high recovery across all perturbation types (~0.96). Most destructive: closure_collapse (recovery=0.956). Fragmentation requires persistent disruption. |
| N7 | Organizational Coupling Taxonomy | 4 classes: synchronizing (39.8%), stabilizing (34.8%), weakly coupled (9.2%), unsynchronized (16.2%). |
| N8 | Dynamical Nulls | **Key finding:** Closure correlation collapse = 0.993 under temporal scramble. Synchronization collapse = 0.264. Temporal structure is REQUIRED for deep closure alignment but NOT for shallow frequency matching. |
| N9 | Synthesis | Recursive continuity CAN be co-maintained, at two levels. |

## Key Discovery
**Recursive co-maintenance operates at two distinct levels:**
1. **Shallow synchronization:** frequency-driven phase alignment. Survives temporal scramble (collapse=0.264). Trivial — any two oscillators with similar frequencies synchronize.
2. **Deep closure alignment:** temporally ordered closure correlation. Destroyed by temporal scramble (collapse=0.993). This is the real finding — closure correlation between coupled recursive continuities REQUIRES preserved temporal structure.

## Dynamical Null Insight (N8)
The true dynamical null (shuffling temporal ordering within trajectories) reveals that different coupling properties have different temporal requirements:
- Phase synchronization is partially driven by static frequency matching (only 26% collapse)
- Closure correlation is almost entirely temporally driven (99% collapse)
- The organizing quality of coupled recursive continuity resides in temporal ordering, not in marginal distributions

## Next: Phase O — Shared Recursive Identity
Deep closure alignment across extended timescales approaches "shared recursive identity" — where coupled processes maintain a common closure trajectory. Phase O should investigate this regime: what happens when closure correlation persists across hundreds of steps?
