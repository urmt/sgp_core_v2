# RD-PSEUDOREPLICATION WARNING

**Source:** Research Director (RD-WELL.8A.R2 authorization)
**Status:** ACTIVE WARNING
**Date:** 2026-06-17

## Statement

**"Multiple measurements drawn from the same underlying realization may create the appearance of replication without providing independent evidence."**

This warning now becomes central to the program.

## Evidence

RD-WELL.8A.R1 reported N=5 for GS, RB, AM. Upon inspection, these were:
- 5 temporal samples from a single trajectory
- Not 5 independent replications

Temporal samples from the same trajectory are **pseudoreplicates** — they share the same underlying realization and are therefore not independent.

## Distinction

| Type | Independence | Evidence Strength |
|------|--------------|-------------------|
| Independent replication | High | Strong |
| Temporal sampling | Low (same trajectory) | Weak |
| Transform sampling | Zero (same data) | None |

## Required Protocol

1. **Define replication unit explicitly.** The project must choose: trajectory, parameter regime, timestep, slice, or transform.
2. **Report unique trajectories, not total measurements.**
3. **Distinguish temporal sampling from replication.**
4. **Never report N without specifying what N counts.**

## Relationship to Other Warnings

- **RD-COVERAGE WARNING:** Coverage may be apparent rather than real.
- **RD-CI RULE:** Confidence intervals require independent samples.
- **RD-SMALL-N WARNING:** Few independent replications may generate unstable estimates.
