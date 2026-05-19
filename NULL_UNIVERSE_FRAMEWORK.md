# NULL UNIVERSE FRAMEWORK — SGP-CORE V2

**Date:** 2025-05-13  
**Status:** FOUNDATIONAL

---

## Purpose

Build adversarial test suite to determine what FALSE organization looks like.

Every positive finding must be tested against null models that:
1. Preserve superficial similarity
2. Destroy genuine structure
3. Reveal what metrics actually measure

---

## Null Model Taxonomy

### 1. Random Clouds (Type I)

**What it destroys:** All structure

```
Input: Any dataset
Operation: Shuffle all elements randomly
Preserves: Marginal distributions
```

**Expected:** No inflection point, flat D(k), no model advantage

**Used for:** Baseline comparison

---

### 2. Shuffled Topology (Type II)

**What it destroys:** Neighbor relationships

```
Input: Data + neighbor graph
Operation: Randomize neighbor assignments
Preserves: Local point positions, total edges
```

**Expected:** k0 unchanged but structure removed

**Used for:** Topology specificity

---

### 3. Fake Clusters (Type III)

**What it destroys:** True clustering

```
Input: Clustered data
Operation: Move points between clusters randomly
Preserves: Number of clusters, cluster sizes
```

**Expected:** D(k) similar but spurious structure

**Used for:** Clustering specificity

---

### 4. Deceptive Dimension (Type IV)

**What it destroys:** True dimensionality

```
Input: High-dimensional data
Operation: Project to random subspace + noise
Preserves: Same N, same nominal D
```

**Expected:** Flat or misleading D(k)

**Used for:** Dimensionality specificity

---

### 5. Phase Transition Imposters (Type V)

**What it destroys:** Real phase behavior

```
Input: Continuous data
Operation: Add random time-dependent noise
Preserves: Marginal distribution
```

**Expected:** Artificial "transition" at random k

**Used for:** Phase detection specificity

---

### 6. High-D Random Persistence (Type VI)

**What it creates:** False persistence

```
Input: Random data
Operation: Add smooth low-freq component
Preserves: Appears "structured"
```

**Expected:** Spurious k0, misleading model fit

**Used for:** Persistence specificity

---

### 7. Correlated Noise (Type VII)

**What it creates:** Correlated randomness

```
Input: Uncorrelated noise
Operation: Add covariance structure
Preserves: Noise properties
```

**Expected:** Artificial coherence

**Used for:** Correlation specificity

---

### 8. Topology-Destroyed (Type VIII)

**What it destroys:** Graph structure

```
Input: Network/graph data
Operation: Random edge rewiring
Preserves: Same degree distribution
```

**Expected:** Connectivity unchanged but structure lost

**Used for:** Network analysis specificity

---

## Comparison Framework

For any positive finding:

| Null Type | Comparison | What It Proves |
|----------|------------|---------------|
| Type I | vs random | General structure |
| Type II | vs topology shuffle | Topology specificity |
| Type III | vs fake clusters | Clustering specificity |
| Type IV | vs random projection | Dimensionality specificity |
| Type V | vs noise injection | Transition specificity |
| Type VI | vs smooth random | Persistence specificity |
| Type VII | vs uncorrelated | Correlation specificity |
| Type VIII | vs rewired network | Network specificity |

---

## Null Metrics

| Metric | Null Value | Signal Value | Discrimination |
|--------|------------|---------------|----------------|
| R²_sigmoid | ~0.3-0.5 | >0.9 | HIGH |
| k0_defined | undefined | in range | HIGH |
| Null ΔR² | 0 | >0.5 | HIGH |
| Model_rank | random | sigmoid | HIGH |
| Effect_size | ~0 | >0.5σ | HIGH |

---

## Implementation

### Null Generator Interface

```python
class NullModel:
    def __init__(self, data, params):
        self.data = data
        self.params = params
    
    def generate(self):
        """Return null version of data"""
        pass
    
    def compare_metrics(self, original, null):
        """Return discrimination metrics"""
        pass
```

### Required Null Comparisons

Every experiment MUST report:
1. Null model type used
2. Null performance (R², k0, etc.)
3. Effect size (signal - null)
4. Statistical significance
5. Direction (is signal higher or lower?)

---

## Falsification Tests

### If Null Performs Well, That Indicates:

| Null Result | Interpretation |
|------------|----------------|
| Random R² > 0.8 | Metrics too sensitive |
| Shuffle preserves k0 | k0 measures local density |
| Fake clusters fit | Clustering non-specific |
| Random projection works | D(k) is data-independent |

**These results INVALIDATE findings - must recalibrate metrics**

---

## Null Universe Execution

All positive claims require:

```
positive_result → test against ≥3 null types → pass if signal > null
```

No claim passes without null comparison.

---

## Status

**FRAMEWORK SPECIFIED**  
Next: Implementation in null_models/ directory