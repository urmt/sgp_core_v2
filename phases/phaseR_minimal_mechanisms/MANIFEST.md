# Phase R — Minimal Generative Mechanisms for Recursive Continuity

## Directory Structure
```
phaseR_minimal_mechanisms/
├── MANIFEST.md
├── scripts/
│   ├── R1_R2_ablation_minimal_models.py
│   ├── R3_R4_necessary_sufficient_degeneracy.py
│   ├── R5_thresholds.py
│   ├── R6_compression.py
│   ├── R7_R8_nulls_taxonomy.py
│   └── R9_synthesis.py
├── outputs/
│   ├── R1_ablation_hierarchy.csv              (1 KB)
│   ├── R2_minimal_models.csv                  (1 KB)
│   ├── R3_necessary_sufficient.csv            (1 KB)
│   ├── R4_continuity_degeneracy.csv           (1 KB)
│   ├── R5_reconstruction_thresholds.csv       (5 KB)
│   ├── R6_organizational_compression.csv      (1 KB)
│   ├── R7_adversarial_nulls.csv               (1 KB)
│   └── R8_mechanism_taxonomy.csv              (1 KB)
└── summaries/
    ├── r1_summary.json through r9_synthesis.json
    └── validation_report.json
```

## Primary Question
**What is the absolute minimum generative mechanism required for recursive continuity?**

Phases K→Q established closure VALUE distribution as the TRUE invariant of recursive continuity. Phase R is a reductionist phase that systematically determines the minimal necessary mechanisms by progressive removal, adversarial nulls, and degeneracy analysis.

## Sub-Phase Summary

| Sub-phase | Title | Key Finding |
|-----------|-------|-------------|
| R1 | Mechanism Ablation Hierarchy | **Phase coupling removal → catastrophic failure (17.5% survival). ALL other mechanisms survive individually (>65%).** |
| R2 | Minimal Closure Model | Minimal coupled (N=2, K=0.2, α=0.1) preserves continuity at 94.5%. Even no_dynamics (static random) achieves 69% baseline. |
| R3 | Necessary vs Sufficient Conditions | **No single mechanism is NECESSARY for continuity. ALL mechanisms are individually SUFFICIENT.** |
| R4 | Continuity Degeneracy | **10/12 architectures produce same continuity profile.** Highly degenerate system. |
| R5 | Reconstruction Thresholds | **Sharp K threshold: ~0.2-0.4 for robust survival.** α and β have NO collapse threshold — continuity persists without closure dynamics. |
| R6 | Organizational Compression | **142x compression to 90% variance (1000D → 7D). 2 PCs predict final closure R²=0.89.** Last 5 timesteps → perfect prediction. |
| R7 | Adversarial Null Program | **Catastrophic only: negative coupling, inverted closure, all_adversarial (0%).** 11/16 programs resilient. |
| R8 | Mechanism Taxonomy | 1 ESSENTIAL (phase_coupling), 1 SUPPORTING (topology), 1 DECORATIVE (closure_dynamics), 4 EPIPHENOMENAL |
| R9 | Synthesis | Recursive continuity reduces to **phase coupling as the sole essential mechanism**. Everything else is individually dispensable. |

## Key Discovery
**Phase coupling (Kuramoto-style synchronization) is the single ESSENTIAL mechanism for recursive continuity:**
- Removal → survival collapse from 95% to 17.5%
- Threshold: K ≥ 0.2 for robust survival
- No other mechanism shows a catastrophic failure when removed individually

**All other mechanisms are individually dispensable:**
- Closure dynamics (α=0): survival still 92.5-95%
- Closure cross-coupling (β=0): survival 92.5%
- Topology (sparse): survival 65%
- Temporal order (jitter): survival 93.8%
- Frequency alignment: survival 100%
- Reconstruction: survival 97.5%

## Mechanism Taxonomy

| Mechanism | Class | Survival After Removal | Closure Change |
|-----------|-------|----------------------|----------------|
| Phase coupling | **ESSENTIAL** | 17.5% | -0.415 |
| Topology | **SUPPORTING** | 65.0% | -0.232 |
| Closure dynamics | **DECORATIVE** | 90.0% | -0.129 |
| Cross-coupling | EPIPHENOMENAL | 92.5% | -0.026 |
| Reconstruction | EPIPHENOMENAL | 97.5% | +0.035 |
| Temporal order | EPIPHENOMENAL | 93.8% | -0.035 |
| Frequency alignment | EPIPHENOMENAL | 100.0% | +0.312 |

## Compression & Degeneracy
- **142x compression** (1000D → 7D for 90% variance)
- **2 PCs** predict final closure with R² = 0.89
- **10/12 degenerate architectures** produce same continuity profile
- System is overdetermined: all mechanisms sufficient, none necessary individually

## Next: Phase S — Phase Coupling Formalization
Formalize the mathematical structure of the essential phase coupling mechanism identified in Phase R.
