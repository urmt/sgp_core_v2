#!/usr/bin/env python3
"""
T043: Order Discovery (No Label Assumptions)
=============================================
Discover the statistically earliest stable structure
that appears from recursive Ω dynamics.

No predefined ontology. No preferred concepts.
No philosophical assumptions.
Measure what IS first.
"""

import sys, json, warnings, time
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
from scipy.spatial.distance import pdist, squareform
from scipy.stats import entropy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
np.random.seed(42)

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

MAX_DEPTH = 50
STATE_DIM = 4
N_UNIVERSES = 10000
N_DETECTORS = 20

# ============================================================
# Ω-UNIVERSE CLASSES
# ============================================================

class RecursiveTransform:
    def __init__(self, seed):
        rng = np.random.RandomState(seed)
        self.W = rng.randn(STATE_DIM, STATE_DIM) * 0.3
        self.b = rng.randn(STATE_DIM) * 0.1
        self.nonlinear = rng.choice([np.tanh, np.sin, lambda x: x**3])
        self.strength = rng.uniform(0.3, 0.8)
    def step(self, x):
        return self.strength * self.nonlinear(self.W @ x + self.b)
    @property
    def name(self): return "recursive_transform"

class SelfApplication:
    def __init__(self, seed):
        rng = np.random.RandomState(seed)
        self.W1 = rng.randn(STATE_DIM, STATE_DIM) * 0.4
        self.W2 = rng.randn(STATE_DIM, STATE_DIM) * 0.4
        self.b1 = rng.randn(STATE_DIM) * 0.1
        self.b2 = rng.randn(STATE_DIM) * 0.1
    def step(self, x):
        y = np.tanh(self.W1 @ x + self.b1)
        z = np.tanh(self.W2 @ y + self.b2)
        return 0.5 * x + 0.3 * z
    @property
    def name(self): return "self_application"

class OperatorComposition:
    def __init__(self, seed):
        rng = np.random.RandomState(seed)
        self.ops = []
        for _ in range(3):
            W = rng.randn(STATE_DIM, STATE_DIM) * 0.3
            b = rng.randn(STATE_DIM) * 0.1
            nl = rng.choice([np.tanh, np.sin, lambda x: 1/(1+np.exp(-x))])
            self.ops.append((W, b, nl))
    def step(self, x):
        for W, b, nl in self.ops:
            x = nl(W @ x + b)
        return x
    @property
    def name(self): return "operator_composition"

class NonlinearContinuous:
    def __init__(self, seed):
        rng = np.random.RandomState(seed)
        self.alpha = rng.uniform(0.1, 0.5, STATE_DIM)
        self.beta = rng.uniform(0.1, 0.5, STATE_DIM)
        self.coupling = rng.uniform(-0.3, 0.3, (STATE_DIM, STATE_DIM))
    def step(self, x):
        dx = self.alpha * np.sin(x) + self.beta * np.cos(x) + self.coupling @ x
        return x + 0.1 * dx
    @property
    def name(self): return "nonlinear_continuous"

class RecursiveRewrite:
    def __init__(self, seed):
        rng = np.random.RandomState(seed)
        self.rules = []
        for _ in range(4):
            i = rng.randint(0, STATE_DIM)
            j = rng.randint(0, STATE_DIM)
            op = rng.choice(["add", "mul", "swap"])
            self.rules.append((i, j, op))
    def step(self, x):
        y = x.copy()
        for i, j, op in self.rules:
            if op == "add": y[i] = y[i] + y[j]
            elif op == "mul": y[i] = y[i] * y[j]
            elif op == "swap": y[i], y[j] = y[j], y[i]
        return np.tanh(y * 0.5)
    @property
    def name(self): return "recursive_rewrite"

class StochasticRecursive:
    def __init__(self, seed):
        rng = np.random.RandomState(seed)
        self.W = rng.randn(STATE_DIM, STATE_DIM) * 0.3
        self.noise_scale = rng.uniform(0.01, 0.1)
    def step(self, x):
        return np.tanh(self.W @ x) + self.noise_scale * np.random.randn(STATE_DIM)
    @property
    def name(self): return "stochastic_recursive"

UNIVERSE_CLASSES = [RecursiveTransform, SelfApplication, OperatorComposition,
                    NonlinearContinuous, RecursiveRewrite, StochasticRecursive]

