#!/usr/bin/env python3
"""
T028: TRANSITION MANIFOLD DYNAMICS
===================================
"Is the bridge region an actual dynamical transition manifold,
or merely a sparse geometric artifact?"

Builds on T027's flow invariant by testing whether Φ-space is
genuinely dynamical — whether systems are attracted to, repelled
from, or channeled through the bridge region under perturbation.

Sections:
  A — Dynamic perturbation trajectories through Φ-space
  B — Transition basin dynamics (attractor/escape/crossing)
  C — Manifold stability tensor (Jacobian ∂Φ/∂ε)
  D — Geodesic transition analysis (shortest paths, betweenness)
  E — Temporal flow coherence (autocorrelation, persistence decay)
  F — Synthetic continuation fields (inter-system interpolation)
  G — Catastrophe / bifurcation detection
  H — Null geometry destruction

Success: trajectory dynamics are systematic, bridge is a transit corridor,
         geodesic centrality elevated, null destruction breaks prediction.
"""

import sys, json, warnings, math, itertools, collections
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform, cdist
from scipy.stats import pearsonr, spearmanr, gaussian_kde, ttest_ind, linregress
from scipy.spatial import Delaunay
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.linear_model import LinearRegression
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
FEATURE_NAMES = [
    "pc1", "pc2", "effective_rank", "tau_m1", "tau_m2", "tau_m3", "tau_m4",
    "temporal_corr", "phase_corr", "pc1_ratio", "replay_displacement",
    "abl_full_pc1", "abl_no_m1_pc1", "abl_no_m2_pc1", "abl_no_m3_pc1",
    "abl_no_m4_pc1", "m2_contribution",
]

def print_sep():
    print("\n" + "=" * 70)

# =====================================================================
# LOADING & EMERGENCE COORDINATE COMPUTATION
# =====================================================================

class EmergenceProjector:
    """Computes (C,F,A,R) from 17D feature vectors using fixed standardization."""

    def __init__(self):
        feat = pd.read_csv(OUT / "clustering_feature_matrix.csv")
        feat = feat[feat["system"].isin(ALL_SYSTEMS)].set_index("system").loc[ALL_SYSTEMS]
        self.X_raw = feat[FEATURE_NAMES].values.astype(float)
        self.feat_mean = self.X_raw.mean(axis=0)
        self.feat_std = self.X_raw.std(axis=0)

        # Reference Φ values
        coord = pd.read_csv(OUT / "emergence_coordinates.csv")
        coord = coord[coord["system"].isin(ALL_SYSTEMS)].reset_index(drop=True)
        self.ref_Phi = coord[["C", "F", "A", "R"]].values

        # Compute raw composite values for standardization
        raw = self._compute_raw_composites(self.X_raw)
        self.phi_mean = {ax: float(np.mean(raw[ax])) for ax in ["C", "F", "A", "R"]}
        self.phi_std = {ax: float(np.std(raw[ax])) for ax in ["C", "F", "A", "R"]}

    def _zscore(self, X):
        return (X - self.feat_mean) / np.maximum(self.feat_std, 1e-12)

    def _compute_raw_composites(self, X):
        """Compute raw C,F,A,R values before final z-score."""
        Xs = self._zscore(X)
        n = Xs.shape[0]
        raw = {}

        abl_cols = [FEATURE_NAMES.index(c) for c in FEATURE_NAMES
                    if c.startswith("abl_") or c == "m2_contribution"]
        tau_cols = [FEATURE_NAMES.index(c) for c in FEATURE_NAMES if c.startswith("tau_")]

        idx = {name: i for i, name in enumerate(FEATURE_NAMES)}

        # C
        c_parts = []
        if "temporal_corr" in idx:
            c_parts.append(-Xs[:, idx["temporal_corr"]])
        if "effective_rank" in idx:
            c_parts.append(-Xs[:, idx["effective_rank"]])
        if "pc1_ratio" in idx:
            c_parts.append(Xs[:, idx["pc1_ratio"]])
        if "replay_displacement" in idx:
            c_parts.append(-Xs[:, idx["replay_displacement"]])
        raw["C"] = np.mean(c_parts, axis=0) if c_parts else np.zeros(n)

        # F
        f_parts = []
        for fname in ["tau_m2", "tau_m4", "phase_corr", "pc2"]:
            if fname in idx:
                f_parts.append(Xs[:, idx[fname]])
        raw["F"] = np.mean(f_parts, axis=0) if f_parts else np.zeros(n)

        # A
        a_parts = []
        if len(abl_cols) >= 2:
            abl_slice = Xs[:, abl_cols]
            a_parts.append(np.linalg.norm(abl_slice, axis=1))
            a_parts.append(np.std(abl_slice, axis=1))
        if "tau_m1" in idx:
            a_parts.append(Xs[:, idx["tau_m1"]])
        raw["A"] = np.mean(a_parts, axis=0) if a_parts else np.zeros(n)

        # R
        r_parts = []
        if "pc1" in idx:
            r_parts.append(Xs[:, idx["pc1"]])
        if len(tau_cols) >= 2:
            tau_slice = Xs[:, tau_cols]
            r_parts.append(np.mean(tau_slice, axis=1))
            r_parts.append(np.std(tau_slice, axis=1))
        raw["R"] = np.mean(r_parts, axis=0) if r_parts else np.zeros(n)

        return raw

    def project(self, X_new):
        """Project new feature vectors to (C,F,A,R)."""
        X_new = np.atleast_2d(np.asarray(X_new, dtype=float))
        raw = self._compute_raw_composites(X_new)
        Phi = np.zeros((X_new.shape[0], 4))
        for j, ax in enumerate(["C", "F", "A", "R"]):
            Phi[:, j] = (raw[ax] - self.phi_mean[ax]) / max(self.phi_std[ax], 1e-12)
        return Phi


def load_all():
    """Load all baseline data."""
    coord = pd.read_csv(OUT / "emergence_coordinates.csv")
    coord = coord[coord["system"].isin(ALL_SYSTEMS)].reset_index(drop=True)
    Phi = coord[["C", "F", "A", "R"]].values

    flow_df = pd.read_csv(OUT / "emergence_flow_field.csv")
    flow_map = {r["system"]: r["flow_magnitude"] for _, r in flow_df.iterrows()}
    flow_vals = np.array([flow_map[s] for s in ALL_SYSTEMS])

    with open(OUT / "emergence_energy_landscape.json") as f:
        landscape = json.load(f)
    curv_map = {s: landscape["curvature_per_system"][s]["mean_curvature"]
                for s in ALL_SYSTEMS}
    curv_vals = np.array([curv_map[s] for s in ALL_SYSTEMS])
    dens_map = {s: landscape["density_per_system"].get(s, 0) for s in ALL_SYSTEMS}
    dens_vals = np.array([dens_map[s] for s in ALL_SYSTEMS])

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
    collapse_vals = np.array([collapse_slopes[s] for s in ALL_SYSTEMS])

    return {
        "coord": coord, "Phi": Phi,
        "flow": flow_vals, "curv": curv_vals, "dens": dens_vals,
        "collapse_slopes": collapse_slopes, "collapse_vals": collapse_vals,
    }


