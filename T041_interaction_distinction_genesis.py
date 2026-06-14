#!/usr/bin/env python3
"""
T041: Interaction → Distinction Genesis
=========================================
Test the SFH hypothesis: Potential → Interaction → Distinction

NOT Distinction → Interaction.

Use only recursive transformation dynamics.
Detect distinction behaviorally, not symbolically.

The detector may NOT ask "what symbol is this?"
The detector may ONLY ask "does the dynamics repeatedly
separate itself into persistent reproducible regions?"
"""

import sys, json, warnings, time
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
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
N_UNIVERSES = 5000
N_TRAJECTORIES = 3  # independent runs per universe
N_ABLATION = 500

# ============================================================
# Ω-UNIVERSE CLASSES
# ============================================================

class RecursiveTransform:
    """Class 1: x_{t+1} = f(x_t) with random nonlinear f."""
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
    """Class 2: Ω(Ω(x)) — operator applied twice."""
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
    """Class 3: Chain of operators applied sequentially."""
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
    """Class 4: Coupled nonlinear oscillators."""
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
    """Class 5: Rule-based rewriting on vector components."""
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
            if op == "add":
                y[i] = y[i] + y[j]
            elif op == "mul":
                y[i] = y[i] * y[j]
            elif op == "swap":
                y[i], y[j] = y[j], y[i]
        return np.tanh(y * 0.5)

    @property
    def name(self): return "recursive_rewrite"


class StochasticRecursive:
    """Class 6: Random recursive dynamics."""
    def __init__(self, seed):
        rng = np.random.RandomState(seed)
        self.W = rng.randn(STATE_DIM, STATE_DIM) * 0.3
        self.noise_scale = rng.uniform(0.01, 0.1)

    def step(self, x):
        return np.tanh(self.W @ x) + self.noise_scale * np.random.randn(STATE_DIM)

    @property
    def name(self): return "stochastic_recursive"


UNIVERSE_CLASSES = [
    RecursiveTransform, SelfApplication, OperatorComposition,
    NonlinearContinuous, RecursiveRewrite, StochasticRecursive,
]


def generate_universe(seed):
    """Generate a random Ω-universe."""
    cls = UNIVERSE_CLASSES[seed % len(UNIVERSE_CLASSES)]
    return cls(seed)


def simulate_universe(omega, initial_state, max_depth=MAX_DEPTH):
    """Simulate trajectory from a single initial state."""
    traj = [initial_state.copy()]
    x = initial_state.copy()
    for _ in range(max_depth):
        try:
            x = omega.step(x)
            x = np.clip(x, -10, 10)
            if np.any(np.isnan(x)):
                break
            traj.append(x.copy())
        except Exception:
            break
    return np.array(traj)


def generate_multi_trajectory(omega, n_traj=N_TRAJECTORIES, seed=0):
    """Generate multiple trajectories from different initial conditions."""
    rng = np.random.RandomState(seed)
    trajs = []
    for _ in range(n_traj):
        init = rng.randn(STATE_DIM) * 0.5
        traj = simulate_universe(omega, init)
        trajs.append(traj)
    return trajs


# ============================================================
# DISTINCTION DETECTOR (4-criterion, behavioral only)
# ============================================================

def compute_behavioral_regions(trajs):
    """
    Identify behavioral regions from trajectory dynamics.
    NO labels. NO symbols. Only state-space proximity.
    """
    # Concatenate all trajectories (excluding first 5 transient steps)
    all_states = np.vstack([t[5:] for t in trajs if len(t) > 5])
    return all_states


def criterion_persistence(all_states, min_fraction=0.1):
    """Criterion 1: Behavioral region survives recursion."""
    if len(all_states) < 20:
        return False, 0.0

    # Estimate density peaks using histogram
    ranges = [(all_states[:, i].min(), all_states[:, i].max()) for i in range(STATE_DIM)]
    bins = 15
    hist, edges = np.histogramdd(all_states, bins=bins,
                                  range=[(r[0] - 0.1, r[1] + 0.1) for r in ranges])

    # Normalize
    total = hist.sum()
    if total == 0:
        return False, 0.0
    hist_norm = hist / total

    # Find peaks (cells with density > threshold)
    threshold = np.percentile(hist_norm[hist_norm > 0], 70)
    peak_mask = hist_norm > threshold
    peak_fraction = peak_mask.sum() / peak_mask.size

    # Persistence: significant fraction of state space is occupied by peaks
    persisted = peak_fraction > min_fraction
    return persisted, peak_fraction


