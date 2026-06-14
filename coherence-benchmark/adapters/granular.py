"""Pilot B: Granular relaxation dataset.

Simulates 2D granular packing under gravity after partial removal.
Uses soft-sphere discrete element method with contact forces.

Matches T920 specification:
  - n=100 grains (reduced from 1000 for tractability)
  - 2000 time steps
  - Remove 10% of grains at t=500
  - Monitor reorganization (positions → C metric)
"""

import numpy as np

from .base import DataAdapter
from typing import Any


RNG = np.random.default_rng(42)


def _soft_sphere_force(
    dx: float, dy: float,
    r1: float, r2: float,
    stiffness: float = 500.0,
    damping: float = 2.0,
) -> tuple[float, float, float]:
    """Compute contact force between two soft spheres.

    Returns (fx, fy, overlap_magnitude).
    """
    dist = np.sqrt(dx * dx + dy * dy)
    overlap = r1 + r2 - dist
    if overlap <= 0:
        return 0.0, 0.0, 0.0

    nx, ny = dx / dist, dy / dist
    fn = stiffness * overlap
    return fn * nx, fn * ny, overlap


def _generate_granular_run(
    n_grains: int = 100,
    n_steps: int = 2000,
    removal_step: int = 500,
    removal_fraction: float = 0.1,
    seed: int = 42,
) -> np.ndarray:
    """Run granular DEM simulation.

    Returns:
        positions: (n_grains, n_steps) array of y-positions.
    """
    rng = np.random.default_rng(seed)

    radii = rng.uniform(0.8, 1.5, n_grains)
    masses = radii ** 2

    box_width = 40.0

    x = rng.uniform(2, box_width - 2, n_grains)
    y = rng.uniform(5, 30, n_grains)
    vx = rng.uniform(-0.5, 0.5, n_grains)
    vy = rng.uniform(-0.5, 0.5, n_grains)

    gy = -1.0
    dt = 0.01
    stiffness = 500.0
    damping = 2.0
    friction = 0.3

    n_remove = max(1, int(n_grains * removal_fraction))
    removed = np.zeros(n_grains, dtype=bool)

    all_x = np.zeros((n_grains, n_steps))
    all_positions = np.zeros((n_grains, n_steps))

    for step in range(n_steps):
        if step == removal_step:
            remove_idx = rng.choice(
                np.where(~removed)[0], size=n_remove, replace=False
            )
            removed[remove_idx] = True

        forces_x = np.zeros(n_grains)
        forces_y = np.full(n_grains, gy * masses)

        for i in range(n_grains):
            if removed[i]:
                continue
            for j in range(i + 1, n_grains):
                if removed[j]:
                    continue
                dx = x[j] - x[i]
                dy = y[j] - y[i]
                if abs(dx) > 3.0 or abs(dy) > 3.0:
                    continue
                fx, fy, ov = _soft_sphere_force(
                    dx, dy, radii[i], radii[j], stiffness, damping
                )
                forces_x[i] += fx
                forces_y[i] += fy
                forces_x[j] -= fx
                forces_y[j] -= fy

            vx[i] += forces_x[i] / masses[i] * dt
            vy[i] += forces_y[i] / masses[i] * dt

            vx[i] *= (1.0 - friction * dt)
            vy[i] *= (1.0 - friction * dt)

            x[i] += vx[i] * dt
            y[i] += vy[i] * dt

            if x[i] - radii[i] < 0:
                x[i] = radii[i]
                vx[i] *= -0.5
            elif x[i] + radii[i] > box_width:
                x[i] = box_width - radii[i]
                vx[i] *= -0.5
            if y[i] - radii[i] < 0:
                y[i] = radii[i]
                vy[i] *= -0.5

        all_x[:, step] = np.where(removed, np.nan, x)
        all_positions[:, step] = np.where(removed, np.nan, y)

    return all_positions, all_x


class GranularAdapter(DataAdapter):
    """Granular relaxation dataset (Pilot B)."""

    def __init__(
        self,
        n_grains: int = 100,
        n_steps: int = 2000,
        removal_step: int = 500,
        removal_fraction: float = 0.1,
    ):
        self.n_grains = n_grains
        self.n_steps = n_steps
        self.removal_step = removal_step
        self.removal_fraction = removal_fraction

    def load(self, seed: int = 42) -> tuple[np.ndarray, dict[str, Any]]:
        positions_y, positions_x = _generate_granular_run(
            n_grains=self.n_grains,
            n_steps=self.n_steps,
            removal_step=self.removal_step,
            removal_fraction=self.removal_fraction,
            seed=seed,
        )

        nan_mask = np.isnan(positions_y)
        col_means = np.nanmean(positions_y, axis=1, keepdims=True)
        positions_y = np.where(nan_mask, col_means, positions_y)

        with np.errstate(invalid="ignore"):
            final_x = np.nanmean(positions_x[:, -100:], axis=1)
        final_x = np.where(np.isnan(final_x),
                           np.nanmean(positions_x[:, :500], axis=1),
                           final_x)
        order = np.argsort(final_x)
        n_bins = min(20, self.n_grains // 5)
        bins = np.array_split(order, n_bins)
        binned_data = np.array([
            np.mean(positions_y[b], axis=0) for b in bins
        ])

        metadata = {
            "name": "granular_relaxation",
            "description": (
                f"2D granular packing, {self.n_grains} grains → {n_bins} spatial bins, "
                f"{self.removal_fraction*100:.0f}% removed at t={self.removal_step}"
            ),
            "perturbation_time": self.removal_step,
            "n_components": n_bins,
            "n_timepoints": self.n_steps,
            "is_predictive": False,
        }
        return binned_data, metadata
