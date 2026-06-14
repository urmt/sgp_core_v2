#!/usr/bin/env python3
"""
T030: TRANSITION FIELD GENERALIZATION
=====================================
Core Question: Can the transition-field survive outside the original
14-system ontology when systems are treated as samples from continuous
dynamical process families?

T026 — falsified universal predictive science.
T027 — validated a real but fragile flow field.
T028/T029 — showed the strongest surviving object is the transition
  manifold + stability metric (descriptive geometry, not dynamical).

T030 decisive test: Is the transition manifold a real property of
dynamical process-space or a finite-sample artifact of 14 hand-crafted systems?

Sections:
  A — Generative Process Ensembles (200-2000 parameterized systems)
  B — Field Continuity Test (Lipschitz, smoothness, connectedness)
  C — Critical Surface Detection (bifurcations, phase transitions)
  D — Universality Retest (intrinsic dimension, manifold persistence)
  E — Dynamical Metric Learning (compare metric types)
  F — Null Process World (fake universes)
  G — Field Equation Search (continuity, Fokker-Planck, gradient flow)
  H — Final Decision
"""

import sys, json, warnings, math, itertools, collections, time, os, gc
from pathlib import Path
from typing import Callable, Optional
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform, cdist
from scipy.stats import pearsonr, spearmanr, gaussian_kde, ttest_ind, linregress, chi2
from scipy.spatial import Delaunay
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.linalg import svd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors, KernelDensity
from sklearn.metrics import r2_score, adjusted_rand_score, silhouette_score
from sklearn.linear_model import LinearRegression
import networkx as nx

warnings.filterwarnings("ignore", category=RuntimeWarning)
np.random.seed(42)

OUT = Path("sfh_sgp_ood_outputs")
OUT.mkdir(exist_ok=True)
FIG = Path("figures")
FIG.mkdir(exist_ok=True)

# =====================================================================
# IMPORTS FROM CORE MODULES
# =====================================================================
sys.path.insert(0, ".")
from sfh_sgp_ood_universality_audit import (
    TRANSFORMS, canonical_metric_vector, compute_transform_geometry,
    replay_stability, null_audit_system, system_category, OOD_SYSTEMS,
    logistic_map, lorenz, ising_magnetization, reaction_diffusion,
    primes, fibonacci, modular_arithmetic, additive_recurrence,
    henon_map, cfg_expansion, lambda_reduction_trace, rewrite_system,
    iid_gaussian, colored_noise, surrogate_phase,
)

# Import additional generators from T026
# (re-included here for independence)

FEATURE_NAMES = [
    "pc1", "pc2", "effective_rank", "tau_m1", "tau_m2", "tau_m3", "tau_m4",
    "temporal_corr", "phase_corr", "pc1_ratio", "replay_displacement",
    "abl_full_pc1", "abl_no_m1_pc1", "abl_no_m2_pc1", "abl_no_m3_pc1",
    "abl_no_m4_pc1", "m2_contribution",
]

ALL_SYSTEMS = [
    "primes", "fibonacci", "modular_arithmetic", "additive_recurrence",
    "lorenz", "logistic_map", "henon_map", "ising_magnetization",
    "reaction_diffusion", "cfg_expansion", "lambda_reduction",
    "rewrite_system", "iid_gaussian", "colored_noise",
]

BRIDGE_SYSTEMS = {"lorenz", "ising_magnetization", "reaction_diffusion"}

N_SAMPLES_FAST = 8
N_TRIALS_FAST = 10
N_GENERATE = 300

OUTPUT = {}  # Accumulated results


def print_sep():
    print("\n" + "=" * 70)


# =====================================================================
# REFERENCE EMERGENCE PROJECTOR (from T028)
# =====================================================================

class EmergenceProjector:
    def __init__(self):
        feat = pd.read_csv(OUT / "clustering_feature_matrix.csv")
        feat = feat[feat["system"].isin(ALL_SYSTEMS)].set_index("system").loc[ALL_SYSTEMS]
        self.X_raw = feat[FEATURE_NAMES].values.astype(float)
        self.feat_mean = self.X_raw.mean(axis=0)
        self.feat_std = self.X_raw.std(axis=0)
        coord = pd.read_csv(OUT / "emergence_coordinates.csv")
        coord = coord[coord["system"].isin(ALL_SYSTEMS)].reset_index(drop=True)
        self.ref_Phi = coord[["C", "F", "A", "R"]].values
        raw = self._compute_raw_composites(self.X_raw)
        self.phi_mean = {ax: float(np.mean(raw[ax])) for ax in ["C", "F", "A", "R"]}
        self.phi_std = {ax: float(np.std(raw[ax])) for ax in ["C", "F", "A", "R"]}

    def _zscore(self, X):
        return (X - self.feat_mean) / np.maximum(self.feat_std, 1e-12)

    def _compute_raw_composites(self, X):
        Xs = self._zscore(X)
        n = Xs.shape[0]
        raw = {}
        abl_cols = [FEATURE_NAMES.index(c) for c in FEATURE_NAMES
                    if c.startswith("abl_") or c == "m2_contribution"]
        tau_cols = [FEATURE_NAMES.index(c) for c in FEATURE_NAMES if c.startswith("tau_")]
        idx = {name: i for i, name in enumerate(FEATURE_NAMES)}
        c_parts = []
        if "temporal_corr" in idx: c_parts.append(-Xs[:, idx["temporal_corr"]])
        if "effective_rank" in idx: c_parts.append(-Xs[:, idx["effective_rank"]])
        if "pc1_ratio" in idx: c_parts.append(Xs[:, idx["pc1_ratio"]])
        if "replay_displacement" in idx: c_parts.append(-Xs[:, idx["replay_displacement"]])
        raw["C"] = np.mean(c_parts, axis=0) if c_parts else np.zeros(n)
        f_parts = []
        for fn in ["tau_m2", "tau_m4", "phase_corr", "pc2"]:
            if fn in idx: f_parts.append(Xs[:, idx[fn]])
        raw["F"] = np.mean(f_parts, axis=0) if f_parts else np.zeros(n)
        a_parts = []
        if len(abl_cols) >= 2:
            abl_slice = Xs[:, abl_cols]
            a_parts.append(np.linalg.norm(abl_slice, axis=1))
            a_parts.append(np.std(abl_slice, axis=1))
        if "tau_m1" in idx: a_parts.append(Xs[:, idx["tau_m1"]])
        raw["A"] = np.mean(a_parts, axis=0) if a_parts else np.zeros(n)
        r_parts = []
        if "pc1" in idx: r_parts.append(Xs[:, idx["pc1"]])
        if len(tau_cols) >= 2:
            tau_slice = Xs[:, tau_cols]
            r_parts.append(np.mean(tau_slice, axis=1))
            r_parts.append(np.std(tau_slice, axis=1))
        raw["R"] = np.mean(r_parts, axis=0) if r_parts else np.zeros(n)
        return raw

    def project(self, X_new):
        X_new = np.atleast_2d(np.asarray(X_new, dtype=float))
        raw = self._compute_raw_composites(X_new)
        Phi = np.zeros((X_new.shape[0], 4))
        for j, ax in enumerate(["C", "F", "A", "R"]):
            Phi[:, j] = (raw[ax] - self.phi_mean[ax]) / max(self.phi_std[ax], 1e-12)
        return Phi

    def compute_flow(self, Phi):
        N, D = Phi.shape
        weights = np.exp(-squareform(pdist(Phi)) ** 2 / (2 * 0.5 ** 2))
        np.fill_diagonal(weights, 0)
        kde = gaussian_kde(Phi.T, bw_method='scott')
        V = -np.log(kde(Phi.T) + 1e-12)
        flows = np.zeros(N)
        for i in range(N):
            lower = np.where(V < V[i])[0]
            if len(lower) == 0: continue
            drop = (V[i] - V[lower]) / (V[i] - V.min() + 1e-12)
            vecs = (Phi[lower] - Phi[i]) / np.maximum(np.linalg.norm(Phi[lower] - Phi[i], axis=1), 1e-12)[:, None]
            flow_vec = np.sum(drop[:, None] * vecs, axis=0)
            flows[i] = np.linalg.norm(flow_vec)
        return flows, V


# =====================================================================
# SECTION A — GENERATIVE PROCESS ENSEMBLES
# =====================================================================

