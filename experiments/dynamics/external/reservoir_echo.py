"""
Reservoir computer (echo state network) — Tier 1 external benchmark for Phase 005A.

Architecture:
  - N-unit reservoir with random recurrent weights
  - Input-driven dynamics with trained linear readout
  - Spectral radius controls echo state property (coupling analog)
  - Readout trained via ridge regression on a memory task

Metrics:
  - representational_ed: variance of reservoir unit activations (state richness)
  - functional_performance: 1 - normalized MSE on memory task (recall quality)

Falsification targets:
  - P2 strongest test: reservoir states drift while readout remains stable
  - Behavioral stability masking representational drift is the key hypothesis
  - Hysteresis may emerge in latent trajectories even with stable function
"""

import numpy as np


class ReservoirSystem:
    """
    Echo state network with trained readout and controllable spectral radius.

    Coupling = spectral radius of reservoir weights.
    Low coupling (< 1) → echo state property holds, stable dynamics.
    High coupling (> 1) → edge of chaos, unstable dynamics.
    """

    def __init__(self, n_units: int = 100, coupling: float = 0.9,
                 noise_std: float = 0.01, input_dim: int = 1,
                 seed: int = 42):
        self.n = n_units
        self.coupling = coupling
        self.noise_std = noise_std
        self.input_dim = input_dim
        self._rng = np.random.RandomState(seed)

        self._W_raw = self._rng.randn(n_units, n_units) * 0.5
        eigvals = np.linalg.eigvals(self._W_raw)
        max_eig = max(abs(e) for e in eigvals)
        self._W_raw = self._W_raw / (max_eig + 1e-10)

        self.W_in = self._rng.randn(n_units, input_dim) * 0.2

        self.state = np.zeros(n_units)
        self._step_count = 0
        self._trained = False

    @property
    def W(self):
        return self._W_raw * self.coupling

    def step(self) -> float:
        u = np.array([np.sin(self._step_count * 0.1)])

        state_update = np.tanh(self.W @ self.state + self.W_in @ u)
        state_update += self._rng.randn(self.n) * self.noise_std
        self.state = state_update

        self._step_count += 1

        if self._trained:
            pred = (self.W_out.T @ self.state).item()
            target = self._target(self._step_count).item()
            err = (pred - target) ** 2
            return 1.0 / (1.0 + err)
        return float(np.mean(np.abs(self.state)))

    def representational_ed(self) -> float:
        if not self._trained:
            self.train_readout()
        return float(np.std(self.state))

    def functional_performance(self) -> float:
        if not self._trained:
            self.train_readout()
        pred = (self.W_out.T @ self.state).item()
        target = self._target(self._step_count).item()
        return 1.0 / (1.0 + (pred - target) ** 2)

    def _target(self, t: int) -> np.ndarray:
        return np.array([np.sin(t * 0.2)])

    def train_readout(self, warmup: int = 100, train_steps: int = 500, ridge_alpha: float = 1e-4):
        states = []
        targets = []
        for t in range(warmup + train_steps):
            u = np.array([np.sin(t * 0.1)])
            self.state = np.tanh(self.W @ self.state + self.W_in @ u)
            self.state += self._rng.randn(self.n) * self.noise_std
            if t >= warmup:
                states.append(self.state.copy())
                targets.append(self._target(t))

        X = np.array(states)
        Y = np.array(targets)
        self.W_out = np.linalg.solve(X.T @ X + ridge_alpha * np.eye(self.n), X.T @ Y)
        self._trained = True
