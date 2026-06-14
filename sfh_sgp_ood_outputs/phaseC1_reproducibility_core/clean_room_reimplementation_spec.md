# C1_04 — Clean-Room Reimplementation Spec
## Independent replication of SFH-SGP three-class geometry discovery

---

## Preamble

This document specifies every step needed to reproduce the SFH-SGP three-class transform geometry discovery. An independent implementer should be able to replicate all results using **only this document** — no reference to the original codebase.

The pipeline is deterministic given Python 3.9+, numpy, pandas, scikit-learn. No GPU needed. Total wall time ~20 minutes.

---

## 1. Dataset Generation

Generate 14 synthetic time series, each of length L = 512. All use `np.random.seed(42)` before generation.

### 1.1 Arithmetic Sequences

**primes**: First 512 prime numbers.
```
primes = []
candidate = 2
while len(primes) < 512:
    if is_prime(candidate):
        primes.append(candidate)
    candidate += 1
return array(primes, dtype=float)
```

**fibonacci**: Standard F₁=1, F₂=1 recurrence.
```
seq = [1.0, 1.0]
for _ in range(510):
    seq.append(seq[-1] + seq[-2])
return array(seq, dtype=float)
```

**modular_arithmetic**: `t mod 17` for t = 0..511.
```
return array([t % 17 for t in range(512)], dtype=float)
```

**additive_recurrence**: `x_{t+1} = 1.5·x_t + 0.3 (mod 1)` with x₀ = 0.
```
seq = [0.0]
for _ in range(511):
    seq.append((1.5 * seq[-1] + 0.3) % 1.0)
return array(seq, dtype=float)
```

### 1.2 Dynamical Systems

**lorenz**: Lorenz attractor x-component via forward Euler.
```
sigma=10, rho=28, beta=8/3, dt=0.02
x₀=y₀=z₀=1.0
for t in 0..511:
    dx = sigma·(y - x)
    dy = x·(rho - z) - y
    dz = x·y - beta·z
    x += dx·dt; y += dy·dt; z += dz·dt
    record x
return array of 512 points
```

**logistic_map**: Standard logistic with r=3.9, x₀=0.5.
```
seq = [0.5]
for _ in range(511):
    seq.append(3.9 * seq[-1] * (1 - seq[-1]))
return array(seq, dtype=float)
```

**henon_map**: Henon x-component with a=1.4, b=0.3, x₀=y₀=0.
```
x=y=0.0
for t in 0..511:
    xn = 1.0 - 1.4·x² + y
    yn = 0.3·x
    x, y = xn, yn
    record x
return array of 512 points
```

**ising_magnetization**: 2D Ising model, L=6 lattice, T=2.5, Metropolis, record mean magnetization at each step.
```
L=6, T=2.5, n_steps_per_point=5
spin = random.choice([-1,1], size=(L,L))
for t in 0..511:
    for _ in range(n_steps_per_point · L · L):
        pick random (i,j)
        dE = 2·spin[i,j]·(spin[i+1,j] + spin[i-1,j] + spin[i,j+1] + spin[i,j-1])
        if dE < 0 or random() < exp(-dE/T):
            flip spin[i,j]
    record mean(spin)
return array of 512 points
```

**reaction_diffusion**: Gray-Scott model, 16×16 grid, F=0.035, k=0.065, Du=0.16, Dv=0.08, dt=0.5. Record mean U every 5 steps.
```
L=16, seed square L/2±2 with U=0.5, V=0.25
for step in 0..(512·5):
    compute Laplacian via 5-point stencil
    dU = Du·∇²U - UV² + F·(1-U)
    dV = Dv·∇²V + UV² - (F+k)·V
    U += dU·dt; V += dV·dt
    if step % 5 == 0: record mean(U)
return array of 512 points
```

### 1.3 Symbolic Systems