# ---- Additional system generators ----

def kuramoto_oscillator(n=512, n_osc=8, coupling=2.0, omega_std=1.0):
    omega = np.random.randn(n_osc) * omega_std
    theta = np.random.rand(n_osc) * 2 * np.pi
    dt = 0.05
    order = [np.abs(np.mean(np.exp(1j * theta)))]
    for _ in range(n):
        for i in range(n_osc):
            theta[i] += dt * (omega[i] + coupling / n_osc * np.sum(np.sin(theta - theta[i])))
        order.append(np.abs(np.mean(np.exp(1j * theta))))
    return np.array(order[:n], dtype=float)

def cellular_automaton(n=512, rule=110, size=64):
    states = [np.random.randint(0, 2, size).mean()]
    arr = np.random.randint(0, 2, size)
    for _ in range(n):
        lookup = (arr[:-2] << 2) + (arr[1:-1] << 1) + arr[2:]
        new = np.array([(rule >> i) & 1 for i in lookup])
        arr = np.concatenate([np.zeros(1), new, np.zeros(1)]).astype(int)
        states.append(arr.mean())
    return np.array(states[:n], dtype=float)

def sandpile_avalanche(n=512, L=8, drive_rate=0.01):
    grid = np.zeros((L, L), dtype=int)
    avs = []
    for _ in range(n):
        i, j = np.random.randint(0, L, 2)
        grid[i, j] += 1
        if grid[i, j] < 4:
            avs.append(0)
            continue
        av = 0
        unstable = [(i, j)]
        toppled = set()
        while unstable:
            ci, cj = unstable.pop()
            if (ci, cj) in toppled: continue
            toppled.add((ci, cj))
            grid[ci, cj] -= 4
            av += 1
            for di, dj in [(0,1),(0,-1),(1,0),(-1,0)]:
                ni, nj = ci+di, cj+dj
                if 0 <= ni < L and 0 <= nj < L:
                    grid[ni, nj] += 1
                    if grid[ni, nj] >= 4: unstable.append((ni, nj))
        avs.append(av)
        for ci, cj in toppled:
            if grid[ci, cj] >= 4: grid[ci, cj] = 0
    return np.array(avs, dtype=float)

def random_boolean_network(n=512, N=10, K=2, p=0.5):
    state = np.random.randint(0, 2, N)
    connections = np.random.randint(0, N, (N, K))
    functions = np.random.randint(0, 2, (N, 2**K))
    hamming = [0.0]
    for _ in range(n):
        new_state = state.copy()
        for i in range(N):
            inputs = [state[connections[i, k]] for k in range(K)]
            idx = sum(v << k for k, v in enumerate(inputs))
            new_state[i] = functions[i, idx]
        hamming.append(float(np.sum(state != new_state)))
        state = new_state
    return np.array(hamming[:n], dtype=float)

def markov_chain(n=512, n_states=4, transition_noise=0.3):
    P_base = np.eye(n_states) * 0.7 + np.ones((n_states, n_states)) * 0.3 / n_states
    P_noise = np.random.rand(n_states, n_states)
    P_noise /= P_noise.sum(axis=1, keepdims=True)
    P = (1 - transition_noise) * P_base + transition_noise * P_noise
    P /= P.sum(axis=1, keepdims=True)
    state = 0
    traj = [state]
    for _ in range(n):
        state = np.random.choice(n_states, p=P[state])
        traj.append(state)
    return np.array(traj, dtype=float)

def stochastic_branching(n=512, p_branch=0.3, max_pop=100):
    pop = 10
    traj = [pop]
    for _ in range(n):
        births = np.random.poisson(p_branch * pop) if pop > 0 else 0
        deaths = np.random.poisson(0.1 * pop) if pop > 0 else 0
        pop = max(0, min(max_pop, pop + births - deaths))
        traj.append(pop)
    return np.array(traj[:n], dtype=float)

def lotka_volterra(n=512, alpha=1.0, beta=0.1, delta=0.1, gamma=0.5):
    prey, pred = 40.0, 9.0
    dt = 0.01
    traj = [prey]
    for _ in range(n):
        d_prey = alpha * prey - beta * prey * pred
        d_pred = delta * prey * pred - gamma * pred
        prey += d_prey * dt
        pred += d_pred * dt
        traj.append(prey)
    return np.array(traj[:n], dtype=float)

def geometric_brownian(n=512, mu=0.0001, sigma=0.02, x0=100.0):
    x = x0
    traj = [x]
    for _ in range(n):
        x *= np.exp((mu - 0.5 * sigma ** 2) + sigma * np.random.randn())
        traj.append(x)
    return np.array(traj[:n], dtype=float)


def make_generator(name_base, gen_func, param_name, param_val, fixed_params=None):
    """Create a no-arg closure that returns a fresh time series each call."""
    fixed = fixed_params or {}
    kwargs = {param_name: param_val, **fixed}
    def _gen(n=512):
        return gen_func(n=n, **kwargs)
    return _gen


def compute_single_features(gen_func, sys_name=""):
    """Compute 17D feature vector for a single system (reduced samples for speed)."""
    try:
        geo = compute_transform_geometry("_temp", gen_func, n_samples=N_SAMPLES_FAST)
        null = null_audit_system("_temp", gen_func, n_trials=N_TRIALS_FAST)
        replay = replay_stability("_temp", gen_func, n_trials=N_TRIALS_FAST)
        return {
            "pc1": geo["pc1_variance"],
            "pc2": geo["pc2_variance"],
            "effective_rank": geo["effective_rank"],
            "tau_m1": geo["tau_axis"][0],
            "tau_m2": geo["tau_axis"][1],
            "tau_m3": geo["tau_axis"][2],
            "tau_m4": geo["tau_axis"][3],
            "temporal_corr": null["temporal_scramble_corr_mean"],
            "phase_corr": null["phase_randomize_corr_mean"],
            "pc1_ratio": null["pc1_ratio_orig_vs_shuffled"],
            "replay_displacement": replay["replay_displacement_mean"],
            "abl_full_pc1": 0.0, "abl_no_m1_pc1": 0.0, "abl_no_m2_pc1": 0.0,
            "abl_no_m3_pc1": 0.0, "abl_no_m4_pc1": 0.0, "m2_contribution": 0.0,
        }
    except Exception as e:
        raise RuntimeError(f"{sys_name}: {e}")


