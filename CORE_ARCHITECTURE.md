# SGP-CORE V2 ARCHITECTURE

**Version:** 2.0  
**Date:** 2025-05-13  
**Status:** FOUNDATIONAL

---

## Design Principles

1. **Clean-room empirical** - No ontology, no philosophy, no SFH terminology
2. **Adversarial-first** - Null models before positive claims
3. **Validation-first** - All pipelines must pass quick sanity checks before large runs
4. **Reproducibility** - Fixed seeds, provenance tracking, null comparisons
5. **Domain-agnostic** - Infrastructure supports any interacting system type

---

## Directory Structure

```
/sgp_core_v2/
├── datasets/                 # Raw datasets (future)
├── synthetic_universes/      # Generated test systems
├── pipelines/               # Analysis pipelines
├── metrics/                 # Measurement functions
├── null_models/             # Adversarial test systems
├── benchmarks/              # Comparison standards
├── transformers/            # Transformer embedding analysis
├── neuroscience/            # Neural system analysis (future)
├── physics/                 # Physical system analysis (future)
├── ecology/                 # Ecological system analysis (future)
├── dynamics/                # Dynamical system analysis
├── interaction_models/      # Coupling/interaction definitions
├── experiments/             # Experiment configurations
├── validation/              # Quick validation runs
├── visualization/           # Output visualization
├── manuscripts/             # Manuscript drafts (empirical only)
├── archive_legacy/          # OLD SYSTEMS ARCHIVED HERE
├── governance/              # Protocol and rules
└── obsidian_core/          # Clean empirical vault
```

---

## Core Modules

### 1. Synthetic Universes (synthetic_universes/)

Purpose: Create controlled test systems with known properties

Systems:
- `random_clouds/` - Gaussian random distributions
- `hierarchical/` - Nested structure systems
- `sparse/` - Low-connectivity systems
- `attractor/` - Fixed-point and limit-cycle systems
- `coupled/` - Interaction-based systems

### 2. Pipelines (pipelines/)

Standardized analysis workflows:
- `dimensionality_profile.py` - D(k) computation
- `model_fitting.py` - Sigmoid/gompertz/hill fitting
- `bootstrap_stability.py` - Parameter stability
- `null_validation.py` - Null model comparison
- `cross_domain_scaling.py` - Multi-system generalization

### 3. Metrics (metrics/)

Measurement functions:
- `participation_ratio.py` - Eigenvalue-based dimension
- `k0_estimator.py` - Inflection point finding
- `persistence_metric.py` - Attractor lifetime
- `transition_detector.py` - Phase change identification
- `topology_invariant.py` - Structural measures

### 4. Null Models (null_models/)

Adversarial test systems:
- `shuffled_topology/` - Random edge rewiring
- `fake_clusters/` - Pseudo-structure
- `deceptive_dimension/` - False scaling
- `noise_主导/` - Random dominance tests
- `phase_imposter/` - Non-organization transitions

### 5. Validation (validation/)

Quick sanity check framework:
- Small system tests (< 1000 samples)
- Fast execution (< 60 seconds)
- Null comparison required
- Explicit pass/fail criteria

---

## Reproducibility Standards

| Component | Standard |
|-----------|----------|
| RNG | numpy.default_rng(seed=42) |
| Versions | requirements.txt locked |
| Outputs | SHA256 hash logged |
| Provenance | JSON metadata with every run |
| Random seeds | Documented in config |

---

## Null Comparison Requirement

Every positive finding MUST include:

1. **Null baseline** - Equivalent random/synthetic system
2. **Effect size** - Difference from null in standard units
3. **Statistical test** - p-value or confidence interval
4. **Direction** - Is null higher or lower than signal?

---

## Cross-Domain Scaling

The architecture supports any system where:
- Entities interact (coupled oscillators, neurons, nodes, agents)
- State space exists (phase space, embedding space, configuration space)
- Temporal evolution occurs (dynamics, trajectories, time series)

---

## Archive Isolation

All legacy systems moved to:
`/sgp_core_v2/archive_legacy/`

This includes:
- Prior SFH terminology
- Ontology frameworks
- Speculative notes
- Pre-V2 manuscripts

**These are archived, not deleted. Accessible but clearly marked as legacy.**

---

## Sections

| # | Section | Status |
|---|---------|--------|
| 1 | CORE_ARCHITECTURE | ✅ DONE |
| 2 | LEGACY_ISOLATION_REPORT | ✅ DONE |
| 3 | EMPIRICAL_CORE_SPEC | ✅ DONE |
| 4 | NULL_UNIVERSE_FRAMEWORK | ✅ DONE |
| 5 | DYNAMICAL_GEOMETRY_FRAMEWORK | ✅ DONE |
| 6 | METRIC_AUDIT_V2 | ✅ DONE |
| 7 | VALIDATION_EXECUTION_STANDARD | ✅ DONE |
| 8 | CROSS_DOMAIN_ROADMAP | ✅ DONE |
| 9 | OBSIDIAN_GRAPH_REBOOT | ✅ DONE |
| 10 | FINAL_AUDIT_LAUNCH | ✅ DONE |
| 11 | INTEGRATION_VERIFICATION | ✅ DONE |
| 12 | APPENDIX_DIRECTORY_MAP | ✅ DONE |

---

## Status

**FOUNDATIONAL COMPLETE**  
All 12 sections created. V2 infrastructure ready for empirical validation.