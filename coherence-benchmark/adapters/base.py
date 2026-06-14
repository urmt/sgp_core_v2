"""Base adapter interface for real-world datasets."""

import numpy as np
from typing import Any


class DataAdapter:
    """Interface for loading/generating real-world benchmark datasets.

    Each adapter produces a tuple (data, metadata) where:
        data: np.ndarray of shape (n_components, n_timepoints)
        metadata: dict with keys:
            name: str
            description: str
            perturbation_time: int (time index of perturbation)
            n_components: int
            n_timepoints: int
            is_predictive: bool
    """

    def load(self) -> tuple[np.ndarray, dict[str, Any]]:
        raise NotImplementedError
