#!/usr/bin/env python3
"""
T037-AUDIT: Assumption Ablation for Primitive Interaction Genesis
==================================================================
Determine whether T037's geometry-emergence result is genuine
or caused by hidden assumptions.

Method: Remove ONE primitive at a time, recompute emergence.
"""

import sys, json, warnings, time
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from scipy.stats import pearsonr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
np.random.seed(42)

ROOT = Path("/home/student/sgp_core_v2")
OUT = ROOT / "sfh_sgp_ood_outputs"
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

MAX_DEPTH = 25
N_SYMBOLS = 8
N_UNIVERSES = 300  # per ablation condition
N_TRIALS = 3       # multiple trials per condition for variance

# ============================================================
# PRIMITIVE ASSUMPTIONS (8 total)
# ============================================================

ASSUMPTIONS = {
    "symbols": "Discrete symbolic objects (integers 0-N)",
    "identity": "Symbols have fixed identity (hashable, stable)",
    "distinction": "Different symbols are fully distinguishable",
    "recursion": "Rules apply iteratively to their own outputs",
    "state_persistence": "Output of step t becomes input of step t+1",
    "rule_tables": "Deterministic input->output mapping",
    "ordering": "States are ordered sequences (position matters)",
    "memory": "Full trajectory is retained",
}

# ============================================================
# ABLATION SIMULATORS
# ============================================================

def make_rule(seed, n_sym=N_SYMBOLS):
    """Generate a random rule table."""
    rng = np.random.RandomState(seed)
    symbols = list(range(n_sym))
    rule = {}
    for _ in range(rng.randint(2, n_sym + 1)):
        s = symbols[rng.randint(0, len(symbols))]
        o = symbols[rng.randint(0, len(symbols))]
        rule[s] = o
    for _ in range(rng.randint(0, min(n_sym * n_sym, 15))):
        a = symbols[rng.randint(0, len(symbols))]
        b = symbols[rng.randint(0, len(symbols))]
        o = symbols[rng.randint(0, len(symbols))]
        rule[(a, b)] = o
    return rule


def apply_rule(rule, state):
    """Standard rule application."""
    if len(state) == 0:
        return state
    if len(state) == 1:
        return (rule.get(state[0], state[0]),)
    a, b = state[0], state[1]
    key = (a, b)
    if key in rule:
        return (rule[key],) + state[2:]
    return (rule.get(a, a), rule.get(b, b)) + state[2:]


def simulate_standard(seed, max_depth=MAX_DEPTH):
    """Standard T037 simulation (baseline)."""
    rng = np.random.RandomState(seed)
    rule = make_rule(seed)
    n0 = rng.randint(1, 4)
    initial = tuple(rng.randint(0, N_SYMBOLS) for _ in range(n0))
    traj = [initial]
    current = initial
    for _ in range(max_depth):
        try:
            nxt = apply_rule(rule, current)
            if len(nxt) > 12:
                nxt = nxt[:12]
            if len(nxt) == 0:
                nxt = (0,)
            traj.append(nxt)
            current = nxt
        except Exception:
            break
    return traj


def simulate_ablate_symbols(seed, max_depth=MAX_DEPTH):
    """Remove discrete symbols: use continuous values in [0,1]."""
    rng = np.random.RandomState(seed)
    rule = {}
    for _ in range(12):
        s = (rng.rand(),)
        o = (rng.rand(),)
        rule[s] = o
    for _ in range(8):
        a = (rng.rand(),)
        b = (rng.rand(),)
        o = (rng.rand(),)
        rule[(a, b)] = o

    n0 = rng.randint(1, 3)
    initial = tuple((rng.rand(),) for _ in range(n0))
    traj = [initial]
    current = initial
    for _ in range(max_depth):
        try:
            nxt = apply_rule(rule, current)
            if len(nxt) > 8:
                nxt = nxt[:8]
            if len(nxt) == 0:
                nxt = ((0.5),)
            traj.append(nxt)
            current = nxt
        except Exception:
            break
    return traj


def simulate_ablate_identity(seed, max_depth=MAX_DEPTH):
    """Noisy identity: symbols sometimes merge with neighbors."""
    rng = np.random.RandomState(seed)
    rule = make_rule(seed)
    merge_prob = 0.15
    n0 = rng.randint(1, 4)
    initial = tuple(rng.randint(0, N_SYMBOLS) for _ in range(n0))
    traj = [initial]
    current = initial
    for _ in range(max_depth):
        try:
            nxt = apply_rule(rule, current)
            # Noisy identity: randomly merge adjacent symbols
            noisy = []
            for s in nxt:
                if rng.rand() < merge_prob:
                    noisy.append(max(0, min(N_SYMBOLS - 1, s + rng.choice([-1, 1]))))
                else:
                    noisy.append(s)
            nxt = tuple(noisy)
            if len(nxt) > 12:
                nxt = nxt[:12]
            if len(nxt) == 0:
                nxt = (0,)
            traj.append(nxt)
            current = nxt
        except Exception:
            break
    return traj