def rank_corr(x, y):
    if np.std(x) == 0 or np.std(y) == 0:
        return 0.0, 1.0
    return spearmanr(x, y)


# =====================================================================
# SECTION A — DYNAMIC PERTURBATION TRAJECTORIES
# =====================================================================

def section_a_trajectories(proj, data):
    """
    For each system: apply progressive perturbations, trace Φ trajectory.
    Compute drift direction, velocity, curvature, geodesic deviation.
    """
    print_sep()
    print("SECTION A: DYNAMIC PERTURBATION TRAJECTORIES")
    print_sep()

    feat_df = pd.read_csv(OUT / "clustering_feature_matrix.csv")
    feat_df = feat_df[feat_df["system"].isin(ALL_SYSTEMS)].set_index("system").loc[ALL_SYSTEMS]
    X0 = feat_df[FEATURE_NAMES].values.astype(float)

    levels = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0]
    n_trials = 50
    n = len(ALL_SYSTEMS)

    trajectories = np.zeros((n, len(levels), 4))
    drifts = np.zeros((n, len(levels)))

    print(f"  Computing trajectories: {n} systems × {len(levels)} levels × {n_trials} trials")

    for i in range(n):
        for j, sigma in enumerate(levels):
            if sigma == 0:
                trajectories[i, j] = data["Phi"][i]
                drifts[i, j] = 0.0
                continue
            phis = []
            for _ in range(n_trials):
                X_pert = X0.copy()
                X_pert[i] += np.random.normal(0, sigma * proj.feat_std, X0.shape[1])
                phi = proj.project(X_pert[i])
                phis.append(phi[0])
            trajectories[i, j] = np.mean(phis, axis=0)
            drifts[i, j] = np.linalg.norm(trajectories[i, j] - data["Phi"][i])

    # A1 — Drift analysis
    print("\n  A1 — Drift magnitude at max perturbation (σ=3.0)")
    final_drift = drifts[:, -1]
    for i in np.argsort(final_drift)[::-1]:
        print(f"    {ALL_SYSTEMS[i]:<24s} drift={final_drift[i]:.3f} "
              f"flow={data['flow'][i]:.2f}")

    r_drift_flow, p_drift_flow = pearsonr(final_drift, data["flow"])
    print(f"  drift(σ=3) ~ flow: r={r_drift_flow:.3f}, p={p_drift_flow:.4f}")

    # A2 — Trajectory velocity (derivative w.r.t. σ)
    print("\n  A2 — Trajectory velocity (ΔΦ/Δσ at low noise)")
    velocities = np.zeros((n, 3))  # low, mid, high sigma ranges
    for i in range(n):
        for k, (j_start, j_end) in enumerate([(0, 3), (3, 6), (6, 10)]):
            if j_end > j_start:
                vel = np.linalg.norm(trajectories[i, j_end] - trajectories[i, j_start]) / (levels[j_end] - levels[j_start] + 1e-12)
                velocities[i, k] = vel

    for i in np.argsort(velocities[:, 0])[-5:][::-1]:
        print(f"    {ALL_SYSTEMS[i]:<24s} v_low={velocities[i,0]:.3f} "
              f"v_mid={velocities[i,1]:.3f} v_high={velocities[i,2]:.3f}")

    r_vel_flow, p_vel_flow = pearsonr(velocities[:, 0], data["flow"])
    print(f"  velocity(low) ~ flow: r={r_vel_flow:.3f}, p={p_vel_flow:.4f}")

    # A3 — Trajectory curvature (angle between successive displacement vectors)
    print("\n  A3 — Trajectory curvature")
    curvatures = np.zeros(n)
    for i in range(n):
        vecs = np.diff(trajectories[i], axis=0)
        angles = []
        for k in range(len(vecs) - 2):
            v1 = vecs[k]
            v2 = vecs[k+1]
            dot = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-12)
            angles.append(abs(dot))
        curvatures[i] = np.mean(angles) if angles else 0.0

    for i in np.argsort(curvatures)[:5]:
        print(f"    {ALL_SYSTEMS[i]:<24s} straightness={curvatures[i]:.3f} "
              f"(1=totally straight) flow={data['flow'][i]:.2f}")

    r_curv_flow, p_curv_flow = pearsonr(curvatures, data["flow"])
    print(f"  trajectory straightness ~ flow: r={r_curv_flow:.3f}, p={p_curv_flow:.4f}")

    # A4 — Direction of drift (which Φ-component changes most?)
    print("\n  A4 — Drift direction (dominant Φ-axis change)")
    axes = ["C", "F", "A", "R"]
    for j, ax in enumerate(axes):
        axis_change = np.abs(trajectories[:, -1, j] - trajectories[:, 0, j])
        for i in np.argsort(axis_change)[-3:][::-1]:
            print(f"    Δ{ax} for {ALL_SYSTEMS[i]:<24s} = {axis_change[i]:.3f} "
                  f"(flow={data['flow'][i]:.2f})")

    # A5 — Geodesic deviation: does perturbation push along or off the manifold?
    print("\n  A5 — Geodesic deviation")
    manifold_dists = squareform(pdist(data["Phi"]))
    deviations = np.zeros(n)
    for i in range(n):
        final_pos = trajectories[i, -1]
        # Distance to each reference system
        dists = np.linalg.norm(data["Phi"] - final_pos, axis=1)
        # Nearest neighbor in original manifold
        orig_nn = np.argsort(manifold_dists[i])[1]
        new_nn = np.argsort(dists)[0]
        deviations[i] = manifold_dists[orig_nn, new_nn] if new_nn != orig_nn else 0.0

    for i in np.argsort(deviations)[-5:][::-1]:
        print(f"    {ALL_SYSTEMS[i]:<24s} deviation={deviations[i]:.3f} "
              f"flow={data['flow'][i]:.2f}")

    result = {
        "final_drift": {ALL_SYSTEMS[i]: float(final_drift[i]) for i in range(n)},
        "drift_flow_corr": {"r": float(r_drift_flow), "p": float(p_drift_flow)},
        "velocity_low": {ALL_SYSTEMS[i]: float(velocities[i, 0]) for i in range(n)},
        "velocity_flow_corr": {"r": float(r_vel_flow), "p": float(p_vel_flow)},
        "straightness": {ALL_SYSTEMS[i]: float(curvatures[i]) for i in range(n)},
        "straightness_flow_corr": {"r": float(r_curv_flow), "p": float(p_curv_flow)},
    }
    return result, trajectories, drifts, velocities


# =====================================================================
# SECTION B — TRANSITION BASIN DYNAMICS
# =====================================================================

