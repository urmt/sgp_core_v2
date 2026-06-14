#!/usr/bin/env python3
"""
T027: FLOW INVARIANT ANALYSIS
===============================
"Does transition-flow survive without the clusters?"

Tests whether the bridge phenomenon (high-flow regions between coherence
and instability) is fundamental or an artifact of the 14-system taxonomy.

All analysis is CLUSTER-FREE — no P0/P1 labels, no ontology assumptions.
Only Φ-space positions (C,F,A,R), flow magnitude, curvature, and density.

Sections:
  A: Flow-only geometry — remove all cluster assumptions
  B: Flow invariant test — |∇V(Φ)| predicts sensitivity WITHOUT clusters
  C: Local transition geometry — nearest-neighbor analysis, curvature tensor
  D: Dimensional stability — bridge survival under 6 embeddings
  E: Topological analysis — persistent homology, Morse structure
  F: Destroy the system set — removal/replacement stress tests
"""

import sys, json, warnings, math, itertools, collections
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform, cdist
from scipy.spatial import Delaunay
from scipy.stats import pearsonr, spearmanr, gaussian_kde, ttest_ind
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import SpectralEmbedding, Isomap, LocallyLinearEmbedding, MDS
from sklearn.neighbors import NearestNeighbors
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.metrics import r2_score
import networkx as nx

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

BRIDGE_SYSTEMS = {"lorenz", "ising_magnetization", "reaction_diffusion"}

# =====================================================================
# HELPERS
# =====================================================================

def load_all():
    """Load all data without cluster labels."""
    coord = pd.read_csv(OUT / "emergence_coordinates.csv")
    coord = coord[coord["system"].isin(ALL_SYSTEMS)].reset_index(drop=True)
    axes = ["C", "F", "A", "R"]
    Phi = coord[axes].values

    flow_df = pd.read_csv(OUT / "emergence_flow_field.csv")
    flow_map = {r["system"]: r["flow_magnitude"] for _, r in flow_df.iterrows()}

    with open(OUT / "emergence_energy_landscape.json") as f:
        landscape = json.load(f)

    curv_map = {s: landscape["curvature_per_system"][s]["mean_curvature"]
                for s in ALL_SYSTEMS}
    dens_map = {s: landscape["density_per_system"].get(s, 0)
                for s in ALL_SYSTEMS}

    flow_vals = np.array([flow_map[s] for s in ALL_SYSTEMS])
    curv_vals = np.array([curv_map[s] for s in ALL_SYSTEMS])
    dens_vals = np.array([dens_map[s] for s in ALL_SYSTEMS])

    # Collapse data from R2
    with open(OUT / "r2_collapse_forecast.json") as f:
        coll = json.load(f)
    collapse_slopes = {}
    sigmas = coll["sigmas_tested"]
    for sys_name, curve in coll["collapse_curves"].items():
        vals_at = [curve[i] for i in range(min(6, len(sigmas)))]
        if len(vals_at) > 1:
            slope = (vals_at[-1] - vals_at[0]) / (sigmas[min(5, len(sigmas)-1)] - sigmas[0])
        else:
            slope = 0.0
        collapse_slopes[sys_name] = slope

    # Susceptibility data
    with open(OUT / "r2_transition_susceptibility.json") as f:
        susc = json.load(f)

    sensitivity_map = {}
    for sys_name in ALL_SYSTEMS:
        idx = ALL_SYSTEMS.index(sys_name)
        # knockout sensitivity from raw feature matrix
        sensitivity_map[sys_name] = 0.385  # placeholder

    return {
        "coord": coord, "Phi": Phi, "axes": axes,
        "flow": flow_vals, "curv": curv_vals, "dens": dens_vals,
        "flow_map": flow_map, "curv_map": curv_map, "dens_map": dens_map,
        "collapse_slopes": collapse_slopes,
        "coll": coll, "susc": susc,
    }


def rank_corr(x, y):
    """Spearman rank correlation with p-value."""
    if np.std(x) == 0 or np.std(y) == 0:
        return 0.0, 1.0
    return spearmanr(x, y)


def compute_local_flow(Phi, i, k=5):
    """Compute local flow magnitude at point i from neighborhood asymmetry.
    Flow = ||mean(neighbors) - point|| / mean(distances)
    """
    dists = cdist(Phi[i:i+1], Phi)[0]
    idxs = np.argsort(dists)[1:k+1]
    neighbor_center = Phi[idxs].mean(axis=0)
    displacement = np.linalg.norm(neighbor_center - Phi[i])
    mean_dist = dists[idxs].mean()
    return displacement / max(mean_dist, 1e-12)


def embedding_flow_correlation(Phi_orig, Phi_embed, k=5):
    """Correlation between flow fields in original and embedded space."""
    n = len(Phi_orig)
    flow_orig = np.array([compute_local_flow(Phi_orig, i, k) for i in range(n)])
    flow_embed = np.array([compute_local_flow(Phi_embed, i, k) for i in range(n)])
    r, p = pearsonr(flow_orig, flow_embed)
    return r, p, flow_orig, flow_embed


def print_sep():
    print("\n" + "=" * 70)


# =====================================================================
# SECTION A — FLOW-ONLY GEOMETRY
# =====================================================================

