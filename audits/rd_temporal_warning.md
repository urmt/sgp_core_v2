# RD-TEMPORAL WARNING (STRENGTHENED)

**Source:** Research Director (RD-WELL.7C.R1 authorization, RD-WELL.8A.R2 strengthening)
**Status:** ACTIVE WARNING (STRENGTHENED)
**Date:** 2026-06-17

## Statement

**"Representation stability may itself evolve during system evolution."**

A system may be representation-stable at one time and unstable at another. The same field at different temporal windows may exhibit different representation sensitivity. A single-frame measurement is not representative of the full trajectory.

## Evidence from RD-WELL.7C.R1

Temporal variability test on Rayleigh-Taylor (t=0 to t=118):
- t=0 (0%): ΔC_rank = 0.0013
- t=29 (24%): ΔC_rank = 0.0029
- t=59 (50%): ΔC_rank = 0.0024
- t=89 (75%): ΔC_rank = 0.0010
- t=118 (99%): ΔC_rank = 0.0021

Range: 0.0010 to 0.0029 (factor of 2.9). Representation stability varied during system evolution.

## Evidence from RD-WELL.8A.R2

Temporal variability test on Gray-Scott (frame 0 to frame 500):
- Frame 0: ΔC_rank = 0.070
- Frame 100: ΔC_rank = 0.176
- Frame 200: ΔC_rank = 0.181
- Frame 300: ΔC_rank = 0.178
- Frame 400: ΔC_rank = 0.177
- Frame 500: ΔC_rank = 0.181

Range: 0.070 to 0.181 (factor of 2.6). Representation stability varied substantially during system evolution.

## Implications

1. **Single-frame measurements are insufficient.** A measurement at one time may not represent the full trajectory.
2. **Temporal sampling is mandatory.** Any representation stability audit must sample multiple time points.
3. **Temporal averaging may be necessary.** To obtain a representative value, average over multiple time points.
4. **Temporal resolution matters.** The choice of time points affects the result.
5. **A single-frame estimate is increasingly difficult to defend as representative.**

## Required Protocol

For any representation stability audit:
1. Sample at least 5 time points across the trajectory.
2. Report mean(ΔC_rank) and std(ΔC_rank) across time points.
3. Report the temporal range (max - min) of ΔC_rank.
4. Note whether the system exhibits temporal variability.
5. **Never report a single-frame estimate as representative.**

## Relationship to Other Warnings

- **RD-CONSTRAINT:** Constraints may themselves evolve during system evolution.
- **RD-SMALL-N:** Temporal sampling increases N.
- **RD-PROVENANCE:** Time points must be documented.
- **RD-CANONICAL:** Multiple time points may produce different values.
- **RD-PROTOCOL DRIFT:** Protocol choices may affect temporal variability estimates.
