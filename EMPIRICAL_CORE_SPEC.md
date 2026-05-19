# EMPIRICAL CORE SPEC — SGP-CORE V2

**Date:** 2025-05-13  
**Status:** FOUNDATIONAL SPEC

---

## Objective

Build minimal validated pipeline using ONLY synthetic data to verify infrastructure before adding real systems.

Goal: Validate ALL infrastructure before adding neuroscience/transformer/physics domains.

---

## Core Systems (No Neuroscience)

### A. Random Clouds

**Purpose:** Baseline - what does no-organization look like?

```python
# Structure: N x D random Gaussian
# Parameters: N ∈ [100, 10000], D ∈ [10, 1000]
```

**Expected properties:**
- Flat D(k) (dimension = local dimension)
- No inflection point (k0 undefined or >> range)
- No model fit advantage
- Random structure in null comparison

**Test:** Must fail to show any invariant scaling

---

### B. Hierarchical Systems

**Purpose:** Multi-scale structure with known nested organization

```python
# Structure: Nested clusters at multiple scales
# Parameters: depth ∈ [2,5], branching ∈ [2,10]
```

**Expected properties:**
- Multi-phase D(k) (multiple inflections)
- Scale-specific k0 values
- Clear model advantage vs random
- Predictable structure

**Test:** Should show multiple scaling regimes

---

### C. Sparse Systems

**Purpose:** Low-connectivity structure

```python
# Structure: Random graph with p ∈ [0.01, 0.1]
# Parameters: N, p, average_degree
```

**Expected properties:**
- D(k) dependent on connectivity
- k0 shifts with average degree
- Threshold behavior at percolation

**Test:** k0 correlates with connectivity

---

### D. Dynamical Systems

**Purpose:** Time-evolving organization

```python
# Types: 
# - limit_cycle (oscillators)
# - fixed_point (attractors)
# - chaos (lorenz, rossler)
# - coupled (kuramoto variants)
```

**Expected properties:**
- Temporal stability of D(k)
- Transition detection capability
- Attractor persistence measurement

**Test:** Track D(k) evolution over time

---

### E. Transformer Embeddings

**Purpose:** Test on real artificial system embeddings

```python
# Source: Pre-trained transformers (small)
# Layers: Extract from multiple depths
```

**Expected properties:**
- Layer-wise k0 variation (from prior work)
- Sigmoid scaling confirmed
- Architecture-specific signatures

**Test:** Reproduce prior findings with V2 infrastructure

---

## Pipeline Validation

### Quick Validation Run (PHASE A)

Each system runs with:
- N ≤ 1000
- k-range: 10-100
- Trials: 10
- Time: < 30 seconds

Must pass:
1. No runtime errors
2. D(k) computed successfully
3. Model fitting converges
4. Null comparison runs
5. Output metadata generated

### Full Execution (PHASE B)

After PHASE A passes:
- N ≤ 10000
- k-range: 10-500
- Trials: 100
- Full null comparison

---

## Metrics Required

| Metric | Computation | Purpose |
|--------|-------------|---------|
| D(k) | Participation ratio | Dimensionality profile |
| k0 | Sigmoid inflection | Scale invariant |
| A | Sigmoid amplitude | Capacity |
| β | Sigmoid rate | Growth speed |
| R² | Model fit quality | Structure presence |
| AIC/BIC | Model selection | Parsimony |
| Null Δ | Signal - Null | Effect size |
| Bootstrap CV | Stability | Reliability |

---

## Null Model Requirements

For each system, compare against:

1. **Random baseline** - Same N, D, shuffle data
2. **Topology destroy** - Randomize neighbor structure
3. **Covariance scramble** - Preserve eigenvalues, randomize structure

---

## Test Conditions

### Must PASS for Infrastructure Valid

| Test | Pass Condition |
|------|-----------------|
| Random system | No advantage over null |
| Hierarchical | Multi-regime D(k) |
| Sparse | k0 responds to connectivity |
| Dynamical | Temporal stability measured |
| Transformer | Layer progression detected |

### Must FAIL for Falsification

| Test | Fail Condition |
|------|----------------|
| Random shows structure | ⚠️ False positive risk |
| All systems identical | ⚠️ No domain sensitivity |
| Null model passes | ⚠️ Insensitive metrics |

---

## Implementation Status

| Component | Status |
|-----------|--------|
| Directory structure | ✅ Created |
| Pipeline scaffold | ✅ Defined |
| Null models | ✅ Specified |
| Validation framework | ✅ Defined |
| Metric definitions | ✅ Specified |

**Next: Begin pipeline implementation**

---

## Priority

1. Random cloud system → Infrastructure test
2. Hierarchical system → Multi-scale test
3. Null comparison → Validation test
4. Transformer embeddings → Reproduce prior findings

Only after these pass: Add neuroscience/physics/ecology domains