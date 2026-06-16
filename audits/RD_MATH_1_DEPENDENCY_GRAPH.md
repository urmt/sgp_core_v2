# RD-MATH.1 — Dependency Graph

**Date:** 2026-06-15  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Can these quantities be operationalized?"

---

## Variable Classification

### C (Coherence)

| Aspect | Classification | Evidence |
|--------|---------------|----------|
| Direct measurement | **No** | No metric scores C=5; best is C=4 (Effective Complexity) |
| Indirect measurement | **Yes** | C ≈ −MSE (r = −0.89) in granular domain; predictive compression; stability under perturbation |
| Latent | **Partially** | C is 80% reconstructable from MSE within granular domain; cross-domain transfer unknown |
| Requires observer assumptions | **Yes** | Definition of "coherent" requires a reference frame |
| Measurement domain | Granular systems, time series | Not validated outside granular domain |

**Dependency:** C depends on the choice of state space and the definition of "reconstruction." Different state spaces yield different C values.

---

### F (Fertility)

| Aspect | Classification | Evidence |
|--------|---------------|----------|
| Direct measurement | **No** | No metric scores F=5; best is F=4 (Empowerment) |
| Indirect measurement | **Yes** | Empowerment measures capacity for future states; Evolvability Index measures adaptive potential |
| Latent | **Partially** | F has 3 components (capacity, generativity, coherence); no metric captures all 3 |
| Requires observer assumptions | **Yes** | Definition of "fertile" requires a notion of "future states" |
| Measurement domain | Agent-based systems, evolutionary dynamics | Not validated for passive systems |

**Dependency:** F depends on the time horizon and the definition of "future states." Short horizons miss long-term fertility.

---

### I (Interaction)

| Aspect | Classification | Evidence |
|--------|---------------|----------|
| Direct measurement | **No** | No metric scores I=5; best is I=4 (Transfer Entropy) |
| Indirect measurement | **Yes** | Transfer Entropy measures directed information flow; Granger causality measures predictive influence |
| Latent | **Partially** | 66% of metrics score I≤1; ecology/evolutionary metrics measure components, not relational events |
| Requires observer assumptions | **Yes** | Definition of "interaction" requires a notion of "separate entities" |
| Measurement domain | Time series, network dynamics | Not validated for static structures |

**Dependency:** I depends on the definition of "entity" and the time scale of observation. Different definitions yield different I values.

---

### Ψ (Experience)

| Aspect | Classification | Evidence |
|--------|---------------|----------|
| Direct measurement | **No** | No metric scores Ψ=5; best is Ψ=4 (Empowerment, agent-relative) |
| Indirect measurement | **Partial** | All E≥4 metrics are agent-relative; no structure-intrinsic proxy exists |
| Latent | **Yes** | Ψ is defined as "experience" — no direct measurement possible without observer assumptions |
| Requires observer assumptions | **Yes** | Definition of "experience" requires a notion of "observer" |
| Measurement domain | Agent-based systems only | Not validated for non-agent systems |

**Dependency:** Ψ depends entirely on the definition of "observer" and "experience." Without these, Ψ is undefined.

---

## Dependency Graph

```
Ψ (experience)
├── requires: definition of observer
├── requires: definition of experience
└── depends on: I (interaction), F (fertility), C (coherence)

I (interaction)
├── requires: definition of entity
├── requires: time scale
└── measurable via: Transfer Entropy, Granger causality

F (fertility)
├── requires: time horizon
├── requires: definition of future states
└── measurable via: Empowerment, Evolvability Index

C (coherence)
├── requires: state space
├── requires: definition of reconstruction
└── measurable via: Effective Complexity, C ≈ −MSE
```

---

## Key Insight

**All four variables currently require observer assumptions.** None can be measured in a completely observer-independent way with current operationalizations.

This is not a failure. It is a structural feature:

> **The compass Ψ ≈ f(C, F, I) is not a physics equation. It is a framework for organizing measurements relative to an observer.**

The question is not "is Ψ real?" but "given a choice of observer, can C, F, I, and Ψ be operationalized?"

---

## Classification Summary

| Variable | Direct | Indirect | Latent | Requires Observer |
|----------|--------|----------|--------|-------------------|
| C | No | Yes | Partially | Yes |
| F | No | Yes | Partially | Yes |
| I | No | Yes | Partially | Yes |
| Ψ | No | Partial | Yes | Yes |

---

## Artifact

`/home/student/sgp_core_v2/audits/RD_MATH_1_DEPENDENCY_GRAPH.md`