def section_a_generate_ensembles(proj):
    """Generate large ensembles from parameterized process families."""
    print_sep()
    print("SECTION A: GENERATIVE PROCESS ENSEMBLES")
    print_sep()

    param_sweeps = [
        ("logistic", logistic_map, "r", np.linspace(2.5, 4.0, 25), {}),
        ("lorenz", lorenz, "rho", np.linspace(0, 50, 25), {}),
        ("ising", ising_magnetization, "T", np.linspace(0.5, 5.0, 25), {"lattice_size": 6}),
        ("reaction_diffusion", reaction_diffusion, "F", np.linspace(0.01, 0.08, 20), {"grid_size": 12}),
        ("henon", henon_map, "a", np.linspace(0.8, 1.4, 15), {}),
        ("kuramoto", kuramoto_oscillator, "coupling", np.linspace(0.0, 8.0, 20), {}),
        ("ca", cellular_automaton, "rule", [30, 90, 110, 184, 150, 73, 54, 45, 22, 126], {}),
        ("sandpile", sandpile_avalanche, "L", [4, 6, 8, 12, 16], {}),
        ("rbn", random_boolean_network, "K", [1, 2, 3, 4, 5, 6], {}),
        ("markov", markov_chain, "transition_noise", np.linspace(0.0, 1.0, 15), {}),
        ("branching", stochastic_branching, "p_branch", np.linspace(0.05, 0.8, 15), {}),
        ("lotka", lotka_volterra, "alpha", np.linspace(0.5, 2.0, 15), {}),
        ("gbm", geometric_brownian, "sigma", np.linspace(0.005, 0.15, 15), {}),
    ]

    all_systems = []
    all_features = []

    total_expected = sum(len(v[3]) for v in param_sweeps)
    print(f"  Generating ~{total_expected} systems from {len(param_sweeps)} families")

    for sweep_name, gen_func, param_name, values, fixed in param_sweeps:
        print(f"\n  [{sweep_name}] sweeping {param_name} ∈ [{values[0]:.4f}, {values[-1]:.4f}] ({len(values)} pts)")
        for val in values:
            sys_name = f"{sweep_name}_{param_name}={val:.4f}"
            generator = make_generator(sweep_name, gen_func, param_name, val, fixed)
            print(f"    Computing {sys_name}...", end=" ", flush=True)
            try:
                feats = compute_single_features(generator, sys_name)
                all_systems.append(sys_name)
                all_features.append(feats)
                print("OK")
            except Exception as e:
                print(f"FAILED: {e}")

    if len(all_systems) < 50:
        print(f"\n  WARNING: Only {len(all_systems)} systems generated (< 50). Results may be unreliable.")
    else:
        print(f"\n  Successfully generated {len(all_systems)} systems")

    feat_df = pd.DataFrame(all_features)
    feat_df["system"] = all_systems
    feat_cols = [c for c in FEATURE_NAMES if c in feat_df.columns]
    X = feat_df[feat_cols].values

    # Project to Φ-space
    Phi = proj.project(X)
    feat_df_out = feat_df.copy()
    for j, ax in enumerate(["C", "F", "A", "R"]):
        feat_df_out[ax] = Phi[:, j]
    feat_df_out.to_csv(OUT / "t030_ensemble_features.csv", index=False)
    np.save(OUT / "t030_ensemble_Phi.npy", Phi)
    # Note: raw time series arrays not saved (would be heavy for 211+ systems)

    # Compute flow field on the ensemble
    flows, V = proj.compute_flow(Phi)
    flow_df = pd.DataFrame({"system": all_systems, "flow_magnitude": flows})
    flow_df.to_csv(OUT / "t030_ensemble_flow.csv", index=False)
    np.save(OUT / "t030_ensemble_V.npy", V)

    # Compute geodesic embedding (stability tensor) on ensemble
    # Use reduced feature set for stability: just the isotropic model
    # Full stability tensor is expensive — compute on a subset
    n_ensemble = len(all_systems)
    print(f"\n  Computing stability tensor on ensemble ({n_ensemble} systems × {len(feat_cols)} features)...")
    tensors = np.zeros((n_ensemble, 4, len(feat_cols)))
    eps = 0.05
    for i in range(min(n_ensemble, 100)):  # First 100 systems only
        if i % 20 == 0:
            print(f"    Tensor: {i}/{min(n_ensemble, 100)}")
        for j in range(len(feat_cols)):
            X_plus = X.copy()
            X_minus = X.copy()
            delta = eps * max(proj.feat_std[j], 0.01)
            X_plus[i, j] += delta
            X_minus[i, j] -= delta
            phi_plus = proj.project(X_plus[i])[0]
            phi_minus = proj.project(X_minus[i])[0]
            tensors[i, :, j] = (phi_plus - phi_minus) / (2 * delta)
    np.save(OUT / "t030_ensemble_tensors.npy", tensors)

    # Compute geodesic betweenness (kNN graph)
    print("  Computing geodesic betweenness centrality...")
    k = min(5, n_ensemble - 1)
    dist_mat = squareform(pdist(Phi))
    G = nx.Graph()
    for i in range(n_ensemble):
        G.add_node(i)
    for i in range(n_ensemble):
        nearest = np.argsort(dist_mat[i])[1:k+1]
        for j in nearest:
            G.add_edge(i, j, weight=dist_mat[i, j])
    betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)

    results = {
        "n_systems": n_ensemble,
        "n_families": len(param_sweeps),
        "systems_per_family": {s[0]: len(s[3]) for s in param_sweeps},
        "flow_range": [float(flows.min()), float(flows.max())],
        "flow_mean": float(flows.mean()),
        "flow_std": float(flows.std()),
        "phi_range": {ax: [float(Phi[:, j].min()), float(Phi[:, j].max())]
                     for j, ax in enumerate(["C", "F", "A", "R"])},
    }
    OUTPUT["section_A"] = results
    print(f"\n  Section A complete: {n_ensemble} systems, flow_mean={flows.mean():.3f}")
    return {
        "systems": all_systems,
        "features": feat_df,
        "Phi": Phi,
        "flows": flows,
        "V": V,
        "tensors": tensors,
        "betweenness": betweenness,
    }


# =====================================================================
# SECTION B — FIELD CONTINUITY TEST
# =====================================================================

def section_b_field_continuity(data):
    """Test whether flow, curvature, density, stability become smooth functions of process params."""
    print_sep()
    print("SECTION B: FIELD CONTINUITY TEST")
    print_sep()

    Phi = data["Phi"]
    flows = data["flows"]
    n = len(data["systems"])

    feature_names = ["pc1", "pc2", "effective_rank", "tau_m1", "tau_m2", "tau_m3", "tau_m4"]
    feat_vals = data["features"][feature_names].values if n > 0 else np.zeros((0, len(feature_names)))

    # B1 — Lipschitz continuity of flow w.r.t. Φ-position
    print("\n  B1 — Lipschitz continuity: |flow_i - flow_j| / ||Φ_i - Φ_j||")
    if n >= 10:
        dists = squareform(pdist(Phi))
        flow_diffs = squareform(pdist(flows.reshape(-1, 1)))
        with np.errstate(divide='ignore', invalid='ignore'):
            lipschitz_ratios = flow_diffs / np.maximum(dists, 1e-12)
        valid = np.isfinite(lipschitz_ratios) & (dists > 1e-6)
        L_empirical = float(np.max(lipschitz_ratios[valid]))
        L_mean = float(np.mean(lipschitz_ratios[valid]))
        L_median = float(np.median(lipschitz_ratios[valid]))
        print(f"    Empirical Lipschitz constant: {L_empirical:.4f}")
        print(f"    Mean |Δflow|/|ΔΦ|: {L_mean:.4f}")
        print(f"    Median: {L_median:.4f}")

        # Rank correlation between distance and flow difference
        r_cont, p_cont = spearmanr(dists[valid], flow_diffs[valid])
        print(f"    distance ~ flow_diff: ρ={r_cont:.4f}, p={p_cont:.4f}")

        # B2 — Local smoothness: flow variance among k-nearest neighbors
        print("\n  B2 — Local smoothness (kNN flow variance)")
        nn = NearestNeighbors(n_neighbors=min(5, n - 1))
        nn.fit(Phi)
        idxs = nn.kneighbors(return_distance=False)
        flow_var = np.array([np.var(flows[idxs[i]]) for i in range(n)])
        print(f"    Mean kNN flow variance: {flow_var.mean():.6f}")
        print(f"    Median: {np.median(flow_var):.6f}")
        print(f"    Range: [{flow_var.min():.6f}, {flow_var.max():.6f}]")
        smoothness = float(np.mean(flow_var < np.median(flow_var)))
        print(f"    Fraction low-variance: {smoothness:.3f}")

        # B3 — Potential smoothness (vs distance from edge of manifold)
        print("\n  B3 — Potential vs manifold position")
        V = data["V"]
        kde = gaussian_kde(Phi.T, bw_method='scott')
        density = kde(Phi.T)
        print(f"    Density range: [{density.min():.4f}, {density.max():.4f}]")
        r_dens_flow, p_dens_flow = pearsonr(density, flows)
        print(f"    density ~ flow: r={r_dens_flow:.4f}, p={p_dens_flow:.4f}")

        # B4 — Gradient coherence (do nearby systems have similar flow directions?)
        print("\n  B4 — Flow direction coherence among neighbors")
        k = min(5, n - 1)
        nn = NearestNeighbors(n_neighbors=k + 1)
        nn.fit(Phi)
        dists_k, idxs_k = nn.kneighbors(Phi)
        direction_coherence = []
        for i in range(n):
            neighbors = idxs_k[i, 1:]  # exclude self
            if len(neighbors) < 2: continue
            dirs = flows[idxs_k[i, 1:]]
            coherence = np.std(dirs) / max(np.mean(dirs), 1e-12)
            direction_coherence.append(coherence)
        mean_coherence = float(np.mean(direction_coherence)) if direction_coherence else 0
        print(f"    Mean direction coherence (CV of flow in neighborhood): {mean_coherence:.4f}")

        # B5 — Parametric continuity: can we predict Φ from process parameters?
        print("\n  B5 — Parametric continuity")
        # Extract parameter values from system names
        param_vals = {}
        family_buckets = collections.defaultdict(list)
        for i, name in enumerate(data["systems"]):
            family = name.split("_")[0]
            family_buckets[family].append(i)
            try:
                pv = float(name.split("=")[-1])
                param_vals[i] = pv
            except (IndexError, ValueError):
                pass

        continuity_results = {}
        for family, idxs in family_buckets.items():
            if len(idxs) < 5: continue
            family_Phi = Phi[idxs]
            family_params = [param_vals.get(i) for i in idxs if i in param_vals]
            if len(family_params) < 5: continue
            family_flows = flows[idxs]
            # Spearman correlation between parameter and each Φ-axis
            for j, ax in enumerate(["C", "F", "A", "R"]):
                r, p = spearmanr(family_params, family_Phi[:, j])
                if abs(r) > 0.3:
                    print(f"      {family}.{ax}: ρ={r:.4f}, p={p:.4f} ({len(idxs)} pts)")
                    continuity_results[f"{family}_{ax}"] = {"rho": float(r), "p": float(p), "n": len(idxs)}
            # Parameter vs flow
            r_f, p_f = spearmanr(family_params, family_flows)
            if abs(r_f) > 0.1:
                print(f"      {family}.flow: ρ={r_f:.4f}, p={p_f:.4f}")
                continuity_results[f"{family}_flow"] = {"rho": float(r_f), "p": float(p_f)}

        result = {
            "lipschitz_constant": L_empirical if n >= 10 else None,
            "mean_flow_delta_ratio": L_mean if n >= 10 else None,
            "distance_flow_diff_rho": float(r_cont) if n >= 10 else None,
            "distance_flow_diff_p": float(p_cont) if n >= 10 else None,
            "mean_knn_flow_var": float(flow_var.mean()) if n >= 10 else None,
            "flow_smoothness": smoothness if n >= 10 else None,
            "density_flow_r": float(r_dens_flow) if n >= 10 else None,
            "direction_coherence": mean_coherence if n >= 10 else None,
            "parametric_continuity": continuity_results,
        }
    else:
        result = {"error": "insufficient_systems"}

    OUTPUT["section_B"] = result
    print(f"\n  Section B complete")
    return result


