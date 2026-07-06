# Phase 018E — Abstract Optimization

## Date: 2026-07-06

### Paper 1 — Revised Abstract

> High-dimensional dynamical systems under global stabilization exhibit a characteristic collapse of their effective dimensionality, measured by the participation ratio PR, toward PR $\approx 1$. We analyze 21 recordings from rodent medial entorhinal cortex (MEC) and 22 synthetic dynamical conditions across five architectural classes. MEC covariance spectra follow a slow exponential decay with rate $\alpha = 0.039 \pm 0.018$ and participation ratio PR $= 37 \pm 20$, indicating broad but non-uniform spectral support. Synthetic stabilized systems cluster at $\alpha > 0.5$ and PR $< 3$. A reference curve $\text{PR} = (1+e^{-\alpha})/(1-e^{-\alpha})$, derived from a pure geometric series, provides a baseline for comparison: MEC spectra are systematically more concentrated than this reference, while collapsed synthetic systems cluster near it. The broad-spectrum organization resides in instantaneous correlation geometry rather than temporal propagation. These results provide a reproducible empirical characterization of spectral organization in MEC dynamics and identify the gap between biological correlation geometry and synthetic nulls as a target for mechanistic modeling.

**Reviewer read:** "Careful empirical study. Uses 21 MEC + 22 synthetic conditions. Foregrounds preprocessing-matched controls and reproducibility. No grand claims. Probably worth reading."

### Paper 2 — Revised Abstract

> Characterizing the spectral properties of neural covariance data requires careful comparison against appropriate null models. We analyze 21 recordings from rodent medial entorhinal cortex (MEC) and compare their eigenvalue and eigenvector statistics against four random matrix ensembles: GOE, shifted Wigner, sparse Erdős–Rényi, and Ising criticality. At fixed $N \approx 120$, MEC eigenvalue spectra are well-described by a shifted Wigner ensemble ($d = 0.51\sigma$) or an Ising model ($d = 0.51\sigma$), while eigenvector statistics match sparse $p=0.05$ correlations ($d = 0.86\sigma$). This partial agreement is a finite-size coincidence: subsampling analysis reveals that the MEC/sparse ensemble distance in eigenvector space grows as $d(N) \sim N^{2.2 \pm 0.1}$, strongly rejecting the hypothesis that MEC converges to the sparse null at larger $N$. The instantaneous precision geometry ($\alpha \approx 0.33$, PR $\approx 98$, $78\%$ sparsity) provides a richer spectral signature than temporal propagation operators ($\alpha \approx 0.01$). These results establish methodological requirements for null-model comparison in neural covariance analysis and demonstrate that finite-size effects can produce misleading ensemble agreement at experimentally accessible dimensions.

**Reviewer read:** "Methodological cautionary note. Shows finite-size effects can fool you. Scaling analysis resolves the ambiguity. Useful for the field."

### Key Qualities

| Criterion | Paper 1 | Paper 2 |
|-----------|---------|---------|
| No theory hype | ✅ | ✅ |
| Foregrounds controls | ✅ (22 synthetic conditions) | ✅ (4 null ensembles) |
| Minimizes interpretation | ✅ (empirical characterization) | ✅ (methodological requirements) |
| Statistical transparency | ✅ (α, PR, LC with ±SD) | ✅ (d values with σ units) |
| Conservative register | ✅ ("provides", "identify") | ✅ ("requires", "show") |
| No novelty framing | ✅ | ✅ |
| Reproducibility signal | ✅ | ✅ (implicit via scaling analysis) |

### Recommendation

Both abstracts are at target register. No further changes needed.
