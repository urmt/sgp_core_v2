#!/usr/bin/env python3
"""
T029: GEODESIC EMBEDDING — Stability Tensor as Local Metric
===========================================================
Construct Φ-space manifold graph using the stability tensor as local metric,
replacing Euclidean distance with perturbation-response distance.

Core innovation: d_ij² = ||Φ_i - Φ_j||² + λ · ||M_i - M_j||²_F

This combines positional distance in emergence space with dynamical
response similarity. Systems with similar perturbation responses
are "close" even if far in Φ-space, and vice versa.

Sections:
  A: Stability metric computation
  B: Optimal λ via collapse prediction
  C: Combined-manifold graph analysis
  D: Intrinsic dimension comparison
  E: Bridge detection improvement
  F: Null test — shuffle tensor assignment
"""

import json, warnings, itertools
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform, cdist
from scipy.stats import pearsonr, spearmanr
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
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
AXES = ["C", "F", "A", "R"]

def print_sep():
    print("\n" + "=" * 70)

# =====================================================================
# DATA LOADING
# =====================================================================

def load_all():
    coord = pd.read_csv(OUT / "emergence_coordinates.csv")
    coord = coord[coord["system"].isin(ALL_SYSTEMS)].reset_index(drop=True)
    Phi = coord[AXES].values

    flow_df = pd.read_csv(OUT / "emergence_flow_field.csv")
    flow_map = {r["system"]: r["flow_magnitude"] for _, r in flow_df.iterrows()}
    flow_vals = np.array([flow_map[s] for s in ALL_SYSTEMS])

    with open(OUT / "emergence_energy_landscape.json") as f:
        landscape = json.load(f)
    dens_vals = np.array([landscape["density_per_system"].get(s, 0) for s in ALL_SYSTEMS])
    curv_map = {s: landscape["curvature_per_system"][s]["mean_curvature"] for s in ALL_SYSTEMS}
    curv_vals = np.array([curv_map[s] for s in ALL_SYSTEMS])

    with open(OUT / "r2_collapse_forecast.json") as f:
        coll = json.load(f)
    collapse_vals = np.array([np.mean(coll["collapse_curves"][s]) for s in ALL_SYSTEMS])
    sigmas = coll["sigmas_tested"]
    collapse_slopes = {}
    for sys_name, curve in coll["collapse_curves"].items():
        vals_at = [curve[i] for i in range(min(6, len(sigmas)))]
        if len(vals_at) > 1:
            slope = (vals_at[-1] - vals_at[0]) / (sigmas[min(5, len(sigmas)-1)] - sigmas[0])
        else:
            slope = 0.0
        collapse_slopes[sys_name] = slope
    collapse_slope_vals = np.array([collapse_slopes[s] for s in ALL_SYSTEMS])

    tensors = np.load(OUT / "t028_stability_tensor.npy")

    with open(OUT / "t028_transition_manifold_results.json") as f:
        t028 = json.load(f)

    return {
        "Phi": Phi, "flow": flow_vals, "dens": dens_vals, "curv": curv_vals,
        "collapse": collapse_vals, "collapse_slopes": collapse_slope_vals,
        "tensors": tensors, "t028": t028,
    }


# =====================================================================
# SECTION A — Stability Metric Computation
# =====================================================================

