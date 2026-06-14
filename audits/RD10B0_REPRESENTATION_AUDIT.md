# RD-10B.0: Representation Audit — Report

## Status: COMPLETE

---

## Standing Rule Applied

> **When a pattern appears, does it belong to:**
> **the world, the representation, the detector, the question, or the observer?**

---

## Design

1. Generate ONE world (no motif vocabulary)
2. Represent it in 5 ways:
   - **Graph** (adjacency matrix from agent correlations)
   - **Time series** (state trajectories per agent)
   - **State-transition network** (discretized state transitions)
   - **Correlation** (dimension-level correlation matrix)
   - **Phase-space** (embedding in 3D)
3. Apply SAME detectors to each representation
4. Ask: what survives representation changes?

---

## Results (10 worlds × 5 representations)

### Motif Presence Across Representations

| Motif    | Present In | Verdict                    |
|----------|------------|----------------------------|
| network  | 2/5        | HIGHLY REPR-DEPENDENT      |
| binding  | 3/5        | HIGHLY REPR-DEPENDENT      |
| template | 1/5        | MODERATELY REPR-DEPENDENT  |
| recursion| 3/5        | WEAKLY REPR-DEPENDENT      |
| cycle    | 2/5        | WEAKLY REPR-DEPENDENT      |
| hierarchy| 2/5        | WEAKLY REPR-DEPENDENT      |

### Quantitative Representation Dependence

| Motif    | CV     | Range  | Interpretation            |
|----------|--------|--------|---------------------------|
| network  | 1.297  | 16.47  | Changes drastically       |
| binding  | 1.013  | 1.82   | Changes drastically       |
| template | 0.503  | —      | Changes significantly     |
| recursion| 0.474  | 0.63   | Changes moderately        |
| cycle    | 0.450  | 0.71   | Changes moderately        |
| hierarchy| 0.438  | 0.40   | Changes moderately        |

---

## Critical Finding

### The Same World, Represented Differently, Produces Different Motifs

This is the first experiment that directly tests representation dependence.

**Result: Representation matters more than the world for most motifs.**

- **network**: CV=1.297 — appears in graph and state-transition, but values differ by 100x
- **binding**: CV=1.013 — appears in 3 representations, but values differ by 30x
- **template**: only detected in time-series representation
- **recursion, cycle, hierarchy**: weakly representation-dependent (CV ~0.4-0.5)

### What This Means

The earlier RD-10B.3 finding (every motif appears in every world) was an artifact of using only time-series representation.

When the same world is represented differently:
1. Different motifs appear
2. Same motifs have different values
3. Some motifs disappear entirely

**Motifs are not properties of the world.**
**Motifs are properties of the world-representation pair.**

---

## The Standing Rule (Confirmed)

> **When a pattern appears, does it belong to:**
> **the world, the representation, the detector, the question, or the observer?**

RD-10B.0 shows that patterns belong to the **representation**, not just the world.

---

## Implications

### For RD-10B

1. **Detector validation is representation-dependent** — calibrating detectors on one representation does not guarantee they work on another
2. **Motif independence is representation-dependent** — correlations between motifs may change across representations
3. **The emergence-first approach must specify the representation** — "what motifs appear?" is meaningless without specifying "in what representation?"

### For the Program

The representation is not a neutral lens. It actively shapes what patterns appear.

This is deeper than detector dependence:
- Detector dependence: the instrument affects the measurement
- Representation dependence: the language affects what can be measured

### The Deeper Lesson

> **Architectural claims are representation-dependent until proven otherwise.**

This is the strongest methodological finding from RD-10B so far.

---

## Next Steps

1. **RD-10B.1 — Detector Audit**: Test detectors across representations
2. **RD-10B.2 — Detector Independence**: Test if detector correlations are representation-dependent
3. **Search for representation-invariant properties**: What, if anything, survives all representations?

---

## Files

- `audits/rd10b0_representation_audit.py` — single-world experiment
- `audits/rd10b0_multi_world.py` — multi-world experiment
- `audits/rd10b0_results.json` — single-world results
- `audits/RD10B0_REPRESENTATION_AUDIT.md` — this report
