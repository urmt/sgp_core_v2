#!/usr/bin/env python3
"""
T037: Primitive Interaction Genesis (PIG)
==========================================
Search for minimum mathematical substrate from which
distinction, persistence, arithmetic, geometry emerge.

Starting assumption: ONLY interaction potential exists.
No coordinates, no graphs, no arithmetic, no geometry.

Mathematics speaks first. Philosophy follows nowhere.
"""

import sys, json, warnings, time, itertools, hashlib
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import entropy
from scipy.cluster.hierarchy import linkage, fcluster
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
N_UNIVERSES = 1200
N_SYMBOLS = 8  # alphabet size for rule construction

# ============================================================
# PHASE T037-A: INTERACTION-FIRST UNIVERSES
# ============================================================

class InteractionRule:
    """
    A primitive interaction operator Ω.

    Represents: Ω(input) -> output
    where input and output are symbolic objects.
    """

    def __init__(self, rule_dict, name=""):
        self.rule = rule_dict  # {symbol: output_symbol}
        self.name = name
        self.n_symbols = len(set(rule_dict.keys()) | set(rule_dict.values()))

    def apply(self, state):
        """Apply Ω to a state. State is a tuple of symbols."""
        if len(state) == 0:
            return state
        if len(state) == 1:
            s = state[0]
            return (self.rule.get(s, s),)
        # Binary interaction: Ω(a,b)
        a, b = state[0], state[1]
        key = (a, b)
        if key in self.rule:
            result = self.rule[key]
            return (result,) + state[2:]
        # Fallback: try individual applications
        ra = self.rule.get(a, a)
        rb = self.rule.get(b, b)
        return (ra, rb) + state[2:]

    def __repr__(self):
        return self.name


def generate_universe(seed):
    """Generate a random interaction rule system."""
    rng = np.random.RandomState(seed)
    symbols = list(range(N_SYMBOLS))

    rule = {}
    n_unary = rng.randint(2, N_SYMBOLS + 1)
    n_binary = rng.randint(0, min(N_SYMBOLS * N_SYMBOLS, 20))

    for _ in range(n_unary):
        s = symbols[rng.randint(0, len(symbols))]
        o = symbols[rng.randint(0, len(symbols))]
        rule[s] = o

    for _ in range(n_binary):
        a = symbols[rng.randint(0, len(symbols))]
        b = symbols[rng.randint(0, len(symbols))]
        o = symbols[rng.randint(0, len(symbols))]
        rule[(a, b)] = o

    name = f"U_{seed}"
    return InteractionRule(rule, name=name), seed


def simulate_universe(rule, seed, max_depth=MAX_DEPTH):
    """
    Simulate a universe by recursive application of Ω.

    Returns trajectory of states at each depth.
    """
    rng = np.random.RandomState(seed)

    # Start with random initial state
    n_initial = rng.randint(1, 4)
    initial = tuple(rng.randint(0, N_SYMBOLS) for _ in range(n_initial))

    trajectory = [initial]
    current = initial

    for depth in range(max_depth):
        try:
            next_state = rule.apply(current)
            # Bound state size
            if len(next_state) > 12:
                next_state = next_state[:12]
            if len(next_state) == 0:
                next_state = (0,)
            trajectory.append(next_state)
            current = next_state
        except Exception:
            break

    return trajectory


# ============================================================
# PHASE T037-B: EMERGENCE DETECTION
# ============================================================

def detect_distinction(trajectory):
    """
    D1: Stable distinctions — states become repeatedly identifiable.
    Score: fraction of distinct states that appear >= 2 times.
    """
    state_counts = Counter(trajectory)
    if len(state_counts) == 0:
        return 0.0, 0
    repeated = sum(1 for s, c in state_counts.items() if c >= 2)
    score = repeated / len(state_counts)
    # Find transition point: first depth where a repeated state appears
    seen = {}
    transition = len(trajectory)
    for i, s in enumerate(trajectory):
        if s in seen and i > seen[s]:
            transition = min(transition, i)
            break
        seen[s] = i
    return score, transition


def detect_persistence(trajectory):
    """
    D2: Structures survive recursion.
    Score: max consecutive repetitions of any state.
    """
    if len(trajectory) < 2:
        return 0.0, len(trajectory)
    max_run = 1
    current_run = 1
    transition = len(trajectory)
    found = False
    for i in range(1, len(trajectory)):
        if trajectory[i] == trajectory[i-1]:
            current_run += 1
        else:
            current_run = 1
        if current_run > max_run:
            max_run = current_run
            if not found:
                transition = i - current_run + 1
                found = True
    score = min(max_run / 5.0, 1.0)  # normalize: 5+ repetitions = perfect
    return score, transition