def section_a_stability_metric(data):
    print_sep()
    print("SECTION A: STABILITY METRIC COMPUTATION")
    print_sep()

    Phi = data["Phi"]
    tensors = data["tensors"]
    flow = data["flow"]
    n = len(ALL_SYSTEMS)

    # A1 — Φ-space Euclidean distance
    d_phi = squareform(pdist(Phi))
    norm_d_phi = d_phi / (d_phi.max() + 1e-12)

    # A2 — Stability tensor Frobenius distance
    d_stab = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d_stab[i, j] = np.linalg.norm(tensors[i] - tensors[j])
            d_stab[j, i] = d_stab[i, j]
    norm_d_stab = d_stab / (d_stab.max() + 1e-12)

    # A3 — Intrinsic metric distance (local metric g_i = M_i · M_i^T)
    # Riemannian-inspired: dR_ij² = ΔΦ^T · (g_i + g_j)/2 · ΔΦ   (but this mixes Φ and tensor)
    d_riemann = np.zeros((n, n))
    for i in range(n):
        g_i = tensors[i] @ tensors[i].T  # 4×4
        for j in range(i + 1, n):
            g_j = tensors[j] @ tensors[j].T
            g_avg = (g_i + g_j) / 2
            dPhi = Phi[i] - Phi[j]
            d_riemann[i, j] = np.sqrt(max(dPhi @ g_avg @ dPhi, 0))
            d_riemann[j, i] = d_riemann[i, j]
    norm_d_riemann = d_riemann / (d_riemann.max() + 1e-12)
    nan_mask = np.isnan(norm_d_riemann)
    norm_d_riemann[nan_mask] = 0

    # A4 — Metric relationships
    print("\n  A1 — Distance metric correlations")
    metrics = [
        ("dΦ (Euclidean)", d_phi),
        ("dS (Stability Frob)", d_stab),
        ("dR (Riemannian)", d_riemann),
    ]
    for (n1, v1), (n2, v2) in itertools.combinations(metrics, 2):
        r, p = pearsonr(v1.ravel(), v2.ravel())
        print(f"    {n1} vs {n2}: r={r:.4f}, p={p:.4f}")

    # A5 — Per-system stability similarity
    print("\n  A2 — Most similar/dissimilar stability tensors")
    for i, s in enumerate(ALL_SYSTEMS):
        closest = np.argsort(d_stab[i])[1]
        farthest = np.argsort(d_stab[i])[-1]
        print(f"    {s:<24s}  closest={ALL_SYSTEMS[closest]:<24s}  "
              f"farthest={ALL_SYSTEMS[farthest]:<24s}")

    result = {
        "d_phi_corr": float(pearsonr(d_phi.ravel(), d_stab.ravel())[0]),
        "d_phi_riemann_corr": float(pearsonr(d_phi.ravel(), d_riemann.ravel())[0]),
        "d_stab_riemann_corr": float(pearsonr(d_stab.ravel(), d_riemann.ravel())[0]),
    }
    return result, d_phi, d_stab, d_riemann, norm_d_phi, norm_d_stab, norm_d_riemann


# =====================================================================
# SECTION B — Optimal λ Search
# =====================================================================

