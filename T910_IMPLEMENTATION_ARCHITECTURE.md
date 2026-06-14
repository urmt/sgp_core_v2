# T910 — Implementation Architecture

**Status:** Complete
**Precedes:** T920 (pilot benchmark), then full T900 execution
**Language:** Python 3.11+
**Dependencies:** NumPy, SciPy, scikit-learn, PyStan/CmdStanPy, JAX (optional for speed)

---

## WP1 — Metric Engine

### 1.1 Common Interface

```python
@dataclass
class MetricResult:
    metric_name: str
    value: float
    confidence_interval: tuple[float, float] | None
    estimation_method: str
    parameters: dict[str, Any]
    time_series: np.ndarray | None  # C(t) if applicable

class BaseMetric(ABC):
    @abstractmethod
    def compute(self, data: np.ndarray, **kwargs) -> MetricResult:
        ...
```

`data` is always shape `(n_components, n_timepoints)` — domain-agnostic.

### 1.2 Metric Implementations

| Metric | Class | Method | Reference |
|:-------|:------|:-------|:----------|
| **Normalized total correlation (C)** | `TotalCorrelation` | kNN MI (k=3), histogram backup | Kraskov et al. 2004 |
| **Shannon entropy** | `ShannonEntropy` | Plugin estimator, Miller-Madow bias correction | Shannon 1948 |
| **LMC complexity** | `LMCComplexity` | H × disequilibrium | López-Ruiz et al. 1995 |
| **Statistical complexity** | `StatisticalComplexity` | C_μ via CSSR or Betti | Crutchfield & Young 1989 |
| **Transfer entropy** | `TransferEntropy` | kNN estimator, shuffling for significance | Schreiber 2000 |
| **Multiscale entropy** | `MultiscaleEntropy` | Coarse-grained H at τ = [1..20] | Costa et al. 2002 |
| **Network integration** | `NetworkIntegration` | Global efficiency on correlation graph | Latora & Marchiori 2001 |
| **Synergy (PID)** | `SynergyMeasure` | I_∩ via Brody or Ince estimator | Ince 2017 |
| **Integrated info (approx)** | `PhiApprox` | Φ* via geometric partitioning | Oizumi et al. 2016 |

### 1.3 Core Implementation: TotalCorrelation

```python
class TotalCorrelation(BaseMetric):
    def __init__(self, estimator: str = "knn", k: int = 3):
        self.estimator = estimator
        self.k = k

    def compute(self, data: np.ndarray) -> MetricResult:
        # data: (n_components, n_timepoints)
        n, t = data.shape
        # Estimate joint entropy H(X_1...X_n) per timepoint
        H_joint = self._estimate_entropy(data, across="components")
        # Estimate marginal entropies H(X_i)
        H_marginals = np.array([self._estimate_entropy(data[i:i+1]) for i in range(n)])
        # Total correlation
        T = np.sum(H_marginals) - H_joint * n  # H_joint is per-timestep average
        # Wait — need to be more careful. 
        # C = T / H_joint where both are computed per timepoint then averaged.
        ...
```

*See `metrics/` directory for complete implementation.*

**Validation protocol:** Compute C on known distributions:
- Independence: C ≈ 0 (n i.i.d. Gaussians)
- Perfect correlation: C ≈ 1 (n copies of same variable)
- Intermediate: known XOR structure

**Acceptance criterion:** |C_true − C_estimated| < 0.05 for all validation cases.

### 1.4 Output Schema

```python
@dataclass
class MetricResult:
    metric_name: str
    value: float | np.ndarray  # scalar or time series
    confidence_interval: tuple[float, float] | None
    estimation_method: str
    parameters: dict[str, Any]
    metadata: dict[str, Any]  # estimator version, runtime, warnings
```

---

## WP2 — Dataset Adapters

### 2.1 Common Interface

```python
@dataclass
class SystemDataset:
    name: str
    states: np.ndarray          # (n_components, n_timepoints)
    timepoints: np.ndarray      # (n_timepoints,) — time axis
    metadata: dict[str, Any]    # domain, perturbation info, system type
    partition: list[list[int]] | None  # component grouping for hierarchical C
```

### 2.2 Adapter Implementations

