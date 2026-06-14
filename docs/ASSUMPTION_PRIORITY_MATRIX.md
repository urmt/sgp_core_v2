# Assumption Priority Matrix

Ranking all assumptions from `docs/CRITICAL_ASSUMPTIONS_REGISTER.md` by Expected Information Value (EIV).

## Formula

```
EIV = Importance × Uncertainty
```

Where:
- **Importance**: How central the assumption is to the research program (0–10). An assumption is important if its truth or falsehood changes what we do next.
- **Uncertainty**: How unsure we are (0–1). 0 = certain truth, 1 = complete unknown.

EIV ranges from 0 (no value in resolving — already certain or irrelevant) to 10 (maximum value — central and completely unknown).

---

## Full Matrix

Sorted by EIV descending:

| Rank | Assumption | Status | Importance | Uncertainty | **EIV** |
|:---:|---|:---:|:---:|:---:|:---:|
| 1 | **C is causally involved in recovery** | Unknown | 10 | 1.0 | **10.0** |
| 2 | **C × mobility interaction is genuine** | Unknown | 10 | 1.0 | **10.0** |
| 3 | Higher C → higher resilience | Challenged | 10 | 0.6 | 6.0 |
| 4 | C and mobility can be independently measured | Challenged | 10 | 0.6 | 6.0 |
| 5 | Results generalize beyond granular systems | Weakly Supp. | 8 | 0.7 | 5.6 |
| 6 | Mobility causes recovery | Plausible | 9 | 0.4 | 3.6 |
| 7 | Perturbation response reveals resilience | Supported | 7 | 0.2 | 1.4 |
| 8 | Granular DEM is a valid model system | Supported | 7 | 0.2 | 1.4 |
| 9 | Friction is an adequate mobility proxy | Supported | 7 | 0.2 | 1.4 |
| 10 | Recovery metrics capture meaningful properties | Supported | 7 | 0.2 | 1.4 |
| 11 | Binning preserves interaction structure | Supported | 6 | 0.2 | 1.2 |
| 12 | Sliding windows capture dynamics | Supported | 6 | 0.2 | 1.2 |
| 13 | Reconstruction from partial observations (IF-3) | Supported | 5 | 0.2 | 1.0 |
| 14 | C is an informative state variable | Supported | 9 | 0.1 | 0.9 |
| 15 | Interaction structure > raw state | Supported | 8 | 0.1 | 0.8 |
| 16 | C outperforms competitor metrics | Supported | 6 | 0.1 | 0.6 |
| 17 | Metric is independent of ontology | Supported | 5 | 0.1 | 0.5 |
| 18 | SFH ontology necessary for metric | Not Supported | 3 | 0.1 | 0.3 |
| 19 | Metric validity implies ontology validity | Not Supported | 3 | 0.1 | 0.3 |

---

## Decision Gates

| Assumption | What we would do if FALSE | What we would do if TRUE |
|:---|---:|---:|
| **C is causally involved** | Shift to state-description paradigm. Develop C as monitoring tool, not intervention target. Focus on mobility as the actionable variable. | Continue causal program. Design C-based interventions. Invest in causal discovery across systems. |
| **Interaction is genuine** | Adopt Model D (thermometer). C is useful but not causally special. Recovery understanding requires mobility measurement. | Adopt Model C (interaction). C and mobility synergize. Both are necessary for prediction and potentially intervention. |
| **Higher C → higher resilience** | Abandon single-variable resilience prediction. C cannot stand alone as a resilience metric. | Continue using C as a standalone resilience indicator. Justify C-only measurement in field applications. |
| **C and mobility are independent** | C and mobility are the same thing measured differently. Abandon decoupling. C is friction in disguise. | Design joint measurement protocols. Develop independent manipulation techniques. |
| **Generalization** | Results are granular-specific. Abandon cross-domain claims. | Cross-domain theory of coherence and resilience. |

---

## Highest-Value Target

### The single assumption whose resolution would most change our conclusions:

**"Coherence is causally involved in recovery"** (EIV = 10.0)

Why this assumption dominates:

1. **No causal evidence exists** — zero experiments have manipulated C independently. Uncertainty is maximal (1.0).

2. **Maximum branching factor** — if TRUE, we continue the causal program and invest in C-based prediction and intervention across domains. If FALSE, we redirect to a state-description program where C is a monitoring metric but mobility is the causal target. These are fundamentally different research trajectories.

3. **Prerequisite for all applied claims** — every practical claim about C (early warning signals, intervention targeting, resilience management) depends on C having at least some causal role. If C is purely a thermometer, the value proposition shifts from "C enables intervention" to "C enables monitoring, but intervention requires mobility."

4. **Resolvable** — the P1 polydispersity × friction experiment (already designed, `experiments/P1_C_MOBILITY_DECOUPLING_DESIGN.md`) is a direct test of this assumption. It manipulates C by varying grain radius range at fixed friction, holding mobility approximately constant while shifting interaction structure.

5. **Interacts with #2** — the interaction term's genuineness (rank 2) is a necessary condition for C being involved. If the interaction is an artifact, C cannot be causally involved. These two assumptions are the highest-value pair: resolving one partially resolves the other.

**Runner-up**: "C × mobility interaction is genuine" (EIV = 10.0, tied). This is the statistically testable version of the same question. Cross-validation on existing data can partially resolve it without new simulations.

### How to resolve the top-ranked assumption

1. **Immediate** (no new data, ~1 hour): Cross-validate Model D (C × friction interaction) on existing 60-run dataset using k-fold (k=5 or 10), bootstrap confidence intervals, and train/test split. If the interaction R² drops to additive-model levels out-of-sample, the interaction is fragile. If it holds, the case for a genuine C role strengthens.

2. **Short-term** (5-run pilot, new data, ~1 day): Execute pilot for P1 polydispersity experiment. Confirm that varying grain radius range at fixed friction produces measurable C shifts without changing mobility. If yes, proceed. If no, the decoupling strategy fails.

3. **Medium-term** (90-run ensemble, ~1 week): Full P1 experiment: 3 friction × 3 polydispersity levels × 10 replicates. If C shifts at fixed friction predict recovery differences, C has causal power. If recovery is unchanged when C varies but friction is fixed, C is a thermometer.

### Current highest-impact task

**Cross-validation** — because it tests part of the causal question with existing data, in zero time, with zero new simulations. If the interaction fails cross-validation, C's causal involvement is substantially weakened without running a single new grain.