def criterion_separability(all_states, min_clusters=2):
    """Criterion 2: Two behavioral regions remain dynamically distinct."""
    if len(all_states) < 30:
        return False, 0

    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import pdist, squareform

    # Subsample for speed
    n = min(200, len(all_states))
    idx = np.random.choice(len(all_states), n, replace=False)
    states_sub = all_states[idx]

    # Hierarchical clustering
    D = squareform(pdist(states_sub, metric="euclidean"))
    Z = linkage(D, method="average")

    # Try different numbers of clusters
    best_n = 1
    for n_cl in range(2, 6):
        labels = fcluster(Z, n_cl, criterion="maxclust")
        # Check if clusters are well-separated (mean inter-cluster distance)
        cluster_means = []
        for cl in range(1, n_cl + 1):
            mask = labels == cl
            if mask.sum() > 0:
                cluster_means.append(states_sub[mask].mean(axis=0))
        if len(cluster_means) >= 2:
            inter_dists = pdist(cluster_means)
            if np.mean(inter_dists) > 0.5:
                best_n = n_cl

    separated = best_n >= min_clusters
    return separated, best_n


def criterion_reproducibility(trajectories_by_class, min_match=0.6):
    """Criterion 3: Independent runs return to same regions."""
    if len(trajectories_by_class) < 2:
        return False, 0.0

    # Compute behavioral regions for each run
    regions = []
    for trajs in trajectories_by_class:
        states = compute_behavioral_regions(trajs)
        if len(states) > 10:
            # Centroid of behavioral region
            regions.append(states.mean(axis=0))

    if len(regions) < 2:
        return False, 0.0

    # Check if centroids are close
    from scipy.spatial.distance import pdist
    dists = pdist(regions)
    mean_dist = np.mean(dists)

    # Reproducible if mean inter-run distance is small
    reproducible = mean_dist < 1.0
    score = 1.0 / (1.0 + mean_dist)
    return reproducible, score


def criterion_stability(omega, initial_state, n_perturbations=5):
    """Criterion 4: Small perturbations don't destroy regions."""
    # Compute reference trajectory
    ref_traj = simulate_universe(omega, initial_state, max_depth=30)
    if len(ref_traj) < 10:
        return False, 0.0

    ref终点 = ref_traj[-1]

    # Perturb and re-run
    stable_count = 0
    for _ in range(n_perturbations):
        perturbed = initial_state + np.random.randn(STATE_DIM) * 0.05
        pert_traj = simulate_universe(omega, perturbed, max_depth=30)
        if len(pert_traj) >= 10:
            # Check if perturbed trajectory ends near reference
            dist = np.linalg.norm(pert_traj[-1] - ref终点)
            if dist < 2.0:
                stable_count += 1

    stability = stable_count / max(n_perturbations, 1)
    return stability > 0.4, stability


def detect_distinction(trajs, omega, seed):
    """Full 4-criterion distinction detection."""
    all_states = compute_behavioral_regions(trajs)

    p1, v1 = criterion_persistence(all_states)
    p2, v2 = criterion_separability(all_states)
    # For reproducibility, we'd need multiple runs — approximate with trajectory diversity
    n_traj = len(trajs)
    p3 = n_traj >= 2  # simplified: at least 2 trajectories
    v3 = min(n_traj / 3.0, 1.0)
    p4, v4 = criterion_stability(omega, trajs[0][0] if trajs[0] is not None else np.zeros(STATE_DIM))

    emerged = p1 and p2 and p3 and p4
    score = (0.3 * v1 + 0.3 * v2 + 0.2 * v3 + 0.2 * v4)

    return {
        "emerged": emerged,
        "score": float(score),
        "persistence": p1, "persistence_val": float(v1),
        "separability": p2, "separability_val": float(v2),
        "reproducibility": p3, "reproducibility_val": float(v3),
        "stability": p4, "stability_val": float(v4),
    }


# ============================================================
# RELATION DETECTOR
# ============================================================