def section_a_flow_only_geometry(data):
    """
    Remove all cluster/ontology assumptions.
    Analyze Φ-space as a pure continuous manifold.
    """
    print_sep()
    print("SECTION A: FLOW-ONLY GEOMETRY (no cluster assumptions)")
    print_sep()

    Phi = data["Phi"]
    axes = data["axes"]
    flow = data["flow"]
    curv = data["curv"]
    dens = data["dens"]
    systems = data["coord"]["system"].tolist()

    # A1 — Continuous flow field statistics
    print("\n  A1 — Flow field as continuous scalar field")
    print(f"    Flow: mean={flow.mean():.3f}, std={flow.std():.3f}, "
          f"min={flow.min():.3f}, max={flow.max():.3f}")
    high_flow = flow > flow.mean() + flow.std()
    low_flow = flow < flow.mean() - flow.std()
    print(f"    High-flow systems (>{flow.mean()+flow.std():.2f}): "
          f"{', '.join(systems[i] for i in np.where(high_flow)[0])}")
    print(f"    Low-flow systems (<{flow.mean()-flow.std():.2f}): "
          f"{', '.join(systems[i] for i in np.where(low_flow)[0])}")

    # A2 — Φ-space distances to bridge centroid
    print("\n  A2 — Distance to bridge centroid")
    bridge_idx = [i for i, s in enumerate(systems) if s in BRIDGE_SYSTEMS]
    bridge_centroid = Phi[bridge_idx].mean(axis=0)
    dist_to_bridge = np.linalg.norm(Phi - bridge_centroid, axis=1)
    for i, s in enumerate(systems):
        print(f"    d(bridge, {s:<24s}) = {dist_to_bridge[i]:.3f}")

    # A3 — Is flow just a linear combination of C,F,A,R?
    print("\n  A3 — Flow = f(C,F,A,R)?")
    for ax in axes:
        r, p = pearsonr(flow, Phi[:, axes.index(ax)])
        print(f"    flow ~ {ax}: r={r:+.3f}, p={p:.4f}")
    # Multiple regression
    lr = LinearRegression().fit(Phi, flow)
    flow_pred = lr.predict(Phi)
    r2 = r2_score(flow, flow_pred)
    print(f"    Linear model: flow = f(C,F,A,R)  R² = {r2:.4f}")
    print(f"    Coefficients: {dict(zip(axes, lr.coef_))}")
    # Ridge (regularized)
    ridge = Ridge(alpha=1.0).fit(Phi, flow)
    print(f"    Ridge coefs: {dict(zip(axes, ridge.coef_))}")

    # A4 — Curvature-density-flow relationships (cluster-free)
    print("\n  A4 — Field relationships (cluster-free)")
    measures = [
        ("flow", flow), ("curvature", curv), ("density", dens),
        ("dist_to_bridge", dist_to_bridge),
    ]
    for (n1, v1), (n2, v2) in itertools.combinations(measures, 2):
        r, p = pearsonr(v1, v2)
        print(f"    {n1} vs {n2}: r={r:+.3f}, p={p:.4f}")

    # A5 — Are bridge systems outliers in any continuous measure?
    print("\n  A5 — Bridge system status (are they extreme on any axis?)")
    bridge_mask = np.array([s in BRIDGE_SYSTEMS for s in systems])
    metrics = {"C": Phi[:, 0], "F": Phi[:, 1], "A": Phi[:, 2],
               "R": Phi[:, 3], "flow": flow, "curv": curv, "dens": dens}
    for name, vals in metrics.items():
        bridge_vals = vals[bridge_mask]
        other_vals = vals[~bridge_mask]
        z_bridge = (bridge_vals.mean() - vals.mean()) / vals.std()
        print(f"    Bridge z-score({name:>10s}) = {z_bridge:+.3f} "
              f"(bridge={bridge_vals.mean():.3f}, other={other_vals.mean():.3f})")
        if np.std(bridge_vals) > 0 and np.std(other_vals) > 0:
            t, p = ttest_ind(bridge_vals, other_vals)
            print(f"      t-test: t={t:.3f}, p={p:.4f} "
                  f"{'SIGNIFICANT' if p < 0.05 else ''}")

    result = {
        "flow_stats": {"mean": float(flow.mean()), "std": float(flow.std()),
                       "min": float(flow.min()), "max": float(flow.max())},
        "flow_r2_vs_phi": float(r2),
        "high_flow_systems": [s for i, s in enumerate(systems) if high_flow[i]],
        "bridge_distances": {s: float(dist_to_bridge[i])
                            for i, s in enumerate(systems)},
    }
    return result


# =====================================================================
# SECTION B — FLOW INVARIANT TEST
# =====================================================================