def section_b_basin_dynamics(proj, data, trajectories):
    """
    Test whether trajectories are attracted to, repelled from,
    or channeled through the bridge region.
    """
    print_sep()
    print("SECTION B: TRANSITION BASIN DYNAMICS")
    print_sep()

    Phi = data["Phi"]
    flow = data["flow"]
    n = len(ALL_SYSTEMS)

    bridge_idx = [i for i, s in enumerate(ALL_SYSTEMS) if s in BRIDGE_SYSTEMS]
    bridge_centroid = Phi[bridge_idx].mean(axis=0)

    # B1 — Attraction to bridge centroid
    print("\n  B1 — Bridge centroid distance under perturbation")
    dist_to_bridge = np.zeros((n, trajectories.shape[1]))
    for i in range(n):
        for j in range(trajectories.shape[1]):
            dist_to_bridge[i, j] = np.linalg.norm(trajectories[i, j] - bridge_centroid)

    # Does trajectory move toward or away from bridge?
    bridge_direction = np.zeros(n)
    for i in range(n):
        d_start = dist_to_bridge[i, 0]
        d_end = dist_to_bridge[i, -1]
        bridge_direction[i] = d_end - d_start  # positive = moving away

    approaching = [ALL_SYSTEMS[i] for i in range(n) if bridge_direction[i] < 0]
    receding = [ALL_SYSTEMS[i] for i in range(n) if bridge_direction[i] > 0]
    print(f"    Systems approaching bridge: {', '.join(approaching)}")
    print(f"    Systems receding from bridge: {', '.join(receding)}")
    print(f"    Systems on bridge: {', '.join(ALL_SYSTEMS[i] for i in bridge_idx)}")

    r_dir_flow, p_dir_flow = pearsonr(bridge_direction, flow)
    print(f"    bridge_direction ~ flow: r={r_dir_flow:.3f}, p={p_dir_flow:.4f}")

    # B2 — Basin escape frequency
    print("\n  B2 — Basin escape under perturbation")
    with open(OUT / "emergence_energy_landscape.json") as f:
        landscape = json.load(f)
    orig_basins = {s: landscape["basin_assignment"].get(s, -1) for s in ALL_SYSTEMS}

    # For each trajectory point, find closest reference system and check basin
    basin_escapes = np.zeros(n)
    for i in range(n):
        orig_basin = orig_basins[ALL_SYSTEMS[i]]
        for j in range(trajectories.shape[1]):
            dists = np.linalg.norm(Phi - trajectories[i, j], axis=1)
            nearest = ALL_SYSTEMS[np.argmin(dists)]
            nearest_basin = orig_basins[nearest]
            if nearest_basin != orig_basin:
                basin_escapes[i] += 1
        basin_escapes[i] /= max(trajectories.shape[1] - 1, 1)

    for i in np.argsort(basin_escapes)[-5:][::-1]:
        print(f"    {ALL_SYSTEMS[i]:<24s} escape_rate={basin_escapes[i]:.3f} "
              f"flow={flow[i]:.2f} basin={orig_basins[ALL_SYSTEMS[i]]}")

    r_escape_flow, p_escape_flow = pearsonr(basin_escapes, flow)
    print(f"    escape ~ flow: r={r_escape_flow:.3f}, p={p_escape_flow:.4f}")

    # B3 — Bridge crossing
    print("\n  B3 — Bridge crossing events")
    bridge_crossings = np.zeros(n)
    for i in range(n):
        for j in range(trajectories.shape[1]):
            dists = np.linalg.norm(Phi - trajectories[i, j], axis=1)
            nearest = np.argmin(dists)
            if nearest in bridge_idx:
                bridge_crossings[i] += 1
        bridge_crossings[i] /= max(trajectories.shape[1], 1)

    for i in np.argsort(bridge_crossings)[-5:][::-1]:
        print(f"    {ALL_SYSTEMS[i]:<24s} bridge_crossing={bridge_crossings[i]:.3f} "
              f"flow={flow[i]:.2f}")

    r_cross_flow, p_cross_flow = pearsonr(bridge_crossings, flow)
    print(f"    bridge_crossing ~ flow: r={r_cross_flow:.3f}, p={p_cross_flow:.4f}")

    # B4 — Combined: approach → cross → escape sequencing
    print("\n  B4 — Flow directionality (approach → cross → depart)")
    # Systems with negative bridge_direction that CROSS the bridge are "transiting"
    transiting = [s for s in approaching
                  if bridge_crossings[ALL_SYSTEMS.index(s)] > 0]
    print(f"    Systems transiting through bridge: {transiting}")

    result = {
        "approaching_bridge": approaching,
        "receding_from_bridge": receding,
        "bridge_direction_flow_corr": {"r": float(r_dir_flow), "p": float(p_dir_flow)},
        "basin_escape_flow_corr": {"r": float(r_escape_flow), "p": float(p_escape_flow)},
        "bridge_crossing_flow_corr": {"r": float(r_cross_flow), "p": float(p_cross_flow)},
        "transiting_systems": transiting,
    }
    return result


# =====================================================================
# SECTION C — MANIFOLD STABILITY TENSOR
# =====================================================================

def section_c_stability_tensor(proj, data):
    """
    Compute M_ij = ∂Φ_i / ∂ε_j via finite differences.
    4 emergence axes × 17 features = 68-dimensional local tensor.
    """
    print_sep()
    print("SECTION C: MANIFOLD STABILITY TENSOR")
    print_sep()

    feat_df = pd.read_csv(OUT / "clustering_feature_matrix.csv")
    feat_df = feat_df[feat_df["system"].isin(ALL_SYSTEMS)].set_index("system").loc[ALL_SYSTEMS]
    X0 = feat_df[FEATURE_NAMES].values.astype(float)
    n, d = X0.shape
    n_axes = 4
    eps = 0.05

    # C1 — Full stability tensor
    print(f"  Computing stability tensor: {n} systems × {d} features × {n_axes} axes")
    tensors = np.zeros((n, n_axes, d))

    for i in range(n):
        for j in range(d):
            X_plus = X0.copy()
            X_minus = X0.copy()
            delta = eps * max(proj.feat_std[j], 0.01)
            X_plus[i, j] += delta
            X_minus[i, j] -= delta
            phi_plus = proj.project(X_plus[i])[0]
            phi_minus = proj.project(X_minus[i])[0]
            tensors[i, :, j] = (phi_plus - phi_minus) / (2 * delta)

    # C2 — Feature sensitivity ranking
    print("\n  C2 — Most influential features (mean |∂Φ/∂ε| across systems)")
    feature_sensitivity = np.mean(np.abs(tensors), axis=(0, 1))
    top_feats = np.argsort(feature_sensitivity)[-5:][::-1]
    print(f"    Most influential features on Φ-space:")
    for idx in top_feats:
        print(f"      {FEATURE_NAMES[idx]:<20s} mean|∂Φ/∂ε|={feature_sensitivity[idx]:.4f}")

    # C3 — System-level stability norm
    print("\n  C3 — System stability norm (‖M‖_F per system)")
    frob_norms = np.array([np.linalg.norm(tensors[i]) for i in range(n)])
    for i in np.argsort(frob_norms)[::-1]:
        print(f"    {ALL_SYSTEMS[i]:<24s} ‖M‖_F={frob_norms[i]:.4f} "
              f"flow={data['flow'][i]:.2f}")

    r_stab_flow, p_stab_flow = pearsonr(frob_norms, data["flow"])
    print(f"    stability_norm ~ flow: r={r_stab_flow:.3f}, p={p_stab_flow:.4f}")

    # C4 — Anisotropy: ratio of strongest to weakest axis sensitivity
    print("\n  C4 — Tensor anisotropy (axis sensitivity ratio)")
    axis_std = np.std(tensors, axis=(0, 2))
    for j, ax in enumerate(["C", "F", "A", "R"]):
        print(f"    {ax}: cross-system std of sensitivity = {axis_std[j]:.4f}")
    aniso_ratio = float(axis_std.max() / max(axis_std.min(), 1e-10))
    print(f"    Anisotropy ratio (max/min axis): {aniso_ratio:.3f}")

    # C5 — Stable vs unstable directions per system
    print("\n  C5 — Leading eigenmode of perturbation response")
    leading_modes = []
    for i in range(n):
        # 4×17 → SVD gives perturbation patterns
        u, s, vt = np.linalg.svd(tensors[i], full_matrices=False)
        leading = vt[0]
        leading_feat = np.argmax(np.abs(leading))
        leading_modes.append({
            "system": ALL_SYSTEMS[i],
            "singular_values": [float(sv) for sv in s],
            "leading_feature": FEATURE_NAMES[leading_feat],
            "leading_strength": float(s[0]),
        })
        print(f"    {ALL_SYSTEMS[i]:<24s} σ₁={s[0]:.4f} σ₂={s[1]:.4f} "
              f"top_feat={FEATURE_NAMES[leading_feat]}")

    # C6 — Local Lyapunov-like exponent (mean singular value)
    print("\n  C6 — Local expansion rate (mean singular value)")
    lyap_rates = np.array([lm["leading_strength"] for lm in leading_modes])
    for i in np.argsort(lyap_rates)[-3:][::-1]:
        print(f"    {ALL_SYSTEMS[i]:<24s} λ₁={lyap_rates[i]:.4f} "
              f"flow={data['flow'][i]:.2f}")
    r_lyap_flow, p_lyap_flow = pearsonr(lyap_rates, data["flow"])
    print(f"    Lyapunov ~ flow: r={r_lyap_flow:.3f}, p={p_lyap_flow:.4f}")

    result = {
        "feature_sensitivity": {FEATURE_NAMES[i]: float(feature_sensitivity[i])
                                for i in np.argsort(feature_sensitivity)[-8:][::-1]},
        "system_stability_norm": {ALL_SYSTEMS[i]: float(frob_norms[i])
                                  for i in range(n)},
        "stability_flow_corr": {"r": float(r_stab_flow), "p": float(p_stab_flow)},
        "axis_anisotropy_ratio": aniso_ratio,
        "leading_modes": leading_modes,
        "lyapunov_flow_corr": {"r": float(r_lyap_flow), "p": float(p_lyap_flow)},
    }
    return result, tensors