**cfg_expansion**: Simulate CFG S→aSb|ab — track string length at each expansion.
```
seq = [1.0, 2.0]
while len(seq) < 512:
    seq.append(seq[-1] + 2.0)
return array(seq, dtype=float)
```

**lambda_reduction_trace**: Church numeral reduction — term size increases with Poisson noise.
```
sizes = [10.0]
for _ in range(1, 512):
    sizes.append(sizes[-1] + random.poisson(2)·0.5 + 0.5)
return array(sizes, dtype=float)
```

**rewrite_system**: L-system Fibonacci word — track sequence length at each step.
```
a=1.0, b=1.0
for _ in range(512):
    a, b = b, a + b
    record b
return array of 512 values
```

### 1.4 Random Controls

**iid_gaussian**: Standard normal N(0,1), 512 samples.
```
return np.random.randn(512)
```

**colored_noise**: 1/f pink noise via Voss-McCartney algorithm.
```
n=512, levels=floor(log2(n))+1
values = zeros(n)
for level in 0..levels:
    step = 2^level
    noise = randn(ceil(n/step))
    place at indices 0, step, 2·step, ...
    add to values
return values / sqrt(levels)
```

---

## 2. Transforms

Eight transforms applied to each generated signal. Each takes a 1D numpy array and returns a same-length array.

| Name | Operation |
|------|-----------|
| identity | `x.copy()` |
| reverse | `x[::-1]` |
| replay | `h=len(x)//2; concat(x[:h], x[:h])` |
| swap_halves | `h=len(x)//2; concat(x[h:], x[:h])` |
| scale | `x · 1.5` |
| clip | `clip(x, -0.5, 0.5)` |
| dropout | `mask = rand(len(x)) > 0.1; x · mask` |
| noise | `x + N(0, 0.1)` |

---

## 3. Canonical Metrics

Four deterministic metrics. Each takes a 1D array `x` and returns a float. All return 0.0 for L < 2 or NaN/Inf.

### M1 — Signed Ordinal Flow

```
dx = diff(x)          # x_{t+1} - x_t
d = sign(dx)          # ∈ {-1, 0, +1}
if len(d) < 2: return 0.0
return mean(d[:-1] · d[1:])
```
Range: [-1, +1]. +1 = perfectly monotonic, -1 = perfectly alternating, 0 = random sign.

### M2 — Half Correlation

```
h = len(x) // 2
if h < 2: return 0.0
first_half = x[:h], second_half = x[h:]
if std(first_half)==0 or std(second_half)==0: return 0.0
return corrcoef(first_half, second_half)[0,1]
```
Range: [-1, +1]. +1 = halves perfectly correlated, 0 = uncorrelated.

### M3 — Signed Compressibility

```
dx = diff(x)
s = sign(dx)          # ∈ {-1, 0, +1}
if len(s) == 0: return 0.0
runs = 1 + count(s[t] != s[t-1] for t=1..len(s)-1)
return 1.0 - 2.0 · runs / len(s)
```
Range: [-1, +1]. +1 = single run (perfectly compressible), -1 = maximally alternating.

### M4 — Amplitude Transition Asymmetry

```
K = 3                                 # FIXED
mn, mx = min(x), max(x)
if mx - mn < 1e-12: return 0.0
bins = linspace(mn, mx, K+1)
q = digitize(x, bins[1:-1])           # → 0..K-1
P = zeros((K, K))
for t in 0..len(x)-2:
    P[q[t], q[t+1]] += 1.0
P /= row_sums (set zero rows to 1.0)  # row-normalize
m4 = (1/K) · sum_i |P[i,i] - P[i, (i+1)%K] |
return m4
```
Range: [0, +1]. 0 = uniform mixing, 1 = maximal diagonal dominance.

**Canonical embedding:**
```
E(x) = [m1(x), m2(x), m3(x), m4(x)]^T ∈ ℝ⁴
```

---

## 4. Transform-Space PC1 Computation

For each system:

1. Draw n_samples = 50 independent signals from its generator (with `np.random.seed(42)` fixed globally)
2. For each signal `x`:
   - Compute `e_base = E(x)` (4-metric vector)
   - For each of the 8 transforms:
     - Compute `e_tf = E(tf(x))`
     - Compute displacement: `d = e_tf - e_base`
     - Append to list
3. Stack into matrix `X` of shape (400, 4) = 50 × 8 displacement vectors
4. Fit PCA (mean-centered, no scaling): `pca = PCA().fit(X)`
5. Record: `PC1 = explained_variance_ratio_[0]`

This yields `pc1_variance_transform_space` per system.

### Full-Ablation PC1

Same procedure but using a 3-metric embedding instead of 4:

- **no_m2**: `E'(x) = [m1(x), m3(x), m4(x)]` (omit m2)
- **no_m1**: `E'(x) = [m2(x), m3(x), m4(x)]` (omit m1)
- etc.

Record as `abl_no_m2_pc1`, `abl_no_m1_pc1`, etc.

**m2_contribution** = `full_PC1 - no_m2_PC1`

---

## 5. Feature Matrix

Build a 14×17 feature matrix. Columns:

| # | Feature | Source |
|---|---------|--------|
| 1 | pc1 | from step 4 |
| 2 | pc2 | from step 4 (2nd PC variance ratio) |
| 3 | effective_rank | exp(-Σ evr·log(evr+1e-12)) |
| 4 | tau_m1 | PC1 loading coefficient for m1 |
| 5 | tau_m2 | PC1 loading coefficient for m2 |
| 6 | tau_m3 | PC1 loading coefficient for m3 |
| 7 | tau_m4 | PC1 loading coefficient for m4 |
| 8 | temporal_corr | from null audit: corr(E(x), E(scramble(x))) |
| 9 | phase_corr | from null audit: corr(E(x), E(phase_rand(x))) |
| 10 | pc1_ratio | PC1_original / PC1_shuffled_metrics |
| 11 | replay_displacement | mean ||E(replay(x)) - E(x)|| |
| 12 | abl_full_pc1 | same as pc1 (for ablation consistency) |
| 13 | abl_no_m1_pc1 | PC1 without m1 |
| 14 | abl_no_m2_pc1 | PC1 without m2 |
| 15 | abl_no_m3_pc1 | PC1 without m3 |
| 16 | abl_no_m4_pc1 | PC1 without m4 |
| 17 | m2_contribution | full_PC1 - no_m2_PC1 |

Features 8-11 from null audit (see §6), features 12-17 from ablation (§4).

---

## 6. Null Audit

For each system, n_trials = 30:

### Temporal Scramble
```
x = gen()
e_base = E(x)
xs = random_permutation(x)     # destroy temporal order
e_scramble = E(xs)
corr = corrcoef(e_base, e_scramble)[0,1]
```
Record mean correlation across trials as `temporal_corr`.

### Phase Randomization
```
x = gen()
e_base = E(x)
Xf = rfft(x)
phase = exp(2j·π·rand(len(Xf)))
xp = irfft(Xf · phase, n=len(x))     # same power spectrum, random phases
e_phase = E(xp)
corr = corrcoef(e_base, e_phase)[0,1]
```
Record mean as `phase_corr`.

### Shuffled Metrics
```
displ_orig = []
displ_shuf = []
for _ in range(30):
    x = gen()
    e_base = E(x)
    for tf in transforms:
        e_tf = E(tf(x))
        displ_orig.append(e_tf - e_base)
        dx = (e_tf - e_base).copy()
        random_shuffle(dx)
        displ_shuf.append(dx)
pca_orig = PCA().fit(vstack(displ_orig))
pca_shuf = PCA().fit(vstack(displ_shuf))
```
`pc1_ratio = pca_orig.evr[0] / pca_shuf.evr[0]`

---

## 7. Clustering

