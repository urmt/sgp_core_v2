# DIRECTORY INITIALIZATION REPORT — SGP_CORE_V2_002

**Date:** 2025-05-13  
**Status:** COMPLETE

---

## Created Directories

| Path | Purpose | Status |
|------|---------|--------|
| `experiments/` | Run storage | ✅ |
| `experiments/phase_a_validation/` | Quick validation runs | ✅ |
| `experiments/full_scale_runs/` | Large-scale experiments | ✅ |
| `outputs/` | Output root | ✅ |
| `outputs/figures/` | Generated figures | ✅ |
| `outputs/tables/` | Generated tables | ✅ |
| `outputs/raw/` | Raw data outputs | ✅ |
| `outputs/logs/` | Execution logs | ✅ |
| `outputs/metadata/` | Provenance metadata | ✅ |
| `scripts/` | Script root | ✅ |
| `scripts/core/` | Core pipeline scripts | ✅ |
| `scripts/validation/` | Validation runners | ✅ |
| `scripts/nulls/` | Null model generators | ✅ |

---

## Structure

```
/sgp_core_v2/
├── experiments/
│   ├── phase_a_validation/     # Quick sanity checks (N≤100, t≤60s)
│   └── full_scale_runs/        # Large runs (N≤10000)
├── outputs/
│   ├── figures/                # Plots
│   ├── tables/                 # Data tables
│   ├── raw/                   # Raw outputs
│   ├── logs/                   # Runtime logs
│   └── metadata/              # JSON metadata
└── scripts/
    ├── core/                   # Main pipeline
    ├── validation/             # Validation runners
    └── nulls/                  # Null model generators
```

---

## Usage Rules

- **phase_a_validation/**: Quick validation runs
- **full_scale_runs/**: Only after Phase A passes
- **outputs/figures/**: All plots
- **outputs/metadata/**: All provenance JSON
- **scripts/**: All executable code

---

## Initialization Status

**COMPLETE**  
Next: SECTION 2 — Core Synthetic System Generators