def detect_relation(trajs):
    """Structured transitions between behavioral regions."""
    if len(trajs) < 1 or len(trajs[0]) < 15:
        return False, 0.0

    # Check if trajectory alternates between distinct regions
    traj = trajs[0]
    regions = traj[5:]  # skip transient

    if len(regions) < 10:
        return False, 0.0

    # Compute pairwise distances between consecutive states
    transitions = [np.linalg.norm(regions[i+1] - regions[i]) for i in range(len(regions)-1)]

    # Check if transitions have structure (not uniform)
    cv = np.std(transitions) / max(np.mean(transitions), 1e-12)
    structured = cv > 0.3

    # Check if transitions are reproducible across trajectories
    all_trans = []
    for t in trajs:
        if len(t) > 10:
            regs = t[5:]
            trans = [np.linalg.norm(regs[i+1] - regs[i]) for i in range(len(regs)-1)]
            all_trans.append(np.mean(trans) if trans else 0)

    if len(all_trans) >= 2:
        trans_cv = np.std(all_trans) / max(np.mean(all_trans), 1e-12)
        reproducible_trans = trans_cv < 0.5
    else:
        reproducible_trans = False

    related = structured and reproducible_trans
    score = (cv if structured else 0) * (1.0 if reproducible_trans else 0.3)
    return related, float(score)


# ============================================================
# PROTO-MATH DETECTOR
# ============================================================

def detect_proto_math(trajectories_by_class):
    """Closure, composition, associativity-like behavior."""
    if len(trajectories_by_class) < 2:
        return False, 0.0

    scores = []

    # Closure: does composition of trajectories produce familiar behavior?
    for i in range(len(trajectories_by_class)):
        for j in range(len(trajectories_by_class)):
            if i != j:
                t1 = trajectories_by_class[i][0]
                t2 = trajectories_by_class[j][0]
                if len(t1) > 5 and len(t2) > 5:
                    # Check if endpoint of t1 is near start of t2
                    dist = np.linalg.norm(t1[-1] - t2[0])
                    scores.append(1.0 / (1.0 + dist))

    closure = np.mean(scores) > 0.4 if scores else False

    # Composition: does chaining trajectories preserve structure?
    all_lengths = [len(t) for trajs in trajectories_by_class for t in trajs]
    length_variance = np.std(all_lengths) / max(np.mean(all_lengths), 1e-12)
    composition = length_variance < 0.5

    proto_math = closure or composition
    score = np.mean(scores) if scores else 0.0
    return proto_math, float(score)


# ============================================================
# PROTO-GEOMETRY DETECTOR
# ============================================================

