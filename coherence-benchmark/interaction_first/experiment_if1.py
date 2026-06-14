"""IF-1: Systems with interaction-only description.

No predefined objects. Only interaction events.
"""

import numpy as np
from typing import Any


def particle_collisions(
    n_entities: int = 20,
    n_events: int = 2000,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Generate collision events between anonymous entities.

    Entities move in 2D. Collisions occur when distance < threshold.
    Record only the collision events: {time, participants}.
    """
    rng = np.random.default_rng(seed)

    positions = rng.uniform(0, 100, (n_entities, 2))
    velocities = rng.uniform(-2, 2, (n_entities, 2))

    events = []
    for t in range(n_events):
        positions += velocities

        for i in range(n_entities):
            for j in range(i + 1, n_entities):
                dist = np.linalg.norm(positions[i] - positions[j])
                if dist < 3.0:
                    events.append({
                        "time": t,
                        "participants": [int(i), int(j)],
                        "type": "collision",
                    })
                    v_rel = velocities[i] - velocities[j]
                    v_rel_norm = v_rel / max(dist, 1e-10)
                    velocities[i] -= 0.5 * np.dot(v_rel, v_rel_norm) * v_rel_norm
                    velocities[j] += 0.5 * np.dot(v_rel, v_rel_norm) * v_rel_norm

        # Wrap around
        positions = positions % 100

    return events


def game_of_life(
    grid_size: int = 20,
    n_steps: int = 500,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Game of Life. Record each cell state change as an interaction event.

    An event records: {time, cell, triggered_by} where triggered_by is the
    list of neighboring cells whose state influenced this change.
    """
    rng = np.random.default_rng(seed)
    grid = rng.integers(0, 2, (grid_size, grid_size))
    events = []

    for t in range(n_steps):
        new_grid = grid.copy()
        for i in range(grid_size):
            for j in range(grid_size):
                neighbors = []
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = (i + di) % grid_size, (j + dj) % grid_size
                        if grid[ni, nj]:
                            neighbors.append(ni * grid_size + nj)

                n_alive = len(neighbors)
                idx = i * grid_size + j
                if grid[i, j] == 1 and (n_alive < 2 or n_alive > 3):
                    new_grid[i, j] = 0
                    events.append({
                        "time": t, "cell": idx,
                        "type": "death", "triggered_by": neighbors,
                    })
                elif grid[i, j] == 0 and n_alive == 3:
                    new_grid[i, j] = 1
                    events.append({
                        "time": t, "cell": idx,
                        "type": "birth", "triggered_by": neighbors,
                    })
        grid = new_grid

    return events


def persistent_communities(
    n_entities: int = 30,
    n_communities: int = 3,
    n_steps: int = 500,
    within_prob: float = 0.3,
    between_prob: float = 0.02,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Dynamic interaction graph with planted persistent communities.

    Edges appear/disappear each step. Within-community edges are much more
    likely to persist than between-community edges.
    Communities are the ground-truth "objects."

    Returns interaction events: {time, participants: [i, j], weight}.
    """
    rng = np.random.default_rng(seed)
    events = []
    comm_size = n_entities // n_communities
    labels = np.repeat(range(n_communities), comm_size)[:n_entities]

    # Track active edges
    active = set()
    for i in range(n_entities):
        for j in range(i + 1, n_entities):
            p = within_prob if labels[i] == labels[j] else between_prob
            if rng.random() < p:
                active.add((i, j))

    for t in range(n_steps):
        # Record currently active edges as interaction events
        for i, j in active:
            events.append({
                "time": t,
                "participants": [i, j],
                "type": "interaction",
                "ground_truth_community": [int(labels[i]), int(labels[j])],
            })

        # Update edges: each survives with prob depending on community
        new_active = set()
        for i, j in active:
            p_keep = 0.9 if labels[i] == labels[j] else 0.3
            if rng.random() < p_keep:
                new_active.add((i, j))

        # Add new edges
        for i in range(n_entities):
            for j in range(i + 1, n_entities):
                if (i, j) not in new_active:
                    p = within_prob * 0.1 if labels[i] == labels[j] else between_prob * 0.1
                    if rng.random() < p:
                        new_active.add((i, j))

        active = new_active

    return events, labels
