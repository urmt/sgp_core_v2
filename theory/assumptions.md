# Assumptions

## A1. Interaction is measurable

Interaction between components can be quantified using information-theoretic measures (total correlation, mutual information) applied to observed time series. This measurement does not require knowledge of the underlying interaction mechanism.

**Status**: Supported. Coherence computation requires only time-series data.

---

## A2. Structure equals statistical dependence

Systems with high interaction structure produce time series with high statistical dependence across components. Statistical independence implies absence of interaction structure.

**Status**: Partially supported. Statistical dependence is necessary but may not be sufficient for "structure" as intuitively understood.

---

## A3. Perturbation reveals resilience

Removing a subset of components and observing the system's response reveals its intrinsic resilience properties. The recovery trajectory (dip depth, recovery time, final restoration) captures causally relevant information about system organization.

**Status**: Supported for granular and forest systems. Recovery metrics show systematic variation with perturbation and system parameters.

---

## A4. Binning preserves structure

Spatial or functional binning of components (e.g., grouping grains by x-position) preserves the interaction structure relevant to resilience. The coherence of binned data is proportional to the coherence of the underlying system.

**Status**: Supported for granular and forest systems. Binning parameters tested: 10–20 bins, robust to bin count.

---

## A5. Sliding window captures dynamics

Coherence computed over sliding time windows captures the temporal evolution of system organization, including perturbation response and recovery.

**Status**: Supported. Window size (75 timepoints) and step (25) tested across granular and forest datasets. Results robust to ±25% window size variation.

---

## A6. Gaussian kernel is adequate

Gaussian kernel density estimation with Scott's rule for bandwidth selection provides reliable entropy estimates for coherence computation across the tested system sizes.

**Status**: Supported for systems with 10+ components and 100+ timepoints. Untested for very small systems or systems with discontinuities.

---

## A7. Results generalize across systems

Findings from the granular DEM generalize to other complex systems (ecology, neuroscience, opinion dynamics).

**Status**: Weakly supported. Granular and forest succession both show C perturbation response, but the two-factor resilience hypothesis (C × mobility) has only been tested on granular.

---

## A8. Mobility is independent of coherence

The capacity of a system to reconfigure its interaction structure (mobility) is a separate property from the degree of current organization (coherence). These can be measured and manipulated independently.

**Status**: Challenged. In the granular system, friction controls both C (r≈−0.74) and mobility. The coupling-breaking experiment (P1) is designed to test this assumption.