# =====================================================================
# SECTION D — GEODESIC TRANSITION ANALYSIS
# =====================================================================

def section_d_geodesic(data):
    """
    Build nearest-neighbor manifold graph, compute geodesic paths,
    betweenness centrality, transit corridor detection.
    """
    print_sep()
    print("SECTION D: GEODESIC TRANSITION ANALYSIS")
    print_sep()

    Phi = data["Phi"]
    flow = data["flow"]
    n = len(ALL_SYSTEMS)

    # Build kNN graph (k=4) for meaningful geodesic paths
    dist_mat = squareform(pdist(Phi))
    k_nn = min(4, n - 1)

    D1 = nx.Graph()
    for i in range(n):
        D1.add_node(i, system=ALL_SYSTEMS[i], flow=flow[i])
    for i in range(n):
        nearest = np.argsort(dist_mat[i])[1:k_nn+1]
        for j in nearest:
            D1.add_edge(i, j, weight=dist_mat[i, j])

    # Compute shortest paths between all pairs
    print("\n  D1 — Geodesic shortest paths")
    all_paths = dict(nx.all_pairs_dijkstra_path(D1, weight="weight"))
    all_lengths = dict(nx.all_pairs_dijkstra_path_length(D1, weight="weight"))

    # D2 — Geodesic betweenness centrality
    print("\n  D2 — Geodesic betweenness centrality")
    betweenness = nx.betweenness_centrality(D1, weight="weight", normalized=True)
    for i in np.argsort(list(betweenness.values()))[-5:][::-1]:
        print(f"    {ALL_SYSTEMS[i]:<24s} betweenness={betweenness[i]:.4f} "
              f"flow={flow[i]:.2f}")

    r_betw_flow, p_betw_flow = pearsonr(
        [betweenness[i] for i in range(n)], flow)
    print(f"    betweenness ~ flow: r={r_betw_flow:.3f}, p={p_betw_flow:.4f}")

    # D3 — Bridge centrality (are bridge systems on shortest paths?)
    print("\n  D3 — Bridge as transit corridor")
    bridge_idx = [i for i, s in enumerate(ALL_SYSTEMS) if s in BRIDGE_SYSTEMS]
    n_pairs = n * (n - 1) // 2
    bridge_on_path = np.zeros(n)
    for i in range(n):
        count = 0
        total = 0
        for s in range(n):
            for t in range(s + 1, n):
                if s == i or t == i:
                    continue
                path = all_paths[s][t]
                if i in path[1:-1]:
                    count += 1
                total += 1
        bridge_on_path[i] = count / max(total, 1)

    for i in np.argsort(bridge_on_path)[-5:][::-1]:
        print(f"    {ALL_SYSTEMS[i]:<24s} on_shortest_path={bridge_on_path[i]:.3f} "
              f"flow={flow[i]:.2f} {'BRIDGE' if ALL_SYSTEMS[i] in BRIDGE_SYSTEMS else ''}")

    bridge_avg = np.mean([bridge_on_path[i] for i in bridge_idx])
    other_avg = np.mean([bridge_on_path[i] for i in range(n) if i not in bridge_idx])
    print(f"    Bridge avg path inclusion: {bridge_avg:.3f}")
    print(f"    Non-bridge avg: {other_avg:.3f}")
    print(f"    {'CORRIDOR ✓' if bridge_avg > other_avg else 'NOT A CORRIDOR'}")

    # D4 — Shortest path transitions through bridge
    print("\n  D4 — Transition corridor map")
    # Identify path segments that go through high-flow systems
    corridor_edges = []
    for s in range(n):
        for t in range(s + 1, n):
            path = all_paths[s][t]
            path_flows = [flow[node] for node in path]
            if max(path_flows) > flow.mean() + flow.std():
                corridor_edges.append((ALL_SYSTEMS[s], ALL_SYSTEMS[t],
                                       max(path_flows)))
    corridor_edges.sort(key=lambda x: x[2], reverse=True)
    print(f"    Paths through high-flow region: {len(corridor_edges)}")
    for s, t, f in corridor_edges[:6]:
        print(f"      {s} → ... → {t}: max flow on path = {f:.2f}")

    # D5 — Knots of the manifold (high-betweenness, high-flow intersection)
    print("\n  D5 — Manifold knot detection")
    knot_scores = {}
    for i in range(n):
        knot_scores[ALL_SYSTEMS[i]] = betweenness[i] * flow[i]
    for s in sorted(knot_scores, key=lambda k: knot_scores[k], reverse=True)[:4]:
        print(f"    {s:<24s} knot_score={knot_scores[s]:.4f} "
              f"(betweenness={betweenness[ALL_SYSTEMS.index(s)]:.3f} "
              f"× flow={flow[ALL_SYSTEMS.index(s)]:.2f})")

    result = {
        "betweenness": {ALL_SYSTEMS[i]: float(betweenness[i]) for i in range(n)},
        "betweenness_flow_corr": {"r": float(r_betw_flow), "p": float(p_betw_flow)},
        "bridge_path_inclusion": {ALL_SYSTEMS[i]: float(bridge_on_path[i])
                                  for i in range(n)},
        "bridge_avg_inclusion": float(bridge_avg),
        "non_bridge_avg_inclusion": float(other_avg),
        "is_corridor": bridge_avg > other_avg,
        "knot_scores": knot_scores,
    }
    return result


