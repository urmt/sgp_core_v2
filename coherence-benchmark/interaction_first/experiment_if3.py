"""IF-3: Reconstruct objects from interaction history alone.

Input: interaction events only (no entity labels, no object IDs).
Output: discovered groups (emergent objects).

Validates against ground truth communities when available.
"""

import numpy as np
from typing import Any


def _global_cooccurrence(events: list[dict[str, Any]], n_entities: int) -> np.ndarray:
    """Build global co-occurrence matrix: how many times each pair interacted."""
    mat = np.zeros((n_entities, n_entities))
    for e in events:
        parts = e.get("participants", [])
        if len(parts) >= 2:
            i, j = parts[0], parts[1]
            mat[i, j] += 1.0
            mat[j, i] += 1.0
    return mat


def _randomization_baseline(
    events: list[dict[str, Any]],
    n_entities: int,
    n_shuffles: int = 100,
    seed: int = 42,
) -> np.ndarray:
    """Compute expected co-occurrence under random interaction null.

    Shuffle participant IDs within each event to break structure.
    """
    rng = np.random.default_rng(seed)
    base_mat = _global_cooccurrence(events, n_entities)
    expected = np.zeros_like(base_mat)

    for s in range(n_shuffles):
        shuffled = []
        for e in events:
            parts = list(e.get("participants", []))
            rng.shuffle(parts)
            shuffled.append({**e, "participants": parts})
        expected += _global_cooccurrence(shuffled, n_entities)

    return expected / n_shuffles


def spectral_reconstruction(
    events: list[dict[str, Any]],
    n_entities: int,
    n_clusters: int | None = None,
    significance_filter: bool = True,
    seed: int = 42,
) -> dict[str, Any]:
    """Reconstruct object-like groups via spectral clustering on interaction matrix.

    Steps:
        1. Build interaction co-occurrence matrix from event stream.
        2. Subtract random baseline (shuffled-participant null).
        3. Normalize by degree (symmetric normalized Laplacian).
        4. Spectral clustering on the significant interaction graph.

    Returns:
        labels: discovered cluster assignments.
        silhouette: quality of discovered clusters.
    """
    from sklearn.cluster import SpectralClustering
    from sklearn.metrics import silhouette_score

    rng = np.random.default_rng(seed)
    cooc = _global_cooccurrence(events, n_entities)

    if significance_filter:
        baseline = _randomization_baseline(events, n_entities, n_shuffles=50, seed=seed)
        adjacency = np.maximum(cooc - baseline, 0)
    else:
        adjacency = cooc.copy()

    degrees = adjacency.sum(axis=1)
    mask = degrees > 0
    if mask.sum() < 2:
        return {"error": "too few interacting entities"}

    adj_sub = adjacency[mask][:, mask]
    if n_clusters is None:
        n_clusters = max(2, int(np.sqrt(mask.sum())))

    n_valid = min(n_clusters, mask.sum() - 1)

    clf = SpectralClustering(
        n_clusters=max(2, n_valid),
        affinity="precomputed",
        random_state=seed,
        assign_labels="kmeans",
    )
    labels_full = np.full(n_entities, -1)
    labels_sub = clf.fit_predict(adj_sub)
    labels_full[mask] = labels_sub + 0

    sil = -1.0
    if len(np.unique(labels_sub)) > 1 and len(labels_sub) > 1:
        sil = silhouette_score(adj_sub, labels_sub, metric="precomputed")

    return {
        "labels": labels_full,
        "n_discovered": int(len(np.unique(labels_full[labels_full >= 0]))),
        "silhouette": float(sil),
        "n_clusters_requested": n_clusters,
        "significance_filtered": significance_filter,
    }


def reconstruct_from_interaction_history(
    events: list[dict[str, Any]],
    n_entities: int,
    ground_truth_labels: np.ndarray | None = None,
) -> dict[str, Any]:
    """Full reconstruction pipeline: IF-3 single-call interface.

    Runs spectral reconstruction, evaluates against ground truth if available.
    """
    result = spectral_reconstruction(events, n_entities, significance_filter=True)
    if "error" in result:
        result = spectral_reconstruction(events, n_entities, significance_filter=False)

    if "error" in result:
        return result

    if ground_truth_labels is not None:
        from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

        labels_pred = result["labels"]
        valid = labels_pred >= 0
        if valid.sum() > 0:
            ari = adjusted_rand_score(ground_truth_labels[valid], labels_pred[valid])
            nmi = normalized_mutual_info_score(
                ground_truth_labels[valid], labels_pred[valid]
            )
            result["ari"] = float(ari)
            result["nmi"] = float(nmi)

    return result
