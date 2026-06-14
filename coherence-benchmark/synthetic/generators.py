import numpy as np


def independent(n_components: int = 20, n_timepoints: int = 500, seed: int = 42):
    """Each component is i.i.d. N(0,1) noise. True C ≈ 0."""
    rng = np.random.default_rng(seed)
    return rng.normal(0, 1, (n_components, n_timepoints))


def coupled_markov(
    n_components: int = 10,
    n_timepoints: int = 1000,
    coupling: float = 0.4,
    noise: float = 0.1,
    seed: int = 42,
):
    """Each component is AR(1) driven by a common latent factor.

    X_i[t] = alpha * X_i[t-1] + coupling * Z[t-1] + epsilon_i[t]
    Z[t] = 0.9 * Z[t-1] + eta[t]

    coupling=0.0 -> C≈0, coupling large -> C→1.
    """
    rng = np.random.default_rng(seed)
    common_coupling = coupling
    self_coupling = 0.5

    Z = np.zeros(n_timepoints)
    X = rng.normal(0, 1, (n_components, n_timepoints))

    Z[0] = rng.normal(0, 1)
    for t in range(1, n_timepoints):
        Z[t] = 0.9 * Z[t-1] + rng.normal(0, 0.2)
        for i in range(n_components):
            X[i, t] = (self_coupling * X[i, t-1]
                       + common_coupling * Z[t-1]
                       + rng.normal(0, noise))
    return X


def fully_coupled(n_components: int = 10, n_timepoints: int = 500, seed: int = 42):
    """All components are identical copies. True C → 1 as n_components grows."""
    rng = np.random.default_rng(seed)
    base = rng.normal(0, 1, n_timepoints)
    return np.tile(base, (n_components, 1))


def modular(
    n_per_module: int = 4,
    n_modules: int = 3,
    n_timepoints: int = 1000,
    within: float = 0.5,
    between: float = 0.1,
    noise: float = 0.2,
    seed: int = 42,
):
    """Block-diagonal coupling via module-specific latent drivers.

    Each module has a private latent driver Z_m[t]. Components within a module
    share that driver. A weak global driver provides between-module coupling.
    """
    rng = np.random.default_rng(seed)
    n = n_per_module * n_modules

    X = rng.normal(0, 1, (n, n_timepoints))

    # Module-specific latent drivers
    Z_mod = np.zeros((n_modules, n_timepoints))
    for m in range(n_modules):
        Z_mod[m, 0] = rng.normal(0, 1)
        for t in range(1, n_timepoints):
            Z_mod[m, t] = 0.8 * Z_mod[m, t-1] + rng.normal(0, 0.3)

    # Global driver for between-module coupling
    Z_global = np.zeros(n_timepoints)
    Z_global[0] = rng.normal(0, 1)
    for t in range(1, n_timepoints):
        Z_global[t] = 0.8 * Z_global[t-1] + rng.normal(0, 0.3)

    for t in range(1, n_timepoints):
        for m in range(n_modules):
            start = m * n_per_module
            end = (m + 1) * n_per_module
            for i in range(start, end):
                X[i, t] = (0.3 * X[i, t-1]
                           + within * Z_mod[m, t-1]
                           + between * Z_global[t-1]
                           + rng.normal(0, noise))
    return X