# =====================================================================
# SECTION E — TEMPORAL FLOW COHERENCE
# =====================================================================

def section_e_temporal_flow(proj, data):
    """
    Compute time-evolving flow under increasing perturbation.
    Measure flow autocorrelation, persistence, coherence decay.
    """
    print_sep()
    print("SECTION E: TEMPORAL FLOW COHERENCE")
    print_sep()

    feat_df = pd.read_csv(OUT / "clustering_feature_matrix.csv")
    feat_df = feat_df[feat_df["system"].isin(ALL_SYSTEMS)].set_index("system").loc[ALL_SYSTEMS]
    X0 = feat_df[FEATURE_NAMES].values.astype(float)
    n = len(ALL_SYSTEMS)

    levels = np.array([0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0])
    n_trials = 30

    # Flow evolution: at each noise level, compute flow field
    flow_evolution = np.zeros((n, len(levels)))
    print(f"  Computing flow evolution: {len(levels)} levels × {n_trials} trials")

    for j, sigma in enumerate(levels):
        if sigma == 0:
            flow_evolution[:, j] = data["flow"]
            continue
        phis_all = []
        for _ in range(n_trials):
            X_noise = X0 + np.random.normal(0, sigma * proj.feat_std, X0.shape)
            Phi_noise = proj.project(X_noise)
            phis_all.append(Phi_noise)
        Phi_mean = np.mean(phis_all, axis=0)
        # Compute approximate flow from perturbed Φ-space
        for i in range(n):
            dists = np.linalg.norm(Phi_mean - Phi_mean[i], axis=1)
            nn_idx = np.argsort(dists)[1:min(5, n)]
            neighbor_center = Phi_mean[nn_idx].mean(axis=0)
            flow_evolution[i, j] = np.linalg.norm(neighbor_center - Phi_mean[i]) / max(dists[nn_idx].mean(), 1e-12)

    # E1 — Flow autocorrelation (correlation between successive σ levels)
    print("\n  E1 — Flow field autocorrelation over noise levels")
    auto_corrs = []
    for j in range(len(levels) - 1):
        r, _ = pearsonr(flow_evolution[:, j], flow_evolution[:, j + 1])
        auto_corrs.append(r)
        print(f"    r(σ={levels[j]:.1f}, σ={levels[j+1]:.1f}) = {r:.4f}")

    # E2 — Flow persistence time (σ where autocorrelation drops below 0.5)
    print("\n  E2 — Flow persistence threshold")
    persistence_sigma = None
    for j, ac in enumerate(auto_corrs):
        if ac < 0.5:
            persistence_sigma = levels[j + 1]
            print(f"    Flow decorrelates at σ ≈ {persistence_sigma:.1f} (r={ac:.3f})")
            break
    if persistence_sigma is None:
        persistence_sigma = levels[-1]
        print(f"    Flow never decorrelates (min r={auto_corrs[-1]:.3f})")

    # E3 — Coherence decay rate
    print("\n  E3 — Coherence decay")
    decay_rates = np.zeros(n)
    for i in range(n):
        if np.std(flow_evolution[i]) > 0 and len(levels) > 2:
            slope, _, _, _, _ = linregress(levels[1:], flow_evolution[i, 1:])
            decay_rates[i] = slope if not np.isnan(slope) else 0.0
        else:
            decay_rates[i] = 0.0

    for i in np.argsort(abs(decay_rates))[-5:][::-1]:
        print(f"    {ALL_SYSTEMS[i]:<24s} decay_rate={decay_rates[i]:.4f} "
              f"initial_flow={data['flow'][i]:.2f}")

    r_decay_flow, p_decay_flow = pearsonr(abs(decay_rates), data["flow"])
    print(f"    |decay| ~ flow: r={r_decay_flow:.3f}, p={p_decay_flow:.4f}")

    # E4 — Rank preservation of flow field
    print("\n  E4 — Flow rank preservation")
    ref_rank = np.argsort(np.argsort(data["flow"]))
    rank_corrs = []
    for j in range(len(levels)):
        cur_rank = np.argsort(np.argsort(flow_evolution[:, j]))
        r, _ = spearmanr(ref_rank, cur_rank)
        rank_corrs.append(r)
    print(f"    Rank correlation at σ=0: {rank_corrs[0]:.4f}")
    print(f"    Rank correlation at σ={levels[-1]:.1f}: {rank_corrs[-1]:.4f}")
    print(f"    {'RANKS STABLE ✓' if rank_corrs[-1] > 0.5 else 'RANKS LOST ✗'}")

    result = {
        "autocorrelations": [float(ac) for ac in auto_corrs],
        "persistence_sigma": float(persistence_sigma) if persistence_sigma else None,
        "decay_rates": {ALL_SYSTEMS[i]: float(decay_rates[i]) for i in range(n)},
        "decay_flow_corr": {"r": float(r_decay_flow), "p": float(p_decay_flow)},
        "rank_preservation": [float(rc) for rc in rank_corrs],
        "ranks_stable": rank_corrs[-1] > 0.5,
    }
    return result, flow_evolution


# =====================================================================
# SECTION F — SYNTHETIC CONTINUATION FIELDS
# =====================================================================