### Algorithm
- Hierarchical clustering with Ward linkage
- Euclidean distance on the 17-feature matrix (z-score normalized)
- Cut dendrogram at height yielding 3 clusters (verified by silhouette maximum)

### Standard Interpretation
- Cluster 1 → Class 1: ordered/structural (primes, fibonacci, modular, cfg, lambda, rewrite)
- Cluster 2 → Class 2: interacting nonlinear (lorenz, ising, reaction_diffusion)
- Cluster 3 → Class 3: recurrent/m2-driven (additive_recurrence, logistic, henon, iid_gaussian, colored_noise)

### Silhouette Score
Compute on z-scored 17-feature matrix using Euclidean distance.

**Expected output**: silhouette ≈ 0.35.

---

## 8. Stability Tests

For each test, re-cluster on modified features and compute adjusted Rand index (ARI) vs original clustering.

| Test | Modification |
|------|-------------|
| remove_spectral | drop temporal_corr, phase_corr |
| remove_tau_axis | drop tau_m1..tau_m4 |
| remove_null_audit | drop temporal_corr, phase_corr, pc1_ratio |
| remove_replay | drop replay_displacement |
| remove_ablation | drop abl_* and m2_contribution |
| gaussian_noise_0.3 | add N(0, 0.3) to all features, 50 replicates |

---

## 9. Cross-Metric Transfer

- View 1: 4 tau-axis features only
- View 2: 6 ablation features only
- 5-fold cross-validation
- Classifier: RandomForest (n_estimators=100, all other defaults)
- Report: mean CV accuracy, per-class F1

---

## 10. Minimal Basis Search

Exhaustive search over all 1-feature, 2-feature, and 3-feature subsets of the 17 features.

For each subset:
- Cluster on those features only (Ward, same procedure as §7)
- Compute Rand index against full 17-feature clustering

**Expected result**: the 3-feature `{pc1, pc1_ratio, abl_no_m2_pc1}` perfectly recovers the full clustering.

---

## 11. Phase V: Order Parameter Validation

### 11.1 Perturbation Sensitivity (Logistic Map)

Scan logistic r from 3.5 to 4.0 in steps of ~0.02 (via np.arange(3.5, 4.0, 0.02)).

At each r value:
- Generate 512 points from logistic at that r
- Compute full PC1 and no_m2 PC1 (via 50-sample transform-space procedure in §4)
- Compute m2_contribution = full_PC1 - no_m2_PC1
- Compute derivative via central difference: d(contrib)/dr ≈ (contribution_{r+1} - contribution_{r-1}) / (2·step)

**Key verification**: max |d(contrib)/dr| ≈ 55, occurring near r=4.0.

### 11.2 Causal Metric Swaps

Take 3 reference systems: logistic (r=4.0), logistic (r=3.5), iid_gaussian.

For each pair (A, B):
- Extract actual m1,m3,m4 values from A, m2 value from B
- Combine into mixed metric vector
- Compute PC1 and m2_contribution
- Test: does swapping only m2 move A toward B's class?

**Test condition**: `m2_preserved_others_swapped` — preserve target's m2 while swapping m1,m3,m4 with source.

### 11.3 New Domain Classification

Generate 6 additional systems:

**ca_rule30**, **ca_rule110**, **ca_rule184**: Elementary 1D cellular automata, random initial condition, 512 steps, record center cell.

**goe_random_matrix**: Gaussian Orthogonal Ensemble, 100×100 matrix, record eigenvalue spacings after histogram bin.

**lfsr_crypto**: 16-bit LFSR with XOR feedback, 512 outputs.

**dfa_trace**: Deterministic finite automaton trace, random walk over 5-state DFA, 512 steps.

For each: compute full_PC1, no_m2_PC1, m2_contribution, temporal_corr. Classify via threshold: m2_contrib < -0.1 → Class 2, > 0.05 → Class 3, else → Class 1.

**Expected**: ca_rule184 → Class 2 (propagating interacting structure).

