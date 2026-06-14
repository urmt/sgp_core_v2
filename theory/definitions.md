# Definitions

## Metric

### Coherence (C)

A unitless scalar in [0, 1] measuring the fraction of total system entropy that arises from joint (interaction) structure rather than component-level randomness.

\[
C = \frac{T}{T + \sum_i H_i}
\]

- T = total correlation = KL divergence between joint distribution and product of marginals
- H_i = Shannon entropy of component i's marginal distribution

Higher C → more coordinated system.

### Total Correlation (T)

The mutual information extended to multiple variables:

\[
T(X_1, \ldots, X_n) = \sum_i H(X_i) - H(X_1, \ldots, X_n)
\]

T = 0 iff all variables are independent.

---

## System Properties

### Interaction Structure

The pattern of statistical dependencies among components, as measured by total correlation. Does not imply direct causal coupling — statistical dependence can arise through indirect pathways.

### Mobility

The capacity of a system to reconfigure its interaction structure within a given time window. Proxies:
- **MSD** (mean squared displacement): average squared distance traveled by components over a time interval
- **RMS velocity**: root-mean-square of component velocities
- **Neighbor turnover**: rate at which nearest-neighbor pairs change
- **Local packing variance**: standard deviation of nearest-neighbor distances

### Resilience

The capacity of a system to recover interaction structure after perturbation. Measured by:
- **ΔC (dip)**: C_pre − C_min; the maximum drop in coherence after perturbation
- **τ_rec**: time steps until C returns to pre-perturbation level
- **Restoration**: C_final / C_pre; fraction of pre-perturbation coherence achieved

---

## Experimental

### Friction (DEM parameter)

Coefficient of Coulomb friction in the discrete element method. Ranges [0, 1]. Controls energy dissipation per collision — higher friction → less grain rearrangement → lower mobility.

### Polydispersity

Spread of grain radii in the DEM. Quantified as [r_min, r_max]. Higher polydispersity → more disordered packing → lower C at fixed friction.

### Removal Perturbation

A fraction (typically 10%) of components are removed at a specific time point. The system is then allowed to evolve, and recovery metrics are measured from the coherence trajectory.

---

## Ontology

### Interaction-First Ontology

The position that interaction patterns are the fundamental units of reality, and objects are derivative phenomena (stable interaction patterns). Contrasts with object-first realism where objects have independent existence and interactions are secondary.

### Emergence

The appearance of properties at a system level that are not present at the component level, arising from interaction structure among components.

### Metastability

A temporary stabilization of interaction structure that persists for some time scale but may transform. The characteristic time scale of metastability is system-dependent.
