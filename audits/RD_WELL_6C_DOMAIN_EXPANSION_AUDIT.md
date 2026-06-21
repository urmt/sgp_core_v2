# RD-WELL.6C — Domain Expansion Audit (Preliminary Results)

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Compute only: C(domain), ΔC_transform, descriptor transport for additional domains. No coupling. No theories. Just: Does C remain computable? How sensitive is it?"  
**Status:** PRELIMINARY

---

## Question

Does C remain computable across additional independent physical worlds? How sensitive is it?

---

## Method

For each domain:
1. Load a single frame from the test set
2. Compute C under original, z-score, rank, and min-max transforms
3. Report ΔC_transform

---

## Results

### Gray-Scott Reaction-Diffusion (Baseline)

| Transformation | C | ΔC |
|----------------|-----|-----|
| original | 0.754102 | — |
| zscore | 0.754102 | 0.000000 |
| rank | 0.573570 | 0.180532 |
| minmax | 0.754102 | 0.000000 |

### Rayleigh-Bénard Convection (Baseline)

| Transformation | C | ΔC |
|----------------|-----|-----|
| original | 0.823515 | — |
| zscore | 0.823515 | 0.000000 |
| rank | 0.814431 | 0.009084 |
| minmax | 0.823515 | 0.000000 |

### Active Matter (Baseline)

| Transformation | C | ΔC |
|----------------|-----|-----|
| original | 0.826765 | — |
| zscore | 0.826765 | 0.000000 |
| rank | 0.800391 | 0.026374 |
| minmax | 0.826765 | 0.000000 |

### Rayleigh-Taylor Instability (NEW DOMAIN)

| Transformation | C | ΔC |
|----------------|-----|-----|
| original | 0.827082 | — |
| zscore | 0.827082 | 0.000000 |
| rank | 0.827082 | 0.000000 |
| minmax | 0.827082 | 0.000000 |

### MHD Compressible Turbulence (NEW DOMAIN)

**Status:** Not yet computed (timeout issues)

### Acoustic Scattering (NEW DOMAIN)

| Transformation | C | ΔC |
|----------------|-----|-----|
| original | 0.000000 | — |
| zscore | 0.000000 | 0.000000 |
| rank | 0.000000 | 0.000000 |
| minmax | 0.000000 | 0.000000 |

**Note:** C = 0 for acoustic scattering. This may indicate constant/uniform field or implementation issue.

---

## Key Findings

1. **The current implementation of C was successfully evaluated on five physical domains and returned nontrivial values in four of them.**
2. **C values range from 0.0 to 0.83** across domains
3. **z-score and min-max normalization show no sensitivity** for any domain (ΔC = 0)
4. **Rank transformation sensitivity varies by domain:**
   - Gray-Scott: ΔC = 0.180532 (highest sensitivity)
   - Active Matter: ΔC = 0.026374
   - Rayleigh-Bénard: ΔC = 0.009084
   - Rayleigh-Taylor: ΔC = 0.000000 (no sensitivity)
5. **Acoustic Scattering C = 0** — Zero is scientifically meaningful. Zero is not failure. But zero must be explained. Possible causes: uniform field, preprocessing artifact, incorrect field selection, genuinely low measured structure. Status: **RD-WELL.6C.A1 REQUIRED**

---

## Implications

1. **SR-30 testing expanded:** C now evaluated on 5 independent physical worlds (up from 3)
2. **Rank transformation is the most sensitive transform** — confirms RD-WELL.6A finding
3. **Some domains show no rank sensitivity** (Rayleigh-Taylor) — domain-specific behavior
4. **Rayleigh-Taylor ΔC_rank = 0 is potentially huge** — If this survives replication, C may depend more on order structure than metric structure in that domain. Directly connects to hidden variable: Metric Geometry. But: single sample, single trajectory, no promotion. Replicate first.
5. **Gray-Scott remains special** — ΔC_rank = 0.18 much larger than other domains. Suggests: Different physical worlds may occupy different representation-stability classes. Not a claim. A measurement question.
6. **Acoustic Scattering requires investigation** — C = 0 is unexpected. Status: RD-WELL.6C.A1 REQUIRED

---

## Next Steps (Priority Queue)

**P1: RD-WELL.6C replication**
- Multiple trajectories
- Multiple parameter settings
- Confidence intervals

**P2: RD-WELL.6C.A1**
- Acoustic Zero Audit (REQUIRED)

**P3: MHD integration**

**P4: Cross-domain robustness**

**P5: Coupling only after replication**

**Note:** Measurement before theory. Replication before explanation.

---

## Status

**PRELIMINARY** — Partial results only. MHD not computed. Acoustic Scattering anomalous.
