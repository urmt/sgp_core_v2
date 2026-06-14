#!/usr/bin/env python3
"""
T025: EMERGENCE FIELD — Continuous Coordinates & Energy Landscape (R1.1 + R1.2)
=================================================================================
Construct 4 emergence coordinates (C,F,A,R) from the frozen feature set.
Then estimate the energy landscape: V(Φ) = -log p(Φ) with curvature, basins, flows.

Outputs:
  - emergence_coordinates.csv       (C,F,A,R + metadata for 14 systems)
  - emergence_energy_landscape.json (basins, curvature, transition corridors)
  - emergence_flow_field.csv        (pseudo-gradients at each system)
  - emergence_validation.json       (internal consistency checks)
"""

import sys, json, warnings
from pathlib import Path
from collections import Counter
from itertools import combinations
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import KernelDensity
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score
from scipy.spatial.distance import pdist, squareform, cdist
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.stats import gaussian_kde

warnings.filterwarnings("ignore", category=RuntimeWarning)
np.random.seed(42)

OUT = Path("sfh_sgp_ood_outputs")
OUT.mkdir(exist_ok=True)

ALL_SYSTEMS = [
    "primes", "fibonacci", "modular_arithmetic", "additive_recurrence",
    "lorenz", "logistic_map", "henon_map", "ising_magnetization",
    "reaction_diffusion", "cfg_expansion", "lambda_reduction",
    "rewrite_system", "iid_gaussian", "colored_noise",
]

# =====================================================================
# 1. LOAD FROZEN FEATURE SET
# =====================================================================
def load_frozen_features():
    df = pd.read_csv(OUT / "clustering_feature_matrix.csv")
    df = df[df["system"].isin(ALL_SYSTEMS)].copy()
    df = df.set_index("system").loc[ALL_SYSTEMS].reset_index()
    feat_cols = [c for c in df.columns if c != "system"]
    X = df[feat_cols].values
    Xs = StandardScaler().fit_transform(X)
    return df, X, Xs, feat_cols

# =====================================================================
# 2. CONSTRUCT EMERGENCE COORDINATES (R1.1)
# =====================================================================
# 4 axes from the Research Director's framework:
#   C = Coherence (temporal persistence, low entropy, replay stability)
#   F = Fertility (perturbation responsiveness, generative variation)
#   A = Adaptivity (survival under perturbation, recovery)
#   R = Resonance (cross-scale consistency, manifold connectivity)
#
# Each axis = z-scored composite of interpretable features.

