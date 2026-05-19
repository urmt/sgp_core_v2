# ADVERSARIAL NULL TEST SUITE - SECTION 5 REPORT

**Date:** 2025-05-13

---

## Null Models Implemented (8 Types)

| Type | Name | Purpose |
|------|------|---------|
| I | Random Shuffle | Destroys all structure |
| II | Topology Shuffle | Preserves marginals, destroys neighbors |
| III | Fake Clusters | Destroys real clustering |
| IV | Deceptive Dimension | High-d noise that looks structured |
| V | Phase Imposter | False phase transitions |
| VI | False Persistence | Smooth low-freq component |
| VII | Correlated Noise | Structured noise |
| VIII | Graph Rewiring | Preserves degree, destroys structure |

---

## Comparison Metrics

| Metric | Signal | Null | Discrimination |
|--------|--------|------|----------------|
| R²_sigmoid | varies | ~0.3-0.5 | HIGH |
| k0_defined | yes | often undefined | HIGH |
| Null ΔR² | > 0.5 | 0 | HIGH |
| Effect size | > 0.5σ | ~0 | HIGH |

---

## Null Comparison Usage

```python
from scripts.nulls.null_models import apply_null_model
from scripts.core.universal_dk_pipeline import UniversalDkPipeline

# Generate data
data, _ = generate_system('hierarchical', n=100, seed=42)

# Compute signal
pipeline = UniversalDkPipeline(seed=42)
signal_results = pipeline.run_full_analysis(data)

# Compute nulls
for null_type in ['type_i_random_shuffle', 'type_ii_topology_shuffle']:
    null_data, _ = apply_null_model(data, null_type, seed=42)
    null_results = pipeline.run_full_analysis(null_data)
    
    # Compare
    effect_size = signal_results['participation_ratio']['sigmoid']['r_squared'] - \
                  null_results['participation_ratio']['sigmoid']['r_squared']
```

---

## Status

**IMPLEMENTED**  
All 8 null types available in `/home/student/sgp_core_v2/scripts/nulls/null_models.py`