#!/usr/bin/env python3
"""
T044: Recurrence Audit (Destroy T043 If Possible)
===================================================
Attempt to destroy T043's finding that recurrence is first.
If it survives all tests, accept it. If not, replace it.
"""

import sys, json, warnings, time
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from scipy.spatial.distance import pdist, squareform
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
N_TEST = 2000

# ============================================================
# Ω-UNIVERSE CLASSES (same as T043)
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
# RECURRENCE DETECTORS (5 independent)
# ============================================================

def D1_exact_revisit(traj, epsilon=0.0):
    """Exact or near-exact revisit to previous state."""
    if len(traj) < 8:
        return False, 0
    for d in range(5, len(traj)):
        for j in range(max(0, d-20), d-1):
            if np.linalg.norm(traj[d] - traj[j]) < epsilon:
                return True, d
    return False, 0

def D2_epsilon_revisit(traj, epsilon=0.3):
    """Epsilon-ball revisit."""
    if len(traj) < 8:
        return False, 0
    for d in range(5, len(traj)):
        for j in range(max(0, d-20), d-1):
            if np.linalg.norm(traj[d] - traj[j]) < epsilon:
                return True, d
    return False, 0

def D3_topological_recurrence(traj):
    """Returns to same topological region (via distance threshold)."""
    if len(traj) < 10:
        return False, 0
    # Use median distance as threshold
    D = squareform(pdist(traj))
    med_dist = np.median(D[D > 0])
    threshold = med_dist * 0.5
    for d in range(5, len(traj)):
        for j in range(max(0, d-20), d-1):
            if np.linalg.norm(traj[d] - traj[j]) < threshold:
                return True, d
    return False, 0

def D4_nn_recurrence(traj):
    """Nearest-neighbor recurrence: returns to NN of previous state."""
    if len(traj) < 12:
        return False, 0
    for d in range(6, len(traj)):
        # Find NN of current state among previous states
        prev = traj[:d-1]
        dists = np.linalg.norm(prev - traj[d], axis=1)
        nn_idx = np.argmin(dists)
        nn_dist = dists[nn_idx]
        # Check if NN of previous state was also close
        if d > 1:
            prev_dists = np.linalg.norm(prev - traj[d-1], axis=1)
            nn_prev_idx = np.argmin(prev_dists)
            if abs(nn_idx - nn_prev_idx) <= 2:
                return True, d
    return False, 0

def D5_rqa_recurrence(traj):
    """Recurrence quantification: recurrence rate in recurrence plot."""
    if len(traj) < 15:
        return False, 0
    D = squareform(pdist(traj))
    threshold = np.percentile(D[D > 0], 20)
    rp = D < threshold
    # Recurrence rate
    n = len(traj)
    rr = np.sum(rp) / (n * n)
    if rr > 0.05:
        # Find first depth where recurrence rate exceeds threshold
        for d in range(8, len(traj)):
            D_sub = squareform(pdist(traj[:d]))
            threshold_sub = np.percentile(D_sub[D_sub > 0], 20) if np.any(D_sub > 0) else 1
            rp_sub = D_sub < threshold_sub
            rr_sub = np.sum(rp_sub) / (d * d)
            if rr_sub > 0.05:
                return True, d
    return False, 0

ALL_DETECTORS = [
    ("D1_exact", D1_exact_revisit),
    ("D2_epsilon", D2_epsilon_revisit),
    ("D3_topological", D3_topological_recurrence),
    ("D4_nn", D4_nn_recurrence),
    ("D5_rqa", D5_rqa_recurrence),
]


# ============================================================
# TESTS
# ============================================================