def section_b_optimal_lambda(data, norm_d_phi, norm_d_stab):
    print_sep()
    print("SECTION B: OPTIMAL λ — Tuning combined metric for collapse prediction")
    print_sep()

    collapse = data["collapse"]
    flow = data["flow"]
    n = len(ALL_SYSTEMS)

    # Helper: correlation between geodesic betweenness and collapse
    def eval_lambda(lmbda):
        d_combined = norm_d_phi + lmbda * norm_d_stab
        # Build kNN graph
        k = min(4, n - 1)
        G = nx.Graph()
        for i in range(n):
            G.add_node(i)
        for i in range(n):
            nearest = np.argsort(d_combined[i])[1:k+1]
            for j in nearest:
                G.add_edge(i, j, weight=d_combined[i, j])
        try:
            betweenness = nx.betweenness_centrality(G, weight="weight")
        except:
            return 0.0, 0.0
        b_vals = np.array([betweenness[i] for i in range(n)])
        if np.std(b_vals) == 0 or np.std(collapse) == 0:
            return 0.0, 0.0
        r, p = pearsonr(b_vals, collapse)
        return abs(r) if not np.isnan(r) else 0.0, float(p)

    # Scan λ
    lambdas = [0, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
    print(f"\n  {'λ':>8s}  {'|r(between, collapse)|':>24s}  {'p':>8s}")
    print(f"  {'-'*44}")

    best_lambda = 0.0
    best_r = 0.0
    results = []
    for lmbda in lambdas:
        r, p = eval_lambda(lmbda)
        results.append({"lambda": lmbda, "r": r, "p": p})
        print(f"  {lmbda:>8.4f}  {r:>24.4f}  {p:>8.4f}")
        if r > best_r:
            best_r = r
            best_lambda = lmbda

    print(f"\n  Best λ = {best_lambda:.4f} (r={best_r:.4f})")
    print(f"  {'Stability metric IMPROVES prediction' if best_lambda > 0 else 'Pure Euclidean is best'}")

    # Compare: pure Φ-space vs best combined
    r_phi, p_phi = eval_lambda(0.0)
    print(f"\n  Pure Φ-space:     r={r_phi:.4f}, p={p_phi:.4f}")
    print(f"  Best combined:    r={best_r:.4f} (λ={best_lambda:.4f})")
    print(f"  {'✓ Combined metric wins' if best_r > r_phi * 1.05 else 'Euclidean Φ-space is sufficient'}")

    result = {
        "lambda_scan": results,
        "best_lambda": float(best_lambda),
        "best_r": float(best_r),
        "phi_only_r": float(r_phi),
        "combined_wins": best_r > r_phi * 1.05,
    }
    return result


# =====================================================================
# SECTION C — Combined-Manifold Graph Analysis
# =====================================================================

def section_c_combined_graph(data, norm_d_phi, norm_d_stab, opt_lambda, opt_lambda_r):
    print_sep()
    print("SECTION C: COMBINED-MANIFOLD GRAPH ANALYSIS")
    print_sep()

    Phi = data["Phi"]
    flow = data["flow"]
    collapse = data["collapse"]
    n = len(ALL_SYSTEMS)

    # Build graphs for pure Φ and combined
    def build_graph(d_mat, k=4):
        G = nx.Graph()
        for i in range(n):
            G.add_node(i, system=ALL_SYSTEMS[i], flow=flow[i])
        for i in range(n):
            nearest = np.argsort(d_mat[i])[1:k+1]
            for j in nearest:
                G.add_edge(i, j, weight=d_mat[i, j])
        return G

    # Use the best lambda (or λ=1 if 0)
    lmbda = opt_lambda if opt_lambda > 0 else 1.0
    d_combined = norm_d_phi + lmbda * norm_d_stab

    G_phi = build_graph(norm_d_phi)
    G_combined = build_graph(d_combined)

    # C1 — Graph statistics
    print("\n  C1 — Graph comparison")
    for name, G in [("Pure Φ", G_phi), ("Combined", G_combined)]:
        print(f"    {name}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        betweenness = nx.betweenness_centrality(G, weight="weight")
        b_vals = np.array([betweenness[i] for i in range(n)])
        r, p = pearsonr(b_vals, flow)
        print(f"      betweenness ~ flow: r={r:.4f}, p={p:.4f}")

    # C2 — Centrality shift
    print("\n  C2 — Centrality shift (Φ → Combined)")
    b_phi = nx.betweenness_centrality(G_phi, weight="weight")
    b_comb = nx.betweenness_centrality(G_combined, weight="weight")
    for i in range(n):
        diff = b_comb[i] - b_phi[i]
        arrow = "↑↑" if diff > 0.05 else "↑" if diff > 0.01 else "→" if diff > -0.01 else "↓"
        print(f"    {ALL_SYSTEMS[i]:<24s}  Φ_b={b_phi[i]:.4f}  →  comb_b={b_comb[i]:.4f}  {arrow}")

    # C3 — Bridge centrality in combined graph
    print("\n  C3 — Bridge centrality")
    bridge_idx = [i for i, s in enumerate(ALL_SYSTEMS) if s in BRIDGE_SYSTEMS]
    b_comb_arr = np.array([b_comb[i] for i in range(n)])
    bridge_b = np.mean([b_comb[i] for i in bridge_idx])
    other_b = np.mean([b_comb[i] for i in range(n) if i not in bridge_idx])
    print(f"    Bridge mean betweenness: {bridge_b:.4f}")
    print(f"    Non-bridge mean betweenness: {other_b:.4f}")
    print(f"    {'✓ Bridge elevated' if bridge_b > other_b else 'Bridge NOT elevated'}")

    # C4 — Community detection comparison
    print("\n  C4 — Community structure (Louvain)")
    try:
        import networkx.algorithms.community as nx_comm
        comm_phi = nx_comm.louvain_communities(G_phi, weight="weight", seed=42)
        comm_comb = nx_comm.louvain_communities(G_combined, weight="weight", seed=42)
        print(f"    Φ-space communities: {len(comm_phi)} groups")
        for ci, comm in enumerate(comm_phi):
            members = [ALL_SYSTEMS[i] for i in comm]
            print(f"      Group {ci}: {', '.join(members)}")
        print(f"    Combined communities: {len(comm_comb)} groups")
        for ci, comm in enumerate(comm_comb):
            members = [ALL_SYSTEMS[i] for i in comm]
            print(f"      Group {ci}: {', '.join(members)}")
    except Exception:
        print("    Louvain failed, using hierarchical clustering")
        # Hierarchical
        Z_phi = linkage(norm_d_phi[np.triu_indices(n, k=1)], method="ward")
        Z_comb = linkage(d_combined[np.triu_indices(n, k=1)], method="ward")
        labels_phi = fcluster(Z_phi, t=3, criterion="maxclust")
        labels_comb = fcluster(Z_comb, t=3, criterion="maxclust")
        print(f"    Φ clusters: {labels_phi}")
        print(f"    Combined clusters: {labels_comb}")

    # C5 — Geodesic betweenness ~ collapse prediction
    print("\n  C5 — Collapse prediction via combined betweenness")
    r_bc, p_bc = pearsonr(b_comb_arr, collapse)
    print(f"    combined_betweenness ~ collapse: r={r_bc:.4f}, p={p_bc:.4f}")
    # Using linear model
    lr = LinearRegression()
    try:
        scores = cross_val_score(lr, b_comb_arr.reshape(-1, 1), collapse,
                                 cv=min(5, n // 2), scoring="r2")
        print(f"    CV R² = {scores.mean():.4f} ± {scores.std():.4f}")
    except:
        print("    CV failed (n too small)")

    result = {
        "phi_betweenness": {ALL_SYSTEMS[i]: float(b_phi[i]) for i in range(n)},
        "combined_betweenness": {ALL_SYSTEMS[i]: float(b_comb[i]) for i in range(n)},
        "bridge_combined_b_mean": float(bridge_b),
        "nonbridge_combined_b_mean": float(other_b),
        "bridge_elevated": bridge_b > other_b,
        "combined_betweenness_flow_r": float(pearsonr(b_comb_arr, flow)[0]),
        "combined_betweenness_flow_p": float(pearsonr(b_comb_arr, flow)[1]),
    }
    return result


# =====================================================================
# SECTION D — Intrinsic Dimension Comparison
# =====================================================================

def section_d_intrinsic_dimension(data, norm_d_phi, norm_d_stab):
    print_sep()
    print("SECTION D: INTRINSIC DIMENSION — Φ vs Stability-Φ")
    print_sep()

    tensors = data["tensors"]
    n = len(ALL_SYSTEMS)

    # D1 — PCA on Φ-space vs tensor-space
    print("\n  D1 — PCA explained variance")
    for name, X in [("Φ-space", data["Phi"]), ("Tensor-space (flattened)",
                    tensors.reshape(n, -1))]:
        pca = PCA().fit(X)
        cumvar = np.cumsum(pca.explained_variance_ratio_)
        n_90 = np.searchsorted(cumvar, 0.90) + 1
        n_95 = np.searchsorted(cumvar, 0.95) + 1
        print(f"    {name:<30s} dim={X.shape[1]:>2d}, 90% var={n_90:>2d}, 95% var={n_95:>2d}")

    # D2 — Participation ratio
    print("\n  D2 — Participation ratio")
    for name, X in [("Φ-space", data["Phi"]), ("Tensor-space", tensors.reshape(n, -1))]:
        pca = PCA().fit(X)
        pr = (pca.explained_variance_ratio_.sum())**2 / (pca.explained_variance_ratio_**2).sum()
        print(f"    {name:<30s} participation_ratio={pr:.3f}")

    # D3 — MLE intrinsic dimension
    print("\n  D3 — MLE intrinsic dimension (k=5)")
    from sklearn.neighbors import NearestNeighbors
    for name, X in [("Φ-space", data["Phi"]), ("Tensor-space", tensors.reshape(n, -1))]:
        nn = NearestNeighbors(n_neighbors=6)
        nn.fit(X)
        dists, _ = nn.kneighbors(X)
        Tk = dists[:, -1]
        Tk1 = np.maximum(dists[:, -2], 1e-12)
        mle = np.mean((len(ALL_SYSTEMS) - 1) / np.sum(np.log(Tk / Tk1))) if len(ALL_SYSTEMS) > 6 else 0
        print(f"    {name:<30s} MLE_dim={mle:.3f}")

    result = {
        "phi_participation_ratio": None,
        "tensor_participation_ratio": None,
    }
    return result


# =====================================================================
# SECTION E — Bridge Detection Improvement
# =====================================================================

def section_e_bridge_detection(data, norm_d_phi, norm_d_stab, opt_lambda):
    print_sep()
    print("SECTION E: BRIDGE DETECTION — Does combined metric improve?")
    print_sep()

    flow = data["flow"]
    Phi = data["Phi"]
    n = len(ALL_SYSTEMS)

    lmbda = opt_lambda if opt_lambda > 0 else 1.0
    d_combined = norm_d_phi + lmbda * norm_d_stab

    # E1 — Bridge separation in combined metric
    print("\n  E1 — Bridge separation")
    for name, d_mat in [("Φ Euclidean", norm_d_phi), ("Stability Frobenius", norm_d_stab),
                        ("Combined", d_combined)]:
        bridge_idx = [i for i, s in enumerate(ALL_SYSTEMS) if s in BRIDGE_SYSTEMS]
        non_bridge = [i for i in range(n) if i not in bridge_idx]
        within_bridge = [d_mat[i, j] for i in bridge_idx for j in bridge_idx if i < j]
        bridge_non = [d_mat[i, j] for i in bridge_idx for j in non_bridge]
        avg_within = np.mean(within_bridge) if within_bridge else 0
        avg_cross = np.mean(bridge_non) if bridge_non else 0
        sep_ratio = avg_within / max(avg_cross, 1e-12)
        print(f"    {name:<25s} within_bridge={avg_within:.3f}  "
              f"cross={avg_cross:.3f}  ratio={sep_ratio:.3f}")

    # E2 — Flow prediction by nearest-neighbor in each metric
    print("\n  E2 — Flow prediction via kNN")
    bridge_idx_set = set([i for i, s in enumerate(ALL_SYSTEMS) if s in BRIDGE_SYSTEMS])
    for name, d_mat in [("Φ Euclidean", norm_d_phi), ("Combined", d_combined)]:
        predicted_flow = np.zeros(n)
        for i in range(n):
            nearest = np.argsort(d_mat[i])[1:4]
            predicted_flow[i] = flow[nearest].mean()
        r, p = pearsonr(flow, predicted_flow)
        # Bridge neighbor accuracy
        bridge_correct = 0
        for i in bridge_idx_set:
            nearest = np.argsort(d_mat[i])[1:4]
            bridge_neighbors = sum(1 for j in nearest if j in bridge_idx_set)
            bridge_correct += bridge_neighbors
        print(f"    {name:<25s} flow_pred_r={r:.4f}, bridge_nn_accuracy={bridge_correct:.0f}/{len(bridge_idx_set)*3}")

    return {"bridge_separation": float(sep_ratio)}


# =====================================================================
# SECTION F — Null Test
# =====================================================================

def section_f_null_test(data, norm_d_phi, norm_d_stab):
    print_sep()
    print("SECTION F: NULL TEST — Shuffle tensor assignment")
    print_sep()

    tensors = data["tensors"]
    flow = data["flow"]
    n = len(ALL_SYSTEMS)

    r_real, _ = pearsonr(flow, [np.linalg.norm(tensors[i]) for i in range(n)])

    n_trials = 1000
    null_corrs = []
    for _ in range(n_trials):
        shuffled_idx = np.random.permutation(n)
        tensors_null = tensors[shuffled_idx]
        frob_null = np.array([np.linalg.norm(tensors_null[i]) for i in range(n)])
        r, _ = pearsonr(flow, frob_null)
        null_corrs.append(abs(r) if not np.isnan(r) else 0.0)

    null_mean = np.mean(null_corrs)
    null_std = np.std(null_corrs)
    z_score = (abs(r_real) - null_mean) / max(null_std, 1e-12)

    print(f"  Real: |r(‖M‖_F, flow)| = {abs(r_real):.4f}")
    print(f"  Null (shuffled): mean |r| = {null_mean:.4f} ± {null_std:.4f}")
    print(f"  Z-score = {z_score:.3f}")
    print(f"  {'✓ Tensor-flow correlation IS significant' if z_score > 2.0 else 'Tensor-flow correlation NOT significant'}")

    # Combined metric null
    print(f"\n  F1 — Combined metric null")
    null_betweenness_corrs = []
    for _ in range(200):
        shuffled_idx = np.random.permutation(n)
        d_stab_null = norm_d_stab.copy()
        # Shuffle rows and cols
        d_stab_null = d_stab_null[shuffled_idx][:, shuffled_idx]
        d_combined_null = norm_d_phi + 1.0 * d_stab_null

        k = min(4, n - 1)
        G = nx.Graph()
        for i in range(n):
            G.add_node(i)
        for i in range(n):
            nearest = np.argsort(d_combined_null[i])[1:k+1]
            for j in nearest:
                G.add_edge(i, j, weight=d_combined_null[i, j])
        try:
            betweenness = nx.betweenness_centrality(G, weight="weight")
            b_vals = np.array([betweenness[i] for i in range(n)])
            if np.std(b_vals) > 0:
                r, _ = pearsonr(b_vals, flow)
                null_betweenness_corrs.append(abs(r) if not np.isnan(r) else 0.0)
        except:
            pass

    if null_betweenness_corrs:
        b_real, _ = pearsonr(flow, [0.0] * n)  # placeholder, filled below
        print(f"    Null mean |r| = {np.mean(null_betweenness_corrs):.4f} ± {np.std(null_betweenness_corrs):.4f}")

    result = {
        "real_frob_flow_r": float(r_real),
        "null_mean_r": float(null_mean),
        "null_std_r": float(null_std),
        "z_score": float(z_score),
        "is_significant": z_score > 2.0,
    }
    return result


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("=" * 70)
    print("T029: GEODESIC EMBEDDING — Stability Tensor as Local Metric")
    print("=" * 70)

    data = load_all()

    # Section A — Distance metrics
    sec_a, d_phi, d_stab, d_riemann, nd_phi, nd_stab, nd_riem = \
        section_a_stability_metric(data)

    # Section B — Optimal λ
    sec_b = section_b_optimal_lambda(data, nd_phi, nd_stab)

    # Section C — Combined graph
    opt_lambda = sec_b["best_lambda"] if sec_b["best_lambda"] > 0 else 1.0
    sec_c = section_c_combined_graph(data, nd_phi, nd_stab, sec_b["best_lambda"], sec_b["best_r"])

    # Section D — Intrinsic dimension
    sec_d = section_d_intrinsic_dimension(data, nd_phi, nd_stab)

    # Section E — Bridge detection
    sec_e = section_e_bridge_detection(data, nd_phi, nd_stab, sec_b["best_lambda"])

    # Section F — Null test
    sec_f = section_f_null_test(data, nd_phi, nd_stab)

    # === FINAL VERDICT ===
    print_sep()
    print("T029 FINAL VERDICT — Does stability tensor improve geodesic embedding?")
    print_sep()

    combined_wins = sec_b["combined_wins"]
    bridge_elevated = sec_c["bridge_elevated"]
    is_significant = sec_f["is_significant"]

    criteria = [
        ("B: Combined metric beats Euclidean (r improvement)", combined_wins,
         f"best_r={sec_b['best_r']:.3f} vs Φ_r={sec_b['phi_only_r']:.3f}"),
        ("C: Bridge elevated in combined graph", bridge_elevated,
         f"bridge_b={sec_c['bridge_combined_b_mean']:.3f} vs other={sec_c['nonbridge_combined_b_mean']:.3f}"),
        ("F: Tensor-flow correlation significant (z>2)", is_significant,
         f"z={sec_f['z_score']:.3f}"),
    ]

    print(f"\n  {'Criterion':<55s}  {'Status':>8s}  {'Evidence':>30s}")
    print(f"  {'-'*95}")
    for name, passed, evidence in criteria:
        status = "✓" if passed else "✗"
        print(f"  {name:<55s}  {status:>8s}  {evidence:>30s}")

    n_passed = sum(1 for _, p, _ in criteria if p)
    print(f"\n  Passed: {n_passed}/{len(criteria)}")

    if n_passed >= 2:
        print("\n  VERDICT: STABILITY TENSOR ENRICHES MANIFOLD STRUCTURE")
        print("  The combined metric captures dynamical response information")
        print("  that pure Φ-space distance misses.")
    elif n_passed >= 1:
        print("\n  VERDICT: PARTIAL IMPROVEMENT")
        print("  Some evidence that stability tensor adds value, but")
        print("  the effect is not universal.")
    else:
        print("\n  VERDICT: STABILITY TENSOR DOES NOT IMPROVE GEODESIC EMBEDDING")
        print("  Euclidean Φ-space is sufficient for the manifold.")

    print_sep()

    # Save
    all_results = {
        "section_a_metrics": sec_a,
        "section_b_optimal_lambda": sec_b,
        "section_c_combined_graph": sec_c,
        "section_d_intrinsic_dimension": sec_d,
        "section_e_bridge_detection": sec_e,
        "section_f_null_test": sec_f,
        "final_verdict": {
            "criteria": [{"name": n, "passed": p, "evidence": e} for n, p, e in criteria],
            "n_passed": n_passed,
            "n_total": len(criteria),
        }
    }
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)): return int(obj)
            if isinstance(obj, (np.floating,)): return float(obj)
            if isinstance(obj, (np.bool_,)): return bool(obj)
            if isinstance(obj, np.ndarray): return obj.tolist()
            return super().default(obj)

    with open(OUT / "t029_geodesic_embedding_results.json", "w") as f:
        json.dump(all_results, f, indent=2, cls=NpEncoder)

    print(f"T029 complete. Results saved to:")
    print(f"  {OUT / 't029_geodesic_embedding_results.json'}")
    print()

if __name__ == "__main__":
    main()
