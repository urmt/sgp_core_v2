# APPENDIX: DIRECTORY MAP — SGP-CORE V2

**Date:** 2025-05-13

---

## Full Directory Structure

```
/sgp_core_v2/
├── archive_legacy/           # Legacy (pre-V2) materials isolated
├── synthetic_universes/      # Test system generators
│   ├── random_clouds/        # Null baseline
│   ├── hierarchical/         # Multi-scale structure
│   ├── sparse_graphs/        # Network topology
│   ├── dynamical/            # Time-evolving systems
│   └── transformer/          # Artificial embeddings
├── null_models/              # Adversarial test suite
│   ├── type_i_random/       # Random shuffle
│   ├── type_ii_topology/    # Neighbor destroy
│   ├── type_iii_clusters/   # Fake clusters
│   ├── type_iv_dimension/   # Deceptive dim
│   ├── type_v_phase/        # False transitions
│   ├── type_vi_persistence/ # False persistence
│   ├── type_vii_correlated/ # Correlated noise
│   └── type_viii_graph/     # Graph rewiring
├── pipeline/                 # Core analysis pipeline
│   ├── data_loader/         # Data ingestion
│   ├── nearest_neighbors/   # k-NN computation
│   ├── dimensionality/      # D(k) calculation
│   ├── fitting/             # Model fitting
│   └── validation/          # Phase A/B runner
├── metrics/                  # Quantitative measures
│   ├── participation_ratio/ # D(k) implementation
│   ├── sigmoid_fit/         # k0, A, β estimation
│   ├── model_selection/     # AIC/BIC comparison
│   ├── bootstrap/          # Stability estimation
│   └── persistence/         # Temporal metrics
├── visualization/            # Plotting and output
│   ├── plots/               # Generated figures
│   ├── reports/            # Summary reports
│   └── dashboard/          # Interactive viewer
├── results/                  # Output storage
│   ├── experiments/         # Individual runs
│   ├── comparisons/         # Cross-system analysis
│   └── archived/           # Historical runs
├── obsidian_graph/          # Knowledge graph (V2 only)
│   ├── 00_vault_meta/
│   ├── 01_concepts/
│   ├── 02_methods/
│   ├── 03_results/
│   ├── 04_systems/
│   ├── 05_metrics/
│   └── 06_comparisons/
├── documentation/            # Architecture docs
├── tests/                    # Integration tests
├── configs/                  # Configuration files
├── logs/                    # Execution logs
├── scripts/                 # Utility scripts
└── README.md                # Entry point
```

---

## Quick Reference

| Purpose | Directory |
|---------|-----------|
| Generate test data | synthetic_universes/ |
| Run null comparison | null_models/ |
| Execute pipeline | pipeline/ |
| Compute metrics | metrics/ |
| View results | visualization/, results/ |
| Knowledge graph | obsidian_graph/ |
| Legacy access | archive_legacy/ |

---

## Status

**DIRECTORY MAP COMPLETE**  
V2 Infrastructure foundation: DONE