### 11.4 Order Parameter Reduction

Test four reduced coordinate sets:

| Condition | Features Used |
|-----------|--------------|
| m2_only | abl_no_m2_pc1 alone |
| m2_plus_pc1 | abl_no_m2_pc1, pc1 |
| m2_plus_tau | abl_no_m2_pc1, tau_m2 |
| non_m2 | all features EXCEPT abl_no_m2_pc1, m2_contribution |

For each: cluster → compute ARI vs full 17-feature clustering.

**Expected**: m2_only → ARI ≈ 0.07 (near random), m2_plus_pc1 → ARI ≈ 0.64 (best single pair), non_m2 → ARI ≈ 0.07 (structure collapses without m2 coordinate).

### 11.5 Critical Transition Scan (High Resolution)

Scan logistic r from 3.5 to 4.0 in steps of 0.0001 (10,000 points).

At each r:
- Generate x from logistic at that r
- Compute m2_contribution via 50-sample procedure
- Compute |d(contrib)/dr| via central difference

Locate peaks — these track the logistic map's periodic windows and band-merging bifurcations.

**Expected**: max derivative ≈ 55.

### 11.6 Adversarial Engineering

**noise+recurrence**: `x_t = (1-α)·noise_t + α·logistic(x_{t-1}, r=3.9)` for α ∈ {0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99}. Compute m2_contribution at each α. Test: can any α produce m2_contrib < -0.1 (Class 2-like)?

**Expected**: Class 2 (negative m2_contrib) cannot be fabricated by adding recurrence to noise.

**lorenz_phase_scrambled**: FFT Lorenz → randomize phases → IFFT. Compute m2_contrib.

**Expected**: m2_contrib remains negative (Class 2 preserved) — temporal chronology is not the discriminating signal.

### 11.7 Scale Stability

Test logistic (r=4.0, r=3.5) and iid_gaussian at signal lengths n ∈ {64, 128, 256, 512, 1024}.

Compute m2_mean and m2_coefficient_of_variation across non-overlapping windows (32-sample windows). Check whether m2 differences between systems persist at all scales.

---

## 12. Verification Targets

The following numeric checkpoints confirm correct reimplementation:

| Checkpoint | Expected Value | Tolerance |
|-----------|---------------|-----------|
| iid_gaussian full PC1 | 0.93 | ±0.02 |
| iid_gaussian no_m2 PC1 | 0.68 | ±0.02 |
| lorenz full PC1 | 0.51 | ±0.02 |
| lorenz no_m2 PC1 | 0.88 | ±0.02 |
| lorenz m2_contribution | -0.38 | ±0.03 |
| logistic (r=3.9) full PC1 | 0.88 | ±0.02 |
| logistic (r=3.9) m2_contribution | 0.19 | ±0.03 |
| silhouette score (17 features, 3 clusters) | 0.35 | ±0.03 |
| ARI: m2_plus_pc1 vs full | 0.64 | ±0.05 |
| ARI: m2_only vs full | 0.07 | ±0.03 |
| ARI: non_m2 vs full | 0.07 | ±0.03 |
| Max |d(m2_contrib)/dr| (logistic, r∈[3.5,4.0]) | 55 | ±5 |
| ARI vs categories (random/null baseline) | 0.27 | ±0.05 |

---

## 13. Required Output Schema

Replication script should produce a single validation report JSON:

```json
{
    "status": "PASS|FAIL",
    "pipeline_version": "clean_room_v1.0",
    "checkpoints": [
        {"name": "iid_gaussian_pc1", "expected": 0.93, "actual": 0.931, "pass": true},
        ...
    ],
    "clustering": {
        "n_clusters": 3,
        "silhouette": 0.35,
        "assignments": {"primes": 1, ..., "lorenz": 2, ..., "logistic_map": 3, ...}
    },
    "artifacts": {
        "transition_scan_max_derivative": 55.2
    }
}
```