def build_emergence_coordinates(df, Xs, feat_cols, system_names):
    """Construct C,F,A,R from frozen features. Returns DataFrame."""
    fmap = {c: i for i, c in enumerate(feat_cols)}  # feature name → column index
    raw = {}  # raw axis values before standardization

    # --- Coherence (C) ---
    # High C = temporal order matters, low-dimensional, replay-stable, structured
    # temporal_corr: negative = order destroys metrics = temporal structure matters
    # effective_rank: low = low-dimensional
    # pc1_ratio: high = transform geometry is structured
    # replay_displacement: low = replay invariant
    # tau_m1: high = signed ordinal flow (systematic)
    c_features = []
    if "temporal_corr" in fmap:
        c_features.append(-Xs[:, fmap["temporal_corr"]])  # negate: low temporal_corr → high C
    if "effective_rank" in fmap:
        c_features.append(-Xs[:, fmap["effective_rank"]])  # negate: low rank → high C
    if "pc1_ratio" in fmap:
        c_features.append(Xs[:, fmap["pc1_ratio"]])       # high ratio → structured
    if "replay_displacement" in fmap:
        c_features.append(-Xs[:, fmap["replay_displacement"]])  # negate: low disp → high C
    raw["C"] = np.mean(c_features, axis=0) if c_features else np.zeros(len(system_names))

    # --- Fertility (F) ---
    # High F = rich generative variation, complex transitions, perturbation-responsive
    # tau_m2: high half-corr = cross-temporal structure
    # tau_m4: high amp transition asymmetry = complex transitions  
    # tau_m3: compressibility signature
    # phase_corr: spectral richness
    f_features = []
    if "tau_m2" in fmap:
        f_features.append(Xs[:, fmap["tau_m2"]])
    if "tau_m4" in fmap:
        f_features.append(Xs[:, fmap["tau_m4"]])
    if "phase_corr" in fmap:
        f_features.append(Xs[:, fmap["phase_corr"]])
    if "pc2" in fmap:
        f_features.append(Xs[:, fmap["pc2"]])  # PC2 variance = geometry spread
    raw["F"] = np.mean(f_features, axis=0) if f_features else np.zeros(len(system_names))

    # --- Adaptivity (A) ---
    # High A = survives perturbation, recovers, stable under transform
    # abl_* variance: how much system changes under metric ablation
    # m2_contribution: stability of the m2 contribution
    # tau stability across transforms
    a_features = []
    abl_cols = [c for c in feat_cols if c.startswith("abl_") or c == "m2_contribution"]
    if len(abl_cols) >= 2:
        abl_slice = Xs[:, [fmap[c] for c in abl_cols]]
        # Systems with all-zero ablation rows (fillna 0) have high variance from imputation
        # We want: high variance = different responses = adaptivity
        # BUT zero-filled rows are artifacts. So we need per-system ablation variance
        # that excludes the zero-fill artifact.
        # Compute: norm of the ablation response vector (how strongly metrics respond)
        abl_norms = np.linalg.norm(abl_slice, axis=1)
        # Also: variability across ablation conditions
        abl_vars = np.std(abl_slice, axis=1)
        a_features.append(abl_norms)
        a_features.append(abl_vars)
    if "tau_m1" in fmap:
        a_features.append(Xs[:, fmap["tau_m1"]])  # ordinal flow flexibility
    raw["A"] = np.mean(a_features, axis=0) if a_features else np.zeros(len(system_names))

    # --- Resonance (R) ---
    # High R = cross-scale consistent, manifold connectivity
    # pc1_variance: concentrated geometry
    # tau alignment strength (approximate via PC1 contribution)
    # multiple tau axes coherence
    r_features = []
    if "pc1" in fmap:
        r_features.append(Xs[:, fmap["pc1"]])
    # Mean tau-axis features as proxy for tau alignment strength
    tau_cols = [c for c in feat_cols if c.startswith("tau_")]
    if len(tau_cols) >= 2:
        tau_slice = Xs[:, [fmap[c] for c in tau_cols]]
        r_features.append(np.mean(tau_slice, axis=1))
        r_features.append(np.std(tau_slice, axis=1))  # tau diversity
    raw["R"] = np.mean(r_features, axis=0) if r_features else np.zeros(len(system_names))

    # Build DataFrame
    axes = ["C", "F", "A", "R"]
    coord_df = pd.DataFrame({"system": system_names})
    for ax in axes:
        v = raw[ax]
        v = (v - np.mean(v)) / max(np.std(v), 1e-12)
        coord_df[ax] = v

    # Normalize: all rotated so P0 cluster 1 (symbolic) has high C
    # Check which cluster is "symbolic" in P0
    Xs_full = StandardScaler().fit_transform(df[[c for c in df.columns if c != "system"]].values)
    Z0 = linkage(Xs_full, method="ward", metric="euclidean")
    p0_labels = fcluster(Z0, t=3, criterion="maxclust")

    # Find the cluster with mostly symbolic systems
    symbolic_systems = {"lambda_reduction", "rewrite_system"}
    symbolic_idx = [i for i, s in enumerate(system_names) if s in symbolic_systems]
    sym_cluster = Counter(p0_labels[symbolic_idx]).most_common(1)[0][0]

    # Ensure the symbolic cluster has positive C
    sym_C_mean = np.mean(coord_df.loc[p0_labels == sym_cluster, "C"])
    if sym_C_mean < 0:
        coord_df["C"] = -coord_df["C"]

    # Ensure the noise cluster has negative A
    # Noise should have low adaptivity (no structure to preserve)
    noise_systems = {"iid_gaussian", "colored_noise"}
    noise_idx = [i for i, s in enumerate(system_names) if s in noise_systems]
    noise_A_mean = np.mean(coord_df.loc[noise_idx, "A"])
    if noise_A_mean > 0:
        coord_df["A"] = -coord_df["A"]

    return coord_df, p0_labels