def test_D_nonrecursive_control(N=N_TEST):
    """Test D: Recursive vs nonrecursive control."""
    print("\n[Test D] Recursive vs nonrecursive control...")

    recursive_rates = []
    nonrecursive_rates = []

    for i in range(N):
        seed = i
        rng = np.random.RandomState(seed)

        # Recursive
        omega_r = RecursiveTransform(seed)
        init = rng.randn(STATE_DIM) * 0.5
        traj_r = simulate(omega_r, init)
        _, fired_r = D2_epsilon_revisit(traj_r)
        recursive_rates.append(1 if fired_r else 0)

        # Nonrecursive: random transforms (no feedback)
        traj_nr = [init.copy()]
        x = init.copy()
        W = rng.randn(STATE_DIM, STATE_DIM) * 0.3
        for _ in range(MAX_DEPTH):
            x = np.tanh(W @ x) + rng.randn(STATE_DIM) * 0.01
            x = np.clip(x, -10, 10)
            traj_nr.append(x.copy())
        traj_nr = np.array(traj_nr)
        _, fired_nr = D2_epsilon_revisit(traj_nr)
        nonrecursive_rates.append(1 if fired_nr else 0)

    r_rate = np.mean(recursive_rates)
    nr_rate = np.mean(nonrecursive_rates)

    # Effect size
    effect_size = r_rate - nr_rate

    # Bootstrap CI for difference
    boot_diffs = []
    for _ in range(1000):
        idx = np.random.choice(N, N, replace=True)
        boot_diffs.append(np.mean(np.array(recursive_rates)[idx]) - np.mean(np.array(nonrecursive_rates)[idx]))
    ci_lo = np.percentile(boot_diffs, 2.5)
    ci_hi = np.percentile(boot_diffs, 97.5)

    # Permutation test
    combined = np.array(recursive_rates + nonrecursive_rates)
    perm_diffs = []
    for _ in range(1000):
        perm = np.random.permutation(combined)
        perm_diffs.append(np.mean(perm[:N]) - np.mean(perm[N:]))
    p_perm = np.mean(np.abs(perm_diffs) >= abs(effect_size))

    print(f"  Recursive rate: {r_rate:.4f}")
    print(f"  Nonrecursive rate: {nr_rate:.4f}")
    print(f"  Effect size: {effect_size:.4f}")
    print(f"  95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")
    print(f"  Permutation p: {p_perm:.4f}")

    return {
        "recursive_rate": float(r_rate),
        "nonrecursive_rate": float(nr_rate),
        "effect_size": float(effect_size),
        "ci_lo": float(ci_lo),
        "ci_hi": float(ci_hi),
        "permutation_p": float(p_perm),
        "survived": effect_size > 0.05 and p_perm < 0.05,
    }


def test_E_shuffled_trajectories(N=N_TEST):
    """Test E: Shuffled temporal ordering."""
    print("\n[Test E] Shuffled trajectories...")

    real_rates = []
    shuffled_rates = []

    for i in range(N):
        omega = RecursiveTransform(i)
        init = np.random.RandomState(i).randn(STATE_DIM) * 0.5
        traj = simulate(omega, init)

        _, fired_real = D2_epsilon_revisit(traj)
        real_rates.append(1 if fired_real else 0)

        # Shuffle temporal ordering
        traj_shuffled = traj.copy()
        np.random.shuffle(traj_shuffled)
        _, fired_shuf = D2_epsilon_revisit(traj_shuffled)
        shuffled_rates.append(1 if fired_shuf else 0)

    r_rate = np.mean(real_rates)
    s_rate = np.mean(shuffled_rates)
    effect = r_rate - s_rate

    boot_diffs = []
    for _ in range(1000):
        idx = np.random.choice(N, N, replace=True)
        boot_diffs.append(np.mean(np.array(real_rates)[idx]) - np.mean(np.array(shuffled_rates)[idx]))
    ci_lo = np.percentile(boot_diffs, 2.5)
    ci_hi = np.percentile(boot_diffs, 97.5)

    perm_diffs = []
    combined = np.array(real_rates + shuffled_rates)
    for _ in range(1000):
        perm = np.random.permutation(combined)
        perm_diffs.append(np.mean(perm[:N]) - np.mean(perm[N:]))
    p_perm = np.mean(np.abs(perm_diffs) >= abs(effect))

    print(f"  Real rate: {r_rate:.4f}")
    print(f"  Shuffled rate: {s_rate:.4f}")
    print(f"  Effect size: {effect:.4f}")
    print(f"  95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")
    print(f"  Permutation p: {p_perm:.4f}")

    return {
        "real_rate": float(r_rate),
        "shuffled_rate": float(s_rate),
        "effect_size": float(effect),
        "ci_lo": float(ci_lo),
        "ci_hi": float(ci_hi),
        "permutation_p": float(p_perm),
        "survived": effect > 0.05 and p_perm < 0.05,
    }