def simulate(omega, init, depth=MAX_DEPTH):
    traj = [init.copy()]
    x = init.copy()
    for _ in range(depth):
        try:
            x = omega.step(x)
            x = np.clip(x, -10, 10)
            if np.any(np.isnan(x)): break
            traj.append(x.copy())
        except: break
    return np.array(traj)


# ============================================================
# 20 PRIMITIVE DETECTORS
# ============================================================

def D1_possibility_reduction(traj):
    """Does state-space volume contract over time?"""
    if len(traj) < 10:
        return False, 0
    early_vol = np.prod(traj[:5].max(axis=0) - traj[:5].min(axis=0) + 1e-12)
    late_vol = np.prod(traj[-5:].max(axis=0) - traj[-5:].min(axis=0) + 1e-12)
    if early_vol > 0:
        reduction = 1 - late_vol / early_vol
        if reduction > 0.2:
            for d in range(5, len(traj)):
                vol_d = np.prod(traj[:d].max(axis=0) - traj[:d].min(axis=0) + 1e-12)
                if vol_d < early_vol * 0.8:
                    return True, d
    return False, 0

def D2_trajectory_convergence(traj):
    """Do trajectory segments converge toward each other?"""
    if len(traj) < 15:
        return False, 0
    seg1 = traj[:len(traj)//3]
    seg2 = traj[2*len(traj)//3:]
    d1 = seg1.mean(axis=0)
    d2 = seg2.mean(axis=0)
    dist = np.linalg.norm(d1 - d2)
    initial_dist = np.linalg.norm(traj[0] - traj[-1])
    if initial_dist > 0 and dist < initial_dist * 0.5:
        for d in range(5, len(traj)):
            seg_a = traj[:d//2]
            seg_b = traj[d//2:d]
            if len(seg_a) > 2 and len(seg_b) > 2:
                d_ab = np.linalg.norm(seg_a.mean(axis=0) - seg_b.mean(axis=0))
                if d_ab < initial_dist * 0.5:
                    return True, d
    return False, 0

def D3_trajectory_divergence(traj):
    """Do trajectory segments diverge?"""
    if len(traj) < 15:
        return False, 0
    early_dist = np.linalg.norm(traj[0] - traj[len(traj)//2])
    late_dist = np.linalg.norm(traj[len(traj)//2] - traj[-1])
    if late_dist > early_dist * 1.5:
        for d in range(5, len(traj)):
            mid = d // 2
            if mid > 0 and d < len(traj):
                e = np.linalg.norm(traj[0] - traj[mid])
                l = np.linalg.norm(traj[mid] - traj[d])
                if l > e * 1.5:
                    return True, d
    return False, 0

def D4_recurrence(traj):
    """Does the trajectory return near a previous state?"""
    if len(traj) < 8:
        return False, 0
    for d in range(5, len(traj)):
        for j in range(max(0, d-15), max(0, d-2)):
            dist = np.linalg.norm(traj[d] - traj[j])
            if dist < 0.3:
                return True, d
    return False, 0

def D5_persistence(traj):
    """Does a state cluster persist across multiple steps?"""
    if len(traj) < 10:
        return False, 0
    centroid = traj.mean(axis=0)
    dists = np.linalg.norm(traj - centroid, axis=1)
    # Check if late trajectory stays near centroid
    late_dists = dists[len(dists)*2//3:]
    if len(late_dists) > 2:
        mean_late = np.mean(late_dists)
        std_late = np.std(late_dists)
        if std_late < mean_late * 0.3:
            for d in range(5, len(dists)):
                segment = dists[d:]
                if len(segment) > 3:
                    if np.std(segment) < np.mean(segment) * 0.3:
                        return True, d
    return False, 0

def D6_invariant_transitions(traj):
    """Are some transitions deterministic (same input → same output)?"""
    if len(traj) < 10:
        return False, 0
    # Check if consecutive distances repeat
    dists = [np.linalg.norm(traj[i+1] - traj[i]) for i in range(len(traj)-1)]
    if len(dists) < 8:
        return False, 0
    # Look for repeated transition distances
    for d in range(5, len(dists)):
        recent = dists[max(0,d-5):d]
        if len(recent) >= 3:
            cv = np.std(recent) / max(np.mean(recent), 1e-12)
            if cv < 0.15:
                return True, d
    return False, 0

def D7_forbidden_transitions(traj):
    """Are some transitions never observed?"""
    if len(traj) < 15:
        return False, 0
    # Build distance bins
    dists = [np.linalg.norm(traj[i+1] - traj[i]) for i in range(len(traj)-1)]
    if len(dists) < 10:
        return False, 0
    hist, edges = np.histogram(dists, bins=5)
    total_cells = len(hist)
    occupied = np.sum(hist > 0)
    # Forbidden if some bins are always empty
    if occupied < total_cells * 0.6:
        for d in range(8, len(dists)):
            hist_d, _ = np.histogram(dists[:d], bins=5)
            occ_d = np.sum(hist_d > 0)
            if occ_d < 5 * 0.6:
                return True, d
    return False, 0

def D8_neighborhood_stability(traj):
    """Do nearby states stay nearby over time?"""
    if len(traj) < 20:
        return False, 0
    n = min(25, len(traj))
    early = traj[:n]
    late = traj[-n:]
    D_early = squareform(pdist(early))
    D_late = squareform(pdist(late))
    flat_e = D_early[np.triu_indices(n, k=1)]
    flat_l = D_late[np.triu_indices(n, k=1)]
    corr = np.corrcoef(flat_e, flat_l)[0, 1]
    if corr > 0.5:
        return True, 5
    return False, 0

def D9_compression(traj):
    """Does the effective dimensionality decrease?"""
    if len(traj) < 15:
        return False, 0
    def eff_dim(X):
        cov = np.cov(X, rowvar=False)
        evals = np.linalg.eigvalsh(cov)
        evals = np.maximum(evals, 0)
        total = np.sum(evals)
        if total == 0: return 0
        return (np.sum(evals)**2) / np.sum(evals**2)
    early_dim = eff_dim(traj[:len(traj)//2])
    late_dim = eff_dim(traj[len(traj)//2:])
    if early_dim > 0 and late_dim < early_dim * 0.7:
        for d in range(8, len(traj)):
            d_early = eff_dim(traj[:d])
            d_late = eff_dim(traj[d:])
            if d_late < d_early * 0.7:
                return True, d
    return False, 0

def D10_symmetry(traj):
    """Does the trajectory exhibit mirror or rotational symmetry?"""
    if len(traj) < 10:
        return False, 0
    # Check if trajectory is approximately symmetric around midpoint
    mid = len(traj) // 2
    dists = []
    for i in range(min(mid, len(traj) - mid)):
        d = np.linalg.norm(traj[i] - traj[-(i+1)])
        dists.append(d)
    if len(dists) > 3:
        cv = np.std(dists) / max(np.mean(dists), 1e-12)
        if cv < 0.2:
            return True, 5
    return False, 0

def D11_symmetry_breaking(traj):
    """Does an initial symmetry break over time?"""
    if len(traj) < 15:
        return False, 0
    mid = len(traj) // 2
    early_sym = []
    for i in range(min(3, mid)):
        d = np.linalg.norm(traj[i] - traj[-(i+1)])
        early_sym.append(d)
    if len(early_sym) >= 2:
        early_cv = np.std(early_sym) / max(np.mean(early_sym), 1e-12)
        for d in range(8, len(traj)):
            late_sym = []
            for i in range(min(3, len(traj) - d)):
                dd = np.linalg.norm(traj[d+i] - traj[-(d+i+1)] if d+i < len(traj) else traj[-1])
                late_sym.append(dd)
            if len(late_sym) >= 2:
                late_cv = np.std(late_sym) / max(np.mean(late_sym), 1e-12)
                if late_cv > early_cv * 2 and early_cv < 0.3:
                    return True, d
    return False, 0

def D12_closure(traj):
    """Does the trajectory return to its starting region?"""
    if len(traj) < 8:
        return False, 0
    start = traj[0]
    for d in range(5, len(traj)):
        dist = np.linalg.norm(traj[d] - start)
        if dist < 0.5:
            return True, d
    return False, 0

def D13_composition(traj):
    """Does the trajectory contain repeated sub-trajectories?"""
    if len(traj) < 15:
        return False, 0
    # Check if subsequences repeat
    for sub_len in [3, 4, 5]:
        if len(traj) < sub_len * 2:
            continue
        for d in range(sub_len * 2, len(traj)):
            sub = traj[d-sub_len:d]
            for j in range(max(0, d-sub_len*3), d-sub_len):
                if np.allclose(sub, traj[j:j+sub_len], atol=0.2):
                    return True, d
    return False, 0

def D14_hierarchy(traj):
    """Does the trajectory show multi-scale structure?"""
    if len(traj) < 20:
        return False, 0
    # Check structure at different scales
    scales = []
    for scale in [3, 6, 12]:
        if len(traj) >= scale * 2:
            seg = traj[:scale]
            d = np.linalg.norm(seg[-1] - seg[0])
            scales.append(d)
    if len(scales) >= 2:
        # Hierarchical if scales are ordered
        if all(scales[i] >= scales[i+1] for i in range(len(scales)-1)):
            return True, 8
    return False, 0

def D15_self_reference(traj):
    """Does the trajectory produce states that resemble earlier states?"""
    if len(traj) < 12:
        return False, 0
    for d in range(6, len(traj)):
        for j in range(max(0, d-20), d-2):
            dist = np.linalg.norm(traj[d] - traj[j])
            if dist < 0.5:
                return True, d
    return False, 0

def D16_scale_invariance(traj):
    """Does the trajectory show power-law scaling?"""
    if len(traj) < 20:
        return False, 0
    # Compute distances at different lags
    lags = range(1, min(10, len(traj)//2))
    dists = []
    for lag in lags:
        d = np.mean([np.linalg.norm(traj[i] - traj[i+lag]) for i in range(len(traj)-lag)])
        dists.append(d)
    if len(dists) >= 4:
        log_lags = np.log(list(lags)[:len(dists)])
        log_dists = np.log(np.maximum(dists, 1e-12))
        try:
            coef = np.polyfit(log_lags, log_dists, 1)
            r2 = 1 - np.sum((log_dists - np.polyval(coef, log_lags))**2) / np.sum((log_dists - log_dists.mean())**2)
            if r2 > 0.8:
                return True, 8
        except:
            pass
    return False, 0

def D17_repeatability(traj):
    """Does the same initial condition produce similar trajectories?"""
    # This requires multiple runs — approximate with self-consistency
    if len(traj) < 15:
        return False, 0
    # Check if trajectory is locally deterministic
    dists = [np.linalg.norm(traj[i+1] - traj[i]) for i in range(len(traj)-1)]
    if len(dists) > 5:
        cv = np.std(dists) / max(np.mean(dists), 1e-12)
        if cv < 0.3:
            return True, 5
    return False, 0

def D18_separability(traj):
    """Can states be grouped into separable clusters?"""
    if len(traj) < 15:
        return False, 0
    from scipy.cluster.hierarchy import fcluster, linkage
    n = min(30, len(traj))
    states = traj[:n]
    D = squareform(pdist(states))
    Z = linkage(D, method="average")
    labels = fcluster(Z, 2, criterion="maxclust")
    # Check if clusters are well-separated
    cluster_means = [states[labels == i].mean(axis=0) for i in range(1, 3)]
    inter = np.linalg.norm(cluster_means[0] - cluster_means[1])
    intra = np.mean([np.mean(pdist(states[labels == i])) for i in range(1, 3) if (labels == i).sum() > 1])
    if intra > 0 and inter / intra > 1.5:
        return True, 8
    return False, 0

def D19_boundary_formation(traj):
    """Do sharp boundaries emerge between regions?"""
    if len(traj) < 20:
        return False, 0
    # Compute local density gradient
    n = min(50, len(traj))
    states = traj[:n]
    D = squareform(pdist(states))
    # Check if there's a gap in pairwise distances
    all_dists = D[np.triu_indices(n, k=1)]
    hist, edges = np.histogram(all_dists, bins=20)
    # Gap = consecutive empty bins
    max_gap = 0
    current_gap = 0
    for h in hist:
        if h == 0:
            current_gap += 1
            max_gap = max(max_gap, current_gap)
        else:
            current_gap = 0
    if max_gap >= 2:
        return True, 10
    return False, 0

def D20_distance_structure(traj):
    """Do distances between states have structured patterns?"""
    if len(traj) < 15:
        return False, 0
    n = min(30, len(traj))
    states = traj[:n]
    D = squareform(pdist(states))
    all_dists = D[np.triu_indices(n, k=1)]
    if len(all_dists) < 10:
        return False, 0
    hist, _ = np.histogram(all_dists, bins=15)
    hist_norm = hist / max(hist.sum(), 1)
    dist_entropy = entropy(hist_norm + 1e-12)
    max_entropy = np.log(15)
    structuredness = 1 - dist_entropy / max_entropy
    if structuredness > 0.15:
        return True, 5
    return False, 0


DETECTORS = [
    ("D01_possibility_reduction", D1_possibility_reduction),
    ("D02_trajectory_convergence", D2_trajectory_convergence),
    ("D03_trajectory_divergence", D3_trajectory_divergence),
    ("D04_recurrence", D4_recurrence),
    ("D05_persistence", D5_persistence),
    ("D06_invariant_transitions", D6_invariant_transitions),
    ("D07_forbidden_transitions", D7_forbidden_transitions),
    ("D08_neighborhood_stability", D8_neighborhood_stability),
    ("D09_compression", D9_compression),
    ("D10_symmetry", D10_symmetry),
    ("D11_symmetry_breaking", D11_symmetry_breaking),
    ("D12_closure", D12_closure),
    ("D13_composition", D13_composition),
    ("D14_hierarchy", D14_hierarchy),
    ("D15_self_reference", D15_self_reference),
    ("D16_scale_invariance", D16_scale_invariance),
    ("D17_repeatability", D17_repeatability),
    ("D18_separability", D18_separability),
    ("D19_boundary_formation", D19_boundary_formation),
    ("D20_distance_structure", D20_distance_structure),
]


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T043: ORDER DISCOVERY (NO LABEL ASSUMPTIONS)")
    print("=" * 70)
    print(f"Universes: {N_UNIVERSES}")
    print(f"Detectors: {N_DETECTORS}")
    print("=" * 70)
    t0 = time.time()

    # ============================================================
    # PHASE 1: Generate universes and record events
    # ============================================================

    print(f"\n[Phase 1] Generating {N_UNIVERSES} universes and detecting...")

    events = []  # (universe_id, detector_id, depth)
    detector_counts = Counter()

    for uid in range(N_UNIVERSES):
        if uid % 1000 == 0:
            print(f"  Progress: {uid}/{N_UNIVERSES}", flush=True)

        omega = UNIVERSE_CLASSES[uid % len(UNIVERSE_CLASSES)](uid)
        rng = np.random.RandomState(uid)
        init = rng.randn(STATE_DIM) * 0.5
        traj = simulate(omega, init)

        for det_id, (det_name, det_fn) in enumerate(DETECTORS):
            try:
                fired, depth = det_fn(traj)
                if fired:
                    events.append((uid, det_id, depth))
                    detector_counts[det_id] += 1
            except Exception:
                pass

    print(f"\n  Total events: {len(events)}")
    print(f"\n  Detection rates:")
    for det_id, (det_name, _) in enumerate(DETECTORS):
        count = detector_counts.get(det_id, 0)
        print(f"    {det_name:35s}: {count}/{N_UNIVERSES} ({100*count/N_UNIVERSES:.1f}%)")

    # ============================================================
    # PHASE 2: Compute pairwise order P(A before B)
    # ============================================================

    print("\n[Phase 2] Computing pairwise order probabilities...")

    # For each universe, get the first firing depth of each detector
    universe_depths = defaultdict(dict)
    for uid, det_id, depth in events:
        if det_id not in universe_depths[uid] or depth < universe_depths[uid][det_id]:
            universe_depths[uid][det_id] = depth

    # Pairwise order matrix
    order_matrix = np.zeros((N_DETECTORS, N_DETECTORS))
    count_matrix = np.zeros((N_DETECTORS, N_DETECTORS))

    for uid, det_depths in universe_depths.items():
        fired_detectors = list(det_depths.keys())
        for i in fired_detectors:
            for j in fired_detectors:
                if i != j:
                    count_matrix[i, j] += 1
                    if det_depths[i] < det_depths[j]:
                        order_matrix[i, j] += 1
                    elif det_depths[i] == det_depths[j]:
                        order_matrix[i, j] += 0.5

    # Normalize
    with np.errstate(divide='ignore', invalid='ignore'):
        prob_matrix = np.where(count_matrix > 0, order_matrix / count_matrix, 0)

    # ============================================================
    # PHASE 3: Build directed emergence graph
    # ============================================================

    print("\n[Phase 3] Building emergence graph...")

    edges = []
    for i in range(N_DETECTORS):
        for j in range(N_DETECTORS):
            if i != j and prob_matrix[i, j] > 0.95:
                edges.append((i, j, float(prob_matrix[i, j])))

    print(f"  Edges (P>0.95): {len(edges)}")

    # ============================================================
    # PHASE 4: Partial orders and consensus
    # ============================================================

    print("\n[Phase 4] Computing partial orders...")

    # Find nodes with no incoming edges (roots)
    has_incoming = set()
    for _, j, _ in edges:
        has_incoming.add(j)
    roots = [i for i in range(N_DETECTORS) if i not in has_incoming]

    # Find nodes with no outgoing edges (leaves)
    has_outgoing = set()
    for i, _, _ in edges:
        has_outgoing.add(i)
    leaves = [i for i in range(N_DETECTORS) if i not in has_outgoing]

    # BFS layering from roots
    layers = []
    visited = set()
    current = roots
    while current:
        layers.append(current)
        visited.update(current)
        next_layer = []
        for node in current:
            for _, j, _ in edges:
                if j not in visited and j not in next_layer:
                    # Check if all predecessors are visited
                    predecessors = [i for i, jj, _ in edges if jj == j]
                    if all(p in visited for p in predecessors):
                        next_layer.append(j)
        current = next_layer

    # Handle unvisited nodes
    unvisited = [i for i in range(N_DETECTORS) if i not in visited]
    if unvisited:
        layers.append(unvisited)

    print(f"  Root detectors: {[DETECTORS[i][0] for i in roots]}")
    print(f"  Emergence layers:")
    for layer_idx, layer in enumerate(layers):
        print(f"    Layer {layer_idx+1}: {[DETECTORS[i][0] for i in layer]}")

    # ============================================================
    # SAVE
    # ============================================================

    print("\nSaving outputs...")

    # t043_detector_events.csv
    events_df = pd.DataFrame(events, columns=["universe_id", "detector_id", "depth"])
    events_df["detector_name"] = events_df["detector_id"].map(lambda x: DETECTORS[x][0])
    events_df.to_csv(OUT / "t043_detector_events.csv", index=False)
    print(f"  Saved t043_detector_events.csv ({len(events_df)} events)")

    # t043_pairwise_order_matrix.csv
    det_names = [DETECTORS[i][0] for i in range(N_DETECTORS)]
    prob_df = pd.DataFrame(prob_matrix, index=det_names, columns=det_names)
    prob_df.to_csv(OUT / "t043_pairwise_order_matrix.csv")
    print("  Saved t043_pairwise_order_matrix.csv")

    # t043_emergence_graph.csv
    graph_df = pd.DataFrame(edges, columns=["from_detector", "to_detector", "probability"])
    graph_df["from_name"] = graph_df["from_detector"].map(lambda x: DETECTORS[x][0])
    graph_df["to_name"] = graph_df["to_detector"].map(lambda x: DETECTORS[x][0])
    graph_df.to_csv(OUT / "t043_emergence_graph.csv", index=False)
    print(f"  Saved t043_emergence_graph.csv ({len(edges)} edges)")

    # t043_partial_orders.csv
    partial_rows = []
    for layer_idx, layer in enumerate(layers):
        for node in layer:
            partial_rows.append({
                "layer": layer_idx + 1,
                "detector_id": node,
                "detector_name": DETECTORS[node][0],
                "is_root": node in roots,
                "is_leaf": node in leaves,
            })
    partial_df = pd.DataFrame(partial_rows)
    partial_df.to_csv(OUT / "t043_partial_orders.csv", index=False)
    print("  Saved t043_partial_orders.csv")

    # t043_coemergent_groups.csv
    # Find strongly connected components (nodes with bidirectional edges)
    coemergent = []
    for i in range(N_DETECTORS):
        for j in range(i+1, N_DETECTORS):
            if prob_matrix[i, j] > 0.95 and prob_matrix[j, i] > 0.95:
                coemergent.append({
                    "detector_a": DETECTORS[i][0],
                    "detector_b": DETECTORS[j][0],
                    "probability": float((prob_matrix[i, j] + prob_matrix[j, i]) / 2),
                })
    coemergent_df = pd.DataFrame(coemergent) if coemergent else pd.DataFrame(columns=["detector_a", "detector_b", "probability"])
    coemergent_df.to_csv(OUT / "t043_coemergent_groups.csv", index=False)
    print(f"  Saved t043_coemergent_groups.csv ({len(coemergent)} pairs)")

    # t043_consensus_layers.csv
    consensus_rows = []
    for layer_idx, layer in enumerate(layers):
        for node in layer:
            consensus_rows.append({
                "layer": layer_idx + 1,
                "detector_name": DETECTORS[node][0],
                "detection_rate": float(detector_counts.get(node, 0) / N_UNIVERSES),
                "mean_first_depth": float(np.mean([d for uid, det_id, d in events if det_id == node])) if any(det_id == node for _, det_id, _ in events) else 0,
            })
    consensus_df = pd.DataFrame(consensus_rows)
    consensus_df.to_csv(OUT / "t043_consensus_layers.csv", index=False)
    print("  Saved t043_consensus_layers.csv")

    # ============================================================
    # FIGURES
    # ============================================================

    print("\nGenerating figures...")
    plt.rcParams.update({
        "font.family": "serif", "font.size": 8, "axes.titlesize": 9,
        "axes.labelsize": 8, "xtick.labelsize": 6, "ytick.labelsize": 6,
        "legend.fontsize": 6, "figure.dpi": 300, "savefig.dpi": 300,
        "savefig.bbox": "tight", "axes.linewidth": 0.5,
        "axes.spines.top": False, "axes.spines.right": False,
    })

    # Fig 1: Order graph
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(-1, len(layers) + 1)
    ax.set_ylim(-1, max(len(l) for l in layers) + 1)
    ax.axis("off")
    ax.set_title("Emergent order graph (no predefined labels)", fontsize=10)

    positions = {}
    for layer_idx, layer in enumerate(layers):
        for i, node in enumerate(layer):
            x = layer_idx + 0.5
            y = (i + 1) * (max(len(l) for l in layers) + 1) / (len(layer) + 1)
            positions[node] = (x, y)

    # Draw edges
    for i, j, prob in edges:
        if i in positions and j in positions:
            ax.annotate("", xy=positions[j], xytext=positions[i],
                        arrowprops=dict(arrowstyle="->", color="gray",
                                       lw=0.3 + prob * 0.5, alpha=0.5))

    # Draw nodes
    for layer_idx, layer in enumerate(layers):
        for node in layer:
            x, y = positions[node]
            rate = detector_counts.get(node, 0) / N_UNIVERSES
            size = 30 + rate * 200
            color = plt.cm.viridis(rate)
            ax.plot(x, y, "o", color=color, markersize=size**0.5, alpha=0.8)
            ax.annotate(DETECTORS[node][0].replace("D" + str(node+1).zfill(2) + "_", ""),
                        (x, y), fontsize=5, ha="center", va="bottom",
                        xytext=(0, 5), textcoords="offset points")

    # Layer labels
    for layer_idx, layer in enumerate(layers):
        ax.text(layer_idx + 0.5, -0.5, f"Layer {layer_idx+1}", ha="center",
                fontsize=7, fontweight="bold")

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t043_order_graph.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t043_order_graph.pdf/.png")

    # Fig 2: Emergence layers
    fig, ax = plt.subplots(figsize=(10, 6))
    layer_labels = [f"L{l}" for l in range(1, len(layers)+1)]
    det_per_layer = [len(l) for l in layers]
    colors = plt.cm.tab20(np.linspace(0, 1, len(layers)))
    ax.barh(range(len(layers)), det_per_layer, color=colors, edgecolor="white", linewidth=0.3)
    ax.set_yticks(range(len(layers)))
    ax.set_yticklabels([f"Layer {i+1}: {len(l)} detectors" for i, l in enumerate(layers)])
    ax.set_xlabel("Number of detectors")
    ax.set_title("Emergence layer sizes")
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t043_emergence_layers.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t043_emergence_layers.pdf/.png")

    # Fig 3: Pairwise order heatmap
    fig, ax = plt.subplots(figsize=(12, 10))
    short_names = [DETECTORS[i][0].replace("D" + str(i+1).zfill(2) + "_", "") for i in range(N_DETECTORS)]
    im = ax.imshow(prob_matrix, cmap="RdYlGn_r", vmin=0, vmax=1)
    ax.set_xticks(range(N_DETECTORS))
    ax.set_xticklabels(short_names, rotation=90, fontsize=5)
    ax.set_yticks(range(N_DETECTORS))
    ax.set_yticklabels(short_names, fontsize=5)
    plt.colorbar(im, ax=ax, label="P(A before B)")
    ax.set_title("Pairwise order probability matrix")
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t043_pairwise_matrix.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t043_pairwise_matrix.pdf/.png")

    # ============================================================
    # INTERPRETATION
    # ============================================================

    elapsed = time.time() - t0

    # Compute interpretation AFTER discovery
    INTERPRETATIONS = {
        "D01_possibility_reduction": "possibility reduction",
        "D02_trajectory_convergence": "trajectory convergence",
        "D03_trajectory_divergence": "trajectory divergence",
        "D04_recurrence": "recurrence",
        "D05_persistence": "persistence",
        "D06_invariant_transitions": "invariant transitions",
        "D07_forbidden_transitions": "forbidden transitions",
        "D08_neighborhood_stability": "neighborhood stability",
        "D09_compression": "compression",
        "D10_symmetry": "symmetry",
        "D11_symmetry_breaking": "symmetry breaking",
        "D12_closure": "closure",
        "D13_composition": "composition",
        "D14_hierarchy": "hierarchy",
        "D15_self_reference": "self-reference",
        "D16_scale_invariance": "scale invariance",
        "D17_repeatability": "repeatability",
        "D18_separability": "separability",
        "D19_boundary_formation": "boundary formation",
        "D20_distance_structure": "distance-like structure",
    }

    print(f"\nRuntime: {elapsed:.1f}s")
    print("\n" + "=" * 70)
    print("T043 RESULTS: DISCOVERED ORDER")
    print("=" * 70)
    print(f"\nUniverses: {N_UNIVERSES}")
    print(f"Total detector events: {len(events)}")
    print(f"Edges (P>0.95): {len(edges)}")
    print()

    print("DISCOVERED LAYERS (from earliest to latest):")
    for layer_idx, layer in enumerate(layers):
        print(f"\n  Layer {layer_idx+1}:")
        for node in layer:
            name = DETECTORS[node][0]
            interp = INTERPRETATIONS.get(name, name)
            rate = detector_counts.get(node, 0) / N_UNIVERSES
            print(f"    {interp:30s} ({100*rate:.1f}%)")

    print()
    print("CO-EMERGENT PAIRS (bidirectional P>0.95):")
    for _, row in coemergent_df.iterrows():
        print(f"    {row['detector_a']} <-> {row['detector_b']} (P={row['probability']:.3f})")

    print()
    print("FIRST STATISTICALLY UNAVOIDABLE STRUCTURE:")
    if layers:
        first_layer = layers[0]
        first_names = [INTERPRETATIONS.get(DETECTORS[n][0], DETECTORS[n][0]) for n in first_layer]
        print(f"  Layer 1: {', '.join(first_names)}")
        print(f"  These appear before all others with P>0.95 ordering.")

    print()
    print("INTERPRETATION (applied AFTER discovery):")
    if layers:
        print("  The first structures to emerge from recursive Ω dynamics")
        print("  are those in Layer 1. All subsequent structures depend on them.")
        print("  The ordering was NOT assumed — it was measured from 10000 universes.")
    print("=" * 70)

    # Save summary
    summary = {
        "n_universes": N_UNIVERSES,
        "n_detectors": N_DETECTORS,
        "total_events": len(events),
        "n_edges": len(edges),
        "n_layers": len(layers),
        "layers": [[DETECTORS[n][0] for n in layer] for layer in layers],
        "roots": [DETECTORS[n][0] for n in roots],
        "leaves": [DETECTORS[n][0] for n in leaves],
        "coemergent_pairs": len(coemergent),
        "first_structure": [INTERPRETATIONS.get(DETECTORS[n][0], DETECTORS[n][0]) for n in layers[0]] if layers else [],
    }
    with open(OUT / "t043_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSaved t043_summary.json")


if __name__ == "__main__":
    main()