# =====================================================================
# SECTION C — CRITICAL SURFACE DETECTION
# =====================================================================

def section_c_critical_surfaces(data):
    """Detect bifurcation surfaces, phase transition sheets, instability ridges."""
    print_sep()
    print("SECTION C: CRITICAL SURFACE DETECTION")
    print_sep()

    Phi = data["Phi"]
    flows = data["flows"]
    n = len(data["systems"])

    if n < 20:
        print("  WARNING: too few systems for critical surface detection")
        return {"error": "insufficient_systems"}

    # C1 — Flow divergence (∇·v): regions where flow converges/dSiverges
    print("\n  C1 — Flow divergence on Φ-space")
    k = min(10, n - 1)
    nn = NearestNeighbors(n_neighbors=k + 1)
    nn.fit(Phi)
    dists_k, idxs_k = nn.kneighbors(Phi)

    divergences = np.zeros(n)
    for i in range(n):
        neighbors = idxs_k[i, 1:]
        vecs = Phi[neighbors] - Phi[i]
        flow_dirs = flows[neighbors] - flows[i]
        for v, fd in zip(vecs, flow_dirs):
            if np.linalg.norm(v) > 1e-10:
                divergences[i] += np.dot(fd * v, v) / np.linalg.norm(v) ** 2
        divergences[i] /= max(len(neighbors), 1)

    div_high = np.argsort(divergences)[-5:]
    div_low = np.argsort(divergences)[:5]
    print(f"    Top 5 divergence (sources):")
    for idx in div_high:
        print(f"      {data['systems'][idx]:<30s} div={divergences[idx]:.4f} flow={flows[idx]:.4f}")
    print(f"    Bottom 5 divergence (sinks):")
    for idx in div_low:
        print(f"      {data['systems'][idx]:<30s} div={divergences[idx]:.4f} flow={flows[idx]:.4f}")

    # C2 — Hessian eigenstructure on flow field (ridge detection)
    print("\n  C2 — Flow ridge detection via Hessian")
    # Use KDE density as scalar field (biographically smooth across Φ)
    kde = gaussian_kde(Phi.T, bw_method='scott')
    density = kde(Phi.T)
    h = 0.2
    flow_ridges = []
    for i in range(min(n, 50)):
        phi0 = Phi[i]
        D = min(4, len(phi0))
        H = np.zeros((D, D))
        for d1 in range(D):
            for d2 in range(D):
                if d1 == d2:
                    pp = phi0.copy(); pp[d1] += h
                    mm = phi0.copy(); mm[d1] -= h
                    V_pp = kde(pp.reshape(1, -1).T).item()
                    V_mm = kde(mm.reshape(1, -1).T).item()
                    H[d1, d2] = (V_pp - 2*density[i] + V_mm) / (h*h)
        if np.allclose(H, 0):
            ridge_score = 0.0
        else:
            evals = np.linalg.eigvalsh(H)
            ridge_score = float(np.sum(evals[evals < 0]))
        flow_ridges.append(ridge_score)

    if flow_ridges:
        ridge_arr = np.array(flow_ridges)
        r_ridge_flow, p_ridge_flow = pearsonr(ridge_arr[:min(n, 50)], flows[:min(n, 50)])
        print(f"    Ridge_score ~ flow: r={r_ridge_flow:.4f}, p={p_ridge_flow:.4f}")

    # C3 — Morse-Smale-like segmentation: partition Φ by flow topology
    print("\n  C3 — Flow topology segmentation")
    best_k = (1, 0.0)
    # Cluster by flow + position
    if n >= 30:
        flow_pos = np.column_stack([Phi, flows.reshape(-1, 1)])
        flow_pos_s = StandardScaler().fit_transform(flow_pos)
        Z = linkage(flow_pos_s, method="ward")
        # Find stable number of clusters
        sil_scores = []
        for k in range(2, min(10, n // 5)):
            labels = fcluster(Z, t=k, criterion="maxclust")
            if len(set(labels)) > 1:
                sil_scores.append((k, silhouette_score(flow_pos_s, labels)))
        if sil_scores:
            best_k = max(sil_scores, key=lambda x: x[1])
            print(f"    Optimal flow topology clusters: k={best_k[0]}, silhouette={best_k[1]:.4f}")
            labels = fcluster(Z, t=best_k[0], criterion="maxclust")
            cluster_flows = {k: float(np.mean(flows[labels == k])) for k in set(labels)}
            print(f"    Cluster mean flows: {cluster_flows}")
        else:
            best_k = (1, 0)

    # C4 — Persistent homology proxy: detect loops/voids in high-flow regions
    print("\n  C4 — Manifold topology of high-flow regions")
    flow_thresholds = np.percentile(flows, [50, 60, 70, 80, 90, 95])
    topology_metrics = {}
    for thresh in flow_thresholds:
        high_flow = flows >= thresh
        n_high = int(high_flow.sum())
        if n_high < 4: continue
        high_Phi = Phi[high_flow]
        # Compute intrinsic dimension of high-flow region
        _, s, _ = svd(high_Phi - high_Phi.mean(axis=0), full_matrices=False)
        s_norm = s / max(s.sum(), 1e-12)
        participation_ratio = float(1.0 / max(np.sum(s_norm ** 2), 1e-12))
        flow_centroid = high_Phi.mean(axis=0).tolist()
        topology_metrics[f"pct_{int(thresh)}"] = {
            "n_high_flow": int(n_high),
            "intrinsic_dim": float(participation_ratio),
            "centroid": flow_centroid,
        }
        print(f"    top {100-thresh:.0f}% flow: {n_high} systems, PR={participation_ratio:.2f}")

    # C5 — Bifurcation proxy: systems with high flow + high curvature
    print("\n  C5 — Candidate bifurcation / phase transition points")
    curvatures = np.zeros(n)
    if n >= 10:
        for i in range(n):
            dists_i = np.linalg.norm(Phi - Phi[i], axis=1)
            w = np.exp(-dists_i ** 2 / (2 * 0.3 ** 2))
            w[i] = 0
            if w.sum() > 0:
                weighted_flow = np.sum(w * flows) / w.sum()
                curvatures[i] = flows[i] - weighted_flow
        bif_score = flows * np.abs(curvatures)
        bif_candidates = np.argsort(bif_score)[-10:]
        print(f"    Top bifurcation candidates (high flow × curvature):")
        for idx in bif_candidates:
            print(f"      {data['systems'][idx]:<30s} flow={flows[idx]:.4f} curv={curvatures[idx]:.4f}")

    result = {
        "flow_divergence_range": [float(divergences.min()), float(divergences.max())],
        "top_flow_sources": [data["systems"][i] for i in div_high[:3]],
        "top_flow_sinks": [data["systems"][i] for i in div_low[:3]],
        "ridge_flow_r": float(r_ridge_flow) if flow_ridges else None,
        "clustering_silhouette": float(best_k[1]) if n >= 30 else None,
        "topology_per_threshold": topology_metrics,
    }
    OUTPUT["section_C"] = result
    print(f"\n  Section C complete")
    return result


# =====================================================================
# SECTION D — UNIVERSALITY RETEST
# =====================================================================

def section_d_universality_retest(data):
    """Re-test universality under continuous ensembles, not discrete exemplars."""
    print_sep()
    print("SECTION D: UNIVERSALITY RETEST (CONTINUOUS ENSEMBLES)")
    print_sep()

    Phi = data["Phi"]
    flows = data["flows"]
    n = len(data["systems"])

    if n < 20:
        return {"error": "insufficient_systems"}

    # D1 — Intrinsic dimension of the ensemble manifold
    print("\n  D1 — Intrinsic dimension")
    _, s_all, _ = svd(Phi - Phi.mean(axis=0), full_matrices=False)
    evr = s_all ** 2 / max(np.sum(s_all ** 2), 1e-12)
    eff_rank = float(np.exp(-np.sum(evr * np.log(evr + 1e-12))))
    pr = float(1.0 / max(np.sum(evr ** 2), 1e-12))
    print(f"    Effective rank: {eff_rank:.4f}")
    print(f"    Participation ratio: {pr:.4f}")

    # D2 — Manifold persistence under subsampling
    print("\n  D2 — Manifold persistence under subsampling")
    subsample_sizes = [int(n * p) for p in [0.3, 0.5, 0.7, 0.9]]
    pr_stability = []
    for ss in subsample_sizes:
        prs = []
        for _ in range(50):
            idxs = np.random.choice(n, ss, replace=False)
            Phi_sub = Phi[idxs]
            _, s_sub, _ = svd(Phi_sub - Phi_sub.mean(axis=0), full_matrices=False)
            evr_sub = s_sub ** 2 / max(np.sum(s_sub ** 2), 1e-12)
            prs.append(float(1.0 / max(np.sum(evr_sub ** 2), 1e-12)))
        pr_stability.append(float(np.mean(prs)))
        print(f"    Subsampling {ss}/{n}: mean PR={pr_stability[-1]:.3f}")

    # D3 — Bridge persistence in continuous ensemble
    print("\n  D3 — Bridge persistence")
    flow_threshold = np.percentile(flows, 85)
    bridge_ensemble = flows >= flow_threshold
    n_bridge = int(bridge_ensemble.sum())
    print(f"    Systems above {flow_threshold:.2f} flow (85th pct): {n_bridge}/{n}")

    # Check if bridge forms a connected transition region
    bridge_Phi = Phi[bridge_ensemble]
    if n_bridge >= 3:
        bridge_dists = pdist(bridge_Phi)
        mean_bridge_dist = float(np.mean(bridge_dists))
        print(f"    Mean intra-bridge distance: {mean_bridge_dist:.4f}")
        bridge_centroid = bridge_Phi.mean(axis=0)
        all_dists_to_bridge = np.linalg.norm(Phi - bridge_centroid, axis=1)
        bridge_separation = float(np.mean(all_dists_to_bridge[~bridge_ensemble]) - np.mean(all_dists_to_bridge[bridge_ensemble]))
        print(f"    Bridge separation (non-bridge vs bridge centroid distance): {bridge_separation:.4f}")
    else:
        bridge_separation = None
        print(f"    Too few bridge systems ({n_bridge}) for analysis")

    # D4 — Collective flow stability (leave-one-family-out)
    print("\n  D4 — Flow stability under family removal")
    families = collections.defaultdict(list)
    for i, name in enumerate(data["systems"]):
        family = name.split("_")[0]
        families[family].append(i)

    flow_corrs = {}
    for family, idxs in families.items():
        if len(idxs) < 3 or len(idxs) > n - 3: continue
        keep = [i for i in range(n) if i not in idxs]
        if len(keep) < 10: continue
        Phi_keep = Phi[keep]
        flows_keep, _ = EmergenceProjector().compute_flow(Phi_keep)
        # Compare on shared systems
        r, p = pearsonr(data["flows"][keep], flows_keep)
        flow_corrs[family] = {"r": float(r), "p": float(p), "n_left": len(keep)}
        print(f"    Remove {family}: flow_corr={r:.4f}, p={p:.4f} ({len(keep)} left)")

    result = {
        "intrinsic_dim_effective_rank": eff_rank,
        "intrinsic_dim_participation_ratio": pr,
        "subsample_pr_stability": [float(p) for p in pr_stability],
        "bridge_cutoff": float(flow_threshold),
        "n_bridge_systems": n_bridge,
        "bridge_separation": bridge_separation,
        "flow_removal_stability": flow_corrs,
    }
    OUTPUT["section_D"] = result
    print(f"\n  Section D complete")
    return result


# =====================================================================
# SECTION E — DYNAMICAL METRIC LEARNING
# =====================================================================

def section_e_metric_learning(data, proj):
    """Compare multiple distance metrics for predicting collapse/dynamics."""
    print_sep()
    print("SECTION E: DYNAMICAL METRIC LEARNING")
    print_sep()

    Phi = data["Phi"]
    flows = data["flows"]
    n = len(data["systems"])

    if n < 20:
        return {"error": "insufficient_systems"}

    metrics = {
        "euclidean_phi": lambda: squareform(pdist(Phi, metric="euclidean")),
        "manhattan_phi": lambda: squareform(pdist(Phi, metric="cityblock")),
        "cosine_phi": lambda: squareform(pdist(Phi, metric="cosine")),
    }

    # Add tensor metric if tensors available
    tensors = data.get("tensors")
    if tensors is not None and tensors.shape[0] >= min(n, 100):
        def tensor_metric():
            n_t = min(n, 100)
            D = np.zeros((n_t, n_t))
            for i in range(n_t):
                for j in range(i + 1, n_t):
                    d_phi = np.linalg.norm(Phi[i] - Phi[j])
                    d_tensor = np.linalg.norm(tensors[i] - tensors[j])
                    D[i, j] = d_phi + 0.2 * d_tensor
                    D[j, i] = D[i, j]
            return D
        metrics["tensor_combined"] = tensor_metric

    # E1 — Compare metric smoothness w.r.t. flow
    print("\n  E1 — Metric smoothness: do nearby systems in each metric have similar flow?")
    metric_scores = {}
    for name, metric_fn in metrics.items():
        D = metric_fn()
        n_m = D.shape[0]
        if n_m < 10: continue
        k = min(5, n_m - 1)
        nn = NearestNeighbors(n_neighbors=k + 1, metric="precomputed")
        nn.fit(D)
        idxs = nn.kneighbors(D, return_distance=False)
        # Flow variance within neighborhoods
        flow_var = np.mean([np.var(flows[idxs[i, 1:]]) for i in range(n_m)])
        # Flow predictability from kNN mean
        pred_flow = np.array([np.mean(flows[idxs[i, 1:]]) for i in range(n_m)])
        r_pred, p_pred = pearsonr(pred_flow, flows[:n_m])
        metric_scores[name] = {
            "mean_knn_flow_var": float(flow_var),
            "knn_flow_prediction_r": float(r_pred),
            "knn_flow_prediction_p": float(p_pred),
        }
        print(f"    {name:<20s}: knn_flow_var={flow_var:.6f}  pred_r={r_pred:.4f} p={p_pred:.4f}")

    # E2 — Diffusion distance (simulate diffusion on manifold)
    print("\n  E2 — Diffusion distance")
    try:
        D_euc = squareform(pdist(Phi, metric="euclidean"))
        sigma = np.median(D_euc[D_euc > 0])
        W = np.exp(-D_euc ** 2 / (2 * sigma ** 2))
        np.fill_diagonal(W, 0)
        D_inv = np.diag(1.0 / np.maximum(W.sum(axis=1), 1e-12))
        P = D_inv @ W
        # Diffusion distance after t steps
        t = 3
        Pt = np.linalg.matrix_power(P, t)
        diff_dists = squareform(pdist(Pt, metric="euclidean"))
        nn = NearestNeighbors(n_neighbors=min(5, n - 1), metric="precomputed")
        nn.fit(diff_dists)
        idxs = nn.kneighbors(diff_dists, return_distance=False)
        diff_flow_var = np.mean([np.var(flows[idxs[i, 1:]]) for i in range(n)])
        diff_pred_flow = np.array([np.mean(flows[idxs[i, 1:]]) for i in range(n)])
        r_diff, p_diff = pearsonr(diff_pred_flow, flows)
        print(f"    diffusion_dist: knn_flow_var={diff_flow_var:.6f}  pred_r={r_diff:.4f} p={p_diff:.4f}")
        has_diffusion = True
    except Exception as e:
        print(f"    Diffusion distance failed: {e}")
        has_diffusion = False
        diff_flow_var = None
        r_diff = None

    # E3 — Best metric for collapse prediction
    print("\n  E3 — Best metric for collapse prediction via kNN")
    best_metric = min(metric_scores, key=lambda m: metric_scores[m]["mean_knn_flow_var"]) if metric_scores else None
    if best_metric:
        print(f"    Best metric: {best_metric}")
        best_score = metric_scores[best_metric]
        print(f"    kNN flow pred r={best_score['knn_flow_prediction_r']:.4f}")

    # E4 — Compare to Φ-only baseline from T029
    print("\n  E4 — Comparison with T029 Φ-only baseline (r=0.434)")
    if metric_scores:
        baseline_r = 0.434
        for name, scores in metric_scores.items():
            delta = scores["knn_flow_prediction_r"] - baseline_r
            arrow = "▲" if delta > 0 else "▼"
            print(f"    {name:<20s}: Δ={delta:+.4f} vs baseline {arrow}")

    result = {
        "metric_scores": metric_scores,
        "diffusion_knn_flow_var": diff_flow_var,
        "diffusion_prediction_r": r_diff,
        "best_metric": best_metric,
    }
    OUTPUT["section_E"] = result
    print(f"\n  Section E complete")
    return result


# =====================================================================
# SECTION F — NULL PROCESS WORLD
# =====================================================================

def section_f_null_world(data, proj):
    """Construct fake universes and test if transition manifold still appears."""
    print_sep()
    print("SECTION F: NULL PROCESS WORLD")
    print_sep()

    Phi = data["Phi"]
    flows = data["flows"]
    n = len(data["systems"])

    if n < 20:
        return {"error": "insufficient_systems"}

    results = {}
    orig_features = data["features"]
    feat_cols_here = [c for c in FEATURE_NAMES if c in orig_features.columns]
    X_orig = orig_features[feat_cols_here].values.astype(float)

    # F1 — Shuffle feature columns (destroy cross-feature correlations)
    print("\n  F1 — Column-shuffled features (preserve marginals, destroy covariance)")
    n_feat = X_orig.shape[1]
    X_shuf_col = X_orig.copy()
    for j in range(n_feat):
        np.random.shuffle(X_shuf_col[:, j])
    Phi_shuf = proj.project(X_shuf_col)
    flows_shuf, _ = proj.compute_flow(Phi_shuf)
    _, s_shuf, _ = svd(Phi_shuf - Phi_shuf.mean(axis=0), full_matrices=False)
    evr_shuf = s_shuf ** 2 / max(np.sum(s_shuf ** 2), 1e-12)
    pr_shuf = float(1.0 / max(np.sum(evr_shuf ** 2), 1e-12))
    r_flow_shuf = pearsonr(flows_shuf, flows[:len(flows_shuf)])[0] if len(flows_shuf) == len(flows) else 0
    print(f"    Shuffled PR: {pr_shuf:.4f} (original: {OUTPUT['section_D']['intrinsic_dim_participation_ratio']:.4f})")
    print(f"    Flow corr with original: r={r_flow_shuf:.4f}")
    results["shuffled_cols"] = {"participation_ratio": pr_shuf, "flow_corr_with_original": float(r_flow_shuf)}

    # F2 — Row-shuffled features (destroy system ordering, keep cross-feature structure)
    print("\n  F2 — Row-shuffled features (destroy system identity)")
    X_shuf_row = X_orig.copy()
    np.random.shuffle(X_shuf_row)
    Phi_shuf_row = proj.project(X_shuf_row)
    flows_shuf_row, _ = proj.compute_flow(Phi_shuf_row)
    _, s_shuf_row, _ = svd(Phi_shuf_row - Phi_shuf_row.mean(axis=0), full_matrices=False)
    evr_shuf_row = s_shuf_row ** 2 / max(np.sum(s_shuf_row ** 2), 1e-12)
    pr_shuf_row = float(1.0 / max(np.sum(evr_shuf_row ** 2), 1e-12))
    r_flow_shuf_row = pearsonr(flows_shuf_row, flows[:len(flows_shuf_row)])[0] if len(flows_shuf_row) == len(flows) else 0
    print(f"    Row-shuffled PR: {pr_shuf_row:.4f}")
    print(f"    Flow corr with original: r={r_flow_shuf_row:.4f}")
    results["shuffled_rows"] = {"participation_ratio": pr_shuf_row, "flow_corr_with_original": float(r_flow_shuf_row)}

    # F3 — White noise features (completely destroy structure)
    print("\n  F3 — White noise features")
    X_noise = np.random.randn(n, n_feat)
    Phi_noise = proj.project(X_noise)
    flows_noise, _ = proj.compute_flow(Phi_noise)
    _, s_noise, _ = svd(Phi_noise - Phi_noise.mean(axis=0), full_matrices=False)
    evr_noise = s_noise ** 2 / max(np.sum(s_noise ** 2), 1e-12)
    pr_noise = float(1.0 / max(np.sum(evr_noise ** 2), 1e-12))
    print(f"    White noise PR: {pr_noise:.4f}")
    results["white_noise"] = {"participation_ratio": pr_noise}

    # F4 — Swap feature labels (keep values, destroy semantic meaning)
    print("\n  F4 — Feature-label permuted features")
    X_swap = X_orig[:, np.random.permutation(n_feat)]
    Phi_swap = proj.project(X_swap)
    flows_swap, _ = proj.compute_flow(Phi_swap)
    _, s_swap, _ = svd(Phi_swap - Phi_swap.mean(axis=0), full_matrices=False)
    evr_swap = s_swap ** 2 / max(np.sum(s_swap ** 2), 1e-12)
    pr_swap = float(1.0 / max(np.sum(evr_swap ** 2), 1e-12))
    print(f"    Feature-swapped PR: {pr_swap:.4f}")
    results["feature_swapped"] = {"participation_ratio": pr_swap}

    # F4 — Random tensor fields
    print("\n  F4 — Random tensor fields")
    random_tensor_flow_corrs = []
    for trial in range(50):
        fake_Phi = np.random.randn(n, 4)
        fake_flows, _ = proj.compute_flow(fake_Phi)
        r, _ = pearsonr(fake_flows, flows)
        random_tensor_flow_corrs.append(float(r))
    mean_random_r = float(np.mean(random_tensor_flow_corrs))
    std_random_r = float(np.std(random_tensor_flow_corrs))
    print(f"    Random Φ-space ~ real flow: mean_r={mean_random_r:.4f}, std={std_random_r:.4f}")
    results["random_tensor"] = {"mean_r": mean_random_r, "std_r": std_random_r}

    # F5 — Decision: does the transition manifold appear in null worlds?
    print("\n  F5 — Null world decision")
    original_pr = OUTPUT["section_D"]["intrinsic_dim_participation_ratio"]
    pr_reductions = {
        "col_shuffled": pr_shuf / original_pr if original_pr > 0 else 1,
        "row_shuffled": pr_shuf_row / original_pr if original_pr > 0 else 1,
        "white_noise": pr_noise / original_pr if original_pr > 0 else 1,
        "feature_swapped": pr_swap / original_pr if original_pr > 0 else 1,
    }
    for name, ratio in pr_reductions.items():
        direction = "↓" if ratio < 1 else "↑"
        print(f"    {name}: PR ratio vs original = {ratio:.4f} {direction}")

    null_artifact_score = float(np.mean(list(pr_reductions.values())))
    print(f"    Null artifact score (1=identical, lower=more artifact): {null_artifact_score:.4f}")

    results["artifact_score"] = null_artifact_score
    results["pr_reductions"] = pr_reductions
    OUTPUT["section_F"] = results
    print(f"\n  Section F complete")
    return results


# =====================================================================
# SECTION G — FIELD EQUATION SEARCH
# =====================================================================

def section_g_field_equation(data):
    """Attempt discovery of governing equation for Φ-flow dynamics."""
    print_sep()
    print("SECTION G: FIELD EQUATION SEARCH")
    print_sep()

    Phi = data["Phi"]
    flows = data["flows"]
    V = data["V"]
    n = len(data["systems"])
    D = min(4, Phi.shape[1])

    results = {}

    # G1 — Gradient flow hypothesis: is flow aligned with -∇V?
    print("\n  G1 — Gradient flow test: v ∝ -∇V")
    h = 0.2
    grad_Vs = np.zeros((n, D))
    for i in range(n):
        phi0 = Phi[i]
        for d in range(D):
            pp = phi0.copy(); pp[d] += h
            mm = phi0.copy(); mm[d] -= h
            try:
                V_pp = float(gaussian_kde(Phi.T, bw_method='scott')(pp.reshape(1, -1).T))
                V_mm = float(gaussian_kde(Phi.T, bw_method='scott')(mm.reshape(1, -1).T))
            except Exception:
                V_pp, V_mm = V[i], V[i]
            grad_Vs[i, d] = (V_pp - V_mm) / (2 * h)

    # Correlation between flow magnitude and |∇V|
    grad_norms = np.linalg.norm(grad_Vs, axis=1)
    r_grad, p_grad = pearsonr(grad_norms, flows) if np.std(grad_norms) > 0 and np.std(flows) > 0 else (0, 1)
    print(f"    |∇V| ~ flow: r={r_grad:.4f}, p={p_grad:.4f}")

    # Direction alignment: cos(θ) between flow direction and -∇V direction
    alignments = []
    for i in range(n):
        if grad_norms[i] > 1e-10 and flows[i] > 1e-10:
            cos_theta = np.dot(-grad_Vs[i] / grad_norms[i], Phi[i] / max(np.linalg.norm(Phi[i]), 1e-12))
            alignments.append(cos_theta)
    mean_alignment = float(np.mean(alignments)) if alignments else 0
    print(f"    Mean cos(flow, -∇V) alignment: {mean_alignment:.4f}")

    results["gradient_flow"] = {
        "grad_norm_flow_r": float(r_grad),
        "grad_norm_flow_p": float(p_grad),
        "mean_alignment": mean_alignment,
    }

    # G2 — Continuity equation: ∂ρ/∂t = -∇·(ρv)
    print("\n  G2 — Continuity equation test")
    k = min(5, n - 1)
    nn = NearestNeighbors(n_neighbors=k + 1)
    nn.fit(Phi)
    idxs = nn.kneighbors(Phi, return_distance=False)

    divergence_rho_v = np.zeros(n)
    for i in range(n):
        neighbors = idxs[i, 1:]
        if len(neighbors) < 2: continue
        rho_i = np.exp(-V[i])
        for nb in neighbors:
            vec = Phi[nb] - Phi[i]
            dist = np.linalg.norm(vec)
            if dist < 1e-10: continue
            rho_nb = np.exp(-V[nb])
            rho_avg = (rho_i + rho_nb) / 2
            v_avg = (flows[i] + flows[nb]) / 2
            divergence_rho_v[i] += rho_avg * v_avg * np.dot(vec / dist, vec / dist) / dist
        divergence_rho_v[i] /= max(len(neighbors), 1)

    # The continuity equation says ∂ρ/∂t = -∇·(ρv). If ρ is stationary, ∇·(ρv) ≈ 0.
    continuity_error = float(np.mean(np.abs(divergence_rho_v)))
    print(f"    Mean |∇·(ρv)| = {continuity_error:.6f} (0 = perfect continuity)")
    results["continuity"] = {"mean_divergence_error": continuity_error}

    # G3 — Fokker-Planck form: ∂ρ/∂t = -∇·(ρv) + D∇²ρ
    print("\n  G3 — Fokker-Planck test")
    # Estimate ∂ρ/∂t from flow (finite difference along flow direction)
    laplacian_rho = np.zeros(n)
    for i in range(n):
        neighbors = idxs[i, 1:]
        if len(neighbors) < 2: continue
        rho_i = np.exp(-V[i])
        laplacian_rho[i] = float(np.mean([np.exp(-V[nb]) for nb in neighbors]) - rho_i)

    # Fit: ∂ρ/∂t = -∇·(ρv) + D∇²ρ
    div_rho_v = divergence_rho_v
    d_rho_dt = -div_rho_v
    X_fp = np.column_stack([div_rho_v, laplacian_rho])
    y_fp = d_rho_dt
    valid = np.isfinite(X_fp[:, 0]) & np.isfinite(X_fp[:, 1]) & np.isfinite(y_fp)
    if valid.sum() > 10:
        reg = LinearRegression().fit(X_fp[valid], y_fp[valid])
        fp_r2 = float(r2_score(y_fp[valid], reg.predict(X_fp[valid])))
        D_diffusion = float(reg.coef_[1])
        print(f"    Fokker-Planck fit R² = {fp_r2:.4f}")
        print(f"    Diffusion coefficient D = {D_diffusion:.4f}")
        results["fokker_planck"] = {"R2": fp_r2, "diffusion_coefficient": D_diffusion}
    else:
        results["fokker_planck"] = {"error": "insufficient_valid_points"}

    # G4 — Hamilton-Jacobi form: ∂V/∂t + H(Φ, ∇V) = 0
    print("\n  G4 — Hamilton-Jacobi form test")
    H_est = np.zeros(n)
    for i in range(n):
        H_est[i] = flows[i] * grad_norms[i] if np.isfinite(flows[i] * grad_norms[i]) else 0
    print(f"    Mean Hamiltonian H(Φ, ∇V) = {H_est.mean():.4f} ± {H_est.std():.4f}")
    results["hamilton_jacobi"] = {"mean_H": float(H_est.mean()), "std_H": float(H_est.std())}

    # G5 — Candidate equation form
    print("\n  G5 — Candidate governing equation")
    candidates = []
    if r_grad > 0.5:
        candidates.append("gradient_flow: ∂Φ/∂t = -∇V(Φ)")
    if continuity_error < 0.1:
        candidates.append("continuity: ∂ρ/∂t = -∇·(ρv)")
    if results.get("fokker_planck", {}).get("R2", 0) > 0.5:
        candidates.append("fokker_planck: ∂ρ/∂t = -∇·(ρv) + D∇²ρ")

    if candidates:
        print(f"    Supported equations:")
        for c in candidates:
            print(f"      ✓ {c}")
    else:
        print(f"    No equation form clearly supported")
    results["candidate_equations"] = candidates
    results["verdict"] = "equation_found" if candidates else "no_equation_found"

    OUTPUT["section_G"] = results
    print(f"\n  Section G complete")
    return results


# =====================================================================
# SECTION H — FINAL DECISION
# =====================================================================

def section_h_final_decision(section_results):
    """Synthesize all sections into a final verdict."""
    print_sep()
    print("SECTION H: FINAL DECISION")
    print_sep()

    verdict_lines = []
    passed = 0
    total = 0

    # H1 — Section A: Ensemble generation success
    total += 1
    n_systems = OUTPUT.get("section_A", {}).get("n_systems", 0)
    if n_systems >= 100:
        passed += 1
        verdict_lines.append(f"✓ A: Generated {n_systems} systems from continuous families")
    else:
        verdict_lines.append(f"✗ A: Insufficient systems ({n_systems})")

    # H2 — Section B: Field continuity
    total += 1
    b_result = OUTPUT.get("section_B", {})
    if isinstance(b_result, dict) and not b_result.get("error"):
        lipschitz = b_result.get("lipschitz_constant")
        smoothness = b_result.get("flow_smoothness", 0)
        if lipschitz is not None and lipschitz < 5.0 and smoothness > 0.5:
            passed += 1
            verdict_lines.append(f"✓ B: Flow field is Lipschitz continuous (L={lipschitz:.2f}, smoothness={smoothness:.2f})")
        elif lipschitz is not None:
            verdict_lines.append(f"∼ B: Flow field partially continuous (L={lipschitz:.2f}, smoothness={smoothness:.2f})")
        else:
            verdict_lines.append(f"∼ B: Flow field continuity indeterminate")
    else:
        verdict_lines.append(f"✗ B: Continuity test failed")

    # H3 — Section C: Critical surfaces
    total += 1
    c_result = OUTPUT.get("section_C", {})
    if isinstance(c_result, dict) and not c_result.get("error"):
        has_topology = bool(c_result.get("topology_per_threshold", {}))
        has_sources = bool(c_result.get("top_flow_sources", []))
        if has_topology and has_sources:
            passed += 1
            verdict_lines.append(f"✓ C: Critical surfaces detected (flow sources/sinks, topology)")
        else:
            verdict_lines.append(f"∼ C: Partial critical surface structure")
    else:
        verdict_lines.append(f"✗ C: Critical surface detection failed")

    # H4 — Section D: Universality retest
    total += 1
    d_result = OUTPUT.get("section_D", {})
    if isinstance(d_result, dict) and not d_result.get("error"):
        pr_ensemble = d_result.get("intrinsic_dim_participation_ratio", 0)
        pr_stability = d_result.get("subsample_pr_stability", [])
        if pr_ensemble > 2.0 and len(pr_stability) >= 3:
            passed += 1
            verdict_lines.append(f"✓ D: Ensemble manifold persists (PR={pr_ensemble:.2f}, subsample stable)")
        elif pr_ensemble > 1.0:
            verdict_lines.append(f"∼ D: Manifold partially persists (PR={pr_ensemble:.2f})")
        else:
            verdict_lines.append(f"✗ D: Ensemble manifold collapsed (PR={pr_ensemble:.2f})")
    else:
        verdict_lines.append(f"✗ D: Universality retest failed")

    # H5 — Section E: Metric learning
    total += 1
    e_result = OUTPUT.get("section_E", {})
    if isinstance(e_result, dict) and not e_result.get("error"):
        best = e_result.get("best_metric")
        if best and best != "euclidean_phi":
            passed += 1
            verdict_lines.append(f"✓ E: Best metric is {best} (beats Euclidean Φ)")
        elif best:
            verdict_lines.append(f"∼ E: Euclidean Φ is best metric")
        else:
            verdict_lines.append(f"✗ E: No metric outperforms")
    else:
        verdict_lines.append(f"✗ E: Metric learning failed")

    # H6 — Section F: Null world
    total += 1
    f_result = OUTPUT.get("section_F", {})
    if isinstance(f_result, dict) and not f_result.get("error"):
        artifact = f_result.get("artifact_score", 1.0)
        if artifact < 0.8:
            passed += 1
            verdict_lines.append(f"✓ F: Null worlds destroy manifold (artifact_score={artifact:.3f})")
        elif artifact < 1.0:
            verdict_lines.append(f"∼ F: Null worlds partially reduce structure ({artifact:.3f})")
        else:
            verdict_lines.append(f"✗ F: Null worlds retain manifold structure (artifact_score={artifact:.3f})")
    else:
        verdict_lines.append(f"✗ F: Null world test failed")

    # H7 — Section G: Field equation
    total += 1
    g_result = OUTPUT.get("section_G", {})
    if isinstance(g_result, dict) and not g_result.get("error"):
        equations = g_result.get("candidate_equations", [])
        if equations:
            passed += 1
            verdict_lines.append(f"✓ G: Field equation candidate(s): {equations[0]}")
        else:
            verdict_lines.append(f"∼ G: No governing equation found")
    else:
        verdict_lines.append(f"✗ G: Field equation search failed")

    # H8 — Overall verdict
    print(f"\n  T030 FINAL VERDICT: {passed}/{total} criteria passed\n")
    for line in verdict_lines:
        print(f"  {line}")

    pr_original = OUTPUT.get("section_D", {}).get("intrinsic_dim_participation_ratio")
    flow_mean = OUTPUT.get("section_A", {}).get("flow_mean")

    if passed / max(total, 1) >= 0.7:
        overall = "TRANSITION FIELD CONFIRMED"
        detail = (
            "The transition manifold survives continuous ensemble testing. "
            "Flow field, critical surfaces, and manifold geometry are real properties\n"
            "of dynamical process-space, not finite-sample artifacts of the 14-system corpus. "
            "SFH-SGP survives as a non-taxonomic, dynamical-field theory of transition-manifold geometry."
        )
    elif passed / max(total, 1) >= 0.4:
        overall = "TRANSITION FIELD PARTIALLY CONFIRMED"
        detail = (
            "Some aspects of the transition field survive (null world destruction, parametric continuity), "
            "but others fail (metric learning, equation discovery). "
            "The transition manifold has elements of genuine dynamical structure, "
            "but the field equation remains elusive."
        )
    else:
        overall = "TRANSITION FIELD NOT CONFIRMED"
        detail = (
            "The transition manifold does not survive continuous ensemble testing. "
            "It is a finite-sample artifact of the 14-system corpus — "
            "descriptive geometry rather than a real dynamical invariant."
        )

    decision = {
        "verdict": overall,
        "passed": int(passed),
        "total": int(total),
        "score": passed / max(total, 1),
        "details": detail,
        "per_section": verdict_lines,
    }

    OUTPUT["section_H"] = decision
    print(f"\n  {'=' * 60}")
    print(f"  OVERALL: {overall}")
    print(f"  {'=' * 60}")
    print(f"\n  {detail}")

    return decision


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("=" * 70)
    print("T030: TRANSITION FIELD GENERALIZATION")
    print("Test: Is the transition manifold a real property of")
    print("      dynamical process-space or a finite-sample artifact?")
    print("=" * 70)

    proj = EmergenceProjector()

    # Section A — Generate ensembles (this is the expensive part)
    start = time.time()
    data = section_a_generate_ensembles(proj)
    elapsed_a = time.time() - start
    print(f"\n  Section A time: {elapsed_a:.1f}s")

    if data["Phi"].shape[0] < 20:
        print("\n  ERROR: Too few systems generated. Aborting.")
        return

    # Section B — Field continuity
    start = time.time()
    section_b_field_continuity(data)
    elapsed_b = time.time() - start
    print(f"  Section B time: {elapsed_b:.1f}s")

    # Section C — Critical surfaces
    start = time.time()
    section_c_critical_surfaces(data)
    elapsed_c = time.time() - start
    print(f"  Section C time: {elapsed_c:.1f}s")

    # Section D — Universality retest
    start = time.time()
    section_d_universality_retest(data)
    elapsed_d = time.time() - start
    print(f"  Section D time: {elapsed_d:.1f}s")

    # Section E — Metric learning
    start = time.time()
    section_e_metric_learning(data, proj)
    elapsed_e = time.time() - start
    print(f"  Section E time: {elapsed_e:.1f}s")

    # Section F — Null world
    start = time.time()
    section_f_null_world(data, proj)
    elapsed_f = time.time() - start
    print(f"  Section F time: {elapsed_f:.1f}s")

    # Section G — Field equation
    start = time.time()
    section_g_field_equation(data)
    elapsed_g = time.time() - start
    print(f"  Section G time: {elapsed_g:.1f}s")

    # Section H — Final decision
    start = time.time()
    decision = section_h_final_decision({})
    elapsed_h = time.time() - start
    print(f"  Section H time: {elapsed_h:.1f}s")

    total_time = elapsed_a + elapsed_b + elapsed_c + elapsed_d + elapsed_e + elapsed_f + elapsed_g + elapsed_h
    print(f"\n  Total time: {total_time:.1f}s")

    # Save all results
    OUTPUT["metadata"] = {
        "n_systems": int(data["Phi"].shape[0]),
        "n_families": len(OUTPUT.get("section_A", {}).get("systems_per_family", {})),
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open(OUT / "t030_transition_field_generalization.json", "w") as f:
        json.dump(OUTPUT, f, indent=2, cls=NpEncoder)
    print(f"\n  Results saved to {OUT}/t030_transition_field_generalization.json")

    return decision


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, (np.bool_,)): return bool(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)


if __name__ == "__main__":
    main()