def simulate_ablate_distinction(seed, max_depth=MAX_DEPTH):
    """Symbols become partially indistinguishable (blurred)."""
    rng = np.random.RandomState(seed)
    rule = make_rule(seed)
    blur_prob = 0.2
    n0 = rng.randint(1, 4)
    initial = tuple(rng.randint(0, N_SYMBOLS) for _ in range(n0))
    traj = [initial]
    current = initial
    for _ in range(max_depth):
        try:
            nxt = apply_rule(rule, current)
            # Blurred distinction: randomly replace with average of neighbors
            blurred = []
            for s in nxt:
                if rng.rand() < blur_prob:
                    blurred.append(int(round(np.clip(s + rng.randn() * 1.5, 0, N_SYMBOLS - 1))))
                else:
                    blurred.append(s)
            nxt = tuple(blurred)
            if len(nxt) > 12:
                nxt = nxt[:12]
            if len(nxt) == 0:
                nxt = (0,)
            traj.append(nxt)
            current = nxt
        except Exception:
            break
    return traj


def simulate_ablate_recursion(seed, max_depth=MAX_DEPTH):
    """Remove recursion: rules apply only once, then random walk."""
    rng = np.random.RandomState(seed)
    rule = make_rule(seed)
    n0 = rng.randint(1, 4)
    initial = tuple(rng.randint(0, N_SYMBOLS) for _ in range(n0))
    traj = [initial]
    # First application
    nxt = apply_rule(rule, initial)
    if len(nxt) > 12:
        nxt = nxt[:12]
    traj.append(nxt)
    # Then random walk (no rule application)
    current = nxt
    for _ in range(max_depth - 1):
        # Random perturbation
        noisy = list(current)
        if len(noisy) > 0:
            idx = rng.randint(0, len(noisy))
            noisy[idx] = rng.randint(0, N_SYMBOLS)
        nxt = tuple(noisy)
        if len(nxt) > 12:
            nxt = nxt[:12]
        traj.append(nxt)
        current = nxt
    return traj


def simulate_ablate_state_persistence(seed, max_depth=MAX_DEPTH):
    """No state persistence: each step starts from fresh random state."""
    rng = np.random.RandomState(seed)
    rule = make_rule(seed)
    traj = []
    for _ in range(max_depth + 1):
        n = rng.randint(1, 4)
        state = tuple(rng.randint(0, N_SYMBOLS) for _ in range(n))
        traj.append(state)
    return traj


def simulate_ablate_rule_tables(seed, max_depth=MAX_DEPTH):
    """No deterministic rules: fully stochastic transitions."""
    rng = np.random.RandomState(seed)
    n0 = rng.randint(1, 4)
    initial = tuple(rng.randint(0, N_SYMBOLS) for _ in range(n0))
    traj = [initial]
    for _ in range(max_depth):
        n = rng.randint(1, 4)
        nxt = tuple(rng.randint(0, N_SYMBOLS) for _ in range(n))
        traj.append(nxt)
    return traj


def simulate_ablate_ordering(seed, max_depth=MAX_DEPTH):
    """States are SETS (order doesn't matter)."""
    rng = np.random.RandomState(seed)
    rule = make_rule(seed)
    n0 = rng.randint(1, 4)
    initial = tuple(sorted(rng.randint(0, N_SYMBOLS) for _ in range(n0)))
    traj = [initial]
    current = initial
    for _ in range(max_depth):
        try:
            nxt = apply_rule(rule, current)
            # Enforce ordering (set semantics)
            nxt = tuple(sorted(nxt))
            if len(nxt) > 12:
                nxt = nxt[:12]
            if len(nxt) == 0:
                nxt = (0,)
            traj.append(nxt)
            current = nxt
        except Exception:
            break
    return traj


def simulate_ablate_memory(seed, max_depth=MAX_DEPTH):
    """No memory: only last 2 states retained (Markov order 1)."""
    rng = np.random.RandomState(seed)
    rule = make_rule(seed)
    n0 = rng.randint(1, 4)
    initial = tuple(rng.randint(0, N_SYMBOLS) for _ in range(n0))
    traj = [initial]
    current = initial
    prev = None
    for _ in range(max_depth):
        try:
            # Only last 2 states available
            context = current if prev is None else prev + current
            if len(context) > 12:
                context = context[:12]
            nxt = apply_rule(rule, context)
            if len(nxt) > 12:
                nxt = nxt[:12]
            if len(nxt) == 0:
                nxt = (0,)
            traj.append(nxt)
            prev = current
            current = nxt
        except Exception:
            break
    return traj


