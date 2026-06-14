# C1_01 — Canonical Metric Specification (Frozen V2_079)
## Status: FROZEN | Formula Version: v1.0 | Freeze Date: 2026-05-27

---

## General Conventions

All metrics operate on a discrete time-series signal `x ∈ ℝ^L` with `L ≥ 2`.
Metrics are deterministic functions of `x` alone (no state, no random seed).
If `L < 2`, all metrics return 0.0.
If computation produces NaN or Inf, return 0.0.

---

## M1 — Signed Ordinal Flow

### Formula
```
dx_t = x_{t+1} - x_t
d_t  = sign(dx_t) ∈ {-1, 0, +1}
m1   = (1/(L-2)) * Σ_{t=1}^{L-2} d_t · d_{t+1}
```

### Range
`[-1, +1]`
- +1: all changes same direction (perfectly monotonic)
- -1: perfectly alternating
-  0: no persistence (random sign)

### Expected Range
`[-1.0, 1.0]` — verified 0 failures across all systems and transforms.

### Parameters
None.

### Edge Cases
- `L < 3`: return 0.0 (no adjacent sign products possible)
- Constant signal (all dx=0): d_t = 0 for all t, product = 0, m1 = 0.0

### Invariance
- Invariant under scaling: `m1(a·x) = m1(x)` for `a > 0` (sign is scale-invariant)
- Invariant under translation: `m1(x + c) = m1(x)`
- NOT invariant under monotonic transformation (changes sign pattern)

### Failure Modes
- Zero-signal-difference domination: if most `d_t = 0`, the mean product approaches 0 regardless of structure
- Oscillatory signals with period 2 alternate perfectly producing m1 ≈ -0.33

---

## M2 — Half Correlation

### Formula
```
h   = floor(L/2)
x1  = x[0:h]     (first half)
x2  = x[h:L]     (second half)
m2  = Cov(x1, x2) / sqrt(Var(x1) · Var(x2))
```

Implemented as `np.corrcoef(x1, x2)[0, 1]`.

### Range
`[-1, +1]`
- +1: first and second halves perfectly correlated (persistent structure)
- -1: halves perfectly anti-correlated
-  0: halves uncorrelated (structure changes between halves)

### Expected Range
`[-1.0, 1.0]` — verified 0 failures.

### Parameters
None (L fixed per experiment).

### Edge Cases
- `h < 2`: return 0.0 (insufficient data for correlation)
- `std(x1) == 0` or `std(x2) == 0`: return 0.0 (constant segment inflates correlation)
- Periodic signals: period-2 signal with L=1024 gives m2 ≈ 1.0 (both halves identical)
- Logistic at r=4.0 with L=512: m2 ≈ 0.0 (halves uncorrelated in chaos)
- Logistic at r=3.5 with L=512: m2 ≈ 1.0 (period-4 produces identical halves)

### Invariance
- Invariant under scaling: `m2(a·x) = m2(x)` (correlation is scale-invariant)
- NOT invariant under time reversal: reversing changes which data points are in which half
- NOT invariant under swap (by definition — swap exchanges halves)

### Known Failure Modes
1. **DUPLICATE_STATE_COLLAPSE**: If signal contains duplicate blocks (e.g., replay outputs, sine wave with period dividing L/2), halves can be perfectly correlated spuriously.
2. **PERIODIC_DEGENERACY**: Periodic signals with period dividing L/2 produce m2=1.0 regardless of organizational complexity.
3. **CONSTANT_SEGMENT_ARTIFACT**: If first half is constant, m2 defaults to 0.0 even if second half is structured.

---

## M3 — Signed Compressibility

### Formula
```
dx_t  = x_{t+1} - x_t
s_t   = sign(dx_t) ∈ {-1, 0, +1}
runs  = 1 + count of transitions in s (i.e., locations where s_t ≠ s_{t-1})
m3    = 1 - (2 · runs / L)
```

### Range
`[-1, +1]`
- +1: perfectly compressible (single run, e.g., monotonic signal)
-  0: random sign pattern
- -1: maximally incompressible (perfectly alternating)

### Expected Range
`[-1.0, 1.0]` — verified 0 failures.

### Parameters
None.

### Edge Cases
- `L < 2`: return 0.0 (cannot compute sign of difference)
- Constant signal (all dx=0): s = [0,...,0], runs=1, m3 = 1 - 2/L ≈ 0.996 (for L=512)
- Alternating signal: runs ≈ L-1, m3 ≈ 1 - 2(L-1)/L ≈ -1.0

