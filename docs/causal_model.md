# Causal Model: Coherence, Mobility, and Recovery

## Current Best Model (M1)

```
Mobility ─────────► Recovery
    │
    ▼
Coherence ───────► Recovery
```

Recovery is jointly determined by coherence and mobility. Mobility has both a direct effect on recovery and an indirect effect through coherence.

## Alternative Models

### M0: C-only
```
Coherence ───────► Recovery
```
Failures: R² ≤ 0.10 for all targets; sign ambiguity; τ_rec ambiguity.

### M0b: Friction-only
```
Mobility ─────────► Recovery
```
Failures: R² ≤ 0.30; misses structure-specific contribution.

### M1: Additive
```
Coherence ───────► Recovery
Mobility ─────────► Recovery
```
Partial support: R² = 0.43 (ΔC), 0.31 (τ_rec), 0.50 (restoration). Better than either alone.

### M2: Interaction (best supported)
```
Coherence ───────► Recovery
Mobility ─────────► Recovery
Coherence × Mobility ──► Recovery
```
R² = 0.52 (ΔC), 0.35 (τ_rec), 0.56 (restoration). Interaction term adds explanatory power.

## Causal Ambiguity

### The collinearity problem

In the granular DEM, friction controls both coherence and mobility:
```
Friction ───────► Mobility (direct: dissipation)
Friction ───────► Coherence (via packing structure)
```

Correlation: r(C_pre, friction) ≈ −0.74.

This means the data cannot cleanly distinguish:

1. C is causal, and friction is merely a proxy for low-C states
2. Mobility is causal, and C is merely a correlate
3. Both are causal and interact (current best model M2)

### What we would need to resolve this

An experiment where C and mobility can be independently varied. For example:

- Same friction (same mobility physics), different C → test if C independently affects recovery
- Same C, different friction (different mobility) → test if mobility independently affects recovery

If C is causal: varying C at fixed friction changes recovery.
If mobility is causal: varying friction at fixed C changes recovery.
If interaction is causal: both manipulations change recovery, and the effect of one depends on the level of the other.

## Proposed Causal Diagram Update (Pending P1)

```
Polydispersity ──► Coherence ──┐
                               ├──► Recovery
Friction ────────► Mobility ───┘
      │                           
      └───────────── Coherence × Mobility ──► Recovery
```

## What is at stake

| Finding | Interpretation | Action |
|---------|---------------|--------|
| C alone → recovery | Object-first: structure is primary | Reduce mobility research |
| Mobility alone → recovery | Interaction-first: dynamics are primary | Reduce C research |
| C × mobility → recovery | Both needed: structure in context | Continue two-factor program |
| Neither → recovery | Wrong framing entirely | Restart from fundamentals |