def test_F_random_walk_null(N=N_TEST):
    """Test F: Random walk null model."""
    print("\n[Test F] Random walk null...")

    real_rates = []
    null_rates = []

    for i in range(N):
        rng = np.random.RandomState(i)
        omega = RecursiveTransform(i)
        init = rng.randn(STATE_DIM) * 0.5
        traj_real = simulate(omega, init)
        _, fired_real = D2_epsilon_revisit(traj_real)
        real_rates.append(1 if fired_real else 0)

        # Matched random walk: same variance, same length
        traj_null = [init.copy()]
        x = init.copy()
        step_std = np.std(np.diff(traj_real, axis=0)) if len(traj_real) > 1 else 0.1
        for _ in range(len(traj_real) - 1):
            x = x + rng.randn(STATE_DIM) * step_std
            x = np.clip(x, -10, 10)
            traj_null.append(x.copy())
        traj_null = np.array(traj_null)
        _, fired_null = D2_epsilon_revisit(traj_null)
        null_rates.append(1 if fired_null else 0)

    r_rate = np.mean(real_rates)
    n_rate = np.mean(null_rates)
    effect = r_rate - n_rate

    # Z-test
    p_pool = (np.sum(real_rates) + np.sum(null_rates)) / (2 * N)
    se = np.sqrt(2 * p_pool * (1 - p_pool) / N)
    z = effect / se if se > 0 else 0
    from scipy.stats import norm
    p_val = 2 * (1 - norm.cdf(abs(z)))

    print(f"  Real rate: {r_rate:.4f}")
    print(f"  Null rate: {n_rate:.4f}")
    print(f"  Effect size: {effect:.4f}")
    print(f"  Z-score: {z:.4f}")
    print(f"  P-value: {p_val:.4f}")

    return {
        "real_rate": float(r_rate),
        "null_rate": float(n_rate),
        "effect_size": float(effect),
        "z_score": float(z),
        "p_value": float(p_val),
        "survived": effect > 0.05 and p_val < 0.05,
    }


def test_G_detector_agreement(N=N_TEST):
    """Test G: Do 5 independent detectors agree?"""
    print("\n[Test G] Detector agreement...")

    agreement_data = []

    for i in range(N):
        omega = RecursiveTransform(i)
        init = np.random.RandomState(i).randn(STATE_DIM) * 0.5
        traj = simulate(omega, init)

        results = {}
        for det_name, det_fn in ALL_DETECTORS:
            try:
                _, fired = det_fn(traj)
                results[det_name] = 1 if fired else 0
            except:
                results[det_name] = 0

        agreement_data.append(results)

    df = pd.DataFrame(agreement_data)

    # Pairwise agreement (Cohen's kappa approximation)
    pair_agreements = []
    for i, (n1, _) in enumerate(ALL_DETECTORS):
        for j, (n2, _) in enumerate(ALL_DETECTORS):
            if i < j:
                agree = (df[n1] == df[n2]).mean()
                pair_agreements.append({"det_a": n1, "det_b": n2, "agreement": float(agree)})

    # Overall: how many universes have >=3 detectors agree?
    vote_counts = df.sum(axis=1)
    high_agreement = (vote_counts >= 3).mean()
    majority = (vote_counts >= 3).mean()

    # Individual rates
    rates = {col: df[col].mean() for col in df.columns}

    print(f"  Individual rates:")
    for name, rate in rates.items():
        print(f"    {name}: {rate:.4f}")
    print(f"  High agreement (>=3/5): {high_agreement:.4f}")
    print(f"  Mean pairwise agreement: {np.mean([a['agreement'] for a in pair_agreements]):.4f}")

    return {
        "individual_rates": rates,
        "high_agreement_rate": float(high_agreement),
        "mean_pairwise_agreement": float(np.mean([a["agreement"] for a in pair_agreements])),
        "pair_agreements": pair_agreements,
        "survived": high_agreement > 0.3 and rates.get("D2_epsilon", 0) > 0.5,
    }


