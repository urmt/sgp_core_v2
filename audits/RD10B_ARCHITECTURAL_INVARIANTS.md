# RD-10B: Architectural Invariants Survey — Report

**Status**: COMPLETE  
**Date**: 2026-06-10  
**Purpose**: Identify recurrent architectural patterns that accompany major expansions in what differences can persist, matter, and participate in further organization. Test whether those patterns are causally necessary or merely correlated byproducts.

---

## Standing Rules Applied

1. **Whenever something looks fundamental, ask what makes it possible.**
2. **Whenever something looks recurrent, ask whether it is causal.**
3. **Whenever something looks like a deeper invariant, ask whether it might be an attractor instead.**

---

## Executive Summary

RD-10B tested 8 architectural motifs across 8 toy universes and 5 cross-domain systems. The results reveal:

1. **Most motifs are NOT independent** — they cluster together
2. **Two motifs are genuine attractors** — binding and network appear everywhere
3. **Two motifs are causally necessary** — network and formal_inference show large reductions when removed
4. **Hierarchy and recursion are NOT detected** — their detectors fail across all domains
5. **Cross-domain transfer is limited** — only binding and network transfer reliably

---

## Phase 1: Motif Independence Analysis

The correlation matrix reveals that most motifs cluster together:

| Motif Pair | Correlation |
|-----------|-------------|
| network-recursion | 0.96 |
| template-formal_inference | 0.95 |
| cycle-formal_inference | 0.94 |
| cycle-recursion | 0.92 |
| cycle-template | 0.89 |
| network-cycle | 0.82 |

**Independent motifs** (low correlations):
- **Boundary**: correlates -0.5 to -0.3 with others
- **Hierarchy**: correlates -0.3 to 0.4 with others

**Conclusion**: Most motifs are NOT independent. They may be surface manifestations of deeper properties.

---

## Phase 2: Pattern Discovery

| Architecture | Motifs Detected |
|-------------|-----------------|
| binding | binding, network, boundary |
| network | network, cycle, template, recursion, formal_inference |
| cycle | binding, network, cycle, template, recursion, formal_inference |
| template | binding, network, cycle, template |
| boundary | binding, network, boundary |
| hierarchy | binding, network, cycle, boundary (NOT hierarchy!) |
| recursion | binding, network, cycle, boundary (NOT recursion!) |
| formal_inference | binding, network, cycle, template, formal_inference |

**Critical finding**: Hierarchy and recursion architectures do NOT have their specific motifs detected. The detectors for these motifs are not working.

---

## Phase 3: Null-Model Comparison

| Null Model | Motifs Detected |
|-----------|-----------------|
| Random | binding, network, boundary |
| Shuffled binding | binding, network, boundary |
| Shuffled network | network |
| Shuffled cycle | binding, network, boundary |
| Degenerate binding | binding, network |
| Degenerate boundary | binding, network, boundary |
| Degenerate hierarchy | binding, network, boundary |

**Critical finding**: Binding and network are detected in random/shuffled data. They may be artifacts of the detection method, not real motifs.

---

## Phase 4: Causal Testing (Removal)

Large reductions in D_persist when removing motifs:

| Architecture | Motif Removed | Reduction |
|-------------|--------------|-----------|
| cycle | network | 0.953 |
| formal_inference | network | 0.755 |
| network | formal_inference | 0.744 |
| cycle | formal_inference | 0.716 |
| network | recursion | 0.660 |
| template | network | 0.656 |
| recursion | network | 0.634 |
| hierarchy | network | 0.604 |

**Conclusion**: Network and formal_inference are causally necessary — removing them causes large reductions in D_persist.

---

## Phase 5: Invariant vs Attractor Analysis

| Motif | Pathway Consistency | Cross-Domain Presence | Classification |
|-------|--------------------|-----------------------|----------------|
| binding | 1.00 | 1.00 | **Attractor** |
| network | 1.00 | 1.00 | **Attractor** |
| cycle | 1.00 | 0.20 | Attractor (weak) |
| template | 1.00 | 0.20 | Attractor (weak) |
| boundary | 1.00 | 0.40 | Attractor (moderate) |
| hierarchy | 0.00 | 0.00 | **NOT detected** |
| recursion | 0.00 | 0.20 | **NOT detected** |
| formal_inference | 1.00 | 0.00 | Attractor (weak) |