ABLATION_SIMS = {
    "baseline": simulate_standard,
    "no_symbols": simulate_ablate_symbols,
    "no_identity": simulate_ablate_identity,
    "no_distinction": simulate_ablate_distinction,
    "no_recursion": simulate_ablate_recursion,
    "no_state_persistence": simulate_ablate_state_persistence,
    "no_rule_tables": simulate_ablate_rule_tables,
    "no_ordering": simulate_ablate_ordering,
    "no_memory": simulate_ablate_memory,
}

# ============================================================
# EMERGENCE DETECTION (same as T037)
# ============================================================

def detect_distinction(trajectory):
    state_counts = Counter(trajectory)
    if len(state_counts) == 0:
        return 0.0
    repeated = sum(1 for c in state_counts.values() if c >= 2)
    return repeated / len(state_counts)

def detect_persistence(trajectory):
    if len(trajectory) < 2:
        return 0.0
    max_run = 1
    run = 1
    for i in range(1, len(trajectory)):
        if trajectory[i] == trajectory[i-1]:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 1
    return min(max_run / 5.0, 1.0)

def detect_composition(trajectory):
    if len(trajectory) < 3:
        return 0.0
    count = 0
    for i in range(1, len(trajectory)):
        prev = set(trajectory[i-1])
        curr = set(trajectory[i])
        if len(curr) > 1 and curr != prev:
            count += 1
    return count / max(len(trajectory) - 1, 1)

def detect_closure(trajectory):
    if len(trajectory) < 3:
        return 0.0
    seen = set()
    loops = 0
    for s in trajectory:
        if s in seen:
            loops += 1
        seen.add(s)
    return min(loops / max(len(trajectory), 1), 1.0)

def detect_arithmetic(trajectory):
    lengths = [len(s) for s in trajectory]
    unique_lengths = len(set(lengths))
    return max(0, min((unique_lengths - 1) / 4.0, 1.0))

def detect_geometry(trajectory):
    """
    D6: Adjacency relations emerge without coordinates.
    Score: whether state transitions are non-random
    (measured by comparing to shuffled baseline).
    """
    if len(trajectory) < 10:
        return 0.0
    state_ids = [hash(s) % 30 for s in trajectory]
    n_states = len(set(state_ids))
    if n_states < 3:
        return 0.0

    # Build transition matrix
    mat_size = min(n_states, 30)
    trans = np.zeros((mat_size, mat_size))
    for i in range(len(state_ids) - 1):
        a = state_ids[i] % mat_size
        b = state_ids[i+1] % mat_size
        trans[a, b] += 1

    # Normalize rows
    row_sums = trans.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    trans_norm = trans / row_sums

    # Compare to shuffled baseline (10 random shuffles)
    real_structuredness = np.std(trans_norm[trans_norm.sum(axis=1) > 0])
    shuffled_stds = []
    for _ in range(10):
        flat = trans_norm.flatten()
        np.random.shuffle(flat)
        shuffled = flat.reshape(trans_norm.shape)
        shuffled_stds.append(np.std(shuffled[shuffled.sum(axis=1) > 0]))

    mean_shuffled = np.mean(shuffled_stds)
    if mean_shuffled == 0:
        return 0.0

    # Score: how much more structured than random
    ratio = real_structuredness / mean_shuffled
    score = max(0, min(1, (ratio - 1.0) / 2.0))  # ratio=3 means perfect
    return score