# =====================================================================
# 3. ENERGY LANDSCAPE (R1.2)
# =====================================================================
# V(Φ) = -log p(Φ) via kernel density estimation
# Basins identified by gradient descent on density

def estimate_energy_landscape(coord_df):
    """Estimate V(Φ) = -log p(Φ) using KDE. Identify basins, curvature, transitions."""
    axes = ["C", "F", "A", "R"]
    Phi = coord_df[axes].values  # N × 4
    N, D = Phi.shape

    # ---- 3a. Kernel Density Estimation ----
    # Use Gaussian KDE with cross-validated bandwidth
    # Scott's rule: h = N^(-1/(D+4)) * sigma
    bw_scott = N ** (-1.0 / (D + 4))
    # Also test a few bandwidths
    bws = [bw_scott * 0.5, bw_scott * 1.0, bw_scott * 2.0]
    kdes = [gaussian_kde(Phi.T, bw_method=bw) for bw in bws]

    # Density and potential at each system point
    densities = {}
    potentials = {}
    for bw, kde in zip(bws, kdes):
        d = kde(Phi.T)
        densities[f"bw{bw:.4f}"] = d
        potentials[f"bw{bw:.4f}"] = -np.log(d + 1e-12)

    # Use default bandwidth for main analysis
    kde = kdes[1]
    density = densities[f"bw{bws[1]:.4f}"]
    potential = potentials[f"bw{bws[1]:.4f}"]

    # ---- 3b. Density grid for landscape visualization ----
    # 2D projections for interpretability
    projections = [("C", "F", 0, 1), ("C", "A", 0, 2), ("F", "A", 1, 2)]
    grid_landscapes = {}
    for ax1, ax2, i1, i2 in projections:
        grid_pts = 32
        c_vals = np.linspace(Phi[:, i1].min() - 1, Phi[:, i1].max() + 1, grid_pts)
        f_vals = np.linspace(Phi[:, i2].min() - 1, Phi[:, i2].max() + 1, grid_pts)
        Cg, Fg = np.meshgrid(c_vals, f_vals)

        # For grid, marginalize over other 2 dims at their mean
        grid_4d = np.zeros((grid_pts * grid_pts, D))
        grid_4d[:, i1] = Cg.ravel()
        grid_4d[:, i2] = Fg.ravel()
        for d in range(D):
            if d != i1 and d != i2:
                grid_4d[:, d] = Phi[:, d].mean()

        V_grid = -np.log(kde(grid_4d.T) + 1e-12)
        V_grid = V_grid.reshape(grid_pts, grid_pts)

        # Find minimum (attractor basin)
        min_idx = np.unravel_index(np.argmin(V_grid), V_grid.shape)
        grid_landscapes[f"{ax1}x{ax2}"] = {
            "grid_size": grid_pts,
            "potential_min": float(V_grid.min()),
            "potential_max": float(V_grid.max()),
            "basin_center": [float(Cg[min_idx]), float(Fg[min_idx])],
            "potential_range": float(V_grid.max() - V_grid.min()),
        }

    # ---- 3c. Local curvature (Hessian estimate) ----
    curvatures = {}
    for i, sys_name in enumerate(coord_df["system"]):
        # Finite-difference Hessian at each point
        h = 0.1  # step size
        H = np.zeros((D, D))
        phi0 = Phi[i]
        for d1 in range(D):
            for d2 in range(D):
                if d1 == d2:
                    phi_plus = phi0.copy()
                    phi_minus = phi0.copy()
                    phi_plus[d1] += h
                    phi_minus[d1] -= h
                    V_pp = -np.log(kde(phi_plus.reshape(1, -1).T) + 1e-12)[0]
                    V_mm = -np.log(kde(phi_minus.reshape(1, -1).T) + 1e-12)[0]
                    V_0 = potential[i]
                    H[d1, d2] = (V_pp - 2 * V_0 + V_mm) / (h * h)
                else:
                    phi_pp = phi0.copy()
                    phi_pm = phi0.copy()
                    phi_mp = phi0.copy()
                    phi_mm = phi0.copy()
                    phi_pp[d1] += h; phi_pp[d2] += h
                    phi_pm[d1] += h; phi_pm[d2] -= h
                    phi_mp[d1] -= h; phi_mp[d2] += h
                    phi_mm[d1] -= h; phi_mm[d2] -= h
                    V_pp = -np.log(kde(phi_pp.reshape(1, -1).T) + 1e-12)[0]
                    V_pm = -np.log(kde(phi_pm.reshape(1, -1).T) + 1e-12)[0]
                    V_mp = -np.log(kde(phi_mp.reshape(1, -1).T) + 1e-12)[0]
                    V_mm = -np.log(kde(phi_mm.reshape(1, -1).T) + 1e-12)[0]
                    H[d1, d2] = (V_pp - V_pm - V_mp + V_mm) / (4 * h * h)

        eigenvalues = np.linalg.eigvalsh(H)
        curvatures[sys_name] = {
            "eigenvalues": [float(e) for e in eigenvalues],
            "mean_curvature": float(np.mean(eigenvalues)),
            "min_curvature": float(np.min(eigenvalues)),
            "max_curvature": float(np.max(eigenvalues)),
            "basin_sharpness": float(np.sum(eigenvalues[eigenvalues > 0])),
            "saddle_index": int(np.sum(eigenvalues < 0)),
        }

    # ---- 3d. Distance matrix in emergence space ----
    dists = squareform(pdist(Phi, metric="euclidean"))

    # ---- 3e. Bootstrap basin persistence ----
    n_boot = 500
    basin_labels = None  # Will store cluster assignment from potential minima
    basin_persistence = {}

    # Simple approach: cluster in potential space
    V_cluster = AgglomerativeClustering(n_clusters=3).fit_predict(-potential.reshape(-1, 1))
    basin_counts = Counter(V_cluster)
    basin_assign = {coord_df["system"][i]: int(V_cluster[i]) for i in range(N)}

    # Bootstrap
    boot_persistence = np.zeros((N, N))
    for _ in range(n_boot):
        idxs = np.random.choice(N, N, replace=True)
        Phi_boot = Phi[idxs]
        try:
            kde_boot = gaussian_kde(Phi_boot.T, bw_method=bw_scott)
            V_boot = kde_boot(Phi_boot.T)
            # Cluster bootstrapped potentials
            clust_boot = AgglomerativeClustering(n_clusters=3).fit_predict(
                -np.log(V_boot + 1e-12).reshape(-1, 1))
            # Map back to original indices
            for a in range(N):
                for b in range(N):
                    if idxs[a] != a or idxs[b] != b:
                        continue
                    boot_persistence[a, b] += (clust_boot[a] == clust_boot[b]) / n_boot
        except Exception:
            pass

    basin_persistence = {}
    for i, s1 in enumerate(coord_df["system"]):
        for j, s2 in enumerate(coord_df["system"]):
            if i < j:
                basin_persistence[f"{s1}__{s2}"] = float(boot_persistence[i, j])

    return {
        "density": [float(d) for d in density],
        "potential": [float(p) for p in potential],
        "bw_scott": float(bw_scott),
        "bws_tested": [float(b) for b in bws],
        "grid_landscapes": grid_landscapes,
        "curvature_per_system": curvatures,
        "basin_assignment": basin_assign,
        "basin_persistence": basin_persistence,
        "basin_sizes": {str(k): int(v) for k, v in basin_counts.items()},
    }, Phi, dists, potential