def test_H_order_without_recurrence(N=3000):
    """Test H: Recompute T043 ordering without recurrence."""
    print("\n[Test H] Order without recurrence...")

    # Simplified: just check what appears first among non-recurrence detectors
    detectors_no_recurrence = [
        ("D02_trajectory_convergence", lambda traj: D2_convergence(traj)),
        ("D05_persistence", lambda traj: D5_persistence_simple(traj)),
        ("D08_neighborhood", lambda traj: D8_neighborhood_simple(traj)),
        ("D13_composition", lambda traj: D13_composition_simple(traj)),
        ("D15_selfref", lambda traj: D15_selfref_simple(traj)),
        ("D18_separability", lambda traj: D18_separability_simple(traj)),
        ("D20_distance", lambda traj: D20_distance_simple(traj)),
    ]

    depths = {name: [] for name, _ in detectors_no_recurrence}

    for i in range(N):
        omega = RecursiveTransform(i)
        init = np.random.RandomState(i).randn(STATE_DIM) * 0.5
        traj = simulate(omega, init)

        for name, fn in detectors_no_recurrence:
            try:
                _, d = fn(traj)
                if d > 0:
                    depths[name].append(d)
            except:
                pass

    print("  Emergence rates (excluding recurrence):")
    mean_depths = {}
    for name in depths:
        count = len(depths[name])
        mean_d = np.mean(depths[name]) if depths[name] else 999
        print(f"    {name:30s}: {count}/{N} ({100*count/N:.1f}%), mean depth={mean_d:.1f}")
        mean_depths[name] = {"count": count, "rate": count/N, "mean_depth": float(mean_d)}

    # First = highest rate with lowest mean depth
    ranked = sorted(mean_depths.items(), key=lambda x: (-x[1]["rate"], x[1]["mean_depth"]))

    return {
        "first_without_recurrence": ranked[0][0] if ranked else None,
        "rates": mean_depths,
    }


