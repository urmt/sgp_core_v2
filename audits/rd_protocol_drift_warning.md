# RD-PROTOCOL DRIFT WARNING

**Source:** Research Director (RD-WELL.8A.R2 assessment)
**Status:** ACTIVE WARNING
**Date:** 2026-06-17

## Statement

**"Apparently contradictory measurements may arise from changes in analysis protocol rather than changes in the underlying phenomenon."**

## Evidence

Gray-Scott:
- Frame choice changed (frame 0 vs frame 500)
- Measurement implementation changed (single frame vs sequence of frames)
- Resulting ΔC_rank changed substantially (0.07 vs 0.18)

## Distinction from Other Warnings

| Warning | Focus |
|---------|-------|
| RD-TEMPORAL WARNING | System evolution during measurement |
| RD-PSEUDOREPLICATION WARNING | Non-independent measurements treated as independent |
| RD-CANONICAL WARNING | Multiple versions of same measurement |
| RD-PROTOCOL DRIFT WARNING | Analysis protocol changes affecting results |

## Required Protocol

1. **Document all protocol choices** before computing measurements.
2. **Freeze protocol** before executing audit.
3. **Report protocol version** with every measurement.
4. **Test protocol sensitivity** when possible.

## Relationship to Other Warnings

- **RD-TEMPORAL WARNING:** Temporal variability may be amplified or attenuated by protocol choices.
- **RD-PSEUDOREPLICATION WARNING:** Protocol drift can create apparent replication where none exists.
- **RD-CANONICAL WARNING:** Protocol drift can create multiple canonical values.