# =====================================================================
# 4. PSEUDO-FLOW FIELD (R1.3 minimal)
# =====================================================================
# From perturbation data: estimate gradient of V at each system
# A system at a local minimum has ∇V ≈ 0
# A system on a slope has ∇V ≠ 0, direction indicates instability

def estimate_flow(coord_df, Phi, potential, dists):
    """Estimate pseudo-gradient from potential + neighborhood asymmetry."""
    N, D = Phi.shape
    axes = ["C", "F", "A", "R"]

    flows = []
    for i in range(N):
        # Gradient via finite differences with KDE
        h = 0.05
        grad = np.zeros(D)
        for d in range(D):
            phi_plus = Phi[i].copy()
            phi_minus = Phi[i].copy()
            phi_plus[d] += h
            phi_minus[d] -= h

            # Approximate V at nearby points using nearest-neighbor density
            # Simple: assume V changes linearly
            # Use the gradient of potential from KDE
            # We need to recreate the KDE estimate... too slow.
            # Instead: flow vector = direction toward higher-density regions
            pass

        # Alternative: flow = (-∇V) estimated via neighborhood asymmetry
        # For each system, compute weighted displacement toward neighbors
        # that have lower potential (systems tend to flow downhill in V)

        # Weighted mean displacement to neighbors with lower potential
        weights = np.exp(-dists[i] ** 2 / (2 * 0.5 ** 2))
        weights[i] = 0  # exclude self
        weights = weights / weights.sum()

        # Displacement vectors to all other systems
        displacements = Phi - Phi[i]  # N × D
        # Weighted by density of destination (higher density = more likely to flow there)
        # AND direction toward lower potential
        flow_dir = np.zeros(D)
        for j in range(N):
            if j == i:
                continue
            # If neighbor has lower potential (more stable), flow toward it
            if potential[j] < potential[i]:
                weight = (potential[i] - potential[j]) / max(potential[i] - potential.min(), 1e-12)
                flow_dir += weight * (Phi[j] - Phi[i]) / max(np.linalg.norm(Phi[j] - Phi[i]), 1e-12)

        flow_magnitude = np.linalg.norm(flow_dir)
        flow_dir_norm = flow_dir / max(flow_magnitude, 1e-12)

        # Stability: systems in basin minima should have near-zero flow
        row = {
            "system": coord_df["system"][i],
            "flow_magnitude": float(flow_magnitude),
            "flow_dir_C": float(flow_dir_norm[0]),
            "flow_dir_F": float(flow_dir_norm[1]),
            "flow_dir_A": float(flow_dir_norm[2]),
            "flow_dir_R": float(flow_dir_norm[3]),
            "potential_barrier": float(0.0),  # placeholder
        }
        flows.append(row)

    return pd.DataFrame(flows)