def detect_composition(trajectory):
    """
    D3: Structures combine into larger structures.
    Score: fraction of transitions where output contains
    substructure from multiple distinct inputs.
    """
    if len(trajectory) < 3:
        return 0.0, len(trajectory)
    compositional = 0
    total = len(trajectory) - 1
    transition = len(trajectory)
    found = False
    for i in range(1, len(trajectory)):
        prev = set(trajectory[i-1])
        curr = set(trajectory[i])
        # Compositional if current state contains symbols from
        # multiple distinct previous states (recombination)
        if len(curr) > 1 and curr != prev:
            compositional += 1
            if not found:
                transition = i
                found = True
    score = compositional / max(total, 1)
    return score, transition


def detect_closure(trajectory):
    """
    D4: Interaction loops emerge.
    Score: fraction of states that reappear (cycle detection).
    """
    if len(trajectory) < 3:
        return 0.0, len(trajectory)
    seen = set()
    loop_start = len(trajectory)
    loops = 0
    for i, s in enumerate(trajectory):
        if s in seen:
            loops += 1
            loop_start = min(loop_start, i)
        seen.add(s)
    score = min(loops / max(len(trajectory), 1), 1.0)
    return score, loop_start


def detect_arithmetic(trajectory):
    """
    D5: Repeated compositions produce countable classes.
    Score: how many distinct state-length classes emerge.
    """
    lengths = [len(s) for s in trajectory]
    unique_lengths = len(set(lengths))
    # Arithmetic emerges if we see >2 distinct lengths
    score = min((unique_lengths - 1) / 4.0, 1.0)  # 5+ classes = perfect
    transition = 0
    seen_lengths = set()
    for i, l in enumerate(lengths):
        if l not in seen_lengths:
            seen_lengths.add(l)
            if len(seen_lengths) >= 2 and transition == 0:
                transition = i
    return max(0, score), transition


def detect_geometry(trajectory):
    """
    D6: Adjacency relations emerge without coordinates.
    Score: whether state transitions form structured patterns
    (non-random transition matrix).
    """
    if len(trajectory) < 5:
        return 0.0, len(trajectory)
    # Build transition frequency matrix (by state hash)
    state_ids = {}
    for s in trajectory:
        sid = hash(s) % 100
        state_ids[s] = sid
    id_seq = [state_ids[s] for s in trajectory]

    n_states = len(set(id_seq))
    if n_states < 2:
        return 0.0, len(trajectory)

    # Compute transition matrix
    trans = np.zeros((min(n_states, 20), min(n_states, 20)))
    for i in range(len(id_seq) - 1):
        a = id_seq[i] % min(n_states, 20)
        b = id_seq[i+1] % min(n_states, 20)
        trans[a, b] += 1

    # Normalize
    row_sums = trans.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    trans_norm = trans / row_sums

    # Measure structuredness: deviation from uniform
    uniform = np.ones_like(trans_norm) / trans_norm.shape[1]
    kl = np.sum(trans_norm * np.log((trans_norm + 1e-12) / (uniform + 1e-12)))
    max_kl = np.log(trans_norm.shape[1])
    score = min(kl / max(max_kl, 1e-12), 1.0)

    # Transition point: first time a state repeats
    seen = set()
    transition = len(trajectory)
    for i, s in enumerate(trajectory):
        if s in seen:
            transition = i
            break
        seen.add(s)

    return score, transition


