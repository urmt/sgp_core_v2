# RD-WELL.5D.R3B — Measurement Transport Audit (Revised)

**Date:** 2026-06-16  
**Auditor:** OpenCode  
**Trigger:** Research Director directive — "Does the same measurement mean the same thing across worlds?"  
**Status:** COMPLETE (Revised)

---

## Question

Does the same measurement mean the same thing across worlds?

---

## Measurement Transport Audit Table (Revised)

### Operational vs Semantic Comparability

| Measurement | Gray-Scott | Rayleigh-Bénard | Active Matter | Operational | Semantic |
|-------------|------------|-----------------|---------------|-------------|----------|
| Mean | [0.497, 0.504] | [0.100, 0.161] | [1.000, 1.000] | High | Unknown |
| Variance | [0.083, 0.084] | [0.005, 0.050] | [0.000, 0.000] | High | Unknown |
| Entropy | [-0.007, -0.001] | [-86.38, -10.20] | [-2283.67, -391.78] | Medium | Unknown |
| Power Spectrum | [8.85M, 9.07M] | [6.44M, 327.94M] | [4.29B, 4.30B] | Medium | Unknown |
| Connected Components | [1069, 1168] | [1, 1] | [3, 16] | Observer-dependent | Observer-dependent |

**Legend:**
- **Operational:** Can the same computation be applied?
- **Semantic:** Does the quantity represent similar physical content?

---

## Key Findings

1. **Mean and Variance:** High operational comparability — same computation can be applied. Semantic comparability unknown.
2. **Entropy and Power Spectrum:** Medium operational comparability — same computation can be applied with caveats. Semantic comparability unknown.
3. **Connected Components:** Observer-dependent — requires threshold choice, adjacency definition, segmentation procedure. This is one of the highest-risk descriptors in the archive.

---

## Connected Components — Special Warning

Connected components are especially dangerous because they require:
- threshold choice
- adjacency definition
- segmentation procedure

These are observer choices. This is exactly the sort of quantity that has repeatedly generated false survivors in the archive.

**Relabel:** Connected Components → Observer-dependent (not "Low comparability")

---

## Implications

**Same descriptor value ≠ same phenomenon**

The selected descriptors produced identical values under the current operationalization, but this does not mean the same phenomenon is being observed.

**Safe wording:**
> Some operational measurements may remain computable and behaviorally similar across independent physical worlds.

Status: **UNDER TEST**

---

## Status

Measurement transport audit complete (revised with operational vs semantic comparability).

---

## Artifact

- Data: `/home/student/sgp_core_v2/audits/rd_well5d_r3b/measurement_transport_audit.json`
- Script: `/home/student/sgp_core_v2/audits/rd_well5d_r3b/run_measurement_transport_audit.py`