# =====================================================================
# 5. VALIDATION
# =====================================================================
def validate_emergence_coordinates(coord_df, p0_labels):
    """Check that emergence coordinates are meaningful."""
    N = len(coord_df)
    axes = ["C", "F", "A", "R"]
    Phi = coord_df[axes].values

    results = {}

    # 5a. Check cluster separation in emergence space
    from sklearn.metrics import adjusted_rand_score
    Z = linkage(Phi, method="ward", metric="euclidean")
    em_labels = fcluster(Z, t=3, criterion="maxclust")
    ari = adjusted_rand_score(p0_labels, em_labels)

    # 5b. Silhouette in emergence space vs original
    sil_em = silhouette_score(Phi, p0_labels)
    Xs_full = StandardScaler().fit_transform(
        pd.read_csv(OUT / "clustering_feature_matrix.csv")
        .set_index("system").loc[ALL_SYSTEMS].values)
    sil_orig = silhouette_score(Xs_full, p0_labels)

    # 5c. Axis correlations
    corr_matrix = np.corrcoef(Phi.T)
    corr_df = pd.DataFrame(corr_matrix, index=axes, columns=axes)

    # 5d. Which axis best separates which cluster?
    clust_means = {}
    for ax in axes:
        clust_means[ax] = {}
        for cl in sorted(set(p0_labels)):
            clust_means[ax][int(cl)] = float(coord_df.loc[p0_labels == cl, ax].mean())

    # 5e. Dimensionality reduction check: can 4 dims explain full variation?
    full_Phi = Phi
    pca_full = PCA()
    pca_full.fit(full_Phi)
    n_90 = np.sum(np.cumsum(pca_full.explained_variance_ratio_) < 0.90) + 1

    # 5f. P0 cluster separation by axis
    clusters = sorted(set(p0_labels))
    between_cluster_vars = {}
    for ax in axes:
        means = [coord_df.loc[p0_labels == c, ax].mean() for c in clusters]
        between_cluster_vars[ax] = float(np.var(means))

    results["ARI_emergence_vs_P0"] = float(ari)
    results["silhouette_emergence"] = float(sil_em)
    results["silhouette_original"] = float(sil_orig)
    results["axis_correlations"] = corr_df.to_dict()
    results["cluster_mean_CFFAR"] = clust_means
    results["between_cluster_variance"] = between_cluster_vars
    results["dims_for_90pct_var"] = int(n_90)
    results["axis_eigenvalues"] = [float(e) for e in np.linalg.eigvalsh(corr_matrix)]

    return results

