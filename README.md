# SGP Core V2 — Recursive Organizational Geometry

## Overview

SGP Core V2 is a research project analyzing recursive organizational geometry through systematic phase-based analysis. The project examines whether recursively persistent relational structures exhibit invariant properties across recursive depth, sector organization, and phase evolution.

## Repository Structure

```
sgp_core_v2/
├── docs/               # Documentation
│   ├── theory/         # Theory documents
│   ├── glossary/       # Term definitions
│   ├── methodology/  # Methodology documents
│   ├── phase_summaries/ # Phase summaries
│   └── publication_notes/ # Publication preparation
├── phases/            # Phase analysis artifacts (265-308+)
├── datasets/          # Data storage
├── analysis/          # Analysis tools
├── figures/           # Figure storage
├── results/           # Results storage
├── papers/            # Publication materials
└── archive/          # Archived materials
```

## Reproducibility Goals

This repository is organized for:
- **Independent verification**: All code and data are version-controlled
- **Scientific traceability**: Complete audit trail of phase development
- **Publication readiness**: Structured for journal submission
- **Methodological rigor**: Systematic phase-based analysis with consistent frameworks

## Phase Organization

Each phase (phaseXXX/) contains:
- Framework definition
- Metrics data (CSV)
- Results (JSON)
- Analysis documents
- Sector reports
- RG stability analysis
- Geometry summary
- Forbidden interpretations
- Update summary

## No Ontology Claims

This project is **strictly mathematical**. We study:
- Recursive persistence structures
- Organizational boundedness
- Scale-invariant geometry
- RG stability patterns

We do NOT study:
- Physics or cosmology
- Consciousness or mind
- Physical reality
- Universe generation

All phases include forbidden interpretations documentation to prevent ontological overreach.

## Key Findings (Phases 280-308)

- **RECURSIVELY_STABLE**: 26/28 phases achieve this verdict
- **RG Correlation**: Mean 0.933, range [0.80, 0.96]
- **Boundedness**: Mean 0.919, universally bounded
- **Retention**: Universal persistence (100% pass rate)
- **Sector Hierarchy**: Projection > Antisymmetry > Neutral

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run phase analysis
python phases/phaseXXX/phaseXXX_compute.py

# Update index files after new phases
# See docs/phase_summaries/master_phase_index.csv
```

## Citation

When citing this work, reference the specific phase and include:
- Version number
- Date
- Verdict
- Key metrics

## License

MIT License - See LICENSE file for details.

## Contributing

All contributions must:
1. Follow existing phase structure
2. Include forbidden interpretations
3. Update master_phase_index.csv
4. Update cross_phase_stability_table.csv
5. Use commit format: `PHASE XXX COMPLETE — [VERDICT]`