"""
Kuramoto oscillator grid — Tier 1 external benchmark for Phase 005A.

Architecture:
  - 2D grid of N coupled phase oscillators
  - Nearest-neighbor coupling with strength K
  - Natural frequencies drawn from Lorentzian distribution
  - Noise term for perturbation

Metrics:
  - representational_ed: circular variance of phase distribution (phase dispersion)
  - functional_performance: global order parameter R (synchronization quality)

Falsification targets:
  - P1: Synchronization transitions may be too fast for short-timescale TRACK B
  - P2: Synchronization (function) and phase dispersion (rep) may be inseparable
  - Reversible phase-locking may eliminate hysteresis (weakens P1)
"""

import numpy as np


class KuramotoGridSystem:
    """
    2D Kuramoto oscillator grid with controllable coupling and noise.

    State: N oscillators, each with phase θ_i ∈ [0, 2π)
    Coupling K scales nearest-neighbor interactions.
    """

    def __init__(self, n_oscillators: int = 64, coupling: float = 1.0,
                 noise_std: float = 0.05, dt: float = 0.1, seed: int = 42):
        self.n = n_oscillators
        self.coupling = coupling
        self.noise_std = noise_std
        self.dt = dt
        self._rng = np.random.RandomState(seed)

        grid_size = int(np.sqrt(n_oscillators))
        while grid_size * grid_size < n_oscillators:
            grid_size += 1
        self.grid_size = grid_size
        self.n = grid_size * grid_size

        self.natural_freqs = self._rng.randn(self.n) * 0.5

        self.phases = self._rng.uniform(0, 2 * np.pi, self.n)

        self._neighbors = self._build_neighbors()

    def _build_neighbors(self):
        gs = self.grid_size
        neighbors = []
        for i in range(self.n):
            r, c = divmod(i, gs)
            nbrs = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < gs and 0 <= nc < gs:
                    nbrs.append(nr * gs + nc)
            neighbors.append(nbrs)
        return neighbors

    def step(self) -> float:
        phases = self.phases
        phase_diff = np.zeros(self.n)

        for i in range(self.n):
            diff_sum = 0.0
            for j in self._neighbors[i]:
                diff_sum += np.sin(phases[j] - phases[i])
            phase_diff[i] = self.natural_freqs[i] + self.coupling * diff_sum

        self.phases = phases + self.dt * phase_diff + self._rng.randn(self.n) * self.noise_std * np.sqrt(self.dt)
        self.phases = np.mod(self.phases, 2 * np.pi)

        return float(self._order_parameter())

    def representational_ed(self) -> float:
        return float(1.0 - self._order_parameter())

    def functional_performance(self) -> float:
        return float(self._order_parameter())

    def _order_parameter(self) -> float:
        return abs(np.mean(np.exp(1j * self.phases)))

    def phase_entropy(self, n_bins: int = 20) -> float:
        hist, _ = np.histogram(self.phases, bins=n_bins, range=(0, 2 * np.pi), density=True)
        hist = hist / (np.sum(hist) + 1e-10)
        return -float(np.sum(hist * np.log(hist + 1e-10)))