| Adapter | Source | States | Components | Notes |
|:--------|:-------|:-------|:-----------|:------|
| `SandpileAdapter` | Simulation | Grain heights (100×100 grid, flattened) | 10,000 | Generate on demand, seed-controlled |
| `ReactionDiffusionAdapter` | Simulation | Concentration (50×50 grid, flattened) | 2,500 | FitzHugh-Nagumo kinetics |
| `EcosystemAdapter` | Cedar Creek LTER | Species abundance per plot | 20–80 | Real data, drought perturbation |
| `MicrobiomeAdapter` | HMP / Dethlefsen 2011 | OTU abundance | >100 | Antibiotic perturbation |
| `NeuralCultureAdapter` | CRCNS | Spike trains | 60 | Chemical perturbation |
| `fMRIConnectivityAdapter` | HCP S1200 | BOLD time series (ROIs) | 100 | Sleep/awake perturbation |
| `SocialNetworkAdapter` | Pushshift/Reddit | User interaction counts | Varies | API policy shock |
| `GranularAdapter` | Simulation (LAMMPS) | Grain positions | 1,000 | Removal perturbation |

### 2.3 Adapter Contract

```python
class DatasetAdapter(ABC):
    @abstractmethod
    def load(self) -> SystemDataset:
        ...

    @abstractmethod
    def perturbed_segments(self) -> list[tuple[int, int]]:
        """Return (start, end) indices of perturbation windows."""
        ...

    @abstractmethod
    def baseline_segments(self) -> list[tuple[int, int]]:
        """Return (start, end) indices of baseline windows."""
        ...
```

### 2.4 Simulated Dataset Generators

For cases where real data is unavailable or insufficient:

```python
class SandpileGenerator:
    """Bak-Tang-Wiesenfeld sandpile on n×n grid."""

    def __init__(self, size: int = 100, seed: int = 42):
        self.size = size
        self.rng = np.random.default_rng(seed)

    def run(self, n_steps: int = 10000, perturb_at: int | None = 5000) -> SystemDataset:
        # Returns states at regular intervals
        ...
```

---

## WP3 — Recovery-Dynamics Framework

### 3.1 C(t) Estimation Pipeline

```python
class RecoveryAnalyzer:
    def __init__(self, metric: BaseMetric):
        self.metric = metric

    def estimate_trajectory(self, dataset: SystemDataset,
                            window: int = 50, stride: int = 10) -> np.ndarray:
        """Compute C(t) using sliding window over timepoints."""
        n_timepoints = dataset.states.shape[1]
        timepoints = np.arange(0, n_timepoints - window, stride)
        C_t = np.zeros(len(timepoints))
        for i, t in enumerate(timepoints):
            window_data = dataset.states[:, t:t+window]
            C_t[i] = self.metric.compute(window_data).value
        return C_t
```

### 3.2 Dynamical Model Fitting

```python
class DynamicalModel(ABC):
    @abstractmethod
    def fit(self, C_t: np.ndarray, t: np.ndarray,
            connectivity: float | None = None) -> dict[str, Any]:
        ...

    @abstractmethod
    def predict(self, C_0: float, t: np.ndarray) -> np.ndarray:
        ...

    @abstractmethod
    def waic(self) -> float:
        ...
```

**Models to fit:**

| Model | Equation | Free params | Nested in coherence? |
|:------|:---------|:-----------:|:--------------------:|
| **Coherence (SFH)** | dC/dt = αγC(1−C) − βC | α, β, σ² | — |
| **Active inference surrogate** | dC/dt = −k(C − C*) | k, C*, σ² | Yes (at equilibrium) |
| **Entropy model** | dC/dt = −βC | β, σ² | Yes (α=0 limit) |
| **Null AR(1)** | C_t = φ·C_{t−1} + ε | φ, σ² | No |

### 3.3 Model Comparison

```python
class ModelComparison:
    def __init__(self, models: dict[str, DynamicalModel]):
        self.models = models

    def summary(self) -> pd.DataFrame:
        """Return table with R², RMSE, WAIC, LOO-CV, BF for each model."""
        ...

    def best_model(self) -> str:
        """Return name of model with lowest WAIC."""
        ...

    def bayes_factor(self, model_a: str, model_b: str) -> float:
        """Return BF_{AB}."""
        ...
```

---

## WP4 — Hierarchical Bayesian Model

### 4.1 Stan Model Structure

```stan
data {
  int<lower=1> N_datasets;
  int<lower=1> N_obs[N_datasets];        // timepoints per dataset
  vector[N_datasets] gamma;               // connectivity per dataset
  array[N_datasets] vector[N_obs] C_obs;  // observed C(t)
  array[N_datasets] vector[N_obs] t;      // time
  int<lower=1, upper=2> domain[N_datasets]; // domain ID (predictive vs non)
}

parameters {
  real<lower=0> alpha;           // global coherence drive
  real<lower=0> beta;            // global entropy decay
  vector[2] domain_offset_a;     // domain-level offset for alpha
  vector[N_datasets] ds_offset_a; // dataset-level offset for alpha
  real<lower=0> sigma_domain_a;  // variance of domain offsets
  real<lower=0> sigma_ds_a;      // variance of dataset offsets
  real<lower=0> sigma_obs;       // observation noise
}

model {
  // Priors
  alpha ~ cauchy(0, 1);
  beta ~ cauchy(0, 1);
  domain_offset_a ~ normal(0, sigma_domain_a);
  ds_offset_a ~ normal(0, sigma_ds_a);
  sigma_obs ~ exponential(1);

  // Likelihood
  for (d in 1:N_datasets) {
    real a_eff = alpha + domain_offset_a[domain[d]] + ds_offset_a[d];
    real C_eq = fmax(1 - beta / (a_eff * gamma[d]), 0);
    real tau = 1 / fmax(a_eff * (2*C_eq - 1) * gamma[d] - beta, 1e-6);

    for (j in 2:N_obs[d]) {
      real C_pred = C_eq + (C_obs[d, j-1] - C_eq) * exp(-(t[d, j] - t[d, j-1]) / tau);
      C_obs[d, j] ~ normal(C_pred, sigma_obs);
    }
  }
}
```