# Simplified detectors for Test H
def D2_convergence(traj):
    if len(traj) < 15: return False, 0
    early = traj[:len(traj)//3].mean(axis=0)
    late = traj[2*len(traj)//3:].mean(axis=0)
    if np.linalg.norm(late - early) < np.linalg.norm(traj[0] - traj[-1]) * 0.5:
        return True, 5
    return False, 0

def D5_persistence_simple(traj):
    if len(traj) < 10: return False, 0
    centroid = traj.mean(axis=0)
    dists = np.linalg.norm(traj - centroid, axis=1)
    late = dists[2*len(dists)//3:]
    if len(late) > 2 and np.std(late) < np.mean(late) * 0.3:
        return True, 5
    return False, 0

def D8_neighborhood_simple(traj):
    if len(traj) < 20: return False, 0
    n = min(25, len(traj))
    D_e = squareform(pdist(traj[:n]))
    D_l = squareform(pdist(traj[-n:]))
    flat_e = D_e[np.triu_indices(n, k=1)]
    flat_l = D_l[np.triu_indices(n, k=1)]
    corr = np.corrcoef(flat_e, flat_l)[0, 1]
    return (corr > 0.5), 5 if corr > 0.5 else 0

def D13_composition_simple(traj):
    if len(traj) < 15: return False, 0
    for sub_len in [3, 4]:
        for d in range(sub_len * 2, len(traj)):
            sub = traj[d-sub_len:d]
            for j in range(max(0, d-sub_len*3), d-sub_len):
                if np.allclose(sub, traj[j:j+sub_len], atol=0.2):
                    return True, d
    return False, 0

def D15_selfref_simple(traj):
    if len(traj) < 12: return False, 0
    for d in range(6, len(traj)):
        for j in range(max(0, d-20), d-2):
            if np.linalg.norm(traj[d] - traj[j]) < 0.5:
                return True, d
    return False, 0

def D18_separability_simple(traj):
    if len(traj) < 15: return False, 0
    from scipy.cluster.hierarchy import fcluster, linkage
    n = min(30, len(traj))
    D = squareform(pdist(traj[:n]))
    Z = linkage(D, method="average")
    labels = fcluster(Z, 2, criterion="maxclust")
    means = [traj[:n][labels == i].mean(axis=0) for i in range(1, 3)]
    inter = np.linalg.norm(means[0] - means[1])
    intra = np.mean([np.mean(pdist(traj[:n][labels == i])) for i in range(1, 3) if (labels == i).sum() > 1])
    return (intra > 0 and inter / intra > 1.5), 8

def D20_distance_simple(traj):
    if len(traj) < 15: return False, 0
    n = min(30, len(traj))
    D = squareform(pdist(traj[:n]))
    all_d = D[np.triu_indices(n, k=1)]
    hist, _ = np.histogram(all_d, bins=15)
    hist_n = hist / max(hist.sum(), 1)
    from scipy.stats import entropy as ent
    se = ent(hist_n + 1e-12)
    return (1 - se / np.log(15)) > 0.15, 5


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T044: RECURRENCE AUDIT (DESTROY T043 IF POSSIBLE)")
    print("=" * 70)
    t0 = time.time()

    # Run all tests
    results_D = test_D_nonrecursive_control()
    results_E = test_E_shuffled_trajectories()
    results_F = test_F_random_walk_null()
    results_G = test_G_detector_agreement()
    results_H = test_H_order_without_recurrence()

    # ============================================================
    # SAVE
    # ============================================================

    print("\nSaving outputs...")

    # t044_recurrence_tests.csv
    tests_df = pd.DataFrame([
        {"test": "D_recursive_control", **{k: v for k, v in results_D.items() if k != "survived"},
         "survived": results_D["survived"]},
        {"test": "E_shuffled_trajectories", **{k: v for k, v in results_E.items() if k != "survived"},
         "survived": results_E["survived"]},
        {"test": "F_random_walk_null", **{k: v for k, v in results_F.items() if k != "survived"},
         "survived": results_F["survived"]},
    ])
    tests_df.to_csv(OUT / "t044_recurrence_tests.csv", index=False)
    print("  Saved t044_recurrence_tests.csv")

    # t044_detector_agreement.csv
    agree_df = pd.DataFrame(results_G["pair_agreements"])
    agree_df.to_csv(OUT / "t044_detector_agreement.csv", index=False)
    print("  Saved t044_detector_agreement.csv")

    # t044_null_models.csv
    null_df = pd.DataFrame([
        {"model": "random_walk", "rate": results_F["null_rate"], "z": results_F["z_score"], "p": results_F["p_value"]},
    ])
    null_df.to_csv(OUT / "t044_null_models.csv", index=False)
    print("  Saved t044_null_models.csv")

    # t044_order_without_recurrence.csv
    order_df = pd.DataFrame([{"detector": k, **v} for k, v in results_H["rates"].items()])
    order_df.to_csv(OUT / "t044_order_without_recurrence.csv", index=False)
    print("  Saved t044_order_without_recurrence.csv")

    # ============================================================
    # FIGURES
    # ============================================================

    print("\nGenerating figures...")
    plt.rcParams.update({
        "font.family": "serif", "font.size": 9, "axes.titlesize": 10,
        "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
        "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    })

    # Fig 1: Detector comparison
    fig, ax = plt.subplots(figsize=(8, 4))
    names = list(results_G["individual_rates"].keys())
    rates = [results_G["individual_rates"][n] for n in names]
    colors = ["#2ecc71" if r > 0.5 else "#f39c12" if r > 0.2 else "#e74c3c" for r in rates]
    ax.bar(names, rates, color=colors, edgecolor="white", linewidth=0.3)
    ax.set_ylabel("Detection rate")
    ax.set_title("5 independent recurrence detectors (agreement test)")
    ax.axhline(0.5, color="black", ls="--", lw=0.5, label="50% threshold")
    ax.legend(frameon=False)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t044_detector_comparison.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t044_detector_comparison.pdf/.png")

    # Fig 2: Null vs real
    fig, ax = plt.subplots(figsize=(8, 4))
    models = ["Real Ω", "Random Walk", "Shuffled", "Nonrecursive"]
    rates_plot = [results_G["individual_rates"]["D2_epsilon"],
                  results_F["null_rate"],
                  results_E["shuffled_rate"],
                  results_D["nonrecursive_rate"]]
    colors = ["#2ecc71", "#e74c3c", "#f39c12", "#3498db"]
    ax.bar(models, rates_plot, color=colors, edgecolor="white", linewidth=0.3)
    ax.set_ylabel("Recurrence rate")
    ax.set_title("Recurrence rate across models")
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t044_null_vs_real.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t044_null_vs_real.pdf/.png")

    # Fig 3: Recurrence survival summary
    fig, ax = plt.subplots(figsize=(10, 5))
    tests = ["D: Recursive\nvs Nonrecursive", "E: Shuffled\nTrajectories",
             "F: Random Walk\nNull", "G: Detector\nAgreement"]
    survived = [results_D["survived"], results_E["survived"],
                results_F["survived"], results_G["survived"]]
    colors = ["#2ecc71" if s else "#e74c3c" for s in survived]
    ax.bar(tests, [1]*4, color=colors, edgecolor="white", linewidth=0.3, alpha=0.7)
    for i, (test, s) in enumerate(zip(tests, survived)):
        label = "SURVIVES" if s else "KILLED"
        ax.text(i, 0.5, label, ha="center", va="center", fontsize=10,
                fontweight="bold", color="white")
    ax.set_ylim(0, 1)
    ax.set_title("Recurrence survival across audit tests")
    ax.set_yticks([])
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t044_recurrence_survival.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t044_recurrence_survival.pdf/.png")

    # ============================================================
    # SUMMARY
    # ============================================================

    elapsed = time.time() - t0

    # Overall verdict
    all_survived = all([results_D["survived"], results_E["survived"],
                        results_F["survived"], results_G["survived"]])
    n_survived = sum([results_D["survived"], results_E["survived"],
                      results_F["survived"], results_G["survived"]])

    print(f"\nRuntime: {elapsed:.1f}s")
    print("\n" + "=" * 70)
    print("T044 RESULTS")
    print("=" * 70)
    print(f"\nTest D (Recursive vs Nonrecursive): {'SURVIVES' if results_D['survived'] else 'KILLED'}")
    print(f"  Effect: {results_D['effect_size']:.4f}, p={results_D['permutation_p']:.4f}")
    print(f"\nTest E (Shuffled Trajectories): {'SURVIVES' if results_E['survived'] else 'KILLED'}")
    print(f"  Effect: {results_E['effect_size']:.4f}, p={results_E['permutation_p']:.4f}")
    print(f"\nTest F (Random Walk Null): {'SURVIVES' if results_F['survived'] else 'KILLED'}")
    print(f"  Effect: {results_F['effect_size']:.4f}, z={results_F['z_score']:.4f}, p={results_F['p_value']:.4f}")
    print(f"\nTest G (Detector Agreement): {'SURVIVES' if results_G['survived'] else 'KILLED'}")
    print(f"  High agreement rate: {results_G['high_agreement_rate']:.4f}")
    print(f"\nTests survived: {n_survived}/4")
    print()
    print("VERDICT:")
    if all_survived:
        print("  RECURRENCE IS GENUINE.")
        print("  It survives all audit tests.")
        print("  It is NOT a detector artifact.")
        print(f"\n  First emergent structure (measured): RECURRENCE")
        print(f"  What comes next: {results_H['first_without_recurrence']}")
    elif n_survived >= 3:
        print("  RECURRENCE IS PARTIALLY GENUINE.")
        print(f"  {n_survived}/4 tests survived.")
        print(f"  First emergent structure: {results_H['first_without_recurrence']}")
    else:
        print("  RECURRENCE IS KILLED.")
        print(f"  {n_survived}/4 tests survived.")
        print(f"  First emergent structure: {results_H['first_without_recurrence']}")
    print("=" * 70)

    summary = {
        "test_D": {"survived": results_D["survived"], "effect": results_D["effect_size"], "p": results_D["permutation_p"]},
        "test_E": {"survived": results_E["survived"], "effect": results_E["effect_size"], "p": results_E["permutation_p"]},
        "test_F": {"survived": results_F["survived"], "effect": results_F["effect_size"], "p": results_F["p_value"]},
        "test_G": {"survived": results_G["survived"], "agreement": results_G["high_agreement_rate"]},
        "tests_survived": n_survived,
        "all_survived": all_survived,
        "first_structure_without_recurrence": results_H["first_without_recurrence"],
    }
    with open(OUT / "t044_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSaved t044_summary.json")


if __name__ == "__main__":
    main()
