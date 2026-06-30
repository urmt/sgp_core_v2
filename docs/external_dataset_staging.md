# External Dataset Staging — Phase 005A Division 5

**Purpose:** Apply controlled falsification pressure to the dual-framework architecture
using datasets external to the canonical system suite.

---

## 1. Falsification Strategy

The dual-framework makes five empirically vulnerable claims. Each must be testable
against external data without ad-hoc parameter adjustment.

| Claim | Formulation | Primary Falsifier |
|-------|-------------|-------------------|
| C1 | Timescale-dependency: TRACK B dominates short timescales, TRACK A dominates long timescales | A system where TRACK A dominates at short timescale OR TRACK B dominates at long timescale |
| C2 | Representational hysteresis exceeds functional hysteresis | A system where functional hysteresis ≥ representational hysteresis |
| C3 | Dissociation: representational recovery and functional recovery are separable | A system where representational recovery = functional recovery with high precision |
| C4 | Precursor detectability is system-dependent, not universal | A system with abrupt transitions AND no detectable precursors |
| C5 | Coupling reduction increases representational diversity in distributed systems | A distributed system where coupling reduction decreases ED |

Each failure condition is informative regardless of outcome. Successive failures across
multiple independent datasets would disconfirm the framework. Isolated failures
constrain its applicability domain.

---

## 2. Falsification Matrix

### Tier 1: Controlled Computational Datasets (implementable immediately)

| Dataset | Source Type | Expected (per current framework) | Failure Condition | Challenge Target |
|---------|-------------|----------------------------------|-------------------|-----------------|
| Hopfield network recall | Attractor network with learned patterns | Partial rep hysteresis; function recovers faster | Full rep reversibility (rep loop area < func loop area) | C2 |
| Kuramoto oscillator grid | Coupled phase oscillators | TRACK B dominates; strong cross-correlation | TRACK A dominates at short timescale | C1 |
| Gene regulatory cascade | Boolean network with canalizing functions | System-dependent precursors; smooth ED transitions | Catastrophic bifurcation at single threshold | C4 |
| Reservoir computer echo | Echo state network with trained readout | Rep hysteresis large; func reversibility high | No measurable dissociation (rep=func recovery) | C3 |

### Tier 2: Published Empirical Datasets (requires literature extraction)

| Study Reference | System Type | Expected (per framework) | Failure Condition | Challenge Target |
|-----------------|-------------|--------------------------|-------------------|-----------------|
| Scheffer et al. (2009) *Nature* — early warning signals in ecological systems | Ecosystem collapse regimes | Precursor detectability depends on transition type | Universal EWS across all transition types | C4 |
| Dai et al. (2012) *Science* — experimental bacterial collapse | Microbial population collapse | Dissociation possible; function may persist after rep degradation | Function collapses simultaneously with rep | C3 |
| Lever et al. (2020) *Nature* — tipping points in mutualistic networks | Species interaction networks | TRACK B dominates; coupling structure predicts collapse | TRACK A predicts better (independent species dynamics) | C1 |
| Cavagna et al. (2010) *PNAS* — starling flock correlations | Collective animal behavior | Strong coupled dynamics; short timescale | Long-range order persists under perturbation (TRACK B at long timescale) | C1 |

### Tier 3: Prospective Preregistered Tests (requires experimental design)

| Test | Design | Predicted Outcome | Critical Empirical Signal |
|------|--------|-------------------|--------------------------|
| Coupling sweep on synthetic gene circuit | In silico GRN with inducer gradient | ED increases as coupling decreases; function non-monotonic | ED-function divergence at intermediate coupling |
| Recovery after targeted network ablation | Neural culture with optogenetic lesion | Functional recovery precedes representational | Temporal gap between func and rep restoration |
| Repeated perturbation of institutional trust survey | Human-subject repeated trust game | Cumulative hysteresis; asymmetry between trust loss and recovery | Loop area increases with cycle count |
| Swarm robot foraging under communication bandwidth reduction | Robot swarm with limited signaling | Smooth ED transition; no abrupt collapse | Continuous degradation, no bifurcation |

---

## 3. Escalation Ladder

Each stage must pass before proceeding to the next.