### 4.2 Critical Test (A6)

```python
def test_a6(posterior: StanFit) -> dict[str, Any]:
    """Test whether alpha, beta generalize across domains.

    Returns:
        - domain_offset_sd: posterior of sigma_domain_a
        - significant: bool (is 95% HDI of sigma_domain_a > 0.1?)
        - verdict: "A6 supported" if offsets negligible, else "A6 weakened"
    """
    hdi = az.hdi(posterior["sigma_domain_a"])
    significant = hdi[0] > 0.1  # offset > 0.1 is practically meaningful
    return {
        "hdi": hdi,
        "significant": significant,
        "verdict": "A6 weakened/falsified" if significant else "A6 supported"
    }
```

### 4.3 Hypothesis Testing

| Hypothesis | Test | Decision rule |
|:-----------|:-----|:--------------|
| H1 (cross-domain C works) | sigma_domain_a ≈ 0 | HDI includes 0 or < 0.1 |
| H2 (C beats competitors) | WAIC_coherence < WAIC_competitor | ΔWAIC > 5 on ≥3 datasets |
| H2 (C beats active inference) | BF > 10 on non-predictive systems | WAIC on NP1-NP5 only |

---

## WP5 — Reproducibility

### 5.1 Run Record

Every execution produces a JSON record:

```json
{
    "run_id": "a1b2c3d4",
    "timestamp": "2026-06-04T14:30:00Z",
    "git_commit": "abc123def456",
    "data_hash": "sha256:...",
    "metric_engine_version": "0.1.0",
    "estimator_parameters": {"k": 3, "normalization": "zscore"},
    "random_seed": 42,
    "results": { ... }
}
```

### 5.2 File Structure

```
benchmark/
├── metrics/               # WP1: metric implementations
│   ├── base.py
│   ├── total_correlation.py
│   ├── statistical_complexity.py
│   ├── transfer_entropy.py
│   └── ...
├── adapters/              # WP2: dataset adapters
│   ├── base.py
│   ├── sandpile.py
│   ├── ecosystem.py
│   ├── neural.py
│   └── ...
├── dynamics/              # WP3: recovery-dynamics framework
│   ├── analyzer.py
│   ├── models.py
│   └── comparison.py
├── models/                # WP4: Stan models
│   └── hierarchical.stan
├── reproducibility/       # WP5: run tracking
│   ├── run_record.py
│   └── runs/
├── pilots/                # T920 pilot runs
├── tests/                 # Unit tests for all metrics
├── requirements.txt
└── README.md
```

### 5.3 Testing Requirements

| Test type | Coverage | CI? |
|:----------|:--------:|:---:|
| Metric validation (known distributions) | 100% of metrics | Yes |
| Adapter integration (loads data, correct shape) | 100% of adapters | Yes |
| Model fitting (recovers known params) | All model types | Yes |
| Reproducibility (same seed → same result) | All metrics | Yes |

---

## Dependency Graph

```
WP1 (Metric Engine)
    ↑
WP2 (Dataset Adapters)  ←── T920 pilot datasets
    ↑
WP3 (Recovery Dynamics)
    ↑
WP4 (Hierarchical Model)  ←── T900 pre-registered
    ↑
WP5 (Reproducibility)  ────  T900 protocol
```

**Execution order:** WP1 → WP2 → (T920 pilot) → WP3 → WP4 → Full benchmark.

---

## Decision Gates

| Gate | Check | Fail action |
|:-----|:------|:------------|
| WP1 validation | All metrics pass known-distribution tests (|error| < 0.05) | Fix estimators |
| WP2 integration | All adapters return correct SystemDataset | Fix adapters |
| T920 pilot | C restoration observed in both systems? | No: adjust estimators or protocol |
| T920 pilot | C beats competitors? | No: report as null result |
| Full benchmark | See T900 success criteria | Report outcome |
