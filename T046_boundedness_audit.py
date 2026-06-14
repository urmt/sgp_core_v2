#!/usr/bin/env python3
"""
T046: Boundedness Audit (Destroy T045 If Possible)
====================================================
Test whether boundedness/constraint appears before convergence.
T045's convergence may be an artifact of prior constraint.

The earliest structure may be:
  Constraint → Convergence
not
  Convergence → Constraint
"""

import sys, json, warnings, time
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
from scipy.spatial.distance import pdist, squareform
from scipy.stats import entropy as ent, spearmanr
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
N_TEST = 3000
N_SWEEP = 500

# ============================================================
# Ω-UNIVERSES
# ============================================================

def gen_omega(seed, dim=STATE_DIM):
    rng = np.random.RandomState(seed)
    W = rng.randn(dim, dim) * 0.3
    b = rng.randn(dim) * 0.1
    nl = rng.choice([np.tanh, np.sin, lambda x: x**3])
    strength = rng.uniform(0.3, 0.8)
    return lambda x: strength * nl(W @ x + b)

def gen_expanding(seed, growth=1.0, dim=STATE_DIM):
    rng = np.random.RandomState(seed)
    W = rng.randn(dim, dim) * 0.3
    b = rng.randn(dim) * 0.1
    nl = rng.choice([np.tanh, np.sin, lambda x: x**3])
    strength = rng.uniform(0.3, 0.8)
    def step(x):
        base = strength * nl(W @ x + b)
        scale = 1.0 + growth * 0.1
        return base * scale
    return step

def sim(omega, init, depth=MAX_DEPTH):
    traj = [init.copy()]
    x = init.copy()
    for _ in range(depth):
        try:
            x = omega(x)
            x = np.clip(x, -10, 10)
            if np.any(np.isnan(x)): break
            traj.append(x.copy())
        except: break
    return np.array(traj)


# ============================================================
# BOUNDEDNESS DETECTORS (10 detectors)
# ============================================================

