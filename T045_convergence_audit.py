#!/usr/bin/env python3
"""
T045: Convergence Audit (Destroy T044 If Possible)
====================================================
Attempt to destroy T044's finding that trajectory convergence
is the first emergent structure after recurrence.

No defense. No confirmation bias.
"""

import sys, json, warnings, time
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.spatial.distance import pdist, squareform
from scipy.stats import entropy, norm
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
# CONVERGENCE DETECTORS
# ============================================================

def C1_pairwise_contraction(traj):
    """Pairwise distances between trajectory segments decrease."""
    if len(traj) < 15:
        return False, 0
    n = len(traj)
    seg1 = traj[:n//3]
    seg2 = traj[2*n//3:]
    d1 = seg1.mean(axis=0)
    d2 = seg2.mean(axis=0)
    final_dist = np.linalg.norm(d1 - d2)
    initial_dist = np.linalg.norm(traj[0] - traj[-1])
    if initial_dist > 0 and final_dist < initial_dist * 0.5:
        for d in range(5, n):
            mid = d // 2
            da = np.linalg.norm(traj[:mid].mean(axis=0) - traj[mid:d].mean(axis=0))
            if da < initial_dist * 0.5:
                return True, d
    return False, 0

def C2_basin_attraction(traj):
    """Trajectory enters a bounded region and stays."""
    if len(traj) < 15:
        return False, 0
    # Compute rolling window centroid
    window = 5
    centroids = []
    for i in range(len(traj) - window):
        centroids.append(traj[i:i+window].mean(axis=0))
    centroids = np.array(centroids)
    if len(centroids) < 10:
        return False, 0
    # Check if centroids converge
    early_cent = centroids[:len(centroids)//3].mean(axis=0)
    late_cent = centroids[2*len(centroids)//3:].mean(axis=0)
    convergence = np.linalg.norm(late_cent - early_cent)
    spread = np.std([np.linalg.norm(c - late_cent) for c in centroids[2*len(centroids)//3:]])
    if convergence < 1.0 and spread < 1.0:
        for d in range(window + 5, len(traj)):
            c_early = traj[:d//2].mean(axis=0)
            c_late = traj[d//2:d].mean(axis=0)
            if np.linalg.norm(c_late - c_early) < 1.0:
                return True, d
    return False, 0

def C3_entropy_collapse(traj):
    """State-space entropy decreases over time."""
    if len(traj) < 20:
        return False, 0
    # Compute histogram entropy at different points
    ranges = [(traj[:, i].min() - 0.1, traj[:, i].max() + 0.1) for i in range(traj.shape[1])]
    early_hist, _ = np.histogramdd(traj[:10], bins=5, range=ranges)
    late_hist, _ = np.histogramdd(traj[-10:], bins=5, range=ranges)
    early_ent = entropy(early_hist.flatten() + 1e-12)
    late_ent = entropy(late_hist.flatten() + 1e-12)
    if early_ent > 0 and late_ent < early_ent * 0.7:
        for d in range(10, len(traj)):
            h, _ = np.histogramdd(traj[:d], bins=5, range=ranges)
            if entropy(h.flatten() + 1e-12) < early_ent * 0.7:
                return True, d
    return False, 0

def C4_trajectory_clustering(traj):
    """Trajectory points cluster into tight groups."""
    if len(traj) < 15:
        return False, 0
    from scipy.cluster.hierarchy import fcluster, linkage
    n = min(30, len(traj))
    D = squareform(pdist(traj[:n]))
    Z = linkage(D, method="average")
    labels = fcluster(Z, 3, criterion="maxclust")
    # Check if clusters are compact
    compactness = []
    for i in range(1, 4):
        mask = labels == i
        if mask.sum() > 1:
            intra = np.mean(pdist(traj[:n][mask]))
            compactness.append(intra)
    if compactness and np.mean(compactness) < 1.0:
        return True, 8
    return False, 0

def C5_lyapunov_contraction(traj):
    """Local expansion rates are negative (contraction)."""
    if len(traj) < 15:
        return False, 0
    # Estimate local Lyapunov exponent
    rates = []
    for i in range(2, len(traj)):
        d1 = np.linalg.norm(traj[i] - traj[i-1])
        d0 = np.linalg.norm(traj[i-1] - traj[i-2])
        if d0 > 1e-12:
            rates.append(np.log(d1 / d0))
    if len(rates) > 5:
        mean_rate = np.mean(rates[-len(rates)//2:])
        if mean_rate < -0.1:
            for d in range(8, len(traj)):
                early_rates = []
                for i in range(2, d):
                    d1 = np.linalg.norm(traj[i] - traj[i-1])
                    d0 = np.linalg.norm(traj[i-1] - traj[i-2])
                    if d0 > 1e-12:
                        early_rates.append(np.log(d1 / d0))
                if early_rates and np.mean(early_rates[-len(early_rates)//2:]) < -0.1:
                    return True, d
    return False, 0


ALL_DETECTORS = [
    ("C1_pairwise", C1_pairwise_contraction),
    ("C2_basin", C2_basin_attraction),
    ("C3_entropy", C3_entropy_collapse),
    ("C4_clustering", C4_trajectory_clustering),
    ("C5_lyapunov", C5_lyapunov_contraction),
]


# ============================================================
# UNIVERSE GENERATORS
# ============================================================

def gen_recursive(seed, dim=STATE_DIM):
    rng = np.random.RandomState(seed)
    W = rng.randn(dim, dim) * 0.3
    b = rng.randn(dim) * 0.1
    nl = rng.choice([np.tanh, np.sin, lambda x: x**3])
    strength = rng.uniform(0.3, 0.8)
    def step(x):
        return strength * nl(W @ x + b)
    return step

def gen_repel_only(seed, dim=STATE_DIM):
    """Test B: Only divergent/repulsive dynamics."""
    rng = np.random.RandomState(seed)
    W = rng.randn(dim, dim) * 0.5
    def step(x):
        return x + 0.1 * (W @ x)  # pure expansion
    return step

def gen_expanding(seed, dim=STATE_DIM):
    """Test A: State space grows each step."""
    rng = np.random.RandomState(seed)
    def step(x):
        scale = 1.0 + 0.05 * len(x)  # grows with dimension
        return x * scale + rng.randn(dim) * 0.01
    return step

def gen_bounded(seed, dim=STATE_DIM):
    """Bounded dynamics with attractor."""
    rng = np.random.RandomState(seed)
    center = rng.randn(dim) * 0.5
    W = rng.randn(dim, dim) * 0.3
    def step(x):
        return np.tanh(W @ (x - center) + center)
    return step

def sim(omega, init, depth=MAX_DEPTH, clip=None):
    traj = [init.copy()]
    x = init.copy()
    for _ in range(depth):
        try:
            x = omega(x)
            if clip is not None:
                x = np.clip(x, -clip, clip)
            if np.any(np.isnan(x)):
                break
            traj.append(x.copy())
        except:
            break
    return np.array(traj)


# ============================================================
# TESTS
# ============================================================

def test_A_expanding_universes(N=N_TEST):
    """Test A: Expanding state spaces (no bounded attractors)."""
    print("\n[Test A] Expanding universes...")
    real_rates = []
    expand_rates = []
    for i in range(N):
        omega_r = gen_recursive(i)
        init = np.random.RandomState(i).randn(STATE_DIM) * 0.5
        traj_r = sim(omega_r, init)
        _, f_r = C1_pairwise_contraction(traj_r)
        real_rates.append(1 if f_r else 0)

        omega_e = gen_expanding(i)
        traj_e = sim(omega_e, init, clip=None)
        _, f_e = C1_pairwise_contraction(traj_e)
        expand_rates.append(1 if f_e else 0)

    r = np.mean(real_rates)
    e = np.mean(expand_rates)
    effect = r - e
    perm = []
    combined = np.array(real_rates + expand_rates)
    for _ in range(500):
        p = np.random.permutation(combined)
        perm.append(np.mean(p[:N]) - np.mean(p[N:]))
    pval = np.mean(np.abs(perm) >= abs(effect))
    print(f"  Real: {r:.4f}, Expanding: {e:.4f}, Effect: {effect:.4f}, p={pval:.4f}")
    return {"test": "A_expanding", "real": float(r), "expanding": float(e),
            "effect": float(effect), "p": float(pval), "survived": effect > 0.05 and pval < 0.05}

def test_B_repel_only(N=N_TEST):
    """Test B: Repel-only dynamics."""
    print("\n[Test B] Repel-only dynamics...")
    real_rates = []
    repel_rates = []
    for i in range(N):
        omega_r = gen_recursive(i)
        init = np.random.RandomState(i).randn(STATE_DIM) * 0.5
        traj_r = sim(omega_r, init)
        _, f_r = C1_pairwise_contraction(traj_r)
        real_rates.append(1 if f_r else 0)

        omega_p = gen_repel_only(i)
        traj_p = sim(omega_p, init, clip=None)
        _, f_p = C1_pairwise_contraction(traj_p)
        repel_rates.append(1 if f_p else 0)

    r = np.mean(real_rates)
    p = np.mean(repel_rates)
    effect = r - p
    perm = []
    combined = np.array(real_rates + repel_rates)
    for _ in range(500):
        pp = np.random.permutation(combined)
        perm.append(np.mean(pp[:N]) - np.mean(pp[N:]))
    pval = np.mean(np.abs(perm) >= abs(effect))
    print(f"  Real: {r:.4f}, Repel: {p:.4f}, Effect: {effect:.4f}, p={pval:.4f}")
    return {"test": "B_repel", "real": float(r), "repel": float(p),
            "effect": float(effect), "p": float(pval), "survived": effect > 0.05 and pval < 0.05}

def test_C_scale_audit(N=500):
    """Test C: Different dimensions."""
    print("\n[Test C] Scale audit (dimensions)...")
    dims = [1, 2, 4, 8, 16, 32]
    results = {}
    for dim in dims:
        rates = []
        for i in range(N):
            omega = gen_recursive(i, dim)
            init = np.random.RandomState(i).randn(dim) * 0.5
            traj = sim(omega, init)
            _, f = C1_pairwise_contraction(traj)
            rates.append(1 if f else 0)
        rate = np.mean(rates)
        results[dim] = float(rate)
        print(f"  dim={dim:3d}: convergence rate={rate:.4f}")
    return results

def test_D_shuffled(N=N_TEST):
    """Test D: Temporal shuffling."""
    print("\n[Test D] Shuffled dynamics...")
    real_rates = []
    shuffle_rates = []
    for i in range(N):
        omega = gen_recursive(i)
        init = np.random.RandomState(i).randn(STATE_DIM) * 0.5
        traj = sim(omega, init)
        _, f_r = C1_pairwise_contraction(traj)
        real_rates.append(1 if f_r else 0)

        traj_s = traj.copy()
        np.random.shuffle(traj_s)
        _, f_s = C1_pairwise_contraction(traj_s)
        shuffle_rates.append(1 if f_s else 0)

    r = np.mean(real_rates)
    s = np.mean(shuffle_rates)
    effect = r - s
    perm = []
    combined = np.array(real_rates + shuffle_rates)
    for _ in range(500):
        p = np.random.permutation(combined)
        perm.append(np.mean(p[:N]) - np.mean(p[N:]))
    pval = np.mean(np.abs(perm) >= abs(effect))
    print(f"  Real: {r:.4f}, Shuffled: {s:.4f}, Effect: {effect:.4f}, p={pval:.4f}")
    return {"test": "D_shuffled", "real": float(r), "shuffled": float(s),
            "effect": float(effect), "p": float(pval), "survived": effect > 0.05 and pval < 0.05}

def test_E_null_models(N=N_TEST):
    """Test E: Multiple null models."""
    print("\n[Test E] Null models...")
    real_rate = 0
    null_rates = {}
    for name, gen_fn in [("random_walk", lambda i: None), ("brownian", lambda i: None),
                          ("ornstein_uhlenbeck", lambda i: None)]:
        rates = []
        for i in range(N):
            rng = np.random.RandomState(i)
            init = rng.randn(STATE_DIM) * 0.5
            if name == "random_walk":
                traj = [init.copy()]
                x = init.copy()
                for _ in range(MAX_DEPTH):
                    x = x + rng.randn(STATE_DIM) * 0.1
                    traj.append(x.copy())
                traj = np.array(traj)
            elif name == "brownian":
                traj = [init.copy()]
                x = init.copy()
                for _ in range(MAX_DEPTH):
                    x = x + rng.randn(STATE_DIM) * 0.05
                    traj.append(x.copy())
                traj = np.array(traj)
            elif name == "ornstein_uhlenbeck":
                traj = [init.copy()]
                x = init.copy()
                theta = 0.3
                for _ in range(MAX_DEPTH):
                    x = x + theta * (np.zeros(STATE_DIM) - x) * 0.1 + rng.randn(STATE_DIM) * 0.1
                    traj.append(x.copy())
                traj = np.array(traj)
            _, f = C1_pairwise_contraction(traj)
            rates.append(1 if f else 0)
        null_rates[name] = float(np.mean(rates))
        print(f"  {name:25s}: {null_rates[name]:.4f}")

    # Real rate
    real_rates = []
    for i in range(N):
        omega = gen_recursive(i)
        init = np.random.RandomState(i).randn(STATE_DIM) * 0.5
        traj = sim(omega, init)
        _, f = C1_pairwise_contraction(traj)
        real_rates.append(1 if f else 0)
    real_rate = np.mean(real_rates)
    print(f"  {'real':25s}: {real_rate:.4f}")

    return {"test": "E_nulls", "real": float(real_rate), "nulls": null_rates,
            "survived": all(real_rate > v + 0.05 for v in null_rates.values())}

def test_F_detector_agreement(N=N_TEST):
    """Test F: Multiple independent detectors."""
    print("\n[Test F] Detector agreement...")
    all_results = []
    for i in range(N):
        omega = gen_recursive(i)
        init = np.random.RandomState(i).randn(STATE_DIM) * 0.5
        traj = sim(omega, init)
        row = {}
        for name, fn in ALL_DETECTORS:
            try:
                _, f = fn(traj)
                row[name] = 1 if f else 0
            except:
                row[name] = 0
        all_results.append(row)
    df = pd.DataFrame(all_results)
    rates = {col: df[col].mean() for col in df.columns}
    votes = df.sum(axis=1)
    high_agree = (votes >= 3).mean()
    print(f"  Individual rates: {rates}")
    print(f"  High agreement (>=3/5): {high_agree:.4f}")
    return {"test": "F_agreement", "rates": rates, "high_agreement": float(high_agree),
            "survived": high_agree > 0.3 and rates.get("C1_pairwise", 0) > 0.5}

def test_G_nonmetric(N=N_TEST):
    """Test G: Non-metric formulations."""
    print("\n[Test G] Non-metric convergence...")
    metric_rates = []
    ordinal_rates = []
    for i in range(N):
        omega = gen_recursive(i)
        init = np.random.RandomState(i).randn(STATE_DIM) * 0.5
        traj = sim(omega, init)

        # Metric: pairwise contraction
        _, f_m = C1_pairwise_contraction(traj)
        metric_rates.append(1 if f_m else 0)

        # Ordinal: check if rank order of distances contracts
        if len(traj) >= 15:
            n = len(traj)
            early_dists = pdist(traj[:n//3])
            late_dists = pdist(traj[2*n//3:])
            if len(early_dists) > 3 and len(late_dists) > 3:
                # Rank correlation between early and late
                from scipy.stats import spearmanr
                min_len = min(len(early_dists), len(late_dists))
                rho, _ = spearmanr(early_dists[:min_len], late_dists[:min_len])
                ordinal_rates.append(1 if rho > 0.7 else 0)
            else:
                ordinal_rates.append(0)
        else:
            ordinal_rates.append(0)

    m_rate = np.mean(metric_rates)
    o_rate = np.mean(ordinal_rates)
    print(f"  Metric convergence: {m_rate:.4f}")
    print(f"  Ordinal convergence: {o_rate:.4f}")
    return {"test": "G_nonmetric", "metric": float(m_rate), "ordinal": float(o_rate),
            "survived": o_rate > 0.3}

def test_H_order_without(N=3000):
    """Test H: Order without convergence."""
    print("\n[Test H] Order without convergence...")
    detectors = [
        ("persistence", lambda t: C_persistence(t)),
        ("neighborhood", lambda t: C_neighborhood(t)),
        ("composition", lambda t: C_composition(t)),
        ("selfref", lambda t: C_selfref(t)),
        ("separability", lambda t: C_separability(t)),
        ("distance_struct", lambda t: C_distance(t)),
    ]
    rates = {}
    for name, fn in detectors:
        count = 0
        for i in range(N):
            omega = gen_recursive(i)
            init = np.random.RandomState(i).randn(STATE_DIM) * 0.5
            traj = sim(omega, init)
            try:
                _, f = fn(traj)
                if f: count += 1
            except: pass
        rates[name] = float(count / N)
        print(f"  {name:20s}: {count}/{N} ({100*count/N:.1f}%)")
    first = max(rates, key=rates.get)
    return {"first_without_convergence": first, "rates": rates}


def C_persistence(traj):
    if len(traj) < 10: return False, 0
    c = traj.mean(axis=0)
    d = np.linalg.norm(traj - c, axis=1)
    late = d[2*len(d)//3:]
    return (len(late) > 2 and np.std(late) < np.mean(late) * 0.3), 5

def C_neighborhood(traj):
    if len(traj) < 20: return False, 0
    n = min(25, len(traj))
    D_e = squareform(pdist(traj[:n]))
    D_l = squareform(pdist(traj[-n:]))
    flat_e = D_e[np.triu_indices(n, k=1)]
    flat_l = D_l[np.triu_indices(n, k=1)]
    corr = np.corrcoef(flat_e, flat_l)[0, 1]
    return (corr > 0.5), 5 if corr > 0.5 else 0

def C_composition(traj):
    if len(traj) < 15: return False, 0
    for sl in [3, 4]:
        for d in range(sl * 2, len(traj)):
            sub = traj[d-sl:d]
            for j in range(max(0, d-sl*3), d-sl):
                if np.allclose(sub, traj[j:j+sl], atol=0.2):
                    return True, d
    return False, 0

def C_selfref(traj):
    if len(traj) < 12: return False, 0
    for d in range(6, len(traj)):
        for j in range(max(0, d-20), d-2):
            if np.linalg.norm(traj[d] - traj[j]) < 0.5:
                return True, d
    return False, 0

def C_separability(traj):
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

def C_distance(traj):
    if len(traj) < 15: return False, 0
    n = min(30, len(traj))
    D = squareform(pdist(traj[:n]))
    all_d = D[np.triu_indices(n, k=1)]
    hist, _ = np.histogram(all_d, bins=15)
    hist_n = hist / max(hist.sum(), 1)
    se = entropy(hist_n + 1e-12)
    return (1 - se / np.log(15)) > 0.15, 5


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T045: CONVERGENCE AUDIT (DESTROY T044 IF POSSIBLE)")
    print("=" * 70)
    t0 = time.time()

    rA = test_A_expanding_universes()
    rB = test_B_repel_only()
    rC = test_C_scale_audit()
    rD = test_D_shuffled()
    rE = test_E_null_models()
    rF = test_F_detector_agreement()
    rG = test_G_nonmetric()
    rH = test_H_order_without()

    # ============================================================
    # SAVE
    # ============================================================

    print("\nSaving outputs...")

    tests = [rA, rB, rD, rE, rF, rG]
    tests_df = pd.DataFrame([{k: v for k, v in t.items() if k != "rates" and k != "nulls"} for t in tests])
    tests_df.to_csv(OUT / "t045_convergence_tests.csv", index=False)
    print("  Saved t045_convergence_tests.csv")

    agree_df = pd.DataFrame([{"detector": k, "rate": v} for k, v in rF["rates"].items()])
    agree_df.to_csv(OUT / "t045_detector_agreement.csv", index=False)
    print("  Saved t045_detector_agreement.csv")

    null_df = pd.DataFrame([{"model": k, "rate": v} for k, v in rE["nulls"].items()])
    null_df.to_csv(OUT / "t045_null_models.csv", index=False)
    print("  Saved t045_null_models.csv")

    scale_df = pd.DataFrame([{"dimension": k, "convergence_rate": v} for k, v in rC.items()])
    scale_df.to_csv(OUT / "t045_scale_dependence.csv", index=False)
    print("  Saved t045_scale_dependence.csv")

    nonmetric_df = pd.DataFrame([{"type": "metric", "rate": rG["metric"]},
                                  {"type": "ordinal", "rate": rG["ordinal"]}])
    nonmetric_df.to_csv(OUT / "t045_nonmetric_results.csv", index=False)
    print("  Saved t045_nonmetric_results.csv")

    order_df = pd.DataFrame([{"detector": k, "rate": v} for k, v in rH["rates"].items()])
    order_df.to_csv(OUT / "t045_order_without_convergence.csv", index=False)
    print("  Saved t045_order_without_convergence.csv")

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

    # Fig 1: Survival matrix
    fig, ax = plt.subplots(figsize=(10, 5))
    tests_names = ["A: Expanding", "B: Repel-only", "D: Shuffled", "E: Nulls", "F: Agreement", "G: Nonmetric"]
    survived = [rA["survived"], rB["survived"], rD["survived"], rE["survived"], rF["survived"], rG["survived"]]
    colors = ["#2ecc71" if s else "#e74c3c" for s in survived]
    ax.barh(tests_names, [1]*6, color=colors, edgecolor="white", linewidth=0.3, alpha=0.7)
    for i, (t, s) in enumerate(zip(tests_names, survived)):
        ax.text(0.5, i, "SURVIVES" if s else "KILLED", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")
    ax.set_xlim(0, 1)
    ax.set_title("Convergence survival across audit tests")
    ax.set_xticks([])
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t045_survival_matrix.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t045_survival_matrix.pdf/.png")

    # Fig 2: Null comparison
    fig, ax = plt.subplots(figsize=(8, 4))
    models = ["Real Ω"] + list(rE["nulls"].keys())
    rates_plot = [rE["real"]] + list(rE["nulls"].values())
    colors = ["#2ecc71"] + ["#e74c3c"] * len(rE["nulls"])
    ax.bar(models, rates_plot, color=colors, edgecolor="white", linewidth=0.3)
    ax.set_ylabel("Convergence rate")
    ax.set_title("Convergence rate across models")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t045_null_comparison.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t045_null_comparison.pdf/.png")

    # Fig 3: Scale audit
    fig, ax = plt.subplots(figsize=(8, 4))
    dims = list(rC.keys())
    rates = list(rC.values())
    ax.plot(dims, rates, "o-", color="#555555", markersize=6, lw=1)
    ax.set_xlabel("State-space dimension")
    ax.set_ylabel("Convergence rate")
    ax.set_title("Convergence rate vs dimensionality")
    ax.set_xscale("log", base=2)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t045_scale_audit.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t045_scale_audit.pdf/.png")

    # ============================================================
    # SUMMARY
    # ============================================================

    elapsed = time.time() - t0
    survived_count = sum([rA["survived"], rB["survived"], rD["survived"],
                          rE["survived"], rF["survived"], rG["survived"]])

    print(f"\nRuntime: {elapsed:.1f}s")
    print("\n" + "=" * 70)
    print("T045 RESULTS")
    print("=" * 70)
    print(f"\nTest A (Expanding): {'SURVIVES' if rA['survived'] else 'KILLED'}  (effect={rA['effect']:.4f}, p={rA['p']:.4f})")
    print(f"Test B (Repel):     {'SURVIVES' if rB['survived'] else 'KILLED'}  (effect={rB['effect']:.4f}, p={rB['p']:.4f})")
    print(f"Test D (Shuffled):  {'SURVIVES' if rD['survived'] else 'KILLED'}  (effect={rD['effect']:.4f}, p={rD['p']:.4f})")
    print(f"Test E (Nulls):     {'SURVIVES' if rE['survived'] else 'KILLED'}  (real={rE['real']:.4f})")
    print(f"Test F (Agreement): {'SURVIVES' if rF['survived'] else 'KILLED'}  (agree={rF['high_agreement']:.4f})")
    print(f"Test G (Nonmetric): {'SURVIVES' if rG['survived'] else 'KILLED'}  (ordinal={rG['ordinal']:.4f})")
    print(f"\nTests survived: {survived_count}/6")
    print()
    print(f"Scale dependence: {rC}")
    print()
    print("VERDICT:")
    if survived_count >= 4:
        print("  CONVERGENCE IS GENUINE.")
    elif survived_count >= 2:
        print("  CONVERGENCE IS PARTIALLY GENUINE.")
    else:
        print("  CONVERGENCE IS KILLED.")
    print(f"  First structure without convergence: {rH['first_without_convergence']}")
    print("=" * 70)

    summary = {
        "test_A": {"survived": rA["survived"], "effect": rA["effect"], "p": rA["p"]},
        "test_B": {"survived": rB["survived"], "effect": rB["effect"], "p": rB["p"]},
        "test_D": {"survived": rD["survived"], "effect": rD["effect"], "p": rD["p"]},
        "test_E": {"survived": rE["survived"], "real": rE["real"], "nulls": rE["nulls"]},
        "test_F": {"survived": rF["survived"], "agreement": rF["high_agreement"]},
        "test_G": {"survived": rG["survived"], "metric": rG["metric"], "ordinal": rG["ordinal"]},
        "scale_dependence": rC,
        "tests_survived": survived_count,
        "first_without_convergence": rH["first_without_convergence"],
    }
    with open(OUT / "t045_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSaved t045_summary.json")


if __name__ == "__main__":
    main()
