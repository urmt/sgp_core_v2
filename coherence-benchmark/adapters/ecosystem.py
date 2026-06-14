"""Pilot A: Forest succession dataset.

Simulates temperate forest dynamics after drought perturbation.
Models competitive Lotka-Volterra dynamics with species-specific
drought tolerances and recovery rates.

Matches Cedar Creek LTER specification:
  - n=20 species per plot
  - 40 annual censuses
  - 24 plots with varied initial conditions
  - 1988 drought perturbation at t=5
"""

import numpy as np

from .base import DataAdapter
from typing import Any


RNG = np.random.default_rng(42)


def _lotka_volterra_step(
    abundances: np.ndarray,
    growth_rates: np.ndarray,
    competition: np.ndarray,
    env_stress: float,
    drought_tolerance: np.ndarray,
    noise: float = 0.02,
) -> np.ndarray:
    """Single step of competitive Lotka-Volterra with environmental stress.

    dN_i/dt = r_i * N_i * (1 - (sum_j α_ij N_j)/K_i) - s_i * stress * N_i
    """
    n = len(abundances)
    K = 100.0
    interaction = competition @ abundances / K
    growth = growth_rates * abundances * (1.0 - interaction)
    mortality = drought_tolerance * env_stress * abundances
    noise_term = RNG.normal(0, noise, n) * abundances
    new_abundances = abundances + growth - mortality + noise_term
    return np.maximum(new_abundances, 0.0)


def _generate_one_plot(
    n_species: int = 20,
    n_years: int = 40,
    drought_year: int = 5,
    seed: int | None = None,
) -> np.ndarray:
    """Generate one plot's species abundance time series."""
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = RNG

    growth_rates = rng.uniform(0.1, 0.4, n_species)
    drought_tolerance = rng.uniform(0.0, 1.0, n_species)

    competition = np.ones((n_species, n_species)) * 0.3
    np.fill_diagonal(competition, 1.0)
    for i in range(n_species):
        for j in range(n_species):
            if i != j:
                competition[i, j] *= rng.uniform(0.5, 1.5)

    abundances = rng.uniform(20, 80, n_species)
    species_abundances = [abundances.copy()]

    env_stress = 0.0
    for t in range(n_years):
        if t == drought_year:
            env_stress = 1.0
        elif t > drought_year:
            env_stress *= 0.7

        abundances = _lotka_volterra_step(
            abundances, growth_rates, competition,
            env_stress, drought_tolerance,
        )
        species_abundances.append(abundances.copy())

    return np.array(species_abundances).T


class EcosystemAdapter(DataAdapter):
    """Forest succession dataset (Pilot A)."""

    def __init__(
        self,
        n_plots: int = 24,
        n_species: int = 20,
        n_years: int = 40,
        drought_year: int = 5,
    ):
        self.n_plots = n_plots
        self.n_species = n_species
        self.n_years = n_years
        self.drought_year = drought_year

    def load(self, plot_index: int = 0) -> tuple[np.ndarray, dict[str, Any]]:
        if plot_index >= self.n_plots:
            raise ValueError(f"Only {self.n_plots} plots available")

        data = _generate_one_plot(
            n_species=self.n_species,
            n_years=self.n_years,
            drought_year=self.drought_year,
            seed=plot_index,
        )

        nonzero_var = np.nanvar(data, axis=1) > 1e-10
        data = data[nonzero_var]

        metadata = {
            "name": f"forest_succession_plot_{plot_index}",
            "description": f"Forest succession after drought — plot {plot_index} / {self.n_plots}, {data.shape[0]} surviving species",
            "perturbation_time": self.drought_year,
            "n_components": data.shape[0],
            "n_timepoints": self.n_years + 1,
            "is_predictive": True,
        }
        return data, metadata

    def load_all_plots(self) -> list[tuple[np.ndarray, dict[str, Any]]]:
        return [self.load(i) for i in range(self.n_plots)]
