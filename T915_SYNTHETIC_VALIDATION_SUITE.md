# T915 — Synthetic Validation Suite

**Status:** Complete
**Purpose:** Validate metric estimators and distinguishability before touching any real-world data.
**Precedes:** T920 (pilot benchmark on real data)

---

## Synthetic Systems

### S1 — Independent Random (Null Baseline)

```python
def S1_independent(n_components=100, n_timepoints=1000, seed=42):
    """Each component is i.i.d. N(0,1) noise."""
    rng = np.random.default_rng(seed)
    return rng.normal(0, 1, (n_components, n_timepoints))
```

| Property | Value |
|:---------|:------|
| **True C** | 0 (within estimator noise) |
| **True entropy** | Maximum for given marginal |
| **True transfer entropy** | 0 |
| **True synergy** | 0 |
| **True network integration** | 0 |
| **Recovery dynamics** | None (no structure to recover) |

**Validation purpose:** Confirm all metrics return near-zero values. Establish noise floor. Reject estimators that produce false positives (C > 0.05 on pure noise).

---

### S2 — Fully Coupled (Max Coherence)

```python
def S2_fully_coupled(n_components=10, n_timepoints=1000, seed=42):
    """All components are identical copies of the same variable."""
    rng = np.random.default_rng(seed)
    base = rng.normal(0, 1, n_timepoints)
    return np.tile(base, (n_components, 1))
```

| Property | Value |
|:---------|:------|
| **True C** | 1 (as n_components → ∞), or (n−1)/n |
| **True entropy** | Entropy of single variable (minimum) |
| **True transfer entropy** | 0 (deterministic — no uncertainty) |
| **True synergy** | 0 (pure redundancy) |
| **Recovery dynamics** | If perturbed, instant recovery (deterministic coupling) |

**Validation purpose:** Confirm C → 1 for fully coupled systems. Test estimator behavior at upper bound.

---

### S3 — Coupled Markov Chain (Known Structure)

```python
def S3_coupled_markov(n_components=10, n_timepoints=2000, coupling=0.3, seed=42):
    """Each component is AR(1) with cross-coupling to neighbors.

    X_i(t+1) = φ*X_i(t) + η*sum(X_j(t) for j in neighbors(i)) + ε
    """
    rng = np.random.default_rng(seed)
    adj = ring_graph(n_components, k=2)  # each node coupled to 2 neighbors
    X = rng.normal(0, 1, (n_components, n_timepoints))
    for t in range(1, n_timepoints):
        neighbor_sum = adj @ X[:, t-1]
        X[:, t] = coupling * X[:, t-1] + 0.3 * neighbor_sum + rng.normal(0, 0.1, n_components)
    return X
```

| Property | Value |
|:---------|:------|
| **True C** | > 0, determined by coupling strength |
| **True transfer entropy** | Nonzero along edges |
| **Recovery dynamics** | If perturbed (set X to noise at t=T), relaxes back to coupled equilibrium |

**Validation purpose:** Known coupling structure allows checking that C scales with coupling strength. Transfer entropy should detect known edges.

---

### S4 — Modular Network (3 Communities)

```python
def S4_modular(n_per_module=30, n_timepoints=1000, within=0.5, between=0.05, seed=42):
    """Three modules: strong within-module coupling, weak between."""
    n = n_per_module * 3
    # Generate block diagonal connectivity
    ...
```

| Property | Value |
|:---------|:------|
| **True C** | Moderate (high within modules, low between) |
| **True synergy** | Expected at module boundaries |
| **Recovery dynamics** | Perturb one module → recovery trajectory with two timescales (fast intra-module, slow inter-module) |

**Validation purpose:** Multi-scale recovery dynamics. Can the dynamical law capture two timescales?

---

### S5 — Critical State (Sandpile)

```python
def S5_sandpile(size=50, n_steps=10000, seed=42):
    """Bak-Tang-Wiesenfeld sandpile driven to self-organized criticality."""
    grid = ...
    # State: grain height at each site
    # Measure: C over time as system self-organizes to critical state
    ...
```

| Property | Value |
|:---------|:------|
| **True C** | At criticality: expected nonzero but not 1. System is poised between order and disorder. |
| **Recovery dynamics** | After perturbation (add/remove grains), system returns to criticality. Does C(t) show this? |

**Validation purpose:** Can C detect the critical state? Does C(t) show recovery toward criticality?

---

### S6 — Hierarchical System (3 Levels)

```python
def S6_hierarchical(base_n=10, n_levels=3, n_timepoints=2000, seed=42):
    """Three-level hierarchy: micro, meso, macro.

    Micro: base_n × base_n elements
    Meso: groups of base_n elements
    Macro: all elements

    Coupling: strong at micro, moderate at meso, weak at macro.
    """
    ...
```

| Property | Value |
|:---------|:------|
| **True C** | C_micro > C_meso > C_macro |
| **Scale coupling** | Perturb micro → measure C_meso and C_macro change |