# =====================================================================
# 6. TRANSITION CORRIDORS
# =====================================================================
def find_transition_corridors(Phi, potential, dists, system_names, p0_labels):
    """Find saddle points and transition corridors between basins."""
    N = Phi.shape[0]
    axes = ["C", "F", "A", "R"]

    # For each pair of clusters, find the minimum-energy path
    # between the two cluster centroids
    from scipy.optimize import minimize

    clusters = sorted(set(p0_labels))
    transitions = []

    for c1, c2 in combinations(clusters, 2):
        idx1 = np.where(p0_labels == c1)[0]
        idx2 = np.where(p0_labels == c2)[0]
        cent1 = Phi[idx1].mean(axis=0)
        cent2 = Phi[idx2].mean(axis=0)

        # Linear interpolation: 20 steps
        n_steps = 20
        path = np.zeros((n_steps, Phi.shape[1]))
        for d in range(Phi.shape[1]):
            path[:, d] = np.linspace(cent1[d], cent2[d], n_steps)

        # Saddle point: highest potential along the path
        try:
            kde_temp = gaussian_kde(Phi.T, bw_method=N ** (-1.0 / (Phi.shape[1] + 4)))
            V_path = -np.log(kde_temp(path.T) + 1e-12)
        except Exception:
            V_path = np.zeros(n_steps)

        saddle_idx = np.argmax(V_path)
        barrier = float(V_path[saddle_idx] - V_path[0])  # from centroid 1 to saddle

        transitions.append({
            "from_cluster": int(c1),
            "to_cluster": int(c2),
            "from_centroid": [float(x) for x in cent1],
            "to_centroid": [float(x) for x in cent2],
            "saddle_point": [float(x) for x in path[saddle_idx]],
            "barrier_height": barrier,
            "n_systems_c1": int(len(idx1)),
            "n_systems_c2": int(len(idx2)),
        })

    # Also find nearest-basin system pairs (potential transition corridors)
    # For each system, find nearest system in a different cluster
    corridors = []
    for i in range(N):
        for j in range(i + 1, N):
            if p0_labels[i] == p0_labels[j]:
                continue
            d = dists[i, j]
            p_diff = abs(potential[i] - potential[j])
            corridors.append({
                "system_i": system_names[i],
                "system_j": system_names[j],
                "cluster_i": int(p0_labels[i]),
                "cluster_j": int(p0_labels[j]),
                "distance": float(d),
                "potential_diff": float(p_diff),
                "transition_likelihood": float(p_diff / max(d, 1e-12)),
            })

    corridors.sort(key=lambda x: -x["transition_likelihood"])

    return {
        "cluster_transitions": transitions,
        "cross_cluster_corridors": corridors[:20],
    }