def section_f_synthetic_continuation(proj, data):
    """
    Interpolate between system pairs through feature space.
    Test whether trajectories smoothly pass through bridge region.
    """
    print_sep()
    print("SECTION F: SYNTHETIC CONTINUATION FIELDS")
    print_sep()

    feat_df = pd.read_csv(OUT / "clustering_feature_matrix.csv")
    feat_df = feat_df[feat_df["system"].isin(ALL_SYSTEMS)].set_index("system").loc[ALL_SYSTEMS]
    X0 = feat_df[FEATURE_NAMES].values.astype(float)
    n = len(ALL_SYSTEMS)
    flow = data["flow"]

    # F1 — Interpolation pairs (from stable to bridge, stable to stable, etc.)
    pairs = [
        ("logistic_map", "lorenz"),
        ("cfg_expansion", "lambda_reduction"),
        ("iid_gaussian", "ising_magnetization"),
        ("colored_noise", "reaction_diffusion"),
        ("primes", "lorenz"),
        ("fibonacci", "henon_map"),
    ]

    n_steps = 50
    print(f"  Computing {len(pairs)} synthetic continua, {n_steps} steps each")

    all_continua = {}
    for s1_name, s2_name in pairs:
        i1, i2 = ALL_SYSTEMS.index(s1_name), ALL_SYSTEMS.index(s2_name)

        # Linear interpolation in feature space
        alphas = np.linspace(0, 1, n_steps)
        continuua_Phi = np.zeros((n_steps, 4))
        for k, alpha in enumerate(alphas):
            X_interp = (1 - alpha) * X0[i1] + alpha * X0[i2]
            continuua_Phi[k] = proj.project(X_interp)[0]

        # Trajectory properties
        total_arc = np.sum(np.linalg.norm(np.diff(continuua_Phi, axis=0), axis=1))
        displacement = np.linalg.norm(continuua_Phi[-1] - continuua_Phi[0])
        straightness = displacement / max(total_arc, 1e-12)
        max_curv = 0
        for k in range(1, n_steps - 1):
            v1 = continuua_Phi[k] - continuua_Phi[k-1]
            v2 = continuua_Phi[k+1] - continuua_Phi[k]
            angle = abs(np.dot(v1, v2) / (np.linalg.norm(v1)*np.linalg.norm(v2)+1e-12))
            max_curv = max(max_curv, 1 - angle)

        # Does trajectory pass near bridge?
        bridge_idx = [i for i, s in enumerate(ALL_SYSTEMS) if s in BRIDGE_SYSTEMS]
        bridge_centroid = data["Phi"][bridge_idx].mean(axis=0)
        min_dist_to_bridge = min(np.linalg.norm(continuua_Phi[k] - bridge_centroid)
                                 for k in range(n_steps))

        # Flow along trajectory
        flow_along = np.array([compute_local_flow_knn(continuua_Phi, k)
                               for k in range(n_steps)])
        peak_flow = flow_along.max()

        print(f"\n    {s1_name} → {s2_name}:")
        print(f"      arc_length={total_arc:.3f}, straightness={straightness:.3f}")
        print(f"      max_curvature={max_curv:.4f}")
        print(f"      min_d_to_bridge={min_dist_to_bridge:.3f}")
        print(f"      peak_flow={peak_flow:.3f}")

        all_continua[f"{s1_name}→{s2_name}"] = {
            "straightness": float(straightness),
            "max_curvature": float(max_curv),
            "min_dist_to_bridge": float(min_dist_to_bridge),
            "peak_flow": float(peak_flow),
        }

    # F2 — Do any continua pass smoothly through the bridge region?
    print("\n  F2 — Bridge passage detection")
    bridge_passages = []
    for name, cont in all_continua.items():
        if cont["min_dist_to_bridge"] < 2.0:
            bridge_passages.append(name)
            print(f"    {name}: passes near bridge "
                  f"(d={cont['min_dist_to_bridge']:.3f}, "
                  f"peak_flow={cont['peak_flow']:.3f})")

    # F3 — Feature-space vs Φ-space: is the interpolation linear in both?
    print("\n  F3 — Geometric linearity (feature-space vs Φ-space)")
    for s1_name, s2_name in pairs:
        i1, i2 = ALL_SYSTEMS.index(s1_name), ALL_SYSTEMS.index(s2_name)

        # Linear in feature space is what we did above
        # Now compute direct Φ-space interpolation (linear in Φ)
        alphas = np.linspace(0, 1, n_steps)
        linear_Phi = np.zeros((n_steps, 4))
        for k, alpha in enumerate(alphas):
            linear_Phi[k] = (1 - alpha) * data["Phi"][i1] + alpha * data["Phi"][i2]

        # How different are the two paths?
        cont_Phi = np.zeros((n_steps, 4))
        for k, alpha in enumerate(alphas):
            X_interp = (1 - alpha) * X0[i1] + alpha * X0[i2]
            cont_Phi[k] = proj.project(X_interp)[0]

        path_deviation = np.mean(np.linalg.norm(cont_Phi - linear_Phi, axis=1))
        print(f"    {s1_name}→{s2_name}: mean Φ-deviation from linear = {path_deviation:.3f}")

    result = {
        "continua": all_continua,
        "bridge_passages": bridge_passages,
    }
    return result


def compute_local_flow_knn(Phi, i, k=4):
    """Local flow magnitude at point i in point cloud Phi."""
    n = len(Phi)
    if n < k + 1:
        return 0.0
    dists = cdist(Phi[i:i+1], Phi)[0]
    idxs = np.argsort(dists)[1:k+1]
    neighbor_center = Phi[idxs].mean(axis=0)
    displacement = np.linalg.norm(neighbor_center - Phi[i])
    mean_dist = dists[idxs].mean()
    return displacement / max(mean_dist, 1e-12)


# =====================================================================
# SECTION G — CATASTROPHE / BIFURCATION DETECTION
# =====================================================================

def section_g_bifurcation(data, trajectories):
    """
    Search for:
    - Discontinuous jumps in Φ trajectories
    - Abrupt flow inversion
    - Topology change under perturbation
    """
    print_sep()
    print("SECTION G: CATASTROPHE / BIFURCATION DETECTION")
    print_sep()

    Phi = data["Phi"]
    flow = data["flow"]
    n = len(ALL_SYSTEMS)

    # G1 — Discontinuous jumps (large ΔΦ between adjacent σ levels)
    print("\n  G1 — Jump detection (phase-transition-like events)")
    jumps = []
    for i in range(n):
        for j in range(1, trajectories.shape[1]):
            delta = np.linalg.norm(trajectories[i, j] - trajectories[i, j-1])
            if delta > 0.5:
                jumps.append({
                    "system": ALL_SYSTEMS[i],
                    "sigma": [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0][j],
                    "delta": float(delta),
                    "flow_before": float(flow[i]),
                })

    jumps.sort(key=lambda x: x["delta"], reverse=True)
    print(f"    Total jump events (ΔΦ > 0.5): {len(jumps)}")
    for j in jumps[:8]:
        print(f"      {j['system']:<24s} σ={j['sigma']:.2f} ΔΦ={j['delta']:.3f} "
              f"flow={j['flow_before']:.2f}")

    # G2 — Abrupt flow inversion
    print("\n  G2 — Flow inversion (drift direction flip)")
    n_sigmas = trajectories.shape[1]
    inversions = []
    for i in range(n):
        directions = []
        for j in range(1, n_sigmas):
            vec = trajectories[i, j] - trajectories[i, j-1]
            norm = np.linalg.norm(vec)
            if norm > 0.1:
                directions.append(vec / norm)
        flips = 0
        for j in range(1, len(directions)):
            dot = np.dot(directions[j-1], directions[j])
            if dot < -0.5:
                flips += 1
        inversions.append(flips)
        if flips > 0:
            print(f"    {ALL_SYSTEMS[i]:<24s} direction_flips={flips}")

    print(f"    Total inversions: {sum(inversions)} across all systems")

    # G3 — Topological change detection
    print("\n  G3 — Topological rank shift")
    rank_shifts = np.zeros(n)
    for i in range(n):
        initial_rank = np.argsort(data["Phi"][i])
        final_rank = np.argsort(trajectories[i, -1])
        rank_shifts[i] = np.sum(initial_rank != final_rank)
    for i in np.argsort(rank_shifts)[-5:][::-1]:
        print(f"    {ALL_SYSTEMS[i]:<24s} rank_shift={int(rank_shifts[i])}")

    r_rank_flow, p_rank_flow = pearsonr(rank_shifts, flow)
    print(f"    rank_shift ~ flow: r={r_rank_flow:.3f}, p={p_rank_flow:.4f}")

    result = {
        "jump_events": jumps,
        "n_jumps": len(jumps),
        "n_inversions": int(sum(inversions)),
        "rank_shifts": {ALL_SYSTEMS[i]: float(rank_shifts[i]) for i in range(n)},
        "rank_shift_flow_corr": {"r": float(r_rank_flow), "p": float(p_rank_flow)},
    }
    return result