def section_b_flow_invariant(data):
    """
    Test whether |∇V(Φ)| predicts perturbation sensitivity WITHOUT clusters.
    Core hypothesis: position in flow field determines dynamical stability.
    """
    print_sep()
    print("SECTION B: FLOW INVARIANT TEST (flow→sensitivity without clusters)")
    print_sep()

    Phi = data["Phi"]
    axes = data["axes"]
    flow = data["flow"]
    curv = data["curv"]
    dens = data["dens"]
    systems = data["coord"]["system"].tolist()
    coll = data["coll"]
    susc = data["susc"]

    # B1 — Load collapse slopes
    collapse_slope_vals = np.array([data["collapse_slopes"][s] for s in systems])

    # B2 — Flow-only prediction of collapse sensitivity
    print("\n  B1 — Flow-only prediction of collapse sensitivity")
    print(f"    {'Predictor':<20s}  {'R²':>8s}  {'r':>8s}  {'p':>8s}")
    print(f"    {'-'*48}")

    # Single predictors
    predictors = {
        "flow": flow, "curvature": curv, "density": dens,
    }
    # Add each axis
    for j, ax in enumerate(axes):
        predictors[ax] = Phi[:, j]

    baseline_scores = {}
    for name, vals in predictors.items():
        if np.std(vals) == 0:
            continue
        lr = LinearRegression()
        try:
            scores = cross_val_score(lr, vals.reshape(-1, 1), collapse_slope_vals,
                                     cv=min(5, len(systems)//2), scoring='r2')
            r_mean = scores.mean()
        except:
            r_mean = -np.inf
        r_val, p_val = pearsonr(vals, collapse_slope_vals)
        baseline_scores[name] = {"r2": float(r_mean), "r": float(r_val), "p": float(p_val)}
        print(f"    {name:<20s}  {r_mean:>+8.4f}  {r_val:>+8.3f}  {p_val:>.4f}")

    # Full Φ model (no clusters)
    rf = RandomForestRegressor(n_estimators=100, max_depth=3, random_state=42)
    try:
        rf_scores = cross_val_score(rf, Phi, collapse_slope_vals,
                                    cv=min(5, len(systems)//2), scoring='r2')
        rf_mean = rf_scores.mean()
        print(f"    {'RF(Φ)':<20s}  {rf_mean:>+8.4f}")
    except:
        rf_mean = -np.inf
        print(f"    {'RF(Φ)':<20s}  FAILED (cv too small)")

    # B3 — Flow magnitude directly predicts collapse slope
    print(f"\n  B2 — Direct flow→collapse test")
    r_fc, p_fc = pearsonr(flow, collapse_slope_vals)
    print(f"    flow → collapse_slope: r={r_fc:.4f}, p={p_fc:.5f}")
    r_fc_s, p_fc_s = spearmanr(flow, collapse_slope_vals)
    print(f"    Spearman: ρ={r_fc_s:.4f}, p={p_fc_s:.5f}")

    # B4 — Does flow beat axes individually? (partial correlation test)
    print(f"\n  B3 — Flow vs best single-axis predictor")
    best_ax = max(baseline_scores, key=lambda k: abs(baseline_scores[k]["r"]))
    best_r = baseline_scores[best_ax]["r"]
    print(f"    Best axis: {best_ax} (r={best_r:.3f})")
    print(f"    Flow r: {r_fc:.3f}  {'✓ Flow wins' if abs(r_fc) > abs(best_r) else 'Axis wins'}")

    # B5 — Density-weighted flow (combined field predictor)
    print(f"\n  B4 — Combined field predictor")
    flow_dens = flow * np.maximum(dens, 0.01)
    r_fd, p_fd = pearsonr(flow_dens, collapse_slope_vals)
    print(f"    flow×density → collapse: r={r_fd:.4f}, p={p_fd:.5f}")

    flow_curv = flow * curv
    r_fc2, p_fc2 = pearsonr(flow_curv, collapse_slope_vals)
    print(f"    flow×curvature → collapse: r={r_fc2:.4f}, p={p_fc2:.5f}")

    # B6 — Critical test: is flow better than cluster membership?
    print(f"\n  B5 — Flow vs cluster membership as predictor")
    # Compute cluster-based prediction (using P0 labels from feature matrix)
    feat = pd.read_csv(OUT / "clustering_feature_matrix.csv")
    feat = feat[feat["system"].isin(ALL_SYSTEMS)].set_index("system").loc[ALL_SYSTEMS]
    Xs = StandardScaler().fit_transform(feat.values)
    Z0 = linkage(Xs, method="ward", metric="euclidean")
    from scipy.cluster.hierarchy import fcluster
    p0_labels = fcluster(Z0, t=3, criterion="maxclust")
    cluster_dummies = pd.get_dummies(p0_labels).values
    lr_clust = LinearRegression()
    try:
        clust_scores = cross_val_score(lr_clust, cluster_dummies,
                                       collapse_slope_vals,
                                       cv=min(5, len(systems)//2), scoring='r2')
        clust_r2 = clust_scores.mean()
    except:
        clust_r2 = -np.inf
    flow_r2_alone = baseline_scores["flow"]["r2"]
    print(f"    Cluster model R² = {clust_r2:.4f}")
    print(f"    Flow-only model R² = {flow_r2_alone:.4f}")
    print(f"    {'FIELD > TAXONOMY ✓' if flow_r2_alone > clust_r2 else 'TAXONOMY > FIELD'}")

    # B7 — Bridge vs non-bridge: is the boundary continuous or discrete?
    print(f"\n  B6 — Continuity test: flow as ordered predictor")
    flow_order = np.argsort(flow)
    top_third = flow_order[-len(systems)//3:]
    bot_third = flow_order[:len(systems)//3]
    print(f"    Top 1/3 flow: {', '.join(systems[i] for i in top_third)}")
    print(f"    Bot 1/3 flow: {', '.join(systems[i] for i in bot_third)}")
    top_collapse = collapse_slope_vals[top_third].mean()
    bot_collapse = collapse_slope_vals[bot_third].mean()
    print(f"    Top-3 collapse slope mean: {top_collapse:.4f}")
    print(f"    Bot-3 collapse slope mean: {bot_collapse:.4f}")
    print(f"    {'CONTINUOUS ✓' if top_collapse < bot_collapse else 'DISCRETE?'}")

    result = {
        "flow_collapse_r": float(r_fc),
        "flow_collapse_p": float(p_fc),
        "flow_vs_best_axis": {"flow_r": float(r_fc), "best_axis": best_ax, "best_r": float(best_r)},
        "combined_field_flow_density_r": float(r_fd),
        "combined_field_flow_curvature_r": float(r_fc2),
        "cluster_model_r2": float(clust_r2),
        "flow_only_r2": float(flow_r2_alone),
        "rf_phi_r2": float(rf_mean) if rf_mean != -np.inf else None,
        "single_predictors": baseline_scores,
    }
    return result


# =====================================================================
# SECTION C — LOCAL TRANSITION GEOMETRY
# =====================================================================

def section_c_local_transition(data):
    """
    Compute local geometric properties for each system:
    - Nearest-neighbor graph
    - Local curvature tensor
    - Density gradient
    - Perturbation drift vector
    - Transition probability
    """
    print_sep()
    print("SECTION C: LOCAL TRANSITION GEOMETRY")
    print_sep()

    Phi = data["Phi"]
    axes = data["axes"]
    systems = data["coord"]["system"].tolist()
    flow = data["flow"]
    curv = data["curv"]
    dens = data["dens"]

    n = len(systems)

    # C1 — Nearest-neighbor graph in Φ-space
    print("\n  C1 — Nearest-neighbor graph")
    dist_mat = squareform(pdist(Phi))
    nn = NearestNeighbors(n_neighbors=min(5, n-1), metric="euclidean")
    nn.fit(Phi)
    distances, indices = nn.kneighbors(Phi)

    G = nx.Graph()
    for i in range(n):
        G.add_node(i, system=systems[i], flow=flow[i], curv=curv[i], dens=dens[i])
    for i in range(n):
        for j, d in zip(indices[i, 1:], distances[i, 1:]):
            G.add_edge(i, j, weight=d)

    # Graph statistics
    print(f"    Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    try:
        betweenness = nx.betweenness_centrality(G, weight="weight")
        for i in np.argsort(list(betweenness.values()))[-3:][::-1]:
            print(f"    High betweenness: {systems[i]} "
                  f"(flow={flow[i]:.2f}, centrality={betweenness[i]:.3f})")
    except:
        pass

    # C2 — Local curvature tensor (approximate)
    print("\n  C2 — Local curvature (directional second derivative)")
    curv_tensors = []
    for i in range(n):
        neigh_dist = distances[i, 1:]
        neigh_pos = Phi[indices[i, 1:]]
        if len(neigh_pos) < 4:
            curv_tensors.append(np.zeros((4, 4)))
            continue
        # Second derivative: scatter of neighbor positions around point
        centered = neigh_pos - Phi[i]
        # Weight by inverse distance
        weights = 1.0 / (neigh_dist + 1e-10)
        weights = weights / weights.sum()
        # Weighted covariance = local metric tensor
        cov = np.cov(centered.T, aweights=weights) if len(centered) > 4 else np.cov(centered.T)
        curv_tensors.append(cov)

    # C3 — Local anisotropy (ratio of largest to smallest eigenvalue of local cov)
    print("\n  C3 — Local anisotropy")
    anisotropies = []
    for i, cov in enumerate(curv_tensors):
        if cov.size == 0 or np.allclose(cov, 0):
            anisotropies.append(1.0)
            continue
        eigvals = np.linalg.eigvalsh(cov)
        eigvals = np.maximum(eigvals, 0)
        if eigvals[-1] > 1e-10:
            aniso = eigvals[-1] / max(eigvals[0], 1e-12)
        else:
            aniso = 1.0
        anisotropies.append(float(aniso))

    for i in np.argsort(anisotropies)[-5:][::-1]:
        print(f"    {systems[i]:<24s} anisotropy={anisotropies[i]:.3f} "
              f"flow={flow[i]:.2f} curv={curv[i]:.3f}")

    # C4 — Density gradient (direction of increasing density in Φ-space)
    print("\n  C4 — Density gradient")
    try:
        kde = gaussian_kde(Phi.T, bw_method=0.5)
        eps = 0.01
        density_gradients = []
        for i in range(n):
            grad = np.zeros(4)
            for j in range(4):
                Phi_plus = Phi.copy()
                Phi_minus = Phi.copy()
                Phi_plus[i, j] += eps
                Phi_minus[i, j] -= eps
                d_plus = float(kde(Phi_plus[i:i+1].T))
                d_minus = float(kde(Phi_minus[i:i+1].T))
                grad[j] = (d_plus - d_minus) / (2 * eps)
            density_gradients.append(grad)

        # Systems with steepest density gradient
        grad_norms = [np.linalg.norm(g) for g in density_gradients]
        steepest = np.argsort(grad_norms)[-5:][::-1]
        print(f"    Steepest density gradients:")
        for i in steepest:
            print(f"      {systems[i]:<24s} |∇ρ|={grad_norms[i]:.4f} "
                  f"dir=({', '.join(f'{density_gradients[i][j]:+.3f}' for j in range(4))})")
    except Exception as e:
        print(f"    Density gradient failed: {e}")
        density_gradients = None

    # C5 — Perturbation drift vector
    print("\n  C5 — Perturbation drift (where does noise push the system?)")
    feat = pd.read_csv(OUT / "clustering_feature_matrix.csv")
    feat = feat[feat["system"].isin(ALL_SYSTEMS)].set_index("system").loc[ALL_SYSTEMS]
    X = feat.values.astype(float)
    n_trials = 100
    sigma = 0.3
    drift_vectors = []
    for i in range(n):
        drifts = []
        for _ in range(n_trials):
            X_noise = X.copy()
            X_noise[i] += np.random.normal(0, sigma, X.shape[1])
            dist_shift = np.linalg.norm(X_noise[i] - X[i])
            drifts.append(dist_shift)
        drift_vectors.append(float(np.mean(drifts)))

    for i in np.argsort(drift_vectors)[-5:][::-1]:
        print(f"    {systems[i]:<24s} drift={drift_vectors[i]:.3f} "
              f"flow={flow[i]:.2f}")

    # C6 — Transition probability (from nearest-neighbor flow direction)
    print("\n  C6 — Local transition probability")
    trans_probs = []
    for i in range(n):
        # Probability = fraction of neighbors that are in a different "flow regime"
        neigh_flows = flow[indices[i, 1:]]
        local_std = np.std(neigh_flows)
        mean_flow = flow[i]
        # Transition if neighbor flow differs by > 1 std
        n_trans = np.sum(np.abs(neigh_flows - mean_flow) > max(local_std, 0.5))
        prob = n_trans / max(len(neigh_flows), 1)
        trans_probs.append(prob)

    for i in np.argsort(trans_probs)[-5:][::-1]:
        print(f"    {systems[i]:<24s} trans_prob={trans_probs[i]:.3f} "
              f"flow={flow[i]:.2f}")

    print(f"\n  Correlation: trans_prob ~ flow")
    r_tp, p_tp = pearsonr(trans_probs, flow)
    print(f"    r={r_tp:.3f}, p={p_tp:.4f}")

    result = {
        "flow_by_system": {systems[i]: float(flow[i]) for i in range(n)},
        "anisotropy": {systems[i]: float(anisotropies[i]) for i in range(n)},
        "drift": {systems[i]: float(drift_vectors[i]) for i in range(n)},
        "transition_probability": {systems[i]: float(trans_probs[i]) for i in range(n)},
        "trans_prob_flow_corr": {"r": float(r_tp), "p": float(p_tp)},
    }
    return result


# =====================================================================
# SECTION D — DIMENSIONAL STABILITY
# =====================================================================

def section_d_dimensional_stability(data):
    """
    Test whether bridge/high-flow regions survive under:
    PCA, SpectralEmbedding, Isomap, LLE, MDS, t-SNE
    """
    print_sep()
    print("SECTION D: DIMENSIONAL STABILITY")
    print("=" * 70)
    print("Does the bridge survive under different embeddings?")
    print_sep()

    Phi = data["Phi"]
    flow = data["flow"]
    systems = data["coord"]["system"].tolist()

    # Define embeddings
    embeddings = {
        "PCA": PCA(n_components=2).fit_transform(Phi),
        "SpectralEmbedding": SpectralEmbedding(n_components=2, random_state=42).fit_transform(Phi),
        "Isomap": Isomap(n_components=2).fit_transform(Phi),
        "LLE": LocallyLinearEmbedding(n_components=2, random_state=42).fit_transform(Phi),
        "MDS": MDS(n_components=2, random_state=42, normalized_stress=False).fit_transform(Phi),
    }

    print(f"\n  {'Embedding':<22s}  {'Flow r':>8s}  {'p':>8s}  {'Bridge sep':>10s}  {'Status':>12s}")
    print(f"  {'-'*62}")

    results = {}
    orig_dists = squareform(pdist(Phi))

    for name, Phi_2d in embeddings.items():
        # Flow correlation
        r_flow, p_flow, flow_orig, flow_embed = embedding_flow_correlation(Phi, Phi_2d)

        # Bridge separation: what fraction of nearest neighbors are other bridge systems?
        bridge_idx = [i for i, s in enumerate(systems) if s in BRIDGE_SYSTEMS]
        nn_embed = NearestNeighbors(n_neighbors=min(4, len(systems)-1), metric="euclidean")
        nn_embed.fit(Phi_2d)
        _, embed_idxs = nn_embed.kneighbors(Phi_2d)

        bridge_nn_frac = 0
        for i in bridge_idx:
            neighs = embed_idxs[i, 1:]
            bridge_neighbors = sum(1 for j in neighs if j in bridge_idx)
            bridge_nn_frac += bridge_neighbors / max(len(neighs), 1)
        bridge_nn_frac /= max(len(bridge_idx), 1)

        # Embedding distortion
        embed_dists = squareform(pdist(Phi_2d))
        dist_corr, _ = pearsonr(orig_dists.ravel(), embed_dists.ravel())

        bridge_sep = "SEPARATE" if bridge_nn_frac > 0.3 else "MERGED"
        results[name] = {
            "flow_r": float(r_flow), "flow_p": float(p_flow),
            "bridge_nn_frac": float(bridge_nn_frac),
            "distortion_r": float(dist_corr),
            "bridge_separate": bridge_nn_frac > 0.3,
        }
        print(f"  {name:<22s}  {r_flow:>+8.4f}  {p_flow:>.4f}  "
              f"{bridge_nn_frac:>10.3f}  {bridge_sep:>12s}")

    # D2 — Flow field topology preservation
    print(f"\n  D2 — Flow field rank preservation")
    flow_rank = np.argsort(np.argsort(flow))
    for name, Phi_2d in embeddings.items():
        _, _, flow_orig, flow_embed = embedding_flow_correlation(Phi, Phi_2d)
        embed_rank = np.argsort(np.argsort(flow_embed))
        rank_corr, _ = spearmanr(flow_rank, embed_rank)
        print(f"    {name:<22s} rank_ρ={rank_corr:.4f}")

    # D3 — t-SNE (separate, non-deterministic)
    print(f"\n  D3 — t-SNE (multi-run stability)")
    from sklearn.manifold import TSNE
    tsne_flows = []
    for seed in range(10):
        tsne = TSNE(n_components=2, random_state=seed, perplexity=min(5, len(systems)-1))
        try:
            Phi_tsne = tsne.fit_transform(Phi)
            _, r_tsne, _, _ = embedding_flow_correlation(Phi, Phi_tsne)
            tsne_flows.append(r_tsne)
        except:
            pass
    if tsne_flows:
        print(f"    t-SNE flow_r: mean={np.mean(tsne_flows):.4f} ± "
              f"{np.std(tsne_flows):.4f} over 10 runs")

    result = {
        name: {
            "flow_r": v["flow_r"], "flow_p": v["flow_p"],
            "bridge_nn_frac": v["bridge_nn_frac"],
            "distortion": v["distortion_r"],
        }
        for name, v in results.items()
    }
    result["tsne_multirun"] = {
        "mean_r": float(np.mean(tsne_flows)) if tsne_flows else None,
        "std_r": float(np.std(tsne_flows)) if tsne_flows else None,
    }
    return result


# =====================================================================
# SECTION E — TOPOLOGICAL ANALYSIS
# =====================================================================

def section_e_topological(data):
    """
    Persistent homology, Betti numbers, Morse structure.
    Simplified implementation for 14-point cloud.
    """
    print_sep()
    print("SECTION E: TOPOLOGICAL ANALYSIS")
    print("=" * 70)
    print("Persistent homology, Morse structure, bottleneck detection")
    print_sep()

    Phi = data["Phi"]
    flow = data["flow"]
    systems = data["coord"]["system"].tolist()

    # E1 — Simple persistent homology (Vietoris-Rips for 14 points)
    print("\n  E1 — Persistent homology (Vietoris-Rips)")
    dist_mat = squareform(pdist(Phi))
    n = len(systems)

    # Sort all edges by distance
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            edges.append((dist_mat[i, j], i, j))
    edges.sort(key=lambda x: x[0])

    # Track component births (β₀)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
            return True
        return False

    # Birth times for each component
    n_components = n
    birth_times = {i: 0.0 for i in range(n)}
    death_times = {}
    component_size = {i: 1 for i in range(n)}

    persistence_b0 = []
    current_threshold = 0.0
    edge_idx = 0

    while n_components > 1 and edge_idx < len(edges):
        d, i, j = edges[edge_idx]
        edge_idx += 1
        current_threshold = d

        pi, pj = find(i), find(j)
        if pi != pj:
            # Merge components: the smaller one dies
            if component_size[pi] < component_size[pj]:
                small, big = pi, pj
            else:
                small, big = pj, pi
            union(i, j)
            # small component dies at this threshold
            death_times[small] = d
            persistence_b0.append((birth_times[small], d))
            component_size[big] += component_size[small]
            n_components -= 1

    # The last component never dies
    root = find(0)
    death_times[root] = float('inf')
    persistence_b0.append((birth_times[root], float('inf')))

    print(f"    β₀ persistence pairs: {len(persistence_b0)}")
    for b, d in persistence_b0:
        life = d - b if d != float('inf') else float('inf')
        life_str = f"{life:.3f}" if life != float('inf') else "∞"
        print(f"      birth={b:.3f}, death={d if d!=float('inf') else '∞':>8}, "
              f"lifetime={life_str}")

    # E2 — Simple β₁ detection (loop finding)
    print("\n  E2 — Loop detection (β₁)")
    # For each threshold, build the graph and find cycles
    # We look for the thresholds where loops appear

    # Build the Delaunay triangulation for adjacency
    try:
        delaunay = Delaunay(Phi)
        delaunay_edges = set()
        for simplex in delaunay.simplices:
            for i, j in itertools.combinations(simplex, 2):
                if i != j:
                    delaunay_edges.add((min(i, j), max(i, j)))

        print(f"    Delaunay edges: {len(delaunay_edges)}")

        # Build graph
        G_delaunay = nx.Graph()
        for i in range(n):
            G_delaunay.add_node(i)
        for i, j in delaunay_edges:
            G_delaunay.add_edge(i, j, weight=dist_mat[i, j])

        # Count cycles using fundamental cycles (cyclomatic number)
        cycles = nx.cycle_basis(G_delaunay)
        print(f"    Fundamental cycles found: {len(cycles)}")
        for cyc in cycles[:5]:
            cyc_flows = [flow[i] for i in cyc]
            print(f"      Cycle size={len(cyc)}, mean flow={np.mean(cyc_flows):.3f}, "
                  f"members={', '.join(systems[i] for i in cyc)}")
    except Exception as e:
        print(f"    Delaunay failed: {e}")
        cycles = []

    # E3 — Morse structure: critical points of flow field
    print("\n  E3 — Morse structure (flow field critical points)")
    # A point is a local max if all neighbors have lower flow
    nn = NearestNeighbors(n_neighbors=min(5, n-1), metric="euclidean")
    nn.fit(Phi)
    _, indices = nn.kneighbors(Phi)

    local_maxima = []
    local_minima = []
    for i in range(n):
        neigh_flows = flow[indices[i, 1:]]
        if flow[i] > neigh_flows.max():
            local_maxima.append(i)
        if flow[i] < neigh_flows.min():
            local_minima.append(i)

    print(f"    Local maxima (flow peaks): {[systems[i] for i in local_maxima]}")
    print(f"    Local minima (flow valleys): {[systems[i] for i in local_minima]}")

    # E4 — Bottleneck detection
    print("\n  E4 — Transition corridor detection")
    try:
        # Use minimum spanning tree to find bottlenecks
        G_mst = nx.Graph()
        for i in range(n):
            G_mst.add_node(i)
        for d, i, j in edges:
            G_mst.add_edge(i, j, weight=d)

        mst = nx.minimum_spanning_tree(G_mst, weight="weight")

        # Bottleneck edges: highest-weight edges in MST (edges that connect clusters)
        mst_edges = sorted(mst.edges(data=True), key=lambda x: x[2]["weight"], reverse=True)
        print(f"    MST bottlenecks (longest MST edges):")
        for (i, j, attr) in mst_edges[:4]:
            w = attr["weight"]
            print(f"      {systems[i]} — {systems[j]}: d={w:.3f} "
                  f"(flow {flow[i]:.2f} → {flow[j]:.2f})")

        # Graph Laplacian for spectral clustering (check if natural split exists)
        L = nx.laplacian_matrix(G_delaunay).todense()
        eigvals = np.linalg.eigvalsh(L)
        eig_gap = eigvals[1] - eigvals[0]
        print(f"    Spectral gap (Fiedler): {eig_gap:.4f}")
        print(f"    {'Connected graph' if eig_gap > 0.01 else 'NEAR-DISCONNECTED'}")

    except Exception as e:
        print(f"    Bottleneck detection failed: {e}")
        mst_edges = []

    result = {
        "persistence_b0": [[float(b), float(d) if d != float('inf') else None]
                           for b, d in persistence_b0],
        "n_cycles": len(cycles),
        "local_maxima": [systems[i] for i in local_maxima],
        "local_minima": [systems[i] for i in local_minima],
        "mst_bottlenecks": [
            {"edge": [systems[i], systems[j]], "distance": float(attr["weight"])}
            for (i, j, attr) in mst_edges[:4]
        ] if 'mst_edges' in dir() and mst_edges else [],
    }
    return result


# =====================================================================
# SECTION F — DESTROY THE ORIGINAL SYSTEM SET
# =====================================================================

def section_f_destroy_system_set(data):
    """
    Stress-test flow field survival by:
    - Removing 25%, 50% of systems
    - Replacing with synthetic systems
    - Comparing flow fields
    """
    print_sep()
    print("SECTION F: DESTROY THE ORIGINAL SYSTEM SET")
    print("=" * 70)
    print("Does the flow field survive system removal?")
    print_sep()

    Phi = data["Phi"]
    flow = data["flow"]
    systems = data["coord"]["system"].tolist()
    n = len(systems)

    # F1 — Random removal
    print("\n  F1 — Random system removal (flow field survival)")

    removal_levels = [0.25, 0.50]
    removal_results = []

    for frac in removal_levels:
        n_remove = max(1, int(n * frac))
        trials = 50
        flow_corrs = []
        bridge_preserved = []

        for _ in range(trials):
            remove_idx = np.random.choice(n, n_remove, replace=False)
            keep_idx = [i for i in range(n) if i not in remove_idx]

            # Recompute flow field in remaining subspace
            Phi_sub = Phi[keep_idx]
            n_sub = len(keep_idx)
            if n_sub < 4:
                continue

            # Approximate flow from Φ-space neighborhood
            flow_sub = np.array([compute_local_flow(Phi_sub, i) for i in range(n_sub)])

            # Compare with original flow for kept systems
            orig_flow_sub = flow[keep_idx]
            if np.std(flow_sub) > 0 and np.std(orig_flow_sub) > 0:
                r, _ = pearsonr(flow_sub, orig_flow_sub)
                flow_corrs.append(r)

            # Check if bridge systems are in top 3 flow in remaining set
            bridge_kept = [i for i in keep_idx if systems[i] in BRIDGE_SYSTEMS]
            if bridge_kept:
                top3 = np.argsort(flow_sub)[-3:]
                bridge_in_top3 = sum(1 for i, orig_i in enumerate(keep_idx)
                                     if orig_i in bridge_kept and i in top3)
                bridge_preserved.append(bridge_in_top3 / max(len(bridge_kept), 1))

        mean_corr = np.mean(flow_corrs) if flow_corrs else 0
        std_corr = np.std(flow_corrs) if flow_corrs else 0
        mean_bridge = np.mean(bridge_preserved) if bridge_preserved else 0
        print(f"    Remove {frac*100:.0f}% (n_remove={n_remove}): "
              f"flow_r={mean_corr:.3f}±{std_corr:.3f}, "
              f"bridge_preserved={mean_bridge:.3f}")
        removal_results.append({
            "frac_removed": frac, "n_remove": n_remove, "n_trials": trials,
            "flow_corr_mean": float(mean_corr),
            "flow_corr_std": float(std_corr),
            "bridge_preserved_frac": float(mean_bridge),
        })

    # F2 — Adversarial removal (remove stable systems first)
    print(f"\n  F2 — Adversarial removal (remove low-flow systems)")
    low_flow_idx = np.argsort(flow)[:3]
    high_flow_idx = np.argsort(flow)[-3:]

    # Remove low-flow systems
    keep_idx = [i for i in range(n) if i not in low_flow_idx]
    Phi_sub = Phi[keep_idx]
    flow_sub = np.array([compute_local_flow(Phi_sub, i) for i in range(len(keep_idx))])
    orig_flow_sub = flow[keep_idx]
    r_low, _ = pearsonr(flow_sub, orig_flow_sub)
    print(f"    Remove 3 lowest-flow: flow_r={r_low:.4f}")

    # Remove high-flow systems
    keep_idx2 = [i for i in range(n) if i not in high_flow_idx]
    Phi_sub2 = Phi[keep_idx2]
    flow_sub2 = np.array([compute_local_flow(Phi_sub2, i) for i in range(len(keep_idx2))])
    orig_flow_sub2 = flow[keep_idx2]
    r_high, _ = pearsonr(flow_sub2, orig_flow_sub2)
    print(f"    Remove 3 highest-flow: flow_r={r_high:.4f}")

    # F3 — Synthetic system injection
    print(f"\n  F3 — Synthetic system injection")
    for n_synth in [5, 10]:
        synth_corrs = []
        for _ in range(30):
            # Generate random synthetic points in Φ-space
            synth_Phi = np.random.uniform(-3, 3, (n_synth, 4))
            Phi_aug = np.vstack([Phi, synth_Phi])
            flow_aug = np.array([compute_local_flow(Phi_aug, i)
                                 for i in range(len(Phi_aug))])
            orig_flow_aug = flow_aug[:n]
            if np.std(orig_flow_aug) > 0 and np.std(flow[:n]) > 0:
                r, _ = pearsonr(orig_flow_aug, flow[:n])
                synth_corrs.append(r)

        if synth_corrs:
            print(f"    Inject {n_synth} synthetic: flow_corr={np.mean(synth_corrs):.4f}±"
                  f"{np.std(synth_corrs):.4f}")
        else:
            print(f"    Inject {n_synth} synthetic: FAILED")

    # F4 — Perturb Φ coordinates
    print(f"\n  F4 — Φ-coordinate perturbation")
    for sigma in [0.1, 0.3, 0.5]:
        pert_corrs = []
        for _ in range(30):
            Phi_pert = Phi + np.random.normal(0, sigma, Phi.shape)
            flow_pert = np.array([compute_local_flow(Phi_pert, i)
                                  for i in range(n)])
            if np.std(flow_pert) > 0 and np.std(flow) > 0:
                r, _ = pearsonr(flow_pert, flow)
                pert_corrs.append(r)
        print(f"    σ={sigma:.1f}: flow_corr={np.mean(pert_corrs):.4f}±"
              f"{np.std(pert_corrs):.4f}")

    result = {
        "removal": removal_results,
        "adversarial_low_flow_removal": float(r_low),
        "adversarial_high_flow_removal": float(r_high),
    }
    return result


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("=" * 70)
    print("T027: FLOW INVARIANT ANALYSIS")
    print("\"Does transition-flow survive without the clusters?\"")
    print("=" * 70)

    data = load_all()

    # Section A — Flow-only geometry
    sec_a = section_a_flow_only_geometry(data)

    # Section B — Flow invariant test
    sec_b = section_b_flow_invariant(data)

    # Section C — Local transition geometry
    sec_c = section_c_local_transition(data)

    # Section D — Dimensional stability
    sec_d = section_d_dimensional_stability(data)

    # Section E — Topological analysis
    sec_e = section_e_topological(data)

    # Section F — Destroy the system set
    sec_f = section_f_destroy_system_set(data)

    # === FINAL VERDICT ===
    print_sep()
    print("T027: FINAL VERDICT — Is the flow invariant fundamental?")
    print_sep()

    flow = data["flow"]
    systems = data["coord"]["system"].tolist()
    coll = data["coll"]

    # Criterion 1: Flow predicts collapse without clusters
    r_fc = sec_b["flow_collapse_r"]
    p_fc = sec_b["flow_collapse_p"]
    cluster_r2 = sec_b["cluster_model_r2"]
    flow_r2 = sec_b["flow_only_r2"]

    c1 = (p_fc < 0.05)
    c1a = (flow_r2 > cluster_r2)

    # Criterion 2: Bridge regions survive under all embeddings
    embed_flow_rs = [v["flow_r"] for v in sec_d.values() if isinstance(v, dict) and "flow_r" in v]
    c2 = all(r > 0.3 for r in embed_flow_rs) if embed_flow_rs else False

    # Criterion 3: Flow field survives system removal
    removal_r = [r["flow_corr_mean"] for r in sec_f["removal"]]
    c3 = all(r > 0.5 for r in removal_r) if removal_r else False

    # Criterion 4: Topology shows transition corridors
    n_cycles = sec_e["n_cycles"]
    c4 = n_cycles > 0

    criteria = [
        ("C1: Flow→collapse prediction (p<0.05)", c1, f"r={r_fc:.3f}, p={p_fc:.5f}"),
        ("C1a: Flow beats cluster model (R²)", c1a,
         f"flow_r²={flow_r2:.3f} vs cluster_r²={cluster_r2:.3f}"),
        ("C2: Bridge survives all embeddings", c2,
         f"flow_r={[f'{r:.3f}' for r in embed_flow_rs]}"),
        ("C3: Flow survives system removal", c3,
         f"removal_corr={[f'{r:.3f}' for r in removal_r]}"),
        ("C4: Topological corridors exist", c4, f"n_cycles={n_cycles}"),
    ]

    print(f"\n  {'Criterion':<48s}  {'Status':>8s}  {'Evidence':>25s}")
    print(f"  {'-'*83}")
    for name, passed, evidence in criteria:
        status = "✓" if passed else "✗"
        print(f"  {name:<48s}  {status:>8s}  {evidence:>25s}")

    n_passed = sum(1 for _, p, _ in criteria if p)
    n_total = len(criteria)

    print(f"\n  Passed: {n_passed}/{n_total}")

    # Determine if the flow invariant is established
    is_fundamental = (c1 and c1a and c2 and c3)
    is_valid = (c1 and (c1a or n_cycles > 0))

    print_sep()
    if is_fundamental:
        print("  VERDICT: FLOW INVARIANT IS FUNDAMENTAL ✓")
        print("  The bridge phenomenon is geometry-invariant and survives every attack.")
        print("  Transition-flow is more fundamental than taxonomy.")
    elif is_valid:
        print("  VERDICT: FLOW INVARIANT IS VALID BUT PARTIALLY FRAGILE")
        print("  Flow→collapse prediction works, but some tests show weakness.")
        print("  The field is real but may depend on the specific system set.")
    else:
        print("  VERDICT: FLOW INVARIANT NOT CONFIRMED ✗")
        print("  Flow does NOT consistently predict transition behavior")
        print("  without cluster membership.")

    print_sep()
    print()

    # Save all results
    all_results = {
        "section_a_flow_only_geometry": sec_a,
        "section_b_flow_invariant": sec_b,
        "section_c_local_transition": sec_c,
        "section_d_dimensional_stability": sec_d,
        "section_e_topological": sec_e,
        "section_f_destroy_system_set": sec_f,
        "final_verdict": {
            "criteria": {
                name: {"passed": p, "evidence": e}
                for name, p, e in criteria
            },
            "n_passed": n_passed,
            "n_total": n_total,
            "is_fundamental": is_fundamental,
            "is_valid": is_valid,
        }
    }

    with open(OUT / "t027_flow_invariant_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print("T027 complete. Results saved to:")
    print(f"  {OUT / 't027_flow_invariant_results.json'}")
    print()


if __name__ == "__main__":
    main()
