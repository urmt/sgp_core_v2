"""IF-2: Objectness as persistence of interaction topology.

Instead of measuring objects as persistent particles,
measure objectness as persistence of interaction structure.
"""

import numpy as np
from typing import Any


def _build_interaction_matrix(
    events: list[dict[str, Any]],
    n_entities: int,
    window_size: int,
) -> np.ndarray:
    """Build co-occurrence matrix from event stream.

    Returns (n_entities x n_entities) matrix where entry (i,j) counts
    how many times entities i and j interacted in the given window.
    """
    matrix = np.zeros((n_entities, n_entities))
    for e in events:
        parts = e.get("participants", [])
        if len(parts) >= 2:
            i, j = parts[0], parts[1]
            if i < n_entities and j < n_entities:
                matrix[i, j] += 1.0
                matrix[j, i] += 1.0
    return matrix


def compute_persistence(
    events: list[dict[str, Any]],
    n_entities: int,
    window_size: int = 50,
    threshold: float = 0.0,
) -> dict[str, Any]:
    """Measure objectness as persistence of interaction topology.

    For each pair (i,j), compute the fraction of time windows in which
    they interact. A high persistence score means the interaction is stable.

    Returns:
        pair_persistence: (n_entities x n_entities) persistence matrix.
        entity_stability: per-entity mean persistence of its top-k partners.
        objectness_score: scalar — how much structure is in the interaction graph.
    """
    if len(events) == 0:
        return {"error": "no events"}

    times = np.array([e.get("time", 0) for e in events])
    t_min, t_max = times.min(), times.max()
    n_windows = max(1, (t_max - t_min) // window_size)

    pair_counts = np.zeros((n_entities, n_entities))

    for w in range(n_windows):
        start_t = t_min + w * window_size
        end_t = start_t + window_size
        window_events = [
            e for e in events
            if start_t <= e.get("time", 0) < end_t
        ]
        mat = _build_interaction_matrix(window_events, n_entities, window_size)
        pair_counts += (mat > threshold).astype(float)

    pair_persistence = pair_counts / n_windows

    entity_stability = np.array([
        np.mean(np.sort(pair_persistence[i])[-3:])
        for i in range(n_entities)
    ])

    mean_persistence = pair_persistence[pair_persistence > 0].mean()
    sparsity = np.mean(pair_persistence > 0)

    objectness_score = mean_persistence * sparsity

    return {
        "pair_persistence": pair_persistence,
        "entity_stability": entity_stability,
        "mean_persistence": float(mean_persistence),
        "sparsity": float(sparsity),
        "objectness_score": float(objectness_score),
        "n_windows": n_windows,
        "n_entities": n_entities,
    }


def compare_to_ground_truth(
    pair_persistence: np.ndarray,
    ground_truth_labels: np.ndarray,
) -> dict[str, float]:
    """Check if persistent interaction pairs match ground truth communities.

    Uses silhouette-like score: within-community persistence vs between-community.
    """
    n = len(ground_truth_labels)
    within = []
    between = []
    for i in range(n):
        for j in range(i + 1, n):
            p = pair_persistence[i, j]
            if ground_truth_labels[i] == ground_truth_labels[j]:
                within.append(p)
            else:
                between.append(p)

    within_mean = np.mean(within) if within else 0.0
    between_mean = np.mean(between) if between else 0.0
    separation = within_mean - between_mean

    return {
        "within_community_persistence": float(within_mean),
        "between_community_persistence": float(between_mean),
        "separation": float(separation),
        "relative_separation": float(
            separation / max(within_mean, 1e-10)
        ),
    }
