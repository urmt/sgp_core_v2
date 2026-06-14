# Structured Geometry Program (SGP)

## Core Claim

Interaction dynamics within complex systems can be represented as geometrical structure on a latent manifold, and this geometrical representation captures causally relevant properties that are invisible to standard statistical summaries.

## Mathematical Framework

### Coherence (C)

The central observable. Measures how much the joint behavior of a system departs from statistical independence:

\[
C = \frac{T}{T + \sum_i H_i}
\]

Where:
- \(T\) = total correlation (mutual information across all components)
- \(H_i\) = marginal entropy of component \(i\)

C ranges from 0 (independent components) to 1 (fully coordinated).

### Structural Invariants

SGP identifies properties that persist under certain transformations:
- **Operator closure**: The space of allowed interaction structures forms a closed algebra
- **Replay invariance**: Systems can regenerate dynamics from compressed representations
- **Conservation laws**: Certain interaction structures are conserved under dynamical evolution

### Latent Geometry

High-dimensional interaction data can be projected onto a lower-dimensional manifold where:
- Distance corresponds to difference in interaction pattern, not feature space
- Geodesics correspond to minimal transformation paths between interaction states
- Curvature corresponds to interaction complexity

## Operational Claims

1. **Coherence discriminates structure** — C separates structured from unstructured dynamics across domains (ecology, granular physics, neuroscience, opinion dynamics)
2. **Perturbation detection** — C drops detectably at perturbation boundaries, with higher SNR than competitor metrics (predictive information, statistical complexity, MSE)
3. **Recovery measurement** — Post-perturbation C trajectories reveal system resilience properties not visible in aggregate statistics
4. **Reconstruction** — Interaction structure can be recovered from partial observations when coherence is high

## Status

The formal framework is stable. Individual claims have varying evidence support. See `/results/EVIDENCE_LEDGER.md` for current status of each claim.

## Open Questions

- Is coherence sufficient to characterize recovery, or is a second factor (mobility) required?
- Does the latent manifold exist independently of the coherence metric?
- What is the relationship between SGP coherence and other information-theoretic measures?
