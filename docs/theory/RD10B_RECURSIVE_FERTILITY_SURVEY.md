# RD-10B: Recursive Fertility Survey

**Status**: DESIGN COMPLETE — ready for execution  
**Date**: 2026-06-10  
**Depends on**: RD-10A (stability taxonomy)

---

## Goal

Test whether recursive fertility varies across classes of mathematical systems. Build "toy universes" with different rule classes and measure their capacity for compositional stability.

## Background

The RFH predicts that recursive fertility is not uniformly distributed across mathematical systems. Some rule classes should produce many levels of compositional stability; others should produce few or none. The survey maps this variation.

## Method: Rule-Class Survey

### Rule Classes (Toy Universes)

Each "universe" is a class of mathematical systems with a specific rule type:

| # | Rule Class | Description | Expected Fertility |
|---|-----------|-------------|-------------------|
| 1 | **Cellular Automata** | Discrete grid, local update rules | Variable (depends on rule) |
| 2 | **Coupled Map Lattices** | Continuous state, discrete time, local coupling | Moderate |
| 3 | **Coupled Oscillators** | Continuous time, phase coupling (Kuramoto-type) | Low-moderate |
| 4 | **Reaction-Diffusion** | Continuous space-time, chemical kinetics | High (Turing patterns, self-replication) |
| 5 | **Graph Rewriting** | Discrete graphs, rule-based transformation | High (compositional by construction) |
| 6 | **Boolean Networks** | Binary states, logical update rules | Variable |
| 7 | **Lotka-Volterra Systems** | Predator-prey dynamics, continuous time | Low (limited composition) |
| 8 | **Cellular Automata + Memory** | CA with history-dependent rules | Unknown |

### Measurements Per Universe

For each rule class, generate many instances (different parameters, different rules within the class) and measure:

#### Level 0: Rule Properties
- Symmetry count (number of conserved quantities)
- State space dimensionality
- Nonlinearity measure
- Sensitivity to initial conditions (Lyapunov exponent)

#### Level 1: Stable Object Count
- Run the system from random initial conditions
- Count distinct stable attractors (fixed points, limit cycles, quasi-periodic)
- Classify attractors by type
- Measure attractor basin sizes

#### Level 2: Persistence
- Introduce perturbations to stable objects
- Measure recovery rate
- Measure probability of maintaining identity after perturbation

#### Level 3: Combinability
- Place two stable objects in the same space
- Measure whether they:
  - (a) Destroy each other
  - (b) Coexist without interaction
  - (c) Merge into a new stable object
  - (d) Create a composite with new properties
- Count the number of distinct composites

#### Level 4: Hierarchy Depth
- Starting from Level 1 objects, attempt to build Level 2 composites
- From Level 2 composites, attempt Level 3
- Measure maximum depth achieved
- Measure number of distinct objects at each level

#### Level 5: Capability Threshold Counting (THE KEY MEASUREMENT)

**This is the most important measurement.** Not state count. Not expansion ratio. But: how many structural innovations create new capability classes?

For each compositional level, ask:
- Does this level have capabilities absent from the level below?
- Is the new capability structurally necessary (can't be approximated by scale)?
- Does this represent a genuine threshold crossing?

Count the number of threshold crossings. This is F_cap.

### The Fertility Coefficient (Revised)

**The original F (state count) is wrong.** A crystal has millions of stable states and zero fertility.

**The correct F_cap measures threshold crossings**: how many structural innovations create new capability classes.

Define:

**F_cap = number of structural innovations that create new capability classes**

- F_cap = 0: no capability expansion (stable objects exist but don't enable new classes)
- F_cap = 1: one threshold crossing (one new capability class emerges)
- F_cap > 1: recursive fertility (multiple levels of capability expansion)

Additionally:

**D_cap = depth of capability hierarchy** (how many levels of qualitatively new capabilities exist)

**R_cap = rate of capability expansion** (how quickly new capability classes emerge per compositional level)

For a system to be **recursively fertile**, we need F_cap > 1 AND D_cap > 1.

For a system to be **deeply fertile** (capable of open-ended organization), we need F_cap >> 1 AND D_cap >> 1 AND R_cap > 1.

### Experimental Design

For each rule class:
1. Generate 100 random instances (different parameters/rules)
2. For each instance, measure Levels 0-5
3. Compute F for each instance
4. Compare F distributions across rule classes

### Expected Outcomes

| Prediction | If RFH is correct |
|------------|-------------------|
| F_cap varies across rule classes | Some classes have F_cap >> 0, others F_cap = 0 |
| F_cap correlates with composability | Systems with more composable parts have higher F_cap |
| F_cap is rare | Most rule classes have low F_cap |
| F_cap is not random | F_cap is determined by structural properties of the rules |
| F_cap ≠ F_s | State count and capability threshold count are not identical |

### Falsification Criteria

| Criterion | How to test |
|-----------|-------------|
| F_cap is meaningless | F_cap does not correlate with any measured property of the system |
| F_cap is uniform | All rule classes have approximately the same F_cap |
| F_cap is random | F_cap is determined by noise, not rule structure |
| F_cap is just F_s | F_cap correlates perfectly with state count (then we're back to counting states) |
| Capability transitions are scale | New capabilities at level N can be approximated by scale at level N-1 |
| Hierarchy depth is artifactual | Depth increases with system size without saturation |

## Expected Output

1. F distribution for each of 8 rule classes
2. Correlation between F and rule properties (symmetry, nonlinearity, etc.)
3. Identification of which rule classes have highest F
4. A "fertility landscape" — what structural properties predict F

## Relationship to RD-10A

RD-10A provides the theoretical stability taxonomy. RD-10B tests whether that taxonomy predicts actual fertility across different mathematical systems.

If RD-10A says "topological protection creates Level 1 stability," RD-10B tests whether rule classes with topological protection actually produce more Level 1 objects.
