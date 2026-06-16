# RD-WELL.1 — Dataset Reconnaissance Audit

**Date:** 2026-06-15  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "The Well provides independent worlds"  
**Status:** COMPLETE

---

## Repository

- **URL:** https://github.com/PolymathicAI/the_well
- **Size:** 15TB total across 16 datasets
- **License:** BSD-3-Clause
- **Cloned to:** `/home/student/sgp_core_v2/the_well/`

---

## Dataset Inventory

| # | Dataset | Domain | State Variables | Spatial | Temporal | Resolution | Suitability |
|---|---------|--------|-----------------|---------|----------|------------|-------------|
| 1 | acoustic_scattering_discontinuous | Acoustics | p, u, v | 2D | time-series | — | Low |
| 2 | acoustic_scattering_inclusions | Acoustics | p, u, v | 2D | time-series | — | Low |
| 3 | acoustic_scattering_maze | Acoustics | p, u, v | 2D | time-series | — | Low |
| 4 | active_matter | Biology | concentration, orientation | 2D | time-series | — | **High** |
| 5 | convective_envelope_rsg | Astrophysics | ρ, v, P | 3D | time-series | — | Medium |
| 6 | euler_multi_quadrants_openBC | Fluids | ρ, v, E | 2D | time-series | — | **High** |
| 7 | euler_multi_quadrants_periodicBC | Fluids | ρ, v, E | 2D | time-series | — | **High** |
| 8 | gray_scott_reaction_diffusion | Chemistry | A, B | 2D | time-series | — | **High** |
| 9 | helmholtz_staircase | Acoustics | U | 2D | frequency | — | Low |
| 10 | MHD_256 | Plasma | ρ, v, B, P | 3D | time-series | 256³ | Medium |
| 11 | MHD_64 | Plasma | ρ, v, B, P | 3D | time-series | 64³ | Medium |
| 12 | planetswe | Atmosphere | u, h | 2D (sphere) | time-series | — | Medium |
| 13 | post_neutron_star_merger | Astrophysics | ρ, v, P, Ye | 2D (axisym) | time-series | — | Low |
| 14 | rayleigh_benard | Fluids | T, u, v | 2D | time-series | — | **High** |
| 15 | rayleigh_benard_uniform | Fluids | T, u, v | 2D | time-series | — | **High** |
| 16 | rayleigh_taylor_instability | Fluids | ρ, u, v | 3D | time-series | — | **High** |
| 17 | shear_flow | Fluids | u, v | 2D | time-series | — | Medium |
| 18 | supernova_explosion_128 | Astrophysics | ρ, v, P | 3D | time-series | 128² | Medium |
| 19 | supernova_explosion_64 | Astrophysics | ρ, v, P | 3D | time-series | 64² | Medium |
| 20 | turbulence_gravity_cooling | Astrophysics | ρ, v, P | 3D | time-series | — | Medium |
| 21 | turbulent_radiative_layer_2D | Astrophysics | ρ, v, P, E | 2D | time-series | — | **High** |
| 22 | turbulent_radiative_layer_3D | Astrophysics | ρ, v, P, E | 3D | time-series | — | Medium |
| 23 | viscoelastic_instability | Fluids | u, v, C | 2D | time-series | — | **High** |

---

## Scoring for RD Suitability

### C Validation (Coherence)

**Top 3:**

1. **gray_scott_reaction_diffusion** — Pattern formation from randomness. C should detect emergent spatial coherence.
2. **rayleigh_benard** — Convective cells form coherent structures. C should vary with Rayleigh number.
3. **euler_multi_quadrants_openBC** — Shocks and rarefactions create transient coherence.

### F Exploration (Fertility)

**Top 3:**

1. **gray_scott_reaction_diffusion** — Patterns generate further patterns. High fertility potential.
2. **viscoelastic_instability** — Four coexistent attractors. System can transition between states.
3. **active_matter** — Biological self-organization. Fertility as adaptation.

### I Exploration (Interaction)

**Top 3:**

1. **turbulent_radiative_layer_2D** — Hot/cold gas mixing. Interaction between phases.
2. **rayleigh_taylor_instability** — Dense/light fluid interaction. Clear interaction structure.
3. **euler_multi_quadrants_periodicBC** — Periodic boundaries force sustained interaction.

---

## Selection for Immediate Use

### For C Validation

| Dataset | Why | Cost |
|---------|-----|------|
| gray_scott_reaction_diffusion | Clean pattern formation, known parameters | Low (2D) |
| rayleigh_benard | Classic convection, well-studied | Low (2D) |
| euler_multi_quadrants_openBC | Shocks create coherence transitions | Low (2D) |

### For F Exploration

| Dataset | Why | Cost |
|---------|-----|------|
| gray_scott_reaction_diffusion | Pattern dynamics vary with f, k | Low (2D) |
| viscoelastic_instability | Four attractors, edge states | Low (2D) |
| active_matter | Biological self-organization | Medium (2D) |

### For I Exploration

| Dataset | Why | Cost |
|---------|-----|------|
| turbulent_radiative_layer_2D | Phase mixing, clear interaction | Low (2D) |
| rayleigh_taylor_instability | Instability-driven interaction | Medium (3D) |
| euler_multi_quadrants_periodicBC | Sustained periodic interaction | Low (2D) |

---

## Computational Notes

- **Total Well size:** 15TB (full collection)
- **Recommended start:** 2D datasets only (lower cost)
- **Minimum viable test:** gray_scott_reaction_diffusion (smallest, cleanest)
- **Data format:** HDF5 with PyTorch DataLoader
- **Installation:** `pip install the_well` or from source

---

## Key Insight

The Well provides **independent physics, independent simulators, independent discretizations.**

This directly addresses SR-30:

> Any survivor discovered entirely within one simulator must be treated as simulator-dependent.

C, F, and I can now be tested across:
- Different PDEs (Euler, Navier-Stokes, Gray-Scott, MHD)
- Different boundary conditions (open, periodic)
- Different dimensionalities (2D, 3D)
- Different physical domains (fluids, plasma, chemistry, biology)

**This is exactly what RD needs for cross-domain validation.**

---

## Artifact

- Repository: `/home/student/sgp_core_v2/the_well/`
- Audit: `/home/student/sgp_core_v2/audits/RD_WELL_1_DATASET_RECONNAISSANCE.md`