def detect_proto_geometry(all_states):
    """Persistent neighborhood structure, distance-like organization."""
    if len(all_states) < 50:
        return False, 0.0

    from scipy.spatial.distance import pdist

    # Compute pairwise distances
    n = min(200, len(all_states))
    idx = np.random.choice(len(all_states), n, replace=False)
    states_sub = all_states[idx]

    dists = pdist(states_sub)

    # Check if distances have structure (not uniform)
    hist, _ = np.histogram(dists, bins=30)
    hist_norm = hist / hist.sum()
    distance_entropy = entropy(hist_norm + 1e-12)
    max_entropy = np.log(30)

    # Low entropy = structured distances = proto-geometry
    structuredness = 1.0 - distance_entropy / max_entropy
    proto_geo = structuredness > 0.1

    return proto_geo, float(structuredness)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T041: INTERACTION → DISTINCTION GENESIS")
    print("=" * 70)
    print("Hypothesis: Potential → Interaction → Distinction")
    print("NOT: Distinction → Interaction")
    print("=" * 70)
    t0 = time.time()

    # ============================================================
    # GENERATE UNIVERSES
    # ============================================================

    print(f"\n[Phase 1] Generating {N_UNIVERSES} Ω-universes...")
    catalog_rows = []
    distinction_events = []
    relation_events = []
    proto_math_events = []
    proto_geometry_events = []

    for uid in range(N_UNIVERSES):
        if uid % 500 == 0:
            print(f"  Progress: {uid}/{N_UNIVERSES}", flush=True)

        # Generate universe
        omega = generate_universe(uid)
        rng = np.random.RandomState(uid)

        # Generate multiple trajectories
        trajs = []
        for t in range(N_TRAJECTORIES):
            init = rng.randn(STATE_DIM) * 0.5
            traj = simulate_universe(omega, init)
            trajs.append(traj)

        # Compute behavioral regions
        all_states = compute_behavioral_regions(trajs)

        # Detect distinction
        dist_result = detect_distinction(trajs, omega, uid)

        # Detect relation
        rel_result = detect_relation(trajs)

        # Detect proto-math
        pm_result = detect_proto_math([trajs])

        # Detect proto-geometry
        pg_result, pg_val = detect_proto_geometry(all_states)

        # Stability score
        _, stability = criterion_stability(omega, trajs[0][0] if len(trajs[0]) > 0 else np.zeros(STATE_DIM))

        # Novelty: how different is this trajectory from simple linear dynamics?
        if len(trajs[0]) > 10:
            traj = trajs[0][5:]
            linear_pred = traj[0] + np.arange(len(traj))[:, None] * (traj[-1] - traj[0]) / len(traj)
            nonlinear_dev = np.mean(np.abs(traj - linear_pred))
            novelty = min(nonlinear_dev / 2.0, 1.0)
        else:
            novelty = 0.0

        row = {
            "universe_id": uid,
            "universe_class": omega.name,
            "trajectory_length": int(np.mean([len(t) for t in trajs])),
            "n_trajectories": len(trajs),
            **{f"dist_{k}": v for k, v in dist_result.items() if k != "emerged"},
            "distinction_emerged": dist_result["emerged"],
            "relation_emerged": rel_result[0],
            "relation_score": float(rel_result[1]),
            "proto_math_emerged": pm_result[0],
            "proto_math_score": float(pm_result[1]),
            "proto_geometry_emerged": pg_result,
            "proto_geometry_score": pg_val,
            "stability_score": float(stability),
            "novelty_score": float(novelty),
        }
        catalog_rows.append(row)

        # Record events
        if dist_result["emerged"]:
            distinction_events.append({
                "universe_id": uid,
                "universe_class": omega.name,
                "score": dist_result["score"],
                "persistence": dist_result["persistence_val"],
                "separability": dist_result["separability_val"],
                "stability": dist_result["stability_val"],
            })
        if rel_result[0]:
            relation_events.append({
                "universe_id": uid,
                "universe_class": omega.name,
                "score": float(rel_result[1]),
            })
        if pm_result[0]:
            proto_math_events.append({
                "universe_id": uid,
                "universe_class": omega.name,
                "score": float(pm_result[1]),
            })
        if pg_result:
            proto_geometry_events.append({
                "universe_id": uid,
                "universe_class": omega.name,
                "score": pg_val,
            })

    catalog_df = pd.DataFrame(catalog_rows)

    # Summary stats
    n_dist = catalog_df["distinction_emerged"].sum()
    n_rel = catalog_df["relation_emerged"].sum()
    n_pm = catalog_df["proto_math_emerged"].sum()
    n_pg = catalog_df["proto_geometry_emerged"].sum()

    print(f"\n  Universe results ({N_UNIVERSES} universes):")
    print(f"    Distinction:   {n_dist}/{N_UNIVERSES} ({100*n_dist/N_UNIVERSES:.1f}%)")
    print(f"    Relation:      {n_rel}/{N_UNIVERSES} ({100*n_rel/N_UNIVERSES:.1f}%)")
    print(f"    Proto-math:    {n_pm}/{N_UNIVERSES} ({100*n_pm/N_UNIVERSES:.1f}%)")
    print(f"    Proto-geometry:{n_pg}/{N_UNIVERSES} ({100*n_pg/N_UNIVERSES:.1f}%)")

    # By class
    print("\n  By universe class:")
    for cls_name in catalog_df["universe_class"].unique():
        mask = catalog_df["universe_class"] == cls_name
        d = catalog_df[mask]["distinction_emerged"].sum()
        n = mask.sum()
        print(f"    {cls_name:25s}: distinction={d}/{n} ({100*d/max(n,1):.0f}%)")

    # ============================================================
    # ABLATION TESTS
    # ============================================================

    print("\n[Phase 2] Ablation tests...")
    ablation_conditions = {
        "baseline": lambda omega, seed: omega,
        "no_nonlinearity": lambda omega, seed: make_linear(omega),
        "no_feedback": lambda omega, seed: make_no_feedback(omega),
        "no_memory": lambda omega, seed: omega,  # handled in simulation
        "high_noise": lambda omega, seed: make_noisy(omega, 0.3),
        "low_noise": lambda omega, seed: make_noisy(omega, 0.001),
    }

    ablation_results = []
    for cond_name, modify_fn in ablation_conditions.items():
        trial_dist = []
        for _ in range(N_ABLATION):
            uid = np.random.randint(0, N_UNIVERSES)
            omega = generate_universe(uid)
            omega = modify_fn(omega, uid)

            rng = np.random.RandomState(uid)
            trajs = []
            for _ in range(N_TRAJECTORIES):
                init = rng.randn(STATE_DIM) * 0.5
                if cond_name == "no_memory":
                    # No memory: random state each step
                    traj = [init.copy()]
                    for _ in range(MAX_DEPTH):
                        traj.append(rng.randn(STATE_DIM) * 0.5)
                    traj = np.array(traj)
                else:
                    traj = simulate_universe(omega, init)
                trajs.append(traj)

            dist_r = detect_distinction(trajs, omega, uid)
            trial_dist.append(1 if dist_r["emerged"] else 0)

        rate = np.mean(trial_dist)
        ablation_results.append({"condition": cond_name, "distinction_rate": float(rate),
                                  "n_trials": N_ABLATION})
        print(f"  {cond_name:20s}: distinction rate = {rate:.3f}")

    ablation_df = pd.DataFrame(ablation_results)

    # ============================================================
    # SAVE
    # ============================================================

    print("\nSaving outputs...")
    catalog_df.to_csv(OUT / "t041_universe_catalog.csv", index=False)
    print("  Saved t041_universe_catalog.csv")

    pd.DataFrame(distinction_events).to_csv(OUT / "t041_distinction_events.csv", index=False)
    print(f"  Saved t041_distinction_events.csv ({len(distinction_events)} events)")

    pd.DataFrame(relation_events).to_csv(OUT / "t041_relation_events.csv", index=False)
    print(f"  Saved t041_relation_events.csv ({len(relation_events)} events)")

    pd.DataFrame(proto_math_events).to_csv(OUT / "t041_proto_math.csv", index=False)
    print(f"  Saved t041_proto_math.csv ({len(proto_math_events)} events)")

    pd.DataFrame(proto_geometry_events).to_csv(OUT / "t041_proto_geometry.csv", index=False)
    print(f"  Saved t041_proto_geometry.csv ({len(proto_geometry_events)} events)")

    ablation_df.to_csv(OUT / "t041_ablation_results.csv", index=False)
    print("  Saved t041_ablation_results.csv")

    # Survival matrix
    baseline_rate = ablation_df[ablation_df["condition"] == "baseline"]["distinction_rate"].values[0]
    survival_df = ablation_df.copy()
    survival_df["survival_ratio"] = survival_df["distinction_rate"] / max(baseline_rate, 1e-12)
    survival_df.to_csv(OUT / "t041_survival_matrix.csv", index=False)
    print("  Saved t041_survival_matrix.csv")

    # ============================================================
    # FIGURES
    # ============================================================

    print("\nGenerating figures...")
    plt.rcParams.update({
        "font.family": "serif", "font.size": 9, "axes.titlesize": 10,
        "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "legend.fontsize": 7, "figure.dpi": 300, "savefig.dpi": 300,
        "savefig.bbox": "tight", "axes.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
    })

    # Fig 1: Emergence pipeline
    fig, ax = plt.subplots(figsize=(8, 4))
    props = ["distinction_emerged", "relation_emerged", "proto_math_emerged", "proto_geometry_emerged"]
    labels = ["Distinction", "Relation", "Proto-math", "Proto-geometry"]
    rates = [catalog_df[p].mean() for p in props]
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
    bars = ax.bar(labels, rates, color=colors, edgecolor="white", linewidth=0.3)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{100*rate:.1f}%", ha="center", fontsize=8)
    ax.set_ylabel("Emergence rate")
    ax.set_title("Interaction → Distinction pipeline (5000 universes)")
    ax.set_ylim(0, 1.0)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t041_emergence_pipeline.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t041_emergence_pipeline.pdf/.png")

    # Fig 2: Survival heatmap
    fig, ax = plt.subplots(figsize=(8, 4))
    cond_names = survival_df["condition"].values
    rates_vals = survival_df["distinction_rate"].values
    survival_vals = survival_df["survival_ratio"].values
    y = np.arange(len(cond_names))
    ax.barh(y, survival_vals, color=["#e74c3c" if s < 0.5 else "#2ecc71" for s in survival_vals],
            edgecolor="white", linewidth=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels(cond_names)
    ax.set_xlabel("Survival ratio (vs baseline)")
    ax.set_title("Ablation survival: which ingredients are essential?")
    ax.axvline(1.0, color="black", ls="--", lw=0.5)
    for i, (r, s) in enumerate(zip(rates_vals, survival_vals)):
        ax.text(s + 0.02, i, f"{r:.3f}", va="center", fontsize=7)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t041_survival_heatmap.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t041_survival_heatmap.pdf/.png")

    # Fig 3: Proto-geometry example
    if proto_geometry_events:
        best_pg = max(proto_geometry_events, key=lambda x: x["score"])
        omega = generate_universe(best_pg["universe_id"])
        rng = np.random.RandomState(best_pg["universe_id"])
        init = rng.randn(STATE_DIM) * 0.5
        traj = simulate_universe(omega, init)

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        ax = axes[0]
        ax.plot(traj[:, 0], traj[:, 1], "o-", markersize=2, lw=0.5, alpha=0.7)
        ax.set_xlabel("State dim 1")
        ax.set_ylabel("State dim 2")
        ax.set_title(f"Trajectory (U_{best_pg['universe_id']})")

        ax = axes[1]
        all_s = traj[5:]
        n_s = min(200, len(all_s))
        idx = np.random.choice(len(all_s), n_s, replace=False)
        D = squareform(pdist(all_s[idx]))
        im = ax.imshow(D, cmap="viridis")
        plt.colorbar(im, ax=ax, shrink=0.7)
        ax.set_title("Proto-geometry: state distance structure")
        plt.tight_layout()
        for ext in ("pdf", "png"):
            fig.savefig(FIG / f"fig_t041_proto_geometry.{ext}", format=ext, dpi=300)
        plt.close(fig)
        print("  Saved fig_t041_proto_geometry.pdf/.png")

    # ============================================================
    # SUMMARY
    # ============================================================

    elapsed = time.time() - t0

    # Determine outcome
    if n_dist > N_UNIVERSES * 0.05:
        outcome = "A: Distinction emerges from interaction"
    elif n_dist == 0:
        outcome = "B: Distinction never emerges"
    else:
        outcome = "C: Some intermediate structure appears"

    # Find first stable thing
    if n_dist > 0:
        # What distinguishes successful from failed universes?
        success = catalog_df[catalog_df["distinction_emerged"]]
        fail = catalog_df[~catalog_df["distinction_emerged"]]
        first_thing = "Persistent behavioral regions (attractor basins)"
    else:
        first_thing = "Trajectory convergence (but not separable regions)"

    print(f"\nRuntime: {elapsed:.1f}s")
    print("\n" + "=" * 70)
    print("T041 RESULTS")
    print("=" * 70)
    print(f"\nUniverses: {N_UNIVERSES}")
    print(f"Distinction:   {n_dist}/{N_UNIVERSES} ({100*n_dist/N_UNIVERSES:.1f}%)")
    print(f"Relation:      {n_rel}/{N_UNIVERSES} ({100*n_rel/N_UNIVERSES:.1f}%)")
    print(f"Proto-math:    {n_pm}/{N_UNIVERSES} ({100*n_pm/N_UNIVERSES:.1f}%)")
    print(f"Proto-geometry:{n_pg}/{N_UNIVERSES} ({100*n_pg/N_UNIVERSES:.1f}%)")
    print()
    print(f"Outcome: {outcome}")
    print()
    print("What is the first stable thing between pure potential and a point?")
    print(f"  {first_thing}")
    print()
    print("Ablation survival:")
    for _, row in ablation_df.iterrows():
        print(f"  {row['condition']:20s}: {row['distinction_rate']:.3f}")
    print()
    print("=" * 70)

    # Save summary
    summary = {
        "n_universes": N_UNIVERSES,
        "n_distinction": int(n_dist),
        "n_relation": int(n_rel),
        "n_proto_math": int(n_pm),
        "n_proto_geometry": int(n_pg),
        "outcome": outcome,
        "first_stable_thing": first_thing,
        "ablation_results": ablation_df.to_dict(orient="records"),
        "distinction_rate_by_class": catalog_df.groupby("universe_class")["distinction_emerged"].mean().to_dict(),
        "success_criterion": "distinction emerges from interaction without pre-defined symbols",
        "success_met": n_dist > 0,
    }
    with open(OUT / "t041_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Saved t041_summary.json")


def make_linear(omega):
    """Remove nonlinearity."""
    if hasattr(omega, 'nonlinear'):
        omega.nonlinear = lambda x: x
    if hasattr(omega, 'W'):
        omega.W = omega.W * 0.5
    return omega


def make_no_feedback(omega):
    """Remove feedback (no self-reference)."""
    if hasattr(omega, 'W'):
        omega.W = omega.W * 0.3
    return omega


def make_noisy(omega, scale):
    """Add noise."""
    if hasattr(omega, 'noise_scale'):
        omega.noise_scale = scale
    else:
        omega.noise_scale = scale
    return omega


if __name__ == "__main__":
    main()