# =====================================================================
# SECTION H — NULL GEOMETRY DESTRUCTION
# =====================================================================

def section_h_null_destruction(proj, data):
    """
    Destroy geometry deliberately:
    - Randomize Φ axes
    - Shuffle density field
    - Destroy neighborhood structure
    - Random geodesic rewiring
    Then rerun transition prediction.
    """
    print_sep()
    print("SECTION H: NULL GEOMETRY DESTRUCTION")
    print_sep()

    Phi = data["Phi"]
    flow = data["flow"]
    collapse = data["collapse_vals"]
    n = len(ALL_SYSTEMS)

    # Helper: measure how well a predictor explains collapse
    def predict_collapse(X_pred):
        if np.std(X_pred) == 0 or np.std(collapse) == 0:
            return 0.0
        r, p = pearsonr(np.ravel(X_pred), collapse)
        return float(r) if not np.isnan(r) else 0.0

    baseline_r = predict_collapse(flow)

    # H1 — Shuffle each Φ axis independently
    print(f"\n  H1 — Axis randomization (baseline collapse ~ flow: r={baseline_r:.3f})")
    null_r_axis = []
    for _ in range(100):
        Phi_null = Phi.copy()
        for j in range(4):
            np.random.shuffle(Phi_null[:, j])
        # Recompute flow in shuffled Φ-space
        flow_null = np.array([compute_local_flow_knn(Phi_null, i) for i in range(n)])
        null_r_axis.append(predict_collapse(flow_null))
    print(f"    After axis shuffle: mean r={np.mean(null_r_axis):.3f} ± "
          f"{np.std(null_r_axis):.3f}")

    # H2 — Shuffle the flow field itself
    print(f"\n  H2 — Flow field shuffling")
    null_r_flow = []
    for _ in range(100):
        flow_shuffled = flow.copy()
        np.random.shuffle(flow_shuffled)
        null_r_flow.append(predict_collapse(flow_shuffled))
    print(f"    After flow shuffle: mean r={np.mean(null_r_flow):.3f} ± "
          f"{np.std(null_r_flow):.3f}")

    # H3 — Randomize the feature matrix directly
    print(f"\n  H3 — Feature matrix randomization")
    feat_df = pd.read_csv(OUT / "clustering_feature_matrix.csv")
    feat_df = feat_df[feat_df["system"].isin(ALL_SYSTEMS)].set_index("system").loc[ALL_SYSTEMS]
    X0 = feat_df[FEATURE_NAMES].values.astype(float)
    null_r_feat = []
    for _ in range(50):
        X_null = X0.copy()
        for j in range(X0.shape[1]):
            np.random.shuffle(X_null[:, j])
        Phi_null = proj.project(X_null)
        flow_null = np.array([compute_local_flow_knn(Phi_null, i) for i in range(n)])
        null_r_feat.append(predict_collapse(flow_null))
    print(f"    After feature shuffle: mean r={np.mean(null_r_feat):.3f} ± "
          f"{np.std(null_r_feat):.3f}")

    # H4 — Randomize nearest-neighbor graph (geodesic rewiring)
    print(f"\n  H4 — Geodesic graph rewiring")
    null_r_geo = []
    for _ in range(100):
        Phi_null = Phi.copy()
        # Add random Gaussian noise to each coordinate
        Phi_null += np.random.normal(0, 0.5, Phi.shape)
        flow_null = np.array([compute_local_flow_knn(Phi_null, i) for i in range(n)])
        null_r_geo.append(predict_collapse(flow_null))
    print(f"    After geodesic noise: mean r={np.mean(null_r_geo):.3f} ± "
          f"{np.std(null_r_geo):.3f}")

    # H5 — Density field randomization
    print(f"\n  H5 — Density field shuffling")
    null_r_dens = []
    for _ in range(100):
        dens_shuffled = data["dens"].copy()
        np.random.shuffle(dens_shuffled)
        pred = dens_shuffled
        null_r_dens.append(predict_collapse(pred))
    print(f"    After density shuffle: mean r={np.mean(null_r_dens):.3f} ± "
          f"{np.std(null_r_dens):.3f}")

    # H6 — Full destruction: all sources of structure removed
    print(f"\n  H6 — Complete geometry destruction")
    null_r_all = []
    for _ in range(50):
        Phi_null = Phi.copy()
        for j in range(4):
            np.random.shuffle(Phi_null[:, j])
        # Also add noise
        Phi_null += np.random.normal(0, 0.5, Phi_null.shape)
        flow_null = np.array([compute_local_flow_knn(Phi_null, i) for i in range(n)])
        null_r_all.append(predict_collapse(flow_null))
    print(f"    Full destruction: mean r={np.mean(null_r_all):.3f} ± "
          f"{np.std(null_r_all):.3f}")

    # Summary: is the real flow fundamentally better than null?
    print(f"\n  --- Null Destruction Summary ---")
    print(f"    {'Source':<30s}  {'mean r':>8s}  {'std r':>8s}  {'vs real':>8s}")
    print(f"    {'-'*56}")
    print(f"    {'REAL flow':<30s}  {baseline_r:>+8.3f}  {'':>8s}  {'—':>8s}")
    print(f"    {'Axis shuffle':<30s}  {np.mean(null_r_axis):>+8.3f}  "
          f"{np.std(null_r_axis):>8.4f}  {baseline_r - np.mean(null_r_axis):>+8.3f}")
    print(f"    {'Flow shuffle':<30s}  {np.mean(null_r_flow):>+8.3f}  "
          f"{np.std(null_r_flow):>8.4f}  {baseline_r - np.mean(null_r_flow):>+8.3f}")
    print(f"    {'Feature shuffle':<30s}  {np.mean(null_r_feat):>+8.3f}  "
          f"{np.std(null_r_feat):>8.4f}  {baseline_r - np.mean(null_r_feat):>+8.3f}")
    print(f"    {'Geodesic noise':<30s}  {np.mean(null_r_geo):>+8.3f}  "
          f"{np.std(null_r_geo):>8.4f}  {baseline_r - np.mean(null_r_geo):>+8.3f}")
    print(f"    {'Density shuffle':<30s}  {np.mean(null_r_dens):>+8.3f}  "
          f"{np.std(null_r_dens):>8.4f}  {baseline_r - np.mean(null_r_dens):>+8.3f}")
    print(f"    {'Full destruction':<30s}  {np.mean(null_r_all):>+8.3f}  "
          f"{np.std(null_r_all):>8.4f}  {baseline_r - np.mean(null_r_all):>+8.3f}")

    result = {
        "baseline_flow_collapse_r": float(baseline_r),
        "null_axis_shuffle": {"mean_r": float(np.mean(null_r_axis)),
                              "std_r": float(np.std(null_r_axis))},
        "null_flow_shuffle": {"mean_r": float(np.mean(null_r_flow)),
                              "std_r": float(np.std(null_r_flow))},
        "null_feature_shuffle": {"mean_r": float(np.mean(null_r_feat)),
                                 "std_r": float(np.std(null_r_feat))},
        "null_geodesic_noise": {"mean_r": float(np.mean(null_r_geo)),
                                "std_r": float(np.std(null_r_geo))},
        "null_density_shuffle": {"mean_r": float(np.mean(null_r_dens)),
                                 "std_r": float(np.std(null_r_dens))},
        "null_full_destruction": {"mean_r": float(np.mean(null_r_all)),
                                  "std_r": float(np.std(null_r_all))},
    }
    return result


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("=" * 70)
    print("T028: TRANSITION MANIFOLD DYNAMICS")
    print("\"Is the bridge region an actual dynamical transition manifold,")
    print(" or merely a sparse geometric artifact?\"")
    print("=" * 70)

    proj = EmergenceProjector()
    data = load_all()
    flow = data["flow"]

    # Section A — Dynamic trajectories
    sec_a, trajectories, drifts, velocities = section_a_trajectories(proj, data)

    # Section B — Basin dynamics
    sec_b = section_b_basin_dynamics(proj, data, trajectories)

    # Section C — Stability tensor
    sec_c, tensors = section_c_stability_tensor(proj, data)

    # Section D — Geodesic analysis
    sec_d = section_d_geodesic(data)

    # Section E — Temporal flow
    sec_e, flow_evolution = section_e_temporal_flow(proj, data)

    # Section F — Synthetic continua
    sec_f = section_f_synthetic_continuation(proj, data)

    # Section G — Bifurcation detection
    sec_g = section_g_bifurcation(data, trajectories)

    # Section H — Null destruction
    sec_h = section_h_null_destruction(proj, data)

    # === FINAL VERDICT ===
    print_sep()
    print("T028 FINAL VERDICT — Is the bridge a transition manifold?")
    print_sep()

    drift_r = sec_a["drift_flow_corr"]["r"]
    drift_p = sec_a["drift_flow_corr"]["p"]
    escape_r = sec_b["basin_escape_flow_corr"]["r"]
    cross_r = sec_b["bridge_crossing_flow_corr"]["r"]
    stab_r = sec_c["stability_flow_corr"]["r"]
    lyap_r = sec_c["lyapunov_flow_corr"]["r"]
    between_r = sec_d["betweenness_flow_corr"]["r"]
    is_corridor = sec_d["is_corridor"]
    persistence_sigma = sec_e["persistence_sigma"]
    ranks_stable = sec_e["ranks_stable"]
    n_jumps = sec_g["n_jumps"]
    n_inv = sec_g["n_inversions"]
    null_diff = sec_h["baseline_flow_collapse_r"] - sec_h["null_full_destruction"]["mean_r"]

    criteria = [
        ("A: Drift correlates with flow (p<0.05)",
         drift_p < 0.05, f"r={drift_r:.3f}, p={drift_p:.4f}"),
        ("B: Basin escape correlates with flow (p<0.05)",
         escape_r > 0.3, f"r={escape_r:.3f}"),
        ("B: Bridge crossing correlates with flow",
         cross_r > 0.3, f"r={cross_r:.3f}"),
        ("C: Stability correlates with flow",
         stab_r > 0.3, f"r={stab_r:.3f}"),
        ("D: Bridge is transit corridor",
         is_corridor, f"{'YES' if is_corridor else 'NO'}"),
        ("D: Betweenness correlates with flow",
         between_r > 0.3, f"r={between_r:.3f}"),
        ("E: Flow ranks stable under perturbation",
         ranks_stable, f"{'STABLE' if ranks_stable else 'LOST'}"),
        ("H: Null destruction breaks prediction",
         null_diff > 0.2, f"real - null = {null_diff:.3f}"),
    ]

    print(f"\n  {'Criterion':<48s}  {'Status':>8s}  {'Evidence':>30s}")
    print(f"  {'-'*88}")
    for name, passed, evidence in criteria:
        status = "✓" if passed else "✗"
        print(f"  {name:<48s}  {status:>8s}  {evidence:>30s}")

    n_passed = sum(1 for _, p, _ in criteria if p)
    n_total = len(criteria)

    print(f"\n  Passed: {n_passed}/{n_total}")
    print(f"  Jumps detected: {n_jumps}, Inversions: {n_inv}")

    is_dynamical = (drift_p < 0.05 and is_corridor and ranks_stable and null_diff > 0.2)
    is_partial = (drift_p < 0.05 and (is_corridor or ranks_stable))

    print_sep()
    if is_dynamical:
        print("  VERDICT: BRIDGE IS A GENUINE TRANSITION MANIFOLD ✓")
        print("  Trajectories converge systematically, bridge acts as transit")
        print("  corridor, flow field is causal (null destruction breaks it).")
    elif is_partial:
        print("  VERDICT: BRIDGE IS PARTIALLY DYNAMICAL")
        print("  Some dynamical tests pass, but the manifold signal is")
        print("  not universally strong. Bridge may be geometric sparsity")
        print("  with partial dynamical relevance.")
    else:
        print("  VERDICT: BRIDGE IS DESCRIPTIVE GEOMETRY ONLY ✗")
        print("  Dynamical tests fail. The bridge is a sparse geometric")
        print("  artifact, not a dynamical transition manifold.")

    print_sep()

    # Save all results
    all_results = {
        "section_a_trajectories": sec_a,
        "section_b_basin_dynamics": sec_b,
        "section_c_stability_tensor": sec_c,
        "section_d_geodesic": sec_d,
        "section_e_temporal_flow": sec_e,
        "section_f_synthetic_continua": sec_f,
        "section_g_bifurcation": sec_g,
        "section_h_null_destruction": sec_h,
        "final_verdict": {
            "criteria": {f"C{i+1}": {"name": n, "passed": p, "evidence": e}
                         for i, (n, p, e) in enumerate(criteria)},
            "n_passed": n_passed,
            "n_total": n_total,
            "is_dynamical": is_dynamical,
            "is_partial": is_partial,
        }
    }

    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)): return int(obj)
            if isinstance(obj, (np.floating,)): return float(obj)
            if isinstance(obj, (np.bool_,)): return bool(obj)
            if isinstance(obj, np.ndarray): return obj.tolist()
            return super().default(obj)

    with open(OUT / "t028_transition_manifold_results.json", "w") as f:
        json.dump(all_results, f, indent=2, cls=NpEncoder)

    # Save key numerical data
    np.save(OUT / "t028_stability_tensor.npy", tensors)
    np.save(OUT / "t028_trajectories.npy", trajectories)

    print(f"T028 complete. Results saved to:")
    print(f"  {OUT / 't028_transition_manifold_results.json'}")
    print(f"  {OUT / 't028_stability_tensor.npy'}")
    print(f"  {OUT / 't028_trajectories.npy'}")
    print()


if __name__ == "__main__":
    main()