### Stage 1: Tier 1 Computational Benchmarks (weeks 1–2)

**Success criterion:** At least 3/5 falsification targets survive the Tier 1 datasets
(i.e., the expected behaviors hold, or failures are interpretable as domain constraints).

**Implementation:** Create a standard harness (`experiments/dynamics/external_harness.py`)
that accepts any system with `representational_ed()`, `functional_performance()`, and
`step()` interface, then runs the full TRACK A / TRACK B / precursor / hysteresis pipeline.

**Gate condition:** If > 3/5 Tier 1 datasets disconfirm core claims, pause and
reassess framework viability before proceeding to Tier 2.

### Stage 2: Tier 2 Published Data Retrodiction (weeks 3–4)

**Success criterion:** Framework reproduces reported empirical patterns in at least
3/4 literature datasets without parameter search.

**Method:** Extract time-series data from published figures (WebPlotDigitizer or
author-provided data). Map system observables to representational_ed and
functional_performance via the published operational definitions.

**Gate condition:** Parameter fitting beyond published ranges nullifies the
test. Framework must predict, not postdict.

### Stage 3: Tier 3 Preregistered Protocol (weeks 5–8)

**Success criterion:** Preregistration filed on OSF with explicit predictions,
analysis code, and contingency plans for all outcomes (confirm, disconfirm, null).

---

## 4. Implementation Plan

### 4.1 External Harness Interface

```python
class ExternalSystemAdapter:
    """
    Wraps any external system for the dual-framework pipeline.

    Required interface: representational_ed(), functional_performance(), step()
    """
    def __init__(self, data, rep_fn, func_fn, step_fn):
        self.data = data
        self._rep_fn = rep_fn
        self._func_fn = func_fn
        self._step_fn = step_fn
        self._idx = 0

    def representational_ed(self):
        return self._rep_fn(self.data, self._idx)

    def functional_performance(self):
        return self._func_fn(self.data, self._idx)

    def step(self):
        self._idx += 1
        return 0.0
```

### 4.2 Tier 1 Implementation Order

1. **Hopfield network recall** — `experiments/dynamics/external/hopfield_recall.py`
2. **Kuramoto oscillator grid** — `experiments/dynamics/external/kuramoto_grid.py`
3. **Gene regulatory cascade** — `experiments/dynamics/external/gene_regulatory.py`
4. **Reservoir computer echo** — `experiments/dynamics/external/reservoir_echo.py`

### 4.3 Scoring Protocol

Each dataset generates a report card:

| Dataset | Track A Score | Track B Score | Hysteresis A | Hysteresis B | Precursor Detected | Claims Supported | Claims Challenged |
|---------|--------------|--------------|--------------|--------------|-------------------|------------------|-------------------|
| hopfield | — | — | — | — | — | — | — |
| kuramoto | — | — | — | — | — | — | — |
| gene_reg | — | — | — | — | — | — | — |
| reservoir | — | — | — | — | — | — | — |

Claims supported/challenged count accumulates across datasets.

**Framework viability threshold:** If > 50% of falsification tests across all three
tiers disconfirm core claims, the dual-framework requires structural revision.

---

## 5. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Tier 1 datasets too similar to canonical systems | High | Low-mod | Use intentionally different architectures (Hopfield ≠ DistributedSystem) |
| Published data insufficient resolution for timescale analysis | Medium | High | Contact authors for raw data; use Bayesian estimation on sparse data |
| Parameter sensitivity dominates results | Medium | High | Report parameter sensitivity explicitly; no search, only default parameters |
| Preregistration too vague to be falsifiable | Medium | Medium | Use explicit numerical predictions with ± ranges |
| Systems fail to map onto representational_ed / functional_performance | Medium | High | Document operational mapping failure as finding; do not force-fit |

---

## 6. Relationship to Other Phase 005A Divisions

| Division | Connection |
|----------|-----------|
| Div 1 (collapse dynamics) | External harness reuses TRACK A / TRACK B analyzers |
| Div 3 (precursor signatures) | Same precursor pipeline applied to external data |
| Div 4 (hysteresis topology) | Same hysteresis sweep applied to external systems |
| Div 6–7 (Paper A/B) | External results determine which claims survive into papers |