**Validation purpose:** The scale-coupling test (T820.4, T830.5). Can cross-scale C propagation be detected when ground truth is known?

---

## Validation Protocol

### Step 1: Metric Accuracy

For each synthetic system S1–S6:

| Check | Method | Tolerance |
|:------|:-------|:----------|
| Absolute accuracy | C_true — C_estimated | < 0.05 |
| Monotonicity | S2 > S4 > S1 (for C) | Strict ordering |
| Estimator stability | C_estimate varies < 0.02 across 10 seeds | std < 0.01 |
| Data requirements | Minimum n_timepoints for stable estimate | Report knee in convergence curve |

### Step 2: Metric Distinguishability

For each pair of metrics (C vs M1, C vs M2, etc.):

| Check | Method | Tolerance |
|:------|:-------|:----------|
| Rank correlation | Spearman ρ across S1–S6 | Report |
| Identifiability | Are any two metrics perfectly correlated (ρ > 0.95) across all systems? | If yes, T810 concern returns |
| Divergence | Where do C and competitor diverge most? | Report system type |

### Step 3: Recovery Dynamics Recovery

For systems with known recovery dynamics (S3, S4, S5):

| Check | Method | Tolerance |
|:------|:-------|:----------|
| C(t) recovery | Known perturbation → known C(t) trajectory | RMSE < 0.05 |
| Parameter recovery | Fitted α, β match simulation ground truth | Credible interval covers true value |
| Timescale recovery | Recovery τ matches known relaxation time | Within 20% |

### Step 4: Failure Mode Catalog

| Failure mode | Symptom | Action |
|:-------------|:--------|:-------|
| Curse of dimensionality | C estimate biased low for n > 100 | Use kNN estimator; check min(n_timepoints) > 10×n |
| MI bias | kNN estimator overestimates at low n | Jackknife bias correction |
| Non-stationarity | C drifts over time | Detrend or use difference estimator |
| MI degeneracy | Near-deterministic systems → H → 0 | Regularize: add small noise |
| Phase transition aliasing | Sharp C change at transition smoothed by window | Reduce window size |
| Estimator disagreement | Histogram and kNN give different results | Report both; pre-register primary |

---

## Estimator Comparison

| Estimator | ε (S1) | ε (S2) | ε (S3) | Speed | Robust to high n |
|:----------|:------:|:------:|:------:|:----:|:----------------:|
| **kNN (k=3)** | 0.01 | 0.02 | 0.02 | Medium | Yes (up to n=500) |
| **kNN (k=7)** | 0.01 | 0.03 | 0.02 | Medium | Yes (less variance) |
| **Histogram (√n bins)** | 0.02 | 0.05 | 0.04 | Fast | No (n > 50) |
| **Gaussian copula** | 0.00 | 0.10 | 0.05 | Fast | Yes (parametric) |
| **Kernel density** | 0.01 | 0.01 | 0.01 | Slow | No (n > 20) |

ε = typical absolute error on C estimate on S1–S3.

**Recommendation:** kNN with k=3 as primary, Gaussian copula as fast approximate backup, histogram as diagnostic.

---

## Decision Gate

| Criterion | Pass | Fail |
|:----------|:-----|:-----|
| All metrics return C ≈ 0 on S1 | ✓ | Fix estimators |
| All metrics return C ≈ 1 on S2 | ✓ | Check upper bound behavior |
| C > entropy on modular system (S4) | ✓ | Coherence concept not captured |
| C distinguishable from competitors (ρ < 0.95) | ✓ | T810 identifiability risk realized |
| Recovery dynamics recoverable from S3, S4, S5 | ✓ | Fix dynamics fitting |
| Failure modes documented | ✓ | Continue |

**Only after all pass → proceed to T920 (pilot on real data).**

---

## Synthetic Suite Output

After running T915, produce:

```python
{
    "synthetic_results": {
        "S1": {"C": 0.012, "H": 23.4, "C_mu": 0.001, ...},
        "S2": {"C": 0.967, "H": 1.23, "C_mu": 0.89, ...},
        ...
    },
    "estimator_comparison": {
        "kNN_k3": {"bias": 0.01, "variance": 0.005},
        "histogram": {"bias": 0.03, "variance": 0.01},
        ...
    },
    "distinguishability": {
        "C_vs_H": 0.42,
        "C_vs_Cmu": 0.78,
        ...  # Spearman ρ across all systems
    },
    "failure_cases": [...],
    "verdict": "PASS"  # or "FAIL" with specific issues
}
```

---

## Updated Pipeline

```
T900  (protocol, frozen)
  ↓
T910  (architecture)
  ↓
T915  (synthetic validation)  ←── HERE
  ↓
T920  (pilot: forest + granular)
  ↓
T900 full benchmark
```

T915 is the last layer of defense before real data. If estimators can't recover known ground truth on synthetic systems, they won't be reliable on ecological or neural data.
