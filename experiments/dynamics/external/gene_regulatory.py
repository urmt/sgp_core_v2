"""
Gene regulatory cascade — Tier 1 external benchmark for Phase 005A.

Architecture:
  - N genes with sigmoidal activation dynamics
  - Feed-forward cascade topology (layered regulation)
  - Coupling = regulatory interaction strength
  - Functional task: maintain target expression pattern

Metrics:
  - representational_ed: variance of gene expression levels (diversity)
  - functional_performance: overlap with target expression pattern

Falsification targets:
  - P1: Cascade systems have delayed coupling effects — TRACK B may be weaker
  - P2: Expression noise can decouple representation from function
  - Precursors may emerge as expression variance collapses before function degrades
"""

import numpy as np


class GeneRegulatorySystem:
    """
    Feed-forward gene regulatory cascade with controllable coupling.

    Topology: layered (input → hidden → output) with sparse regulatory weights.
    Coupling scales all weights.
    """

    def __init__(self, n_genes: int = 50, coupling: float = 1.0,
                 noise_std: float = 0.02, seed: int = 42):
        self.n = n_genes
        self.coupling = coupling
        self.noise_std = noise_std
        self._rng = np.random.RandomState(seed)

        n_layers = 4
        layer_sizes = [n_genes // 4] * n_layers
        layer_sizes[-1] = n_genes - sum(layer_sizes[:-1])

        self._layer_sizes = layer_sizes
        self._layer_boundaries = np.cumsum([0] + layer_sizes)

        W_reg = np.zeros((n_genes, n_genes))
        for li in range(n_layers - 1):
            start_i = self._layer_boundaries[li]
            end_i = self._layer_boundaries[li + 1]
            start_j = self._layer_boundaries[li + 1]
            end_j = self._layer_boundaries[li + 2]
            block = self._rng.randn(end_i - start_i, end_j - start_j) * 0.5
            W_reg[start_i:end_i, start_j:end_j] = block

        self._W_raw = W_reg

        self.expression = self._rng.uniform(0.3, 0.7, n_genes)

        self._target = np.zeros(n_genes)
        middle = n_genes // 2
        self._target[middle:] = 1.0

    @property
    def W(self):
        return self._W_raw * self.coupling

    def step(self) -> float:
        input_sum = self.W.T @ self.expression
        activation = 1.0 / (1.0 + np.exp(-input_sum + 0.5))
        decay = self.expression * 0.1
        self.expression = self.expression + activation - decay
        self.expression += self._rng.randn(self.n) * self.noise_std
        self.expression = np.clip(self.expression, 0, 2)
        return float(np.mean(self.expression))

    def representational_ed(self) -> float:
        return float(np.std(self.expression))

    def functional_performance(self) -> float:
        diff = self.expression - self._target
        return float(1.0 / (1.0 + np.mean(diff ** 2)))