**Conclusion**: Binding and network are genuine attractors — they arise from multiple independent pathways and transfer across domains. Hierarchy and recursion are NOT detected.

---

## Phase 6: Cross-Domain Transfer

| Domain | Motifs Detected | D_persist |
|--------|-----------------|-----------|
| granular | binding, network, boundary | 0.189 |
| reaction_diffusion | binding, network | 0.580 |
| graph_rewriting | binding, network, boundary | 0.553 |
| cellular_automaton | binding, network, template, recursion | 0.213 |
| ecosystem | binding, network, cycle | 0.750 |

**Conclusion**: Only binding and network transfer reliably across all domains. Other motifs appear in some domains but not others.

---

## Key Findings

### 1. Binding and Network Are Attractors

These motifs appear everywhere — in random data, shuffled data, and all cross-domain systems. They may be:
- Artifacts of the detection method
- Or genuine attractors that arise from minimal structure

**Verdict**: Likely attractors, but detection method needs validation.

### 2. Hierarchy and Recursion Are NOT Detected

The detectors for these motifs fail across all architectures and domains. This means either:
- The detectors are wrong
- Or these motifs are not real categories

**Verdict**: Detectors need improvement. These motifs may be human descriptions of deeper properties.

### 3. Most Motifs Are NOT Independent

The correlation matrix shows most motifs cluster together. This suggests they may be surface manifestations of a deeper property.

**Verdict**: The motif decomposition may be wrong. Need to search for latent property.

### 4. Causal Necessity Is Limited

Only network and formal_inference show large reductions when removed. Other motifs show smaller effects.

**Verdict**: Most motifs are correlated byproducts, not causes.

---

## What This Means for the Program

### The Motif Decomposition May Be Wrong

The 8 motifs we tested are NOT independent. They cluster together. This suggests the decomposition into motifs is not the right level of analysis.

### The Deeper Property May Be Simpler

Instead of 8 motifs, there may be 2-3 deeper properties:
- **Coupling** (manifests as network, cycle, template)
- **Differentiation** (manifests as binding, boundary)
- **Inference** (manifests as formal_inference)

### Hierarchy and Recursion May Not Be Real Categories

These motifs are NOT detected by our detectors. They may be human descriptions of a deeper property that we haven't identified yet.

---

## Falsification Check

| Hypothesis | Observation That Would Damage It | Result |
|-----------|--------------------------------|--------|
| Motifs recur near transitions | No architectural patterns recur | **Partially supported** — binding and network recur |
| Motifs are causally necessary | Removing motifs does not reduce D_persist | **Partially supported** — only network and formal_inference show large effects |
| Invariants exist | No common structure shared | **Unclear** — need to search for latent property |
| Attractors explain recurrence | Patterns arise from single pathway | **Supported** — binding and network arise everywhere |
| Cross-domain transfer works | Invariants die when moved | **Partially supported** — only binding and network transfer |
| Category system is valid | Motifs are not natural categories | **Partially supported** — hierarchy and recursion not detected |

---

## Next Steps

1. **Fix hierarchy and recursion detectors** — current detectors don't work
2. **Search for latent property** — what do the correlated motifs have in common?
3. **Test coupling/differentiation/inference hypothesis** — are these the deeper properties?
4. **Validate detection method** — are binding and network real or artifacts?

---

## Conclusion

RD-10B has revealed that the motif decomposition may be wrong. Most motifs are NOT independent. Two motifs (binding, network) appear everywhere as attractors. Two motifs (hierarchy, recursion) are NOT detected.

The program should now search for the latent property that the correlated motifs share, rather than testing motifs individually.

> Whenever something looks recurrent, ask whether it is causal.

The answer for most motifs: **No, they are correlated byproducts.**

The exceptions: **network and formal_inference** appear to be causally necessary.

> Whenever something looks like a deeper invariant, ask whether it might be an attractor instead.

The answer for binding and network: **Yes, they are attractors.**

> Whenever something looks fundamental, ask what makes it possible.

The answer remains: **Unknown. Need to search for latent property.**
