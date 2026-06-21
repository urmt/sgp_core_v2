# RD-WELL.5D.R1 — Dataset Loader Audit

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Make loading work for Rayleigh-Bénard, Active Matter, Rayleigh-Taylor"  
**Status:** PARTIAL (Rayleigh-Bénard and Active Matter working, Rayleigh-Taylor pending)

---

## Objective

Make loading work for Rayleigh-Bénard, Active Matter, Rayleigh-Taylor.

This is dataset archaeology — no metrics, no C, no stabilization.

---

## Results

### Gray-Scott (Already Working)

| Pattern | URL | Status |
|---------|-----|--------|
| bubbles | `gray_scott_reaction_diffusion_bubbles_F_0.098_k_0.057.hdf5` | ✓ Working |
| maze | `gray_scott_reaction_diffusion_maze_F_0.029_k_0.057.hdf5` | ✓ Working |
| spirals | `gray_scott_reaction_diffusion_spirals_F_0.018_k_0.051.hdf5` | ✓ Working |

**Schema:**
- Top-level keys: `boundary_conditions`, `dimensions`, `scalars`, `t0_fields`, `t1_fields`, `t2_fields`
- t0_fields: `A`, `B` (scalar fields)
- Shape: (n_trajectories, n_timesteps, x, y)
- Example: `field_A[0]` has shape (1001, 128, 128)

---

### Rayleigh-Bénard (Now Working)

| URL | Status |
|-----|--------|
| `rayleigh_benard_Rayleigh_1e8_Prandtl_1.hdf5` | ✓ Working |

**Schema:**
- Top-level keys: `boundary_conditions`, `dimensions`, `scalars`, `t0_fields`, `t1_fields`, `t2_fields`
- t0_fields: `buoyancy`, `pressure` (scalar fields)
- t1_fields: `velocity` (vector field)
- Shape: (40, 200, 512, 128)
- Example: `buoyancy[0]` has shape (200, 512, 128)

**Working URL:**
```
https://huggingface.co/datasets/polymathic-ai/rayleigh_benard/resolve/main/data/train/rayleigh_benard_Rayleigh_1e8_Prandtl_1.hdf5
```

---

### Active Matter (Now Working)

| URL | Status |
|-----|--------|
| `active_matter_L_10.0_zeta_1.0_alpha_-1.0.hdf5` | ✓ Working |

**Schema:**
- Top-level keys: `boundary_conditions`, `dimensions`, `scalars`, `t0_fields`, `t1_fields`, `t2_fields`
- t0_fields: `concentration` (scalar field)
- t1_fields: `velocity` (vector field)
- t2_fields: `D`, `E` (tensor fields)
- Shape: (3, 81, 256, 256)
- Example: `concentration[0]` has shape (81, 256, 256)

**Working URL:**
```
https://huggingface.co/datasets/polymathic-ai/active_matter/resolve/main/data/train/active_matter_L_10.0_zeta_1.0_alpha_-1.0.hdf5
```

---

### Rayleigh-Taylor (Pending)

Not yet tested. Need to find correct URLs from visualization notebook.

---

## Key Findings

1. **File naming conventions differ across datasets**
   - Gray-Scott: `gray_scott_reaction_diffusion_{pattern}_F_{F}_k_{k}.hdf5`
   - Rayleigh-Bénard: `rayleigh_benard_Rayleigh_{Ra}_Prandtl_{Pr}.hdf5`
   - Active Matter: `active_matter_L_{L}_zeta_{zeta}_alpha_{alpha}.hdf5`

2. **Schema is consistent across datasets**
   - All have `t0_fields`, `t1_fields`, `t2_fields`
   - All have `boundary_conditions`, `dimensions`, `scalars`

3. **Field access patterns**
   - Scalar fields: `field[trajectory, time, x, y]`
   - Vector fields: `field[trajectory, time, x, y, component]`
   - Tensor fields: `field[trajectory, time, x, y, i, j]`

---

## Status

- **Rayleigh-Bénard:** ✓ Working, 10 frames extracted
- **Active Matter:** ✓ Working, 10 frames extracted
- **Rayleigh-Taylor:** Pending

---

## Frame Extraction

### Rayleigh-Bénard

| Field | Shape | Min | Max | Mean |
|-------|-------|-----|-----|------|
| buoyancy | (10, 512, 128) | 0.0000 | 0.9989 | 0.1460 |
| pressure | (10, 512, 128) | -0.0800 | 0.0335 | -0.0042 |
| velocity_magnitude | (10, 512, 128) | 0.0000 | 0.0002 | 0.0000 |

### Active Matter

| Field | Shape | Min | Max | Mean |
|-------|-------|-----|-----|------|
| concentration | (10, 256, 256) | 0.9633 | 1.0406 | 1.0000 |
| velocity_magnitude | (10, 256, 256) | 0.0000 | 0.0027 | 0.0008 |

---

## Next Steps

1. RD-WELL.5D.R2: Blind Operational Reconnaissance
2. Find correct URLs for Rayleigh-Taylor
3. Compute C and coupling (after observation)

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5d_r1/`
- Frames: `/home/student/sgp_core_v2/audits/rd_well5d_r1/rayleigh_benard_frames/`, `/home/student/sgp_core_v2/audits/rd_well5d_r1/active_matter_frames/`
- Scripts: `/home/student/sgp_core_v2/audits/rd_well5d_r1/run_*.py`
