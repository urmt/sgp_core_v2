# ============================================================
# Reproducibility Package — Transition-Field Geometry Paper
# ============================================================

## Quick Start

```bash
# 1. Run the full T031 analysis (7 seconds)
python T031_NULL_GEOMETRY_DISENTANGLEMENT.py

# 2. Generate all figures (PDF + PNG at 600 DPI)
python publication/scripts/generate_all_figures.py

# 3. Generate all tables (LaTeX + CSV)
python publication/scripts/generate_all_tables.py

# 4. Compile the paper
cd publication/chaos_template
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

## Complete Pipeline (single command)

```bash
bash RUN_T031_PIPELINE.sh
```

This runs T031, validates all outputs, extracts the verdict, and logs everything.

## Environment

- Python 3.14+
- NumPy 2.2+
- SciPy 1.15+
- scikit-learn 1.6+
- matplotlib 3.10+
- pandas 2.2+

See `environment.yml` for exact versions.

## Data Requirements

All required data files are in `sfh_sgp_ood_outputs/`:

| File | Description |
|------|-------------|
| `t030_ensemble_Phi.npy` | 211×4 emergence coordinates |
| `t030_ensemble_features.csv` | 211×21 feature matrix |
| `t030_ensemble_flow.csv` | Flow magnitudes per system |
| `t030_ensemble_V.npy` | Vector field directions |
| `t030_ensemble_tensors.npy` | 100×4×17 stability tensors |

## Output Files

### T031 Outputs
| File | Description |
|------|-------------|
| `t031_null_metrics.csv` | Null-model PR, CI, survival |
| `t031_information_geometry.csv` | Fisher entropy, KL divergences |
| `t031_embedding_stability.csv` | Trustworthiness, continuity |
| `t031_geometry_comparison.csv` | Combined metrics |
| `t031_null_rankings.csv` | Null-model rankings |
| `t031_null_geometry_results.json` | Full structured results |

### Figures (publication/figures/)
| File | Description |
|------|-------------|
| `fig1_phi_manifold.pdf` | Φ-space 3D scatter + flow histogram |
| `fig2_flow_topology.pdf` | Ridge/bifurcation segmentation |
| `fig3_null_survival.pdf` | Null-model survival ratios |
| `fig4_causal_destruction.pdf` | PR collapse trajectory |
| `fig5_representation.pdf` | Embedding robustness |
| `fig6_universality_failure.pdf` | Hypothesis survival heatmap |

### Tables (publication/tables/)
| File | Description |
|------|-------------|
| `table1_system_families.tex` | 13 families, parameter ranges |
| `table2_feature_definitions.tex` | 17 raw features |
| `table3_hypothesis_audit.tex` | T027-T031 hypothesis results |
| `table4_null_comparisons.tex` | Null-model comparisons |
| `table5_decision_framework.tex` | 7 criteria, 6/7 passed |

## Dataset Hashes

```
SHA256(sfh_sgp_ood_outputs/t030_ensemble_Phi.npy) = [compute at runtime]
SHA256(sfh_sgp_ood_outputs/t030_ensemble_features.csv) = [compute at runtime]
```

## Determinism

All analyses use `np.random.seed(42)` for reproducibility. The same random state is used across all sections.

## Runtime

| Component | Time |
|-----------|------|
| T031 execution | ~7 seconds |
| Figure generation | ~5 seconds |
| Table generation | ~1 second |
| **Total** | **~13 seconds** |

## Citation

```bibtex
@article{traver2026transition,
  title={Transition-Field Geometry Across Heterogeneous Dynamical Systems},
  author={Traver, Mark Rowe},
  journal={Chaos},
  year={2026},
  publisher={AIP Publishing}
}
```

## License

Analysis code: MIT License
Data: CC BY 4.0
Figures: CC BY 4.0
