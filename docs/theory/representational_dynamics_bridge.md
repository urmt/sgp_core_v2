# Representational Dynamics Bridge

**Phase 005A Division 1 — Bridge Document**

Maps the transition from Phase 004B (representational recovery vs functional recovery) to Phase 005A (adaptive representational dynamics under collapse). Documents the dual-framework comparative architecture and demonstrates constraint compliance.

---

## 1. Historical Evolution

| Phase | Focus | Central Result | Limitation |
|-------|-------|----------------|------------|
| 004A | Collapse reversibility | Coupling reduction induces ED changes that partially reverse | Single-metric framework, no representational/functional distinction |
| 004B | Functional recovery metrics | **Representational recovery ≠ functional recovery** in 5/8 systems | Observables as static endpoint measurements |
| 005A (current) | Adaptive representational dynamics | Collapse trajectory as primary object; dual-framework comparison | (in progress) |

### Phase 004B → 005A Scientific Shift

- **From:** "Does representation recover differently from function?"
- **To:** "What is the structure of collapse trajectories, and which framework (parallel or coupled) better describes them?"

---

## 2. Symbolic Mapping

| Phase 004B Construct | Phase 005A Construct | Relationship |
|----------------------|----------------------|--------------|
| Representational ED (Ψ) | Collapse trajectory (τ_rep) | ED over time becomes trajectory |
| Functional performance (f) | Functional trajectory (τ_func) | Performance over time becomes trajectory |
| Recovery percentage | Path divergence (δ) | Static endpoint → dynamic divergence |
| Dissociation (Ψ↑ f↓) | Divergence trajectory | Point observation → continuous measure |
| Intervention type (coupling sweep) | TRACK B interaction structure | Discrete intervention → continuous coupling |

---

## 3. Dual-Framework Architecture

### TRACK A: Parallel Dynamics

**Hypothesis (for testing):** Representation and function evolve independently under coupling perturbation.

```
τ_rep(t) = f_rep(c(t), noise)
τ_func(t) = f_func(c(t), noise)
Cov(τ_rep, τ_func) ≈ 0
```

**Measurements:**
- Independent trajectory divergence
- Spearman correlation between trajectories
- Precursor signals in each modality separately

**Empirical alignment:** Supported when divergence is low (< 0.15) and correlation is weak.

### TRACK B: Coupled Dynamics

**Hypothesis (for testing):** Representation and function exhibit measurable interaction structure.

```
τ_rep(t) = f(c(t), τ_func(t), noise)
τ_func(t) = g(c(t), τ_rep(t), noise)
Cov(τ_rep, τ_func) ≠ 0
```

**Measurements:**
- Cross-correlation at multiple lags
- Coupling strength (joint velocity product)
- Lead-lag relationship
- Coupled precursor detection

**Empirical alignment:** Supported when cross-correlation > 0.3 or coupling strength > 0.3.

### Comparative Evaluation Protocol

1. Run system at baseline → measure both tracks
2. Compute support scores (0–1) for each track
3. Evidence gap = coupled_support − parallel_support
4. Gap > 0.3 → TRACK B favored; gap < −0.3 → TRACK A favored

---

## 4. Empirical Findings (Phase 005A Division 1 Run)

### Collapse Dynamics (TRACK A vs TRACK B)

| System | Type | TRACK A ρ | TRACK B ρ | Coupling Strength | Lead-Lag | Winner |
|--------|------|-----------|-----------|-------------------|----------|--------|
| Distributed | DistributedSystem | −0.997 | −0.998 | 1.006 | synchronous | B |
| Immune | ImmuneSignalingNetwork | −0.620 | 0.170 | 0.695 | synchronous | B |
| Institution | InstitutionSystem | 0.700 | 0.038 | 0.622 | rep→func | B |
| Ant Colony | AntColony | −0.403 | 0.407 | 0.604 | rep→func | B |

### Precursor Signatures

| System | Collapse Step | Rep Precursors | Func Precursors | Coupled Signals | Winner |
|--------|--------------|----------------|-----------------|-----------------|--------|
| Distributed | 64 | 0 | 0 | 0 | none |
| Immune | 89 | 9 | 1 | 8 | A_parallel |
| Institution | 75 | 4 | 7 | 19 | B_coupled |
| Ant Colony | 64 | 0 | 0 | 0 | none |

### Hysteresis Topology

| System | Rep Loop Area | Rep Reversibility | Func Reversibility | Rep-Func Gap | Coupled Hysteresis | Interaction Fades |
|--------|-------------|------------------|-------------------|--------------|-------------------|-------------------|
| Distributed | 698.40 | 0.000 | 0.871 | 0.871 | 2.409 | No |
| Immune | 853.78 | 0.000 | 0.770 | 0.770 | 2.620 | **Yes** |
| Institution | 599.51 | 0.000 | 0.334 | 0.334 | 0.988 | **Yes** |
| Ant Colony | 7446.74 | 0.000 | 0.000 | 0.000 | 20.033 | **Yes** |

---

## 5. Cross-Cutting Findings

### Finding 1: Representation ≫ Function Hysteresis
Representational trajectories are near-completely irreversible across all systems (reversibility ≈ 0). Functional trajectories show > 0.33 reversibility in 3/4 systems. Consistent with Phase 004B: representation and function are separable.

### Finding 2: Collapse Is Not Abrupt
Systems do not exhibit sudden representational collapse under coupling reduction. Distributed, immune, and ant_colony systems show ED *increases* when coupling decreases. Only institution system shows ED decrease. Collapse is better described as "representational drift" than "collapse."

### Finding 3: Precursor Detection Is System-Dependent
Only immune and institution systems produce detectable precursor signals. Distributed and ant_colony produce none. This is consistent with their dynamics: smoothly increasing ED produces no "precursor anomaly" because there is no sudden transition.

### Finding 4: Coupled Framework Wins Dynamically
TRACK B (coupled) is favored by collapse dynamics analysis across all 4 systems. TRACK A (parallel) wins hysteresis topology. The appropriate framework depends on the timescale:
- **Short timescale (dynamics):** Representation and function are coupled
- **Long timescale (hysteresis):** Representation and function diverge

---

## 6. Constraint Compliance Verification

| Constraint | Status | Notes |
|------------|--------|-------|
| No universal law claims | ✓ Compliant | All findings framed as "consistent with," "suggests," "correlates with" |
| No causal attribution | ✓ Compliant | Analysis is descriptive; no causal claims made |
| No ontological interpretation | ✓ Compliant | Systems are computational models; no claims about "real" cognition |
| Dual-framework architecture | ✓ Compliant | Both TRACK A and TRACK B implemented and compared |
| Empirical priority | ✓ Compliant | Evidence-based comparison; no theoretical precommitment |
| NumPy compatibility | ✓ Compliant | All `np.trapz` replaced with `np.trapezoid` |

---

## 7. Repository Identity

**Current:** Adaptive representational dynamics — collapse trajectories as primary objects, dual-framework comparison, empirical constraint compliance.

**Not:** Observable engineering, universal laws, causal proof, physics of cognition, gauge ontology.

---

## 8. Key References

- `experiments/dynamics/collapse_dynamics.py` — Core dual-framework engine
- `experiments/dynamics/precursor_signatures.py` — Precursor detection (Div 3)
- `experiments/dynamics/hysteresis_topology.py` — Hysteresis analysis (Div 4)
- `experiments/dynamics/metrics.py` — Collapse trajectory metrics
- `experiments/dynamics/analysis.py` — Trajectory pattern classification
- Phase 004B: Functional recovery vs representational recovery dissociation