def detect_dimension(trajectory):
    """
    D7: Scaling laws imply effective dimensionality.
    Score: whether state-space coverage scales as L^d.
    """
    if len(trajectory) < 5:
        return 0.0, len(trajectory)

    # Count unique states at different trajectory lengths
    sample_points = np.linspace(3, len(trajectory), min(8, len(trajectory)//2), dtype=int)
    counts = []
    for n in sample_points:
        unique = len(set(trajectory[:n]))
        counts.append((n, unique))

    if len(counts) < 3:
        return 0.0, len(trajectory)

    # Fit power law: unique ~ L^d
    log_L = np.log([c[0] for c in counts])
    log_N = np.log([c[1] for c in counts])
    log_N = np.maximum(log_N, 1e-12)

    try:
        coef = np.polyfit(log_L, log_N, 1)
        d = coef[0]  # effective dimension
        # Score: d between 0.5 and 3 is "geometric"
        if 0.3 <= d <= 4.0:
            score = 1.0 - abs(d - 1.5) / 2.5  # peak at d=1.5
        else:
            score = 0.0
        score = max(0, min(1, score))
    except Exception:
        score = 0.0
        d = 0.0

    return score, 0


# ============================================================
# PHASE T037-C: EMERGENCE SCORING
# ============================================================

def score_universe(trajectory):
    """Compute all 7 emergence scores for a universe."""
    d1, t1 = detect_distinction(trajectory)
    d2, t2 = detect_persistence(trajectory)
    d3, t3 = detect_composition(trajectory)
    d4, t4 = detect_closure(trajectory)
    d5, t5 = detect_arithmetic(trajectory)
    d6, t6 = detect_geometry(trajectory)
    d7, t7 = detect_dimension(trajectory)

    scores = {
        "distinction_score": d1,
        "persistence_score": d2,
        "composition_score": d3,
        "closure_score": d4,
        "arithmetic_score": d5,
        "geometry_score": d6,
        "dimension_score": d7,
    }

    transitions = {
        "distinction_transition": t1,
        "persistence_transition": t2,
        "composition_transition": t3,
        "closure_transition": t4,
        "arithmetic_transition": t5,
        "geometry_transition": t6,
        "dimension_transition": t7,
    }

    # Emergence index: weighted average
    weights = {
        "distinction_score": 0.20,
        "persistence_score": 0.20,
        "composition_score": 0.15,
        "closure_score": 0.10,
        "arithmetic_score": 0.15,
        "geometry_score": 0.10,
        "dimension_score": 0.10,
    }
    emergence_index = sum(scores[k] * weights[k] for k in weights)

    return scores, transitions, emergence_index


# ============================================================
# PHASE T037-D: TRANSITION ANALYSIS
# ============================================================

def build_transition_chains(scores_list, transitions_list, ids):
    """Identify transition points across all universes."""
    rows = []
    for i, (sc, tr, uid) in enumerate(zip(scores_list, transitions_list, ids)):
        for prop in ["distinction", "persistence", "composition", "closure",
                      "arithmetic", "geometry", "dimension"]:
            key_score = f"{prop}_score"
            key_trans = f"{prop}_transition"
            if key_score in sc and key_trans in tr:
                rows.append({
                    "universe_id": uid,
                    "property": prop,
                    "score": sc[key_score],
                    "transition_depth": tr[key_trans],
                })
    return pd.DataFrame(rows)


# ============================================================
# PHASE T037-E: UNIVERSALITY SEARCH
# ============================================================

def universality_search(catalog_df):
    """Find common mechanisms across successful universes."""
    # Select top 20% by emergence_index
    threshold = catalog_df["emergence_index"].quantile(0.80)
    top = catalog_df[catalog_df["emergence_index"] >= threshold].copy()

    laws = []

    # Check: recursion depth thresholds
    for prop in ["distinction", "persistence", "composition", "arithmetic", "geometry"]:
        col = f"{prop}_transition"
        if col in top.columns:
            vals = top[col].dropna()
            if len(vals) > 0:
                mean_t = vals.mean()
                std_t = vals.std()
                laws.append({
                    "law": f"{prop}_threshold",
                    "mean_depth": float(mean_t),
                    "std_depth": float(std_t),
                    "n_universes": len(vals),
                    "description": f"{prop} typically appears at depth {mean_t:.1f} ± {std_t:.1f}",
                })

    # Check: closure threshold
    closure_scores = top["closure_score"]
    closure_threshold = closure_scores.mean()
    laws.append({
        "law": "closure_threshold",
        "mean_score": float(closure_threshold),
        "description": f"Successful universes have mean closure={closure_threshold:.3f}",
    })

    # Check: emergence index distribution
    all_ei = catalog_df["emergence_index"]
    top_ei = top["emergence_index"]
    laws.append({
        "law": "emergence_separation",
        "mean_top": float(top_ei.mean()),
        "mean_all": float(all_ei.mean()),
        "description": f"Top 20% mean EI={top_ei.mean():.3f} vs all={all_ei.mean():.3f}",
    })

    # Check: dimension score correlation
    if "dimension_score" in top.columns:
        dim_mean = top["dimension_score"].mean()
        laws.append({
            "law": "dimension_emergence",
            "mean_dimension_score": float(dim_mean),
            "description": f"Mean dimension score in successful universes: {dim_mean:.3f}",
        })

    return pd.DataFrame(laws)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T037: PRIMITIVE INTERACTION GENESIS (PIG)")
    print("=" * 70)
    t0 = time.time()

    # Phase A: Generate universes
    print(f"\n[Phase A] Generating {N_UNIVERSES} interaction rule systems...")
    universes = []
    for seed in range(N_UNIVERSES):
        rule, uid = generate_universe(seed)
        universes.append((rule, uid))

    # Simulate and score
    print("[Phase A-B] Simulating and scoring...")
    catalog_rows = []
    all_trajectories = {}

    for i, (rule, uid) in enumerate(universes):
        if i % 200 == 0:
            print(f"  Progress: {i}/{N_UNIVERSES}", flush=True)
        traj = simulate_universe(rule, uid)
        scores, transitions, ei = score_universe(traj)

        catalog_rows.append({
            "universe_id": uid,
            "n_symbols": rule.n_symbols,
            "trajectory_length": len(traj),
            "final_state_size": len(traj[-1]) if traj else 0,
            "emergence_index": ei,
            **scores,
            **transitions,
        })
        all_trajectories[uid] = traj

    catalog_df = pd.DataFrame(catalog_rows)
    print(f"  Total universes: {len(catalog_df)}")
    print(f"  Mean emergence index: {catalog_df['emergence_index'].mean():.4f}")
    print(f"  Max emergence index: {catalog_df['emergence_index'].max():.4f}")

    # Phase C: Scores
    print("\n[Phase C] Emergence score distributions...")
    for col in ["distinction_score", "persistence_score", "composition_score",
                 "closure_score", "arithmetic_score", "geometry_score", "dimension_score"]:
        print(f"  {col}: mean={catalog_df[col].mean():.4f}, max={catalog_df[col].max():.4f}")

    # Phase D: Transition analysis
    print("\n[Phase D] Building transition chains...")
    trans_df = build_transition_chains(
        [dict(row) for _, row in catalog_df.iterrows()],
        [dict(row) for _, row in catalog_df.iterrows()],
        catalog_df["universe_id"].values,
    )
    trans_df.to_csv(OUT / "t037_transition_catalog.csv", index=False)
    print(f"  Transition events: {len(trans_df)}")

    # Phase E: Universality search
    print("\n[Phase E] Universality search...")
    laws_df = universality_search(catalog_df)
    print(f"  Candidate laws: {len(laws_df)}")
    for _, law in laws_df.iterrows():
        print(f"    {law['law']}: {law['description']}")

    # ============================================================
    # SAVE OUTPUTS
    # ============================================================

    print("\nSaving outputs...")

    # t037_universe_catalog.csv
    catalog_df.to_csv(OUT / "t037_universe_catalog.csv", index=False)
    print("  Saved t037_universe_catalog.csv")

    # t037_emergence_scores.csv
    score_cols = ["universe_id", "emergence_index",
                  "distinction_score", "persistence_score", "composition_score",
                  "closure_score", "arithmetic_score", "geometry_score", "dimension_score"]
    catalog_df[score_cols].to_csv(OUT / "t037_emergence_scores.csv", index=False)
    print("  Saved t037_emergence_scores.csv")

    # t037_candidate_laws.csv
    laws_df.to_csv(OUT / "t037_candidate_laws.csv", index=False)
    print("  Saved t037_candidate_laws.csv")

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

    # Fig 1: Emergence index distribution
    fig, axes = plt.subplots(2, 4, figsize=(12, 6))
    props = ["distinction_score", "persistence_score", "composition_score",
             "closure_score", "arithmetic_score", "geometry_score", "dimension_score",
             "emergence_index"]
    labels = ["Distinction", "Persistence", "Composition", "Closure",
              "Arithmetic", "Geometry", "Dimension", "Emergence Index"]
    for i, (col, lab) in enumerate(zip(props, labels)):
        ax = axes[i // 4, i % 4]
        ax.hist(catalog_df[col], bins=25, color="#555555", edgecolor="white", linewidth=0.3, alpha=0.85)
        ax.set_title(lab, fontsize=8)
        ax.axvline(catalog_df[col].mean(), color="black", ls="--", lw=0.5)
    plt.suptitle("Emergence score distributions across 1200 universes", fontsize=10)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t037_emergence_distribution.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t037_emergence_distribution.pdf/.png")

    # Fig 2: Transition network (properties vs depth)
    fig, ax = plt.subplots(figsize=(10, 5))
    prop_names = ["distinction", "persistence", "composition", "arithmetic", "geometry"]
    for i, prop in enumerate(prop_names):
        col = f"{prop}_transition"
        vals = catalog_df[col].dropna()
        vals = vals[vals < MAX_DEPTH]
        if len(vals) > 0:
            ax.hist(vals, bins=MAX_DEPTH, alpha=0.4, label=prop, density=True)
    ax.set_xlabel("Recursion depth")
    ax.set_ylabel("Density")
    ax.set_title("Transition depth distributions across emergence properties")
    ax.legend(frameon=False)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t037_transition_network.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t037_transition_network.pdf/.png")

    # Fig 3: Phase diagram (distinction vs persistence, colored by geometry)
    fig, ax = plt.subplots(figsize=(7, 5))
    sc = ax.scatter(catalog_df["distinction_score"], catalog_df["persistence_score"],
                    c=catalog_df["geometry_score"], cmap="viridis", s=8, alpha=0.6)
    plt.colorbar(sc, ax=ax, label="Geometry score")
    ax.set_xlabel("Distinction score")
    ax.set_ylabel("Persistence score")
    ax.set_title("Phase diagram: distinction vs persistence (colored by geometry)")
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t037_phase_diagram.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t037_phase_diagram.pdf/.png")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    elapsed = time.time() - t0

    # Find best universe
    best_idx = catalog_df["emergence_index"].idxmax()
    best = catalog_df.iloc[best_idx]
    best_uid = int(best["universe_id"])

    # Find universes with high scores on multiple criteria
    high = catalog_df[
        (catalog_df["distinction_score"] > 0.5) &
        (catalog_df["persistence_score"] > 0.5) &
        (catalog_df["composition_score"] > 0.5) &
        (catalog_df["arithmetic_score"] > 0.5) &
        (catalog_df["geometry_score"] > 0.3)
    ]
    n_success = len(high)

    # Check success criterion
    success = n_success > 0

    print(f"\nRuntime: {elapsed:.1f}s")
    print("\n" + "=" * 70)
    print("T037 RESULTS")
    print("=" * 70)
    print(f"Universes generated: {N_UNIVERSES}")
    print(f"Universes with all 5 criteria: {n_success}")
    print()
    print(f"1. Best universe discovered: U_{best_uid}")
    print(f"   Emergence index: {best['emergence_index']:.4f}")
    print(f"   Distinction: {best['distinction_score']:.4f}")
    print(f"   Persistence: {best['persistence_score']:.4f}")
    print(f"   Composition: {best['composition_score']:.4f}")
    print(f"   Arithmetic:  {best['arithmetic_score']:.4f}")
    print(f"   Geometry:    {best['geometry_score']:.4f}")
    print(f"   Dimension:   {best['dimension_score']:.4f}")
    print()
    print(f"2. Minimal rule set: {best['n_symbols']} symbols")
    print(f"   Trajectory length: {best['trajectory_length']}")
    print()
    print(f"3. First appearance of persistence: depth {best['persistence_transition']:.0f}")
    print(f"4. First appearance of arithmetic:  depth {best['arithmetic_transition']:.0f}")
    print(f"5. First appearance of proto-geometry: depth {best['geometry_transition']:.0f}")
    print()
    print("6. Candidate universal emergence laws:")
    for _, law in laws_df.iterrows():
        print(f"   - {law['description']}")
    print()
    print(f"7. Geometry appears to be EMERGENT rather than primitive: {'YES' if best['geometry_score'] > 0.3 else 'INCONCLUSIVE'}")
    print()
    print("=" * 70)

    # Summary JSON
    summary = {
        "n_universes": N_UNIVERSES,
        "n_with_all_5_criteria": n_success,
        "best_universe_id": best_uid,
        "best_emergence_index": float(best["emergence_index"]),
        "best_scores": {k: float(best[k]) for k in
                        ["distinction_score", "persistence_score", "composition_score",
                         "closure_score", "arithmetic_score", "geometry_score", "dimension_score"]},
        "best_transitions": {k: int(best[k]) for k in
                            ["distinction_transition", "persistence_transition", "composition_transition",
                             "closure_transition", "arithmetic_transition", "geometry_transition"]},
        "candidate_laws": laws_df.to_dict(orient="records"),
        "success_criterion": "at least one universe exhibits distinction+persistence+composition+arithmetic+proto-geometry",
        "success_met": success,
    }
    with open(OUT / "t037_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSaved t037_summary.json")


if __name__ == "__main__":
    main()