def detect_dimension(trajectory):
    if len(trajectory) < 5:
        return 0.0
    points = np.linspace(3, len(trajectory), min(8, len(trajectory)//2), dtype=int)
    counts = [(n, len(set(trajectory[:n]))) for n in points]
    if len(counts) < 3:
        return 0.0
    log_L = np.log([c[0] for c in counts])
    log_N = np.log([max(c[1], 1) for c in counts])
    try:
        d = np.polyfit(log_L, log_N, 1)[0]
        if 0.3 <= d <= 4.0:
            return max(0, 1.0 - abs(d - 1.5) / 2.5)
    except Exception:
        pass
    return 0.0


def score_trajectory(trajectory):
    return {
        "distinction": detect_distinction(trajectory),
        "persistence": detect_persistence(trajectory),
        "composition": detect_composition(trajectory),
        "closure": detect_closure(trajectory),
        "arithmetic": detect_arithmetic(trajectory),
        "geometry": detect_geometry(trajectory),
        "dimension": detect_dimension(trajectory),
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T037-AUDIT: ASSUMPTION ABLATION")
    print("=" * 70)
    t0 = time.time()

    conditions = list(ABLATION_SIMS.keys())
    all_results = []

    for cond_name in conditions:
        sim_fn = ABLATION_SIMS[cond_name]
        print(f"\n[{cond_name}] Running {N_UNIVERSES} universes × {N_TRIALS} trials...")

        trial_scores = {k: [] for k in ["distinction", "persistence", "composition",
                                          "closure", "arithmetic", "geometry", "dimension"]}

        for trial in range(N_TRIALS):
            seed_offset = trial * 10000
            for i in range(N_UNIVERSES):
                seed = seed_offset + i
                try:
                    traj = sim_fn(seed)
                    sc = score_trajectory(traj)
                    for k in trial_scores:
                        trial_scores[k].append(sc[k])
                except Exception:
                    for k in trial_scores:
                        trial_scores[k].append(0.0)

        # Compute means and stds
        row = {"condition": cond_name}
        for k in trial_scores:
            vals = np.array(trial_scores[k])
            row[f"{k}_mean"] = float(np.mean(vals))
            row[f"{k}_std"] = float(np.std(vals))
        all_results.append(row)
        print(f"  geometry={row['geometry_mean']:.4f}±{row['geometry_std']:.4f}  "
              f"distinction={row['distinction_mean']:.4f}  "
              f"persistence={row['persistence_mean']:.4f}")

    # ============================================================
    # SURVIVAL MATRIX
    # ============================================================

    print("\nBuilding survival matrix...")
    baseline = [r for r in all_results if r["condition"] == "baseline"][0]

    survival_rows = []
    for r in all_results:
        if r["condition"] == "baseline":
            continue
        row = {"ablation": r["condition"]}
        for prop in ["distinction", "persistence", "composition", "closure",
                      "arithmetic", "geometry", "dimension"]:
            base_val = baseline[f"{prop}_mean"]
            abl_val = r[f"{prop}_mean"]
            survival = abl_val / max(base_val, 1e-12)
            row[f"{prop}_survival"] = float(survival)
            row[f"{prop}_retained_pct"] = float(survival * 100)

        # Overall survival score
        props = ["distinction", "persistence", "composition", "closure",
                 "arithmetic", "geometry", "dimension"]
        mean_survival = np.mean([row[f"{p}_survival"] for p in props])
        row["mean_survival"] = float(mean_survival)

        # Causal necessity: how much does geometry drop?
        row["geometry_necessity"] = float(1.0 - row["geometry_survival"])

        survival_rows.append(row)

    survival_df = pd.DataFrame(survival_rows)
    survival_df = survival_df.sort_values("mean_survival", ascending=True)

    # ============================================================
    # RANK BY CAUSAL NECESSITY
    # ============================================================

    print("\nRanking assumptions by causal necessity...")
    rank_rows = []
    for _, row in survival_df.iterrows():
        ablation = row["ablation"]
        assumption = ablation.replace("no_", "")
        desc = ASSUMPTIONS.get(assumption, "unknown")
        rank_rows.append({
            "assumption": assumption,
            "description": desc,
            "ablation": ablation,
            "geometry_survival": row["geometry_survival"],
            "geometry_necessity": row["geometry_necessity"],
            "mean_survival": row["mean_survival"],
            "rank_necessity": 0,  # will fill
        })
    rank_df = pd.DataFrame(rank_rows)
    rank_df = rank_df.sort_values("geometry_necessity", ascending=False)
    rank_df["rank_necessity"] = range(1, len(rank_df) + 1)

    # ============================================================
    # MINIMAL SUBSTRATE
    # ============================================================

    print("\nIdentifying minimal surviving substrate...")
    # Find assumptions where geometry survives (>50% retention)
    surviving = rank_df[rank_df["geometry_survival"] > 0.5]["assumption"].tolist()
    essential = rank_df[rank_df["geometry_survival"] <= 0.5]["assumption"].tolist()

    # Minimum substrate = all assumptions MINUS essential ones
    all_assumptions = list(ASSUMPTIONS.keys())
    minimal = [a for a in all_assumptions if a not in essential]

    print(f"  Essential (geometry dies without them): {essential}")
    print(f"  Minimal surviving substrate: {minimal}")

    # ============================================================
    # SAVE
    # ============================================================

    print("\nSaving outputs...")

    # t037_assumption_audit.csv
    audit_df = pd.DataFrame([{"assumption": k, "description": v}
                              for k, v in ASSUMPTIONS.items()])
    audit_df.to_csv(OUT / "t037_assumption_audit.csv", index=False)
    print("  Saved t037_assumption_audit.csv")

    # t037_survival_matrix.csv
    survival_df.to_csv(OUT / "t037_survival_matrix.csv", index=False)
    print("  Saved t037_survival_matrix.csv")

    # t037_minimal_substrate.json
    substrate = {
        "all_assumptions": all_assumptions,
        "essential_for_geometry": essential,
        "minimal_surviving_substrate": minimal,
        "n_essential": len(essential),
        "n_minimal": len(minimal),
        "assumption_details": {a: ASSUMPTIONS[a] for a in all_assumptions},
        "geometry_baseline": float(baseline["geometry_mean"]),
        "geometry_retention_without_essential": {
            a: float(survival_df[survival_df["ablation"] == f"no_{a}"]["geometry_survival"].values[0])
            for a in essential if len(survival_df[survival_df["ablation"] == f"no_{a}"]) > 0
        },
    }
    with open(OUT / "t037_minimal_substrate.json", "w") as f:
        json.dump(substrate, f, indent=2)
    print("  Saved t037_minimal_substrate.json")

    # ============================================================
    # FIGURES
    # ============================================================

    print("\nGenerating figures...")
    plt.rcParams.update({
        "font.family": "serif", "font.size": 9, "axes.titlesize": 10,
        "axes.labelsize": 9, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "legend.fontsize": 7, "figure.dpi": 300, "savefig.dpi": 300,
        "savefig.bbox": "tight", "axes.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
    })

    # Fig 1: Assumption ablation (grouped bar)
    fig, ax = plt.subplots(figsize=(10, 5))
    props = ["distinction", "persistence", "composition", "geometry", "arithmetic", "dimension"]
    conditions = [r["condition"] for r in all_results]
    x = np.arange(len(conditions))
    width = 0.13
    for i, prop in enumerate(props):
        vals = [r[f"{prop}_mean"] for r in all_results]
        ax.bar(x + i * width, vals, width, label=prop)
    ax.set_xticks(x + width * 2.5)
    ax.set_xticklabels(conditions, rotation=30, ha="right")
    ax.set_ylabel("Score")
    ax.set_title("Emergence scores across ablation conditions")
    ax.legend(frameon=False, ncol=3)
    ax.set_ylim(0, 1.05)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t037_assumption_ablation.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t037_assumption_ablation.pdf/.png")

    # Fig 2: Survival heatmap
    fig, ax = plt.subplots(figsize=(8, 5))
    surv_props = [f"{p}_survival" for p in ["distinction", "persistence", "composition",
                                              "closure", "arithmetic", "geometry", "dimension"]]
    matrix = survival_df[surv_props].values
    im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1.5)
    ax.set_xticks(range(len(surv_props)))
    ax.set_xticklabels([p.replace("_survival", "") for p in surv_props], rotation=45, ha="right")
    ax.set_yticks(range(len(survival_df)))
    ax.set_yticklabels(survival_df["ablation"].values)
    plt.colorbar(im, ax=ax, label="Survival ratio (vs baseline)")
    ax.set_title("Emergence survival matrix across ablation conditions")

    for i in range(len(survival_df)):
        for j in range(len(surv_props)):
            val = matrix[i, j]
            color = "white" if val < 0.3 or val > 1.2 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=6, color=color)

    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t037_emergence_survival.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t037_emergence_survival.pdf/.png")

    # ============================================================
    # REPORT
    # ============================================================

    elapsed = time.time() - t0
    print(f"\nRuntime: {elapsed:.1f}s")

    print("\n" + "=" * 70)
    print("T037-AUDIT RESULTS")
    print("=" * 70)
    print(f"\nBaseline geometry score: {baseline['geometry_mean']:.4f}")
    print(f"\nAssumption ranking by causal necessity (geometry):")
    for _, r in rank_df.iterrows():
        surv = r["geometry_survival"]
        marker = "ESSENTIAL" if surv <= 0.5 else "non-essential"
        print(f"  {r['rank_necessity']:2d}. {r['assumption']:25s} survival={surv:.3f}  [{marker}]")

    print(f"\nMinimal surviving substrate ({len(minimal)} assumptions):")
    for a in minimal:
        print(f"  - {a}: {ASSUMPTIONS[a]}")

    print(f"\nEssential assumptions ({len(essential)}):")
    for a in essential:
        print(f"  - {a}: {ASSUMPTIONS[a]}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