def hierarchical(
    base_n: int = 8,
    n_levels: int = 3,
    n_timepoints: int = 1500,
    micro_coupling: float = 0.4,
    seed: int = 42,
):
    """Three-level hierarchy with independent AR(1) at each level.

    Micro, meso, and macro components evolve independently but share
    a weak global signal, creating scale-dependent structure.
    """
    rng = np.random.default_rng(seed)

    n_micro = base_n
    n_meso = max(base_n // 2, 2)
    n_macro = max(base_n // 4, 1)
    n_total = n_micro + n_meso + n_macro

    X = np.zeros((n_total, n_timepoints))
    for i in range(n_total):
        X[i, 0] = rng.normal(0, 1)

    # Shared weak signal
    common = np.zeros(n_timepoints)
    common[0] = rng.normal(0, 1)
    for t in range(1, n_timepoints):
        common[t] = 0.7 * common[t-1] + rng.normal(0, 0.3)

    for t in range(1, n_timepoints):
        for i in range(n_micro):
            X[i, t] = 0.5 * X[i, t-1] + micro_coupling * common[t-1] + rng.normal(0, 0.2)

        for j in range(n_meso):
            X[n_micro + j, t] = 0.5 * (X[n_micro + j, t-1]
                                        + 0.3 * np.mean(X[:n_micro, t-1])
                                        + rng.normal(0, 0.2))

        if n_macro > 0:
            X[-1, t] = 0.5 * X[-1, t-1] + 0.2 * np.mean(X[:n_micro, t-1]) + rng.normal(0, 0.2)

        X[:, t] += 0.1 * common[t-1]

    return X


def critical(system: str = "sandpile", seed: int = 42):
    """Self-organized critical system. High variance, intermediate C."""
    if system == "sandpile":
        return _sandpile(size=30, n_steps=5000, seed=seed)
    raise ValueError(f"Unknown critical system: {system}")


def _sandpile(size: int = 30, n_steps: int = 5000, seed: int = 42):
    """Bak-Tang-Wiesenfeld sandpile. Record grain height field at intervals."""
    rng = np.random.default_rng(seed)
    grid = np.zeros((size, size), dtype=int)
    n_cells = size * size

    record_interval = max(n_steps // 200, 1)
    n_records = n_steps // record_interval
    records = np.zeros((n_cells, n_records))

    record_idx = 0
    for step in range(n_steps):
        i, j = rng.integers(0, size, size=2)
        grid[i, j] += 1

        toppling = True
        while toppling:
            toppling = False
            for i in range(size):
                for j in range(size):
                    if grid[i, j] >= 4:
                        grid[i, j] -= 4
                        for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                            ni, nj = i + di, j + dj
                            if 0 <= ni < size and 0 <= nj < size:
                                grid[ni, nj] += 1
                        toppling = True

        if step % record_interval == 0 and record_idx < n_records:
            records[:, record_idx] = grid.ravel().astype(float)
            record_idx += 1

    return records[:, :record_idx]


def recovery(
    system: str = "markov",
    n_components: int = 10,
    n_timepoints: int = 1000,
    seed: int = 42,
):
    """System with known perturbation and recovery trajectory.

    coupling(t) evolves as a sigmoid: high → low → high, so C decreases then recovers.
    """
    rng = np.random.default_rng(seed)
    X = np.zeros((n_components, n_timepoints))

    if system == "logistic":
        X[:, 0] = rng.uniform(0.1, 0.9, n_components)
        pert_start = n_timepoints // 3
        pert_end = n_timepoints // 2
        for t in range(1, n_timepoints):
            for i in range(n_components):
                neighbor_avg = np.mean(X[[(i - 1) % n_components, (i + 1) % n_components], t - 1])
                X[i, t] = 3.8 * X[i, t - 1] * (1 - X[i, t - 1]) + 0.1 * neighbor_avg
            if pert_start <= t <= pert_end:
                X[:, t] += rng.normal(0, 0.3, n_components)
            X[:, t] = np.clip(X[:, t], 0, 1)
    elif system == "markov":
        # Time-varying coupling: sigmoid from high (0.6) to low (0.05) to high
        mid = n_timepoints // 2
        width = n_timepoints // 6
        t_arr = np.arange(n_timepoints)
        coupling = 0.55 - 0.50 / (1 + np.exp(-(t_arr - mid) / width))

        # Common latent driver
        Z = np.zeros(n_timepoints)
        Z[0] = rng.normal(0, 1)
        for t in range(1, n_timepoints):
            Z[t] = 0.9 * Z[t-1] + rng.normal(0, 0.2)

        for i in range(n_components):
            X[i, 0] = rng.normal(0, 1)

        for t in range(1, n_timepoints):
            c = coupling[t]
            for i in range(n_components):
                X[i, t] = (0.5 * X[i, t-1] + c * Z[t-1]
                           + rng.normal(0, 0.15))
    else:
        raise ValueError(f"Unknown recovery system: {system}")

    return X