### Invariance
- Invariant under scaling: `m3(a·x) = m3(x)`
- Invariant under monotonic transformation (preserves sign pattern)

### Known Failure Modes
1. **ZERO_DIFFERENCE_DOMINATION**: If most dx=0 (quantized/discrete signals), runs count underestimates complexity.
2. **SHORT_SIGNAL_BIAS**: m3 approaches 1-2/L for any non-alternating short signal, inflating compressibility.

---

## M4 — Amplitude Transition Asymmetry

### Formula
```
K    = 3 (fixed)
mins = min(x), maxs = max(x)
if maxs - mins < 1e-12: return 0.0
bins = linspace(mins, maxs, K+1)
q_t  = digitize(x_t, bins[1:-1])    →  0, 1, ..., K-1

P = zeros(K, K)
for t in 0..L-2:
    P[q_t, q_{t+1}] += 1.0
row_sums = sum(P, axis=1)
row_sums[row_sums == 0] = 1.0
P = P / row_sums              (row-normalized transition matrix)

m4 = (1/K) * Σ_i |P[i,i] - P[i, (i+1) mod K]|
```

### Range
`[0, 1]`
- 0: uniform mixing (all transitions equally likely)
- 1: maximal diagonal dominance (each state persists)

### Expected Range
`[0.0, 1.0]` — verified 0 failures.

### Parameters
- `K = 3` (fixed; not tuned per system)
- Quantization method: equal-width bins
- Row normalization: zero rows replaced with uniform to avoid division by zero

### Edge Cases
- `L < 2`: return 0.0
- Constant signal: all q_t identical, P[i,i]=1.0 for one row, m4 = 1/3 = 0.333
- Alternating between two quanta: m4 depends on bin assignment

### Known Failure Modes
1. **EQUAL-WIDTH QUANTIZATION ARTIFACT**: If signal is concentrated in one bin (e.g., near-constant), all transitions collapse to single state, producing m4 = 0.333 regardless of signal complexity.
2. **FIXED_K_SENSITIVITY**: K=3 is coarse; some signals may be under-resolved. K was fixed in V2_079 and is NOT tunable.
3. **ROW_NORMALIZATION_ARTIFACT**: Low-population states get unreliable transition estimates. This is mitigated by zero-row default but can inflate m4 for sparse regimes.

---

## TRIVIAL 1D METRIC ARTIFACT

**WARNING**: ANY single metric considered alone produces PC1 = 1.0 in transform space.
This is a mathematical identity: a 1D metric value varies along one dimension, so PCA on a 1D space trivially produces 100% variance on PC1.

This does NOT indicate structure. It is a preprocessing invariant.

Detection rule: if `metric_set_size == 1` and `PC1 ≈ 1.0`, flag as TRIVIAL.

---

## Metric Summary Table

| Metric | Symbol | Range | Estimate | O(L) | Key Parameter |
|--------|--------|-------|----------|------|---------------|
| Signed Ordinal Flow | m1 | [-1, +1] | mean interior product | Yes | None |
| Half Correlation | m2 | [-1, +1] | Pearson corr of halves | Yes | None |
| Signed Compressibility | m3 | [-1, +1] | 1 - 2·runs/L | Yes | None |
| Amp Transition Asymmetry | m4 | [0, +1] | Transition matrix diag dom | Yes | K=3 |

All metrics are O(L). All are deterministic. All have known singularity conditions documented above.

---

## Distinction: Signal vs Artifact vs Degeneracy

**REAL GEOMETRIC SIGNAL**: Effect survives null controls (temporal scramble, phase randomize, shuffled metrics). Differential m2 behavior (adds dimensionality for Lorenz, decreases for noise) is the strongest signal.

**DISTRIBUTIONAL ARTIFACT**: High PC1 that persists under shuffled metrics or phase randomization. IID Gaussian with PC1=0.93 under original metrics is partially distributional (drops to 0.68 when m2 removed).

**ESTIMATOR DEGENERACY**: When metric computation returns default value due to edge case (e.g., constant segment in half correlation). Classified as `duplicate_state_collapse` or `degenerate_dimension`.

**TRIVIAL MATHEMATICAL IDENTITY**: Single-metric PC1 = 1.0. Always true. No information.

---

## Canonical Embedding

```
E(x) = [m1(x), m2(x), m3(x), m4(x)]^T ∈ ℝ⁴
```

This is the FROZEN canonical embedding. No alternative metric sets are canonical.
