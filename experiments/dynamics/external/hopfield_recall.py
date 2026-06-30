"""
Hopfield recall system — Tier 1 external benchmark for Phase 005A.

Architecture:
  - N-neuron Hopfield network with P stored random patterns
  - Hebbian weight matrix, asynchronous update
  - Coupling parameter scales weights (1.0 = full recall, 0.0 = random)
  - Noise injection provides perturbation for dynamics analysis

Metrics:
  - representational_ed: std of pattern overlaps (structure of memory space)
  - functional_performance: max overlap with nearest stored pattern (recall quality)

Falsification targets:
  - C2 (hysteresis): Hopfield with orthogonal patterns may show full reversibility
  - C3 (dissociation): Clean recall may mask altered representational geometry
  - P1 (timescale): Attractor convergence may be too fast for short-timescale TRACK B
"""

import numpy as np


class HopfieldRecallSystem:
    """
    Hopfield network with controllable coupling, noise, and seeded RNG.
    """

    def __init__(self, n_neurons: int = 100, n_patterns: int = 10,
                 coupling: float = 1.0, noise_std: float = 0.05,
                 seed: int = 42):
        self.n_neurons = n_neurons
        self.n_patterns = n_patterns
        self.coupling = coupling
        self.noise_std = noise_std
        self._step_count = 0
        self._seed = seed
        self._rng = np.random.RandomState(seed)

        self.patterns = self._rng.choice([-1, 1], size=(n_patterns, n_neurons)).astype(float)
        self._normalize_patterns()

        self.weights = self._compute_weights(self.patterns)
        self.state = self._initialize_state()

    def _normalize_patterns(self):
        for i in range(self.n_patterns):
            self.patterns[i] /= np.sqrt(self.n_neurons)

    def _compute_weights(self, patterns):
        W = patterns.T @ patterns
        np.fill_diagonal(W, 0.0)
        return W

    def _initialize_state(self) -> np.ndarray:
        target = self.patterns[0].copy()
        noise = self._rng.randn(self.n_neurons) * 0.3
        state = target + noise
        return state / np.linalg.norm(state)

    def step(self) -> float:
        self._step_count += 1
        order = self._rng.permutation(self.n_neurons)
        for i in order:
            field = (self.weights[i] @ self.state) * self.coupling
            field += self._rng.randn() * self.noise_std
            self.state[i] = np.tanh(field * 5.0)
        norm = np.linalg.norm(self.state)
        if norm > 0:
            self.state /= norm
        return float(np.max(self._overlaps()))

    def representational_ed(self) -> float:
        ov = self._overlaps()
        return float(np.std(ov)) if len(ov) > 0 else 0.0

    def functional_performance(self) -> float:
        ov = self._overlaps()
        return float(np.max(ov)) if len(ov) > 0 else 0.0

    def _overlaps(self) -> np.ndarray:
        return np.array([self.state @ p for p in self.patterns])

    def recall_quality(self) -> float:
        return float(np.max(self._overlaps()))

    def pattern_entropy(self) -> float:
        ov = np.abs(self._overlaps())
        total = np.sum(ov)
        if total < 1e-10:
            return 0.0
        probs = ov / total
        return -float(np.sum(probs * np.log(probs + 1e-10)))
