# RD-10B.3: Emergence-First Worlds — Report

## Status: PILOT RUN — Methodology validated, not results

---

## Design

**Standing rule applied:**
> Whenever a pattern appears, ask whether it belongs to the world, the representation, the detector, or the question.

**Protocol:**
1. Generate 50 worlds with NO motif vocabulary
2. Each world: 5-20 agents, 2-8 dimensions, random connectivity/coupling/decay/nonlinearity
3. Run 200 steps, record raw state at each step
4. After all runs: detect transitions in raw observables
5. Post-hoc: ask "what motifs appear?"

**Key difference from RD-10B pilot:**
- Worlds NOT built to exhibit motifs
- Motifs discovered AFTER observation
- Question does not select the answer

---

## Results

### Motif Detection: Every World Exhibits Every Motif

| Motif     | Frequency | Mean Strength | Std   |
|-----------|-----------|---------------|-------|
| binding   | 50/50     | 1.000         | 0.000 |
| hierarchy | 50/50     | 0.233         | 0.321 |
| recursion | 50/50     | 0.406         | 0.207 |
| template  | 50/50     | 0.788         | 0.233 |
| cycle     | 50/50     | 0.735         | 0.224 |

**Every motif appears in every world (100%).**

### What the Detectors Actually Measure

| Detector  | What it measures               | Why it's universal         |
|-----------|--------------------------------|----------------------------|
| binding   | pairwise correlation           | any coupled system has this |
| hierarchy | variance in variance           | any heterogeneous system   |
| recursion | autocorrelation                | any system with memory     |
| template  | self-similarity                | any stable system          |
| cycle     | dominant frequency             | any oscillating system     |

**These are time-series properties, not architectural motifs.**

### World Parameters vs Motif Strengths

| Parameter     | binding | hierarchy | recursion | template | cycle |
|---------------|---------|-----------|-----------|----------|-------|
| coupling      | 0.046   | 0.110     | -0.012    | -0.101   | -0.075|
| decay         | -0.096  | 0.356     | -0.552    | 0.285    | 0.133 |
| nonlinearity  | -0.140  | 0.058     | 0.125     | 0.005    | -0.028|

**Strongest effect:** decay → hierarchy (r=0.356), decay → recursion (r=-0.552)

### Transitions

- Mean transitions per world: 10,808
- Std: 1,996
- Nearly constant — the transition detector is also too sensitive

---

## Critical Finding

### The Post-Hoc Detectors Are Artifacts

The detectors measure **properties of the representation** (time series), not **properties of the world** (architecture).

This is exactly what the standing rule predicts:

> Patterns may belong to the world, the representation, the detector, or the question.

In this case:
- **World:** diverse dynamics (correct)
- **Representation:** time-series (correct)
- **Detector:** measures time-series properties (correct)
- **Question:** "what motifs appear?" selects for time-series properties (correct)

The detectors fail to distinguish world properties from representation properties.

### What Would Genuine Detection Require?

A genuine detector must be invariant to representation changes:

1. **Same world, different representation → same motifs**
2. **Different worlds, same representation → different motifs**

Current detectors fail test 1: they detect the same motifs regardless of world.

---

## Implications

### For RD-10B

The pilot run validated the methodology, not the results:

1. **Representation matters** — the same world described differently produces different motif measurements
2. **Detector matters** — current detectors measure time-series properties, not architecture
3. **Question matters** — "what motifs appear?" selects for time-series properties

### For the Program

The emergence-first approach is correct:

1. Generate worlds without motif vocabulary
2. Observe transitions
3. Post-hoc categorization

But the post-hoc detectors must be:

1. **Representation-invariant** — same motifs regardless of how the world is described
2. **World-sensitive** — different motifs for different architectures
3. **Testable** — positive and negative controls established before use

### The Standing Rule (Confirmed)

> Whenever a pattern appears, ask whether it belongs to the world, the representation, the detector, or the question.

In RD-10B.3, the patterns belong to the **representation** and the **detector**, not the world.

---

## Next Steps

1. **RD-10B.0 — Representation Audit:** Test whether the same world described as graph/lattice/dynamical system produces different motifs
2. **RD-10B.1 — Detector Audit:** Construct positive/negative controls, measure false-positive rates
3. **RD-10B.2 — Detector Independence:** Test if detector outputs are correlated by construction
4. **Redesign detectors** to be representation-invariant

---

## Files

- `audits/rd10b3_emergence_first.py` — experiment code
- `audits/rd10b3_results.json` — raw results
- `audits/rd10b3_discriminating_analysis.py` — analysis code
