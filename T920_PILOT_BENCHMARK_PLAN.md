# T920 — Pilot Benchmark Plan

**Status:** Complete
**Purpose:** First empirical test before committing to full 10-dataset benchmark. Two pilots — one predictive, one non-predictive — to ground-truth the metric engine and recovery-dynamics framework.

---

## Pilot A — Forest Succession (Predictive System)

### Dataset

| Field | Value |
|:------|:------|
| **System** | Temperate forest dynamics (tree species abundance) |
| **Source** | Cedar Creek Ecosystem Science Reserve LTER |
| **Dataset** | Tree species abundance per 0.1-ha plot, 1983–2023 (annual census) |
| **Components** | n = 15–35 tree species per plot |
| **Timepoints** | 40 annual censuses |
| **Perturbation** | 1988 drought (natural experiment) + subsequent succession |
| **Prediction type** | Does C predict which plots recover faster? |

### Why This System

- **Real data** — publicly available, well-studied, 40-year record
- **Natural perturbation** — drought creates a recovery trajectory
- **Non-neural** — active inference has no obvious purchase (trees don't have generative models)
- **Multiple plots** — 24 plots allow cross-validation
- **Ecological succession is well-understood** — competing models exist (neutral theory, niche theory, Markov models)

### Protocol

```
1. Load 24 tree plots × 40 years
2. For each plot, compute C(t) annually using sliding window
3. Identify drought perturbation (1988)
4. Fit recovery trajectory C(t) 1988–2023 to all models:
   a. Coherence model dC/dt = αγC(1-C) - βC
   b. Entropy model dC/dt = -βC
   c. Null AR(1)
5. Compare models via WAIC, LOO-CV
6. Does C predict species richness recovery rate?
7. Does C outperform:
   - Shannon entropy?
   - Species richness (standard metric)?
   - Network integration (species co-occurrence graph)?
```

### Success Criteria

| Criterion | Threshold |
|:----------|:----------|
| C(t) relaxation observed | C_eq > C_post-perturbation with CI not overlapping zero |
| Coherence model WAIC | Lower than entropy model (ΔWAIC > 5) |
| C predicts recovery | Correlation between C(t) slope and species richness recovery |
| C beats richness | C predicts recovery better than species richness alone |
| C beats network | C predicts recovery better than network integration |

### Go/No-Go for Full Benchmark

| Outcome | Decision |
|:--------|:---------|
| Pilot A succeeds on ≥4/5 criteria | Proceed to Pilot B |
| Pilot A succeeds on 2–3/5 criteria | Proceed to Pilot B with caution |
| Pilot A succeeds on <2/5 criteria | Investigate: metric issue, data issue, or coherence hypothesis failing? |
| Pilot A shows C*reduces* after perturbation (opposite direction) | Coherence hypothesis may be falsified early |

---

## Pilot B — Granular Relaxation (Non-Predictive System)

### Dataset

| Field | Value |
|:------|:------|
| **System** | 3D granular packing under vibration |
| **Source** | Simulated (LAMMPS discrete element method) or published experimental data (e.g., Jaeger/Nagel lab) |
| **Observable** | Grain positions (x,y,z) per grain |
| **Components** | n = 1000 grains |
| **Timepoints** | 2000 time steps post-perturbation |
| **Perturbation** | Remove 10% of grains at t=500; monitor reorganization |
| **Prediction type** | Does C(t) relax toward pre-perturbation value? |

### Why This System

- **No generative model** — grains don't predict, don't minimize free energy, don't learn
- **Pure physics** — coherence hypothesis makes a nontrivial claim about physical self-organization
- **If C restores here, active inference cannot explain it** — strongest early discriminator
- **Granular relaxation is well-studied** — known results exist for comparison

### Protocol

```
1. Generate granular packing: 1000 grains, random initial positions
2. Settle under gravity → measure baseline C
3. Remove 10% of grains (random selection)
4. Monitor C(t) for 1500 additional time steps
5. Fit recovery trajectory C(t) to:
   a. Coherence model dC/dt = αγC(1-C) - βC
   b. Pure decay model dC/dt = -βC
   c. Null AR(1)
6. Compare models via WAIC
7. Does C restoration occur?
8. Does C beat entropy and network metrics?
```

### Success Criteria

| Criterion | Threshold |
|:----------|:----------|
| C restoration observed | C(t) increases significantly (p < 0.01) after perturbation |
| C_eq consistent | Asymptotic C matches pre-perturbation baseline within CI |
| Coherence model WAIC | Lower than decay model (ΔWAIC > 5) |
| C beats entropy | C better predicts recovery trajectory than entropy alone |
| Timescale separation | C autocorrelation time ≥ 5× grain autocorrelation time |

### Go/No-Go for Full Benchmark

| Outcome | Decision |
|:--------|:---------|
| Pilot B succeeds on ≥4/5 criteria | Strong signal. Proceed to full 10-dataset benchmark. |
| Pilot B succeeds on 2–3/5 criteria | Moderate signal. Proceed but with lowered expectations. |
| Pilot B fails (<2/5) | **Active inference cannot explain this failure.** Coherence hypothesis weakened or falsified at the physical level. |
| Pilot B shows no C restoration | Non-predictive systems don't restore C → coherence principle is at best domain-restricted. |

---

## Cross-Pilot Analysis

### What the Pair Tests

| If Pilot A succeeds and Pilot B succeeds | Coherence hypothesis gains strong early support across predictive and non-predictive domains |
|:------------------------------------------|:----------------------------------------------------------------------------------------------|
| Pilot A succeeds, Pilot B fails | Coherence is domain-restricted to adaptive/predictive systems — redundant with active inference |
| Pilot A fails, Pilot B succeeds | Unlikely but interesting — coherence works in physics but not ecology |
| Both fail | Early falsification of coherence hypothesis. Program ends here. |

### Timing

| Phase | Duration |
|:------|:---------|
| Build WP1 (metric engine) | 4 weeks |
| Build WP2 (dataset adapters for 2 systems) | 2 weeks |
| Acquire Pilot A data | 1 week |
| Generate Pilot B data | 1 week |
| Run Pilot A analysis | 2 weeks |
| Run Pilot B analysis | 2 weeks |
| Cross-pilot analysis | 1 week |
| **Total** | **13 weeks (3 months)** |

### Deliverables

| Output | Format |
|:-------|:-------|
| Pilot A report | Markdown + figures |
| Pilot B report | Markdown + figures |
| Cross-pilot comparison | Markdown |
| Metric engine (validated) | Python package |
| Go/No-Go recommendation | Decision memo |

---

## Updated File Tree After T920

```
benchmark/
├── metrics/               # WP1
├── adapters/              # WP2
│   ├── base.py
│   ├── ecosystem.py       # Pilot A
│   └── granular.py        # Pilot B
├── dynamics/              # WP3 (partial — only 2 systems)
├── pilots/
│   ├── T920_PILOT_A_REPORT.md
│   └── T920_PILOT_B_REPORT.md
├── requirements.txt
└── README.md
```

---

## Decision Rules Summary

| Scenario | Next step |
|:---------|:----------|
| Both pilots succeed | Full T900 benchmark (remaining 8 datasets) |
| Pilot A only | C is domain-restricted to adaptive systems. Run PS1-PS3 only. Publish domain-restricted result. |
| Pilot B only | Unlikely but publish as interesting physical systems result. |
| Neither pilot | Publish null result. Coherence hypothesis falsified. Program ends. |