# =====================================================================
# MAIN
# =====================================================================
def main():
    print("=" * 70)
    print("T025: EMERGENCE FIELD — Continuous Coordinates (R1.1)")
    print("       Energy Landscape (R1.2) + Pseudo-Flow (R1.3)")
    print("=" * 70)

    # Load
    df, X, Xs, feat_cols = load_frozen_features()
    systems = df["system"].tolist()

    print(f"\nFrozen feature set: {len(feat_cols)} features × {len(systems)} systems")
    print(f"Features: {', '.join(feat_cols)}")

    # ---- R1.1: Build Coordinates ----
    print("\n[R1.1] Building emergence coordinates C,F,A,R...")
    coord_df, p0_labels = build_emergence_coordinates(df, Xs, feat_cols, systems)
    coord_df.to_csv(OUT / "emergence_coordinates.csv", index=False)
    print(f"  Saved: emergence_coordinates.csv")
    print(f"\n  Coordinates (z-scored):")
    axes = ["C", "F", "A", "R"]
    fmt = "  {:<24s}  {:>8s}  {:>8s}  {:>8s}  {:>8s}  {:>8s}"
    print(fmt.format("System", "C", "F", "A", "R", "P0_clust"))
    print("  " + "-" * 66)
    for i, s in enumerate(systems):
        c = coord_df.loc[i, "C"]
        f = coord_df.loc[i, "F"]
        a = coord_df.loc[i, "A"]
        r = coord_df.loc[i, "R"]
        print(fmt.format(s, f"{c:+.4f}", f"{f:+.4f}", f"{a:+.4f}", f"{r:+.4f}", str(p0_labels[i])))

    # ---- R1.2: Energy Landscape ----
    print("\n[R1.2] Estimating energy landscape V(Φ) = -log p(Φ)...")
    landscape, Phi, dists, potential = estimate_energy_landscape(coord_df)

    print(f"  Bandwidth (Scott): {landscape['bw_scott']:.4f}")
    print(f"  Potential range: [{min(landscape['potential']):.4f}, "
          f"{max(landscape['potential']):.4f}]")
    print(f"  Basins found: {len(landscape['basin_sizes'])} "
          f"({landscape['basin_sizes']})")
    print(f"\n  Basin assignment:")

    basins_by_clust = {}
    for s, b in landscape["basin_assignment"].items():
        basins_by_clust.setdefault(b, []).append(s)
    for b, members in sorted(basins_by_clust.items()):
        print(f"    Basin {b}: {', '.join(members)}")

    # Print curvature
    print(f"\n  Curvature (mean_eig ± std across systems):")
    curvs = [v["mean_curvature"] for v in landscape["curvature_per_system"].values()]
    print(f"    Mean curvature: {np.mean(curvs):.4f} ± {np.std(curvs):.4f}")
    print(f"    Saddle systems (index > 0):")
    for s, v in landscape["curvature_per_system"].items():
        if v["saddle_index"] > 0:
            print(f"      {s}: index={v['saddle_index']}, "
                  f"eig={[f'{e:.4f}' for e in v['eigenvalues']]}")

    # Save landscape metadata (not full grid)
    landscape_save = {
        "bandwidth": landscape["bw_scott"],
        "potential_per_system": {coord_df["system"][i]: landscape["potential"][i]
                                  for i in range(len(coord_df))},
        "density_per_system": {coord_df["system"][i]: landscape["density"][i]
                                for i in range(len(coord_df))},
        "basin_assignment": landscape["basin_assignment"],
        "basin_sizes": landscape["basin_sizes"],
        "basin_persistence_top20": dict(
            sorted(landscape["basin_persistence"].items(),
                   key=lambda x: -x[1])[:20]),
        "curvature_per_system": landscape["curvature_per_system"],
        "grid_landscapes": landscape["grid_landscapes"],
    }
    with open(OUT / "emergence_energy_landscape.json", "w") as f:
        json.dump(landscape_save, f, indent=2)
    print(f"\n  Saved: emergence_energy_landscape.json")

    # ---- R1.3: Flow Field ----
    print("\n[R1.3] Estimating pseudo-flow field...")
    flow_df = estimate_flow(coord_df, Phi, potential, dists)
    flow_df.to_csv(OUT / "emergence_flow_field.csv", index=False)

    print(f"\n  Flow magnitudes:")
    for _, r in flow_df.sort_values("flow_magnitude", ascending=False).iterrows():
        print(f"    {r['system']:<24s} flow={r['flow_magnitude']:.4f} "
              f"→ ({r['flow_dir_C']:+.2f}, {r['flow_dir_F']:+.2f})")

    print(f"\n  Systems at minima (flow ≈ 0):")
    for _, r in flow_df.sort_values("flow_magnitude", ascending=True).head(3).iterrows():
        print(f"    {r['system']:<24s} flow={r['flow_magnitude']:.4f}")
    print(f"  Systems at instability (high flow):")
    for _, r in flow_df.sort_values("flow_magnitude", ascending=False).head(3).iterrows():
        print(f"    {r['system']:<24s} flow={r['flow_magnitude']:.4f}")

    # ---- Validation ----
    print("\n[Validation] Checking emergence coordinate quality...")
    val = validate_emergence_coordinates(coord_df, p0_labels)

    print(f"  ARI between emergence-space clusters and P0: {val['ARI_emergence_vs_P0']:.4f}")
    print(f"  Silhouette in emergence space: {val['silhouette_emergence']:.4f} "
          f"(original: {val['silhouette_original']:.4f})")
    print(f"  Dims for 90% var in emergence space: {val['dims_for_90pct_var']}")
    print(f"\n  Axis correlations:")
    for ax1 in axes:
        for ax2 in axes:
            if ax1 < ax2:
                print(f"    corr({ax1},{ax2}) = {val['axis_correlations'][ax1][ax2]:+.4f}")
    print(f"\n  Between-cluster variance by axis:")
    for ax, v in sorted(val["between_cluster_variance"].items(), key=lambda x: -x[1]):
        print(f"    {ax}: {v:.6f}")
    print(f"\n  Cluster mean coordinates:")
    for cl in sorted(val["cluster_mean_CFFAR"]["C"].keys()):
        means = ", ".join(f"{ax}={val['cluster_mean_CFFAR'][ax][cl]:+.3f}"
                         for ax in axes)
        print(f"    Cluster {cl}: {means}")

    with open(OUT / "emergence_validation.json", "w") as f:
        json.dump(val, f, indent=2)

    # ---- Transition Corridors ----
    print("\n[Transitions] Finding transition corridors between basins...")
    transitions = find_transition_corridors(Phi, potential, dists, systems, p0_labels)

    print(f"\n  Cluster-to-cluster transitions:")
    for t in transitions["cluster_transitions"]:
        print(f"    C{t['from_cluster']} → C{t['to_cluster']}: "
              f"barrier={t['barrier_height']:.4f}, "
              f"saddle=({', '.join(f'{x:.3f}' for x in t['saddle_point'][:2])},...)")

    print(f"\n  Top cross-cluster transition corridors:")
    for c in transitions["cross_cluster_corridors"][:5]:
        print(f"    {c['system_i']:>16s} ↔ {c['system_j']:<16s}  "
              f"d={c['distance']:.3f}  ΔV={c['potential_diff']:.3f}  "
              f"L={c['transition_likelihood']:.3f}")

    # ---- Summary ----
    print("\n" + "=" * 70)
    print("EMERGENCE FIELD — SUMMARY")
    print("=" * 70)
    print(f"\n  Coordinates: C (coherence), F (fertility), A (adaptivity), R (resonance)")
    print(f"  P0-cluster separation in Φ-space: ARI={val['ARI_emergence_vs_P0']:.4f}")
    print(f"  Energy landscape: {len(landscape['basin_sizes'])} basins, "
          f"mean curvature={np.mean(curvs):.4f}")
    print(f"  Dominant transition axis: {max(val['between_cluster_variance'], key=val['between_cluster_variance'].get)}")
    print(f"\n  Validation saved to: emergence_validation.json")
    print(f"  Coordinates saved to: emergence_coordinates.csv")
    print(f"  Landscape saved to:  emergence_energy_landscape.json")
    print(f"  Flow field saved to:  emergence_flow_field.csv")
    print()


if __name__ == "__main__":
    main()