def B1_state_growth_rate(traj):
    """Does the volume of visited states grow or shrink?"""
    if len(traj) < 10:
        return False, 0
    ranges = [traj[:, i].max() - traj[:, i].min() for i in range(traj.shape[1])]
    early_range = np.mean([traj[:5, i].max() - traj[:5, i].min() for i in range(traj.shape[1])])
    late_range = np.mean([traj[-5:, i].max() - traj[-5:, i].min() for i in range(traj.shape[1])])
    # Constraint: range stops growing
    if early_range > 0 and late_range < early_range * 1.2:
        for d in range(8, len(traj)):
            r_early = np.mean([traj[:d//2, i].max() - traj[:d//2, i].min() for i in range(traj.shape[1])])
            r_late = np.mean([traj[d//2:d, i].max() - traj[d//2:d, i].min() for i in range(traj.shape[1])])
            if r_late < r_early * 1.2:
                return True, d
    return False, 0

def B2_reachable_state_growth(traj):
    """Does the set of reachable states stop expanding?"""
    if len(traj) < 15:
        return False, 0
    # Count unique states (after binning)
    def count_states(t, bins=10):
        ranges = [(t[:, i].min(), t[:, i].max()) for i in range(t.shape[1])]
        hist, _ = np.histogramdd(t, bins=bins, range=[(r[0]-0.1, r[1]+0.1) for r in ranges])
        return np.sum(hist > 0)
    early_count = count_states(traj[:len(traj)//2])
    late_count = count_states(traj[len(traj)//2:])
    # Constraint: reachable states stop growing
    if late_count <= early_count * 1.3:
        return True, len(traj)//2
    return False, 0

def B3_entropy_growth(traj):
    """Does state entropy stop growing?"""
    if len(traj) < 15:
        return False, 0
    def state_entropy(t):
        ranges = [(t[:, i].min()-0.1, t[:, i].max()+0.1) for i in range(t.shape[1])]
        hist, _ = np.histogramdd(t, bins=5, range=ranges)
        return ent(hist.flatten() + 1e-12)
    early_ent = state_entropy(traj[:len(traj)//2])
    late_ent = state_entropy(traj[len(traj)//2:])
    # Constraint: entropy stops growing (or decreases)
    if late_ent < early_ent * 1.1:
        return True, len(traj)//2
    return False, 0

def B4_transition_freedom(traj):
    """Do transitions become more constrained over time?"""
    if len(traj) < 15:
        return False, 0
    # Compute transition distance variance at different times
    early_trans = [np.linalg.norm(traj[i+1] - traj[i]) for i in range(len(traj)//3)]
    late_trans = [np.linalg.norm(traj[i+1] - traj[i]) for i in range(2*len(traj)//3, len(traj)-1)]
    if early_trans and late_trans:
        early_cv = np.std(early_trans) / max(np.mean(early_trans), 1e-12)
        late_cv = np.std(late_trans) / max(np.mean(late_trans), 1e-12)
        # Constraint: transition variability decreases
        if late_cv < early_cv * 0.7:
            return True, len(traj)//3
    return False, 0

def B5_possibility_elimination(traj):
    """Does the set of possible next-states shrink?"""
    if len(traj) < 20:
        return False, 0
    # Compute "next-state spread" at different times
    window = 5
    spreads = []
    for i in range(len(traj) - window):
        next_states = []
        for j in range(i+1, min(i+window+1, len(traj))):
            next_states.append(traj[j])
        if next_states:
            spread = np.mean(pdist(next_states))
            spreads.append(spread)
    if len(spreads) > 10:
        early_spread = np.mean(spreads[:len(spreads)//3])
        late_spread = np.mean(spreads[2*len(spreads)//3:])
        if late_spread < early_spread * 0.7:
            return True, len(traj)//3
    return False, 0

def B6_forbidden_transition_accumulation(traj):
    """Do forbidden transitions accumulate over time?"""
    if len(traj) < 20:
        return False, 0
    # Bin states and count transitions
    n_bins = 5
    ranges = [(traj[:, i].min()-0.1, traj[:, i].max()+0.1) for i in range(traj.shape[1])]
    def get_bin(state):
        return tuple(np.clip(
            np.digitize(state, [ranges[i][0] + j*(ranges[i][1]-ranges[i][0])/n_bins
                               for j in range(n_bins+1)]) - 1, 0, n_bins-1) for i in range(len(state)))
    # Early transitions
    early_trans = set()
    for i in range(min(10, len(traj)-1)):
        early_trans.add((get_bin(traj[i]), get_bin(traj[i+1])))
    # Late transitions
    late_trans = set()
    for i in range(len(traj)//2, len(traj)-1):
        late_trans.add((get_bin(traj[i]), get_bin(traj[i+1])))
    # Forbidden: transitions in early but not in late
    forbidden_early = early_trans - late_trans
    # Constraint: forbidden transitions accumulate
    if len(forbidden_early) > 0:
        return True, len(traj)//2
    return False, 0

def B7_accessible_volume_ratio(traj):
    """Ratio of accessible to total possible volume shrinks."""
    if len(traj) < 15:
        return False, 0
    total_vol = np.prod([traj[:, i].max() - traj[:, i].min() + 1e-12 for i in range(traj.shape[1])])
    early_vol = np.prod([traj[:len(traj)//2, i].max() - traj[:len(traj)//2, i].min() + 1e-12
                         for i in range(traj.shape[1])])
    # Constraint: early accessible volume is small relative to total
    if total_vol > 0 and early_vol / total_vol < 0.5:
        return True, len(traj)//2
    return False, 0

def B8_constraint_persistence(traj):
    """Do constraints persist across time?"""
    if len(traj) < 20:
        return False, 0
    # Check if trajectory stays within a hyperrectangle
    bounds_lo = np.percentile(traj, 10, axis=0)
    bounds_hi = np.percentile(traj, 90, axis=0)
    # Count points outside bounds
    outside_early = np.sum(np.any(traj[:len(traj)//2] < bounds_lo, axis=1) |
                           np.any(traj[:len(traj)//2] > bounds_hi, axis=1))
    outside_late = np.sum(np.any(traj[len(traj)//2:] < bounds_lo, axis=1) |
                          np.any(traj[len(traj)//2:] > bounds_hi, axis=1))
    # Constraint: few points escape bounds
    early_frac = outside_early / max(len(traj)//2, 1)
    late_frac = outside_late / max(len(traj)//2, 1)
    if early_frac < 0.2 and late_frac < 0.2:
        return True, 5
    return False, 0

def B9_constraint_reproduction(traj):
    """Are constraints reproduced across trajectory segments?"""
    if len(traj) < 20:
        return False, 0
    # Compute bounds for first and second half
    bounds1 = (np.percentile(traj[:len(traj)//2], 10, axis=0),
               np.percentile(traj[:len(traj)//2], 90, axis=0))
    bounds2 = (np.percentile(traj[len(traj)//2:], 10, axis=0),
               np.percentile(traj[len(traj)//2:], 90, axis=0))
    # Check if bounds overlap significantly
    overlap = np.mean(np.maximum(0, np.minimum(bounds1[1], bounds2[1]) -
                                       np.maximum(bounds1[0], bounds2[0])))
    total = np.mean(bounds1[1] - bounds1[0])
    if total > 0 and overlap / total > 0.5:
        return True, len(traj)//2
    return False, 0

def B10_possibility_reduction_rate(traj):
    """Rate at which possibilities are eliminated."""
    if len(traj) < 15:
        return False, 0
    # Track unique states over time
    seen = set()
    elimination_rate = []
    for i in range(len(traj)):
        state_bin = tuple(np.round(traj[i], 1))
        if state_bin in seen:
            elimination_rate.append(1)
        else:
            seen.add(state_bin)
            elimination_rate.append(0)
    # Constraint: elimination rate increases over time
    if len(elimination_rate) > 10:
        early_rate = np.mean(elimination_rate[:len(elimination_rate)//3])
        late_rate = np.mean(elimination_rate[2*len(elimination_rate)//3:])
        if late_rate > early_rate * 1.5 and late_rate > 0.3:
            return True, len(traj)//3
    return False, 0


CONSTRAINT_DETECTORS = [
    ("B1_growth_rate", B1_state_growth_rate),
    ("B2_reachable", B2_reachable_state_growth),
    ("B3_entropy", B3_entropy_growth),
    ("B4_transition_freedom", B4_transition_freedom),
    ("B5_possibility_elim", B5_possibility_elimination),
    ("B6_forbidden_trans", B6_forbidden_transition_accumulation),
    ("B7_volume_ratio", B7_accessible_volume_ratio),
    ("B8_constraint_persist", B8_constraint_persistence),
    ("B9_constraint_repro", B9_constraint_reproduction),
    ("B10_elimination_rate", B10_possibility_reduction_rate),
]


# ============================================================
# CONVERGENCE DETECTOR (from T044/045)
# ============================================================

def convergence_detector(traj):
    """C1: Pairwise distance contraction."""
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


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T046: BOUNDEDNESS AUDIT (DESTROY T045 IF POSSIBLE)")
    print("=" * 70)
    print("Question: Which appears first — convergence or constraint?")
    print("=" * 70)
    t0 = time.time()

    # ============================================================
    # TEST A-B: Detect constraint and convergence in all universes
    # ============================================================

    print(f"\n[Phase 1] Detecting constraint and convergence ({N_TEST} universes)...")
    events = []

    for uid in range(N_TEST):
        if uid % 500 == 0:
            print(f"  Progress: {uid}/{N_TEST}", flush=True)

        omega = gen_omega(uid)
        init = np.random.RandomState(uid).randn(STATE_DIM) * 0.5
        traj = sim(omega, init)

        # Constraint detectors
        for det_name, det_fn in CONSTRAINT_DETECTORS:
            try:
                fired, depth = det_fn(traj)
                if fired:
                    events.append((uid, f"constraint_{det_name}", depth))
            except: pass

        # Convergence detector
        try:
            fired, depth = convergence_detector(traj)
            if fired:
                events.append((uid, "convergence", depth))
        except: pass

    # Compute detection rates
    all_detectors = [f"constraint_{name}" for name, _ in CONSTRAINT_DETECTORS] + ["convergence"]
    rates = {}
    for det in all_detectors:
        count = sum(1 for uid, d, _ in events if d == det)
        rates[det] = count / N_TEST
        print(f"  {det:30s}: {count}/{N_TEST} ({100*count/N_TEST:.1f}%)")

    # ============================================================
    # TEST B: Pairwise order P(constraint_i before convergence)
    # ============================================================

    print("\n[Phase 2] Pairwise order analysis...")

    # Get first depth per universe per detector
    universe_depths = defaultdict(dict)
    for uid, det, depth in events:
        if det not in universe_depths[uid] or depth < universe_depths[uid][det]:
            universe_depths[uid][det] = depth

    # For each constraint detector, compute P(Bi before convergence)
    order_results = []
    for det_name, _ in CONSTRAINT_DETECTORS:
        constraint_key = f"constraint_{det_name}"
        pairs = []
        for uid, depths in universe_depths.items():
            if constraint_key in depths and "convergence" in depths:
                pairs.append(depths[constraint_key] < depths["convergence"])
        if pairs:
            p_before = np.mean(pairs)
            order_results.append({
                "detector": det_name,
                "p_constraint_before_convergence": float(p_before),
                "n_universes": len(pairs),
            })
            print(f"  {det_name:30s}: P(constraint before convergence) = {p_before:.4f}")

    # ============================================================
    # TEST C: Expanding universe sweep
    # ============================================================

    print("\n[Phase 3] Expanding universe sweep...")
    growth_exponents = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
    sweep_results = []

    for growth in growth_exponents:
        constraint_rates = []
        convergence_rates = []
        for i in range(N_SWEEP):
            omega = gen_expanding(i, growth=growth)
            init = np.random.RandomState(i).randn(STATE_DIM) * 0.5
            traj = sim(omega, init)

            # Constraint
            c_fired = False
            for _, det_fn in CONSTRAINT_DETECTORS:
                try:
                    f, _ = det_fn(traj)
                    if f: c_fired = True
                except: pass
            constraint_rates.append(1 if c_fired else 0)

            # Convergence
            try:
                f, _ = convergence_detector(traj)
                convergence_rates.append(1 if f else 0)
            except:
                convergence_rates.append(0)

        c_rate = np.mean(constraint_rates)
        conv_rate = np.mean(convergence_rates)
        sweep_results.append({
            "growth": growth,
            "constraint_rate": float(c_rate),
            "convergence_rate": float(conv_rate),
        })
        print(f"  growth={growth:5.1f}: constraint={c_rate:.3f}, convergence={conv_rate:.3f}")

    # ============================================================
    # TEST D-E: Constraint-without-convergence & vice versa
    # ============================================================

    print("\n[Phase 4] Co-occurrence analysis...")

    n_constraint_only = 0
    n_convergence_only = 0
    n_both = 0
    n_neither = 0

    for uid in range(N_TEST):
        has_constraint = any(d.startswith("constraint_") for _, d, _ in events if _ == uid)
        has_convergence = any(d == "convergence" for _, d, _ in events if _ == uid)

        if has_constraint and not has_convergence:
            n_constraint_only += 1
        elif has_convergence and not has_constraint:
            n_convergence_only += 1
        elif has_constraint and has_convergence:
            n_both += 1
        else:
            n_neither += 1

    print(f"  Constraint only:    {n_constraint_only}/{N_TEST} ({100*n_constraint_only/N_TEST:.1f}%)")
    print(f"  Convergence only:   {n_convergence_only}/{N_TEST} ({100*n_convergence_only/N_TEST:.1f}%)")
    print(f"  Both:               {n_both}/{N_TEST} ({100*n_both/N_TEST:.1f}%)")
    print(f"  Neither:            {n_neither}/{N_TEST} ({100*n_neither/N_TEST:.1f}%)")

    # ============================================================
    # TEST G: Information/entropy audit
    # ============================================================

    print("\n[Phase 5] Entropy audit...")

    entropy_results = []
    for uid in range(min(500, N_TEST)):
        omega = gen_omega(uid)
        init = np.random.RandomState(uid).randn(STATE_DIM) * 0.5
        traj = sim(omega, init)

        if len(traj) < 10:
            continue

        # Compute entropy at different depths
        depths_to_check = [5, 10, 15, 20, 25, 30, 35, 40]
        entropies = []
        for d in depths_to_check:
            if d < len(traj):
                ranges = [(traj[:d, i].min()-0.1, traj[:d, i].max()+0.1) for i in range(traj.shape[1])]
                hist, _ = np.histogramdd(traj[:d], bins=5, range=ranges)
                e = ent(hist.flatten() + 1e-12)
                entropies.append(e)
            else:
                entropies.append(np.nan)

        # Does entropy decrease? (constraint)
        valid_ents = [e for e in entropies if not np.isnan(e)]
        if len(valid_ents) >= 3:
            entropy_decreasing = valid_ents[-1] < valid_ents[0] * 0.8
        else:
            entropy_decreasing = False

        entropy_results.append({
            "uid": uid,
            "entropy_decreasing": entropy_decreasing,
            "early_entropy": valid_ents[0] if valid_ents else 0,
            "late_entropy": valid_ents[-1] if valid_ents else 0,
        })

    ent_df = pd.DataFrame(entropy_results)
    n_ent_decreasing = ent_df["entropy_decreasing"].sum()
    print(f"  Universes with entropy decrease: {n_ent_decreasing}/{len(ent_df)} ({100*n_ent_decreasing/max(len(ent_df),1):.1f}%)")

    # ============================================================
    # SAVE
    # ============================================================

    print("\nSaving outputs...")

    # t046_constraint_events.csv
    constraint_events = [(uid, det, depth) for uid, det, depth in events if det.startswith("constraint_")]
    pd.DataFrame(constraint_events, columns=["universe_id", "detector", "depth"]).to_csv(
        OUT / "t046_constraint_events.csv", index=False)
    print(f"  Saved t046_constraint_events.csv ({len(constraint_events)} events)")

    # t046_order_matrix.csv
    pd.DataFrame(order_results).to_csv(OUT / "t046_order_matrix.csv", index=False)
    print("  Saved t046_order_matrix.csv")

    # t046_constraint_vs_convergence.csv
    cvc_df = pd.DataFrame([{
        "constraint_only": n_constraint_only,
        "convergence_only": n_convergence_only,
        "both": n_both,
        "neither": n_neither,
    }])
    cvc_df.to_csv(OUT / "t046_constraint_vs_convergence.csv", index=False)
    print("  Saved t046_constraint_vs_convergence.csv")

    # t046_entropy_audit.csv
    ent_df.to_csv(OUT / "t046_entropy_audit.csv", index=False)
    print("  Saved t046_entropy_audit.csv")

    # t046_causal_necessity.csv
    causal_df = pd.DataFrame(sweep_results)
    causal_df.to_csv(OUT / "t046_causal_necessity.csv", index=False)
    print("  Saved t046_causal_necessity.csv")

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

    # Fig 1: Emergence order (constraint vs convergence)
    fig, ax = plt.subplots(figsize=(10, 6))
    detectors = [r["detector"] for r in order_results] + ["convergence"]
    p_before = [r["p_constraint_before_convergence"] for r in order_results] + [0.5]
    colors = ["#2ecc71" if p > 0.5 else "#e74c3c" for p in p_before]
    y = np.arange(len(detectors))
    ax.barh(y, p_before, color=colors, edgecolor="white", linewidth=0.3)
    ax.set_yticks(y)
    ax.set_yticklabels(detectors, fontsize=6)
    ax.set_xlabel("P(constraint before convergence)")
    ax.axvline(0.5, color="black", ls="--", lw=0.5, label="50% threshold")
    ax.set_title("Pairwise order: constraint detectors vs convergence")
    ax.legend(frameon=False)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t046_emergence_order.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t046_emergence_order.pdf/.png")

    # Fig 2: Constraint vs convergence co-occurrence
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    ax = axes[0]
    cats = ["Constraint only", "Convergence only", "Both", "Neither"]
    vals = [n_constraint_only, n_convergence_only, n_both, n_neither]
    colors = ["#2ecc71", "#3498db", "#f39c12", "#e74c3c"]
    ax.bar(cats, vals, color=colors, edgecolor="white", linewidth=0.3)
    ax.set_ylabel("Count")
    ax.set_title("Co-occurrence of constraint and convergence")
    plt.xticks(rotation=30, ha="right")

    ax = axes[1]
    growth = [r["growth"] for r in sweep_results]
    c_rates = [r["constraint_rate"] for r in sweep_results]
    conv_rates = [r["convergence_rate"] for r in sweep_results]
    ax.plot(growth, c_rates, "o-", color="#2ecc71", label="Constraint")
    ax.plot(growth, conv_rates, "s-", color="#e74c3c", label="Convergence")
    ax.set_xlabel("Growth exponent")
    ax.set_ylabel("Detection rate")
    ax.set_title("Expanding universe sweep")
    ax.legend(frameon=False)
    ax.set_xscale("log", base=2)

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t046_constraint_convergence.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t046_constraint_convergence.pdf/.png")

    # Fig 3: Entropy flow
    fig, ax = plt.subplots(figsize=(8, 4))
    if len(ent_df) > 0:
        early = ent_df["early_entropy"].dropna()
        late = ent_df["late_entropy"].dropna()
        ax.hist(early - late, bins=30, color="#555555", edgecolor="white", linewidth=0.3, alpha=0.85)
        ax.axvline(0, color="red", ls="--", lw=0.8, label="Zero (no change)")
        ax.set_xlabel("Entropy change (early - late)")
        ax.set_ylabel("Count")
        ax.set_title("Entropy flow: positive = constraint, negative = expansion")
        ax.legend(frameon=False)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t046_entropy_flow.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t046_entropy_flow.pdf/.png")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    elapsed = time.time() - t0

    # Determine which is earlier
    n_constraint_first = sum(1 for r in order_results if r["p_constraint_before_convergence"] > 0.5)
    n_convergence_first = sum(1 for r in order_results if r["p_constraint_before_convergence"] < 0.5)
    n_tied = len(order_results) - n_constraint_first - n_convergence_first

    # Expanding sweep: which collapses first?
    expanding_collapse = []
    for r in sweep_results:
        if r["constraint_rate"] < 0.3 and r["convergence_rate"] >= 0.3:
            expanding_collapse.append(("constraint_first", r["growth"]))
        elif r["convergence_rate"] < 0.3 and r["constraint_rate"] >= 0.3:
            expanding_collapse.append(("convergence_first", r["growth"]))

    print(f"\nRuntime: {elapsed:.1f}s")
    print("\n" + "=" * 70)
    print("T046 RESULTS")
    print("=" * 70)
    print(f"\nOrder analysis:")
    print(f"  Constraint before convergence: {n_constraint_first}/{len(order_results)} detectors")
    print(f"  Convergence before constraint: {n_convergence_first}/{len(order_results)} detectors")
    print(f"  Tied: {n_tied}/{len(order_results)}")
    print()
    print(f"Co-occurrence:")
    print(f"  Constraint only: {n_constraint_only} ({100*n_constraint_only/N_TEST:.1f}%)")
    print(f"  Convergence only: {n_convergence_only} ({100*n_convergence_only/N_TEST:.1f}%)")
    print(f"  Both: {n_both} ({100*n_both/N_TEST:.1f}%)")
    print()
    print(f"Entropy: {n_ent_decreasing}/{len(ent_df)} ({100*n_ent_decreasing/max(len(ent_df),1):.1f}%) show entropy decrease")
    print()
    print("EXPANDING SWEEP:")
    for r in sweep_results:
        print(f"  growth={r['growth']:5.1f}: constraint={r['constraint_rate']:.3f}, convergence={r['convergence_rate']:.3f}")

    print()
    print("VERDICT:")
    if n_constraint_first > n_convergence_first:
        print("  CONSTRAINT APPEARS BEFORE CONVERGENCE.")
        print("  T045 was partially wrong: convergence depends on prior constraint.")
        print("  The earliest structure is: CONSTRAINT / POSSIBILITY RESTRICTION.")
    elif n_convergence_first > n_constraint_first:
        print("  CONVERGENCE APPEARS BEFORE CONSTRAINT.")
        print("  T045 was correct: convergence is fundamental.")
    else:
        print("  MIXED: constraint and convergence are co-emergent.")

    print()
    print("WHAT IS THE EARLIEST UNAVOIDABLE STRUCTURE?")
    if n_constraint_first >= n_convergence_first:
        print("  The first persistent restriction on possibility itself.")
        print("  Not convergence. Not points. Not distinction.")
        print("  RESTRICTION OF POSSIBILITY SPACE.")
    else:
        print("  CONVERGENCE — dynamics contract toward common regions.")
    print("=" * 70)

    # Save summary
    summary = {
        "n_universes": N_TEST,
        "constraint_before_convergence": n_constraint_first,
        "convergence_before_constraint": n_convergence_first,
        "tied": n_tied,
        "constraint_only": n_constraint_only,
        "convergence_only": n_convergence_only,
        "both": n_both,
        "neither": n_neither,
        "entropy_decreasing_fraction": float(n_ent_decreasing / max(len(ent_df), 1)),
        "expanding_sweep": sweep_results,
        "order_results": order_results,
        "verdict": "CONSTRAINT_FIRST" if n_constraint_first > n_convergence_first else "CONVERGENCE_FIRST" if n_convergence_first > n_constraint_first else "CO_EMERGENT",
    }
    with open(OUT / "t046_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSaved t046_summary.json")


if __name__ == "__main__":
    main()
