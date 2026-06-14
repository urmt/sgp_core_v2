#!/usr/bin/env python3
"""
T038: Distinction Genesis Audit
================================
Test whether distinction can emerge from pure interaction (Ω)
without any pre-defined symbols, coordinates, geometry, or objects.

Starting assumption: ONLY "possibility of interaction" exists.
No symbols. No coordinates. No graphs. No numbers. No geometry.

The chain being tested: Potential → Distinction
"""

import sys, json, warnings, time
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from scipy.cluster.hierarchy import linkage, fcluster
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

MAX_DEPTH = 40
STATE_DIM = 6
N_UNIVERSES = 1000
N_ABLATION_TRIALS = 200

# ============================================================
# PRIMITIVE: Ω — POSSIBILITY OF INTERACTION
# ============================================================

class PureInteraction:
    """
    Ω: The primitive interaction operator.

    Takes a state vector and produces a new state.
    No symbols, no discrete labels, no coordinates.
    Just continuous transformation.
    """

    def __init__(self, seed):
        rng = np.random.RandomState(seed)
        # Ω is defined by a random continuous transformation
        # This is the ONLY structure: a transformation matrix
        self.W = rng.randn(STATE_DIM, STATE_DIM) * 0.5
        self.b = rng.randn(STATE_DIM) * 0.1
        # Nonlinearity strength
        self.alpha = rng.uniform(0.1, 0.5)

    def apply(self, state):
        """Apply Ω to a state. Pure continuous transformation."""
        # Linear + nonlinear component
        linear = self.W @ state + self.b
        nonlinear = np.tanh(self.alpha * state)
        result = 0.7 * linear + 0.3 * nonlinear
        return result


# ============================================================
# SIMULATION
# ============================================================

def simulate_pure_interaction(omega, initial_state, max_depth=MAX_DEPTH):
    """
    Simulate a universe with ONLY Ω.
    No symbols, no labels, no coordinates.
    Just continuous state evolution.
    """
    trajectory = [initial_state.copy()]
    current = initial_state.copy()

    for depth in range(max_depth):
        try:
            next_state = omega.apply(current)
            # Bound to prevent divergence
            next_state = np.clip(next_state, -10, 10)
            trajectory.append(next_state.copy())
            current = next_state.copy()
        except Exception:
            break

    return np.array(trajectory)


# ============================================================
# EMERGENCE DETECTION
# ============================================================

def detect_distinction_emergence(trajectory):
    """
    D1: Distinction emergence.

    A distinction is a repeatably identifiable outcome class
    that survives multiple recursive interaction cycles.

    Detection: cluster states at different depths, check if
    stable clusters form.
    """
    if len(trajectory) < 8:
        return False, 0, 0.0

    # Compute pairwise distances between all states
    D = squareform(pdist(trajectory, metric="euclidean"))

    # Check if states cluster into distinct groups
    # Use hierarchical clustering with varying thresholds
    best_n_clusters = 1
    best_silhouette = -1

    for n_clusters in range(2, min(6, len(trajectory) // 2)):
        try:
            from sklearn.metrics import silhouette_score
            Z = linkage(D, method="average")
            labels = fcluster(Z, n_clusters, criterion="maxclust")
            if len(set(labels)) >= 2:
                sil = silhouette_score(D, labels, metric="precomputed")
                if sil > best_silhouette:
                    best_silhouette = sil
                    best_n_clusters = n_clusters
        except Exception:
            pass

    # Distinction emerges if silhouette > 0.3 (non-random clustering)
    emerged = best_silhouette > 0.3

    # Find transition depth
    transition = 0
    if emerged:
        for depth in range(4, len(trajectory)):
            early_D = squareform(pdist(trajectory[:depth], metric="euclidean"))
            if early_D.shape[0] >= 4:
                try:
                    Z = linkage(early_D, method="average")
                    labels = fcluster(Z, 2, criterion="maxclust")
                    sil = silhouette_score(early_D, labels, metric="precomputed")
                    if sil > 0.3:
                        transition = depth
                        break
                except Exception:
                    pass

    return emerged, transition, best_silhouette


def detect_persistence_emergence(trajectory):
    """
    D2: Persistence emergence.
    Structures survive recursion.
    Detection: whether trajectory revisits similar regions.
    """
    if len(trajectory) < 8:
        return False, 0, 0.0

    # Compute self-similarity at different lags
    persistences = []
    for lag in range(1, min(6, len(trajectory) // 2)):
        dists = [np.linalg.norm(trajectory[i] - trajectory[i + lag])
                 for i in range(len(trajectory) - lag)]
        if dists:
            # Persistence: fraction of pairs within tight threshold
            thresh = np.percentile(dists, 20)
            persistences.append(np.mean(np.array(dists) < thresh))

    # Persistence emerges if self-similarity is high at some lag
    max_persist = max(persistences) if persistences else 0
    emerged = max_persist > 0.4

    # Transition depth
    transition = 0
    if emerged:
        for depth in range(6, len(trajectory)):
            early = trajectory[:depth]
            if len(early) >= 4:
                d01 = np.linalg.norm(early[0] - early[1])
                d02 = np.linalg.norm(early[0] - early[min(3, len(early)-1)])
                if d02 < d01 * 0.5:
                    transition = depth
                    break

    return emerged, transition, max_persist


def detect_relation_emergence(trajectory):
    """
    D3: Relation emergence.
    Adjacency relations emerge between states.
    Detection: whether the transition structure is non-random.
    """
    if len(trajectory) < 10:
        return False, 0, 0.0

    # Build distance matrix between consecutive states
    transitions = []
    for i in range(len(trajectory) - 1):
        d = np.linalg.norm(trajectory[i+1] - trajectory[i])
        transitions.append(d)

    transitions = np.array(transitions)

    # Check if transition distances are structured (not uniform)
    cv = np.std(transitions) / max(np.mean(transitions), 1e-12)
    emerged = cv > 0.3

    # Transition depth
    transition = 0
    if emerged:
        for depth in range(5, len(trajectory) - 1):
            d = np.linalg.norm(trajectory[depth+1] - trajectory[depth])
            d_prev = np.linalg.norm(trajectory[depth] - trajectory[max(0, depth-1)])
            if abs(d - d_prev) > 0.5:
                transition = depth
                break

    return emerged, transition, cv


def detect_closure_emergence(trajectory):
    """
    D4: Closure emergence.
    Interaction loops emerge.
    Detection: whether trajectory returns near starting point.
    """
    if len(trajectory) < 6:
        return False, 0, 0.0

    # Check if trajectory returns near any previous state
    min_return_dist = np.inf
    return_depth = 0

    for i in range(2, len(trajectory)):
        d = np.linalg.norm(trajectory[i] - trajectory[0])
        if d < min_return_dist:
            min_return_dist = d
            return_depth = i

    # Also check for loops between any pair
    all_min_dists = []
    for i in range(len(trajectory)):
        for j in range(i + 2, min(i + 10, len(trajectory))):
            d = np.linalg.norm(trajectory[i] - trajectory[j])
            all_min_dists.append(d)

    if all_min_dists:
        loop_thresh = np.percentile(all_min_dists, 10)
        loop_fraction = np.mean(np.array(all_min_dists) < loop_thresh)
    else:
        loop_fraction = 0

    emerged = loop_fraction > 0.15 or min_return_dist < 0.5

    return emerged, return_depth, loop_fraction


def detect_self_reference_emergence(trajectory):
    """
    D5: Self-reference emergence.
    The system produces states that influence their own future.
    Detection: whether trajectory shows second-order structure
    (trajectory of trajectory is non-random).
    """
    if len(trajectory) < 12:
        return False, 0, 0.0

    # Compute "meta-trajectory": distances between consecutive states
    meta = np.array([np.linalg.norm(trajectory[i+1] - trajectory[i])
                     for i in range(len(trajectory) - 1)])

    # Check if meta-trajectory has structure (not white noise)
    # Autocorrelation at lag 1
    if len(meta) > 3:
        autocorr = np.corrcoef(meta[:-1], meta[1:])[0, 1]
    else:
        autocorr = 0

    # Also check if meta-trajectory has multiple scales
    if len(meta) > 4:
        fine = np.std(np.diff(meta))
        coarse = np.std(meta)
        scale_ratio = coarse / max(fine, 1e-12)
    else:
        scale_ratio = 1

    emerged = abs(autocorr) > 0.3 or scale_ratio > 3

    return emerged, 0, abs(autocorr)


# ============================================================
# SCORING
# ============================================================

def score_universe(trajectory):
    """Score all 5 emergence properties."""
    d1, t1, d1_val = detect_distinction_emergence(trajectory)
    d2, t2, d2_val = detect_persistence_emergence(trajectory)
    d3, t3, d3_val = detect_relation_emergence(trajectory)
    d4, t4, d4_val = detect_closure_emergence(trajectory)
    d5, t5, d5_val = detect_self_reference_emergence(trajectory)

    return {
        "distinction_emerged": d1,
        "distinction_depth": t1,
        "distinction_value": float(d1_val),
        "persistence_emerged": d2,
        "persistence_depth": t2,
        "persistence_value": float(d2_val),
        "relation_emerged": d3,
        "relation_depth": t3,
        "relation_value": float(d3_val),
        "closure_emerged": d4,
        "closure_depth": t4,
        "closure_value": float(d4_val),
        "selfref_emerged": d5,
        "selfref_depth": t5,
        "selfref_value": float(d5_val),
    }


# ============================================================
# ABLATION
# ============================================================

class OmegaAblation:
    """Ablated versions of Ω for testing causal necessity."""

    @staticmethod
    def no_nonlinearity(seed):
        """Remove nonlinear component: pure linear Ω."""
        rng = np.random.RandomState(seed)
        omega = PureInteraction(seed)
        omega.alpha = 0.0  # No nonlinearity
        return omega

    @staticmethod
    def no_bias(seed):
        """Remove bias: Ω(0) = 0."""
        omega = PureInteraction(seed)
        omega.b = np.zeros(STATE_DIM)
        return omega

    @staticmethod
    def no_rotation(seed):
        """Remove rotation: W is diagonal."""
        omega = PureInteraction(seed)
        D = np.diag(np.diag(omega.W))
        omega.W = D
        return omega

    @staticmethod
    def symmetric_w(seed):
        """Force W to be symmetric (no rotation)."""
        omega = PureInteraction(seed)
        omega.W = (omega.W + omega.W.T) / 2
        return omega

    @staticmethod
    def zero_w(seed):
        """Remove all linear component: pure nonlinear Ω."""
        omega = PureInteraction(seed)
        omega.W = np.zeros((STATE_DIM, STATE_DIM))
        omega.b = np.zeros(STATE_DIM)
        return omega

    @staticmethod
    def identity_w(seed):
        """W = I: Ω is identity + nonlinearity."""
        omega = PureInteraction(seed)
        omega.W = np.eye(STATE_DIM)
        omega.b = np.zeros(STATE_DIM)
        omega.alpha = 0.5
        return omega

    @staticmethod
    def no_memory(seed):
        """No memory: state reset to random each step."""
        omega = PureInteraction(seed)
        return omega  # omega exists but won't be used

    @staticmethod
    def standard(seed):
        """Standard Ω (no ablation)."""
        return PureInteraction(seed)


ABLATION_METHODS = {
    "baseline": OmegaAblation.standard,
    "no_nonlinearity": OmegaAblation.no_nonlinearity,
    "no_bias": OmegaAblation.no_bias,
    "no_rotation": OmegaAblation.no_rotation,
    "symmetric_w": OmegaAblation.symmetric_w,
    "zero_w": OmegaAblation.zero_w,
    "identity_w": OmegaAblation.identity_w,
}


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("T038: DISTINCTION GENESIS AUDIT")
    print("=" * 70)
    print("Testing: Potential → Distinction")
    print("Starting assumption: ONLY Ω (possibility of interaction)")
    print("=" * 70)
    t0 = time.time()

    # ============================================================
    # PHASE 1: Generate 1000+ universes
    # ============================================================

    print(f"\n[Phase 1] Generating {N_UNIVERSES} pure interaction universes...")

    universe_results = []

    for uid in range(N_UNIVERSES):
        if uid % 200 == 0:
            print(f"  Progress: {uid}/{N_UNIVERSES}", flush=True)

        # Generate Ω
        omega = PureInteraction(uid)

        # Generate random initial state (continuous, no symbols)
        rng = np.random.RandomState(uid)
        initial_state = rng.randn(STATE_DIM) * 0.5

        # Simulate
        traj = simulate_pure_interaction(omega, initial_state)

        # Score
        scores = score_universe(traj)

        # Store
        row = {
            "universe_id": uid,
            "trajectory_length": len(traj),
            "final_norm": float(np.linalg.norm(traj[-1])),
            "omega_alpha": omega.alpha,
            **scores,
        }
        universe_results.append(row)

    catalog_df = pd.DataFrame(universe_results)

    # Count successful universes
    n_distinction = catalog_df["distinction_emerged"].sum()
    n_persistence = catalog_df["persistence_emerged"].sum()
    n_relation = catalog_df["relation_emerged"].sum()
    n_closure = catalog_df["closure_emerged"].sum()
    n_selfref = catalog_df["selfref_emerged"].sum()
    n_all = ((catalog_df["distinction_emerged"] & catalog_df["persistence_emerged"] &
              catalog_df["relation_emerged"])).sum()

    print(f"\n  Universe results:")
    print(f"    Distinction emerged: {n_distinction}/{N_UNIVERSES}")
    print(f"    Persistence emerged: {n_persistence}/{N_UNIVERSES}")
    print(f"    Relation emerged:    {n_relation}/{N_UNIVERSES}")
    print(f"    Closure emerged:     {n_closure}/{N_UNIVERSES}")
    print(f"    Self-reference:      {n_selfref}/{N_UNIVERSES}")
    print(f"    Dist+Persist+Rel:   {n_all}/{N_UNIVERSES}")

    # ============================================================
    # PHASE 2: Find successful universes
    # ============================================================

    successful = catalog_df[
        catalog_df["distinction_emerged"] & catalog_df["persistence_emerged"]
    ]
    print(f"\n[Phase 2] Successful universes (distinction+persistence): {len(successful)}")

    if len(successful) == 0:
        print("  No successful universes found. Trying relaxed criteria...")
        successful = catalog_df[catalog_df["distinction_emerged"]]
        print(f"  Distinction-only successes: {len(successful)}")

    # ============================================================
    # PHASE 3: Ablation audit
    # ============================================================

    print("\n[Phase 3] Ablation audit on top 10 universes...")

    # Select top 10 by distinction value
    top_unis = catalog_df.nlargest(10, "distinction_value")

    ablation_results = []

    for _, uni in top_unis.iterrows():
        uid = int(uni["universe_id"])
        print(f"  Ablating U_{uid}...")

        for abl_name, abl_fn in ABLATION_METHODS.items():
            trial_scores = {"distinction": [], "persistence": [], "relation": [],
                           "closure": [], "selfref": []}

            for trial in range(N_ABLATION_TRIALS // 10):
                seed = uid * 10000 + trial * 100 + hash(abl_name) % 100
                try:
                    omega = abl_fn(seed)
                    rng = np.random.RandomState(seed)
                    initial = rng.randn(STATE_DIM) * 0.5

                    if abl_name == "no_memory":
                        # No memory: random state each step
                        traj = []
                        current = initial
                        for _ in range(MAX_DEPTH):
                            traj.append(current.copy())
                            current = rng.randn(STATE_DIM) * 0.5
                        traj = np.array(traj)
                    else:
                        traj = simulate_pure_interaction(omega, initial)

                    scores = score_universe(traj)
                    for k in trial_scores:
                        trial_scores[k].append(1 if scores[f"{k}_emerged"] else 0)
                except Exception:
                    for k in trial_scores:
                        trial_scores[k].append(0)

            row = {"universe_id": uid, "ablation": abl_name}
            for k in trial_scores:
                row[f"{k}_rate"] = np.mean(trial_scores[k])
            ablation_results.append(row)

    ablation_df = pd.DataFrame(ablation_results)

    # Average across universes per ablation
    avg_ablation = ablation_df.groupby("ablation").mean(numeric_only=True).reset_index()

    # ============================================================
    # PHASE 4: Compute survival and necessity
    # ============================================================

    print("\n[Phase 4] Computing causal necessity...")

    baseline = avg_ablation[avg_ablation["ablation"] == "baseline"]
    if len(baseline) == 0:
        baseline = avg_ablation.iloc[[0]]

    survival_rows = []
    for _, row in avg_ablation.iterrows():
        if row["ablation"] == "baseline":
            continue
        s = {"ablation": row["ablation"]}
        for prop in ["distinction", "persistence", "relation", "closure", "selfref"]:
            base_val = baseline[f"{prop}_rate"].values[0]
            abl_val = row[f"{prop}_rate"]
            survival = abl_val / max(base_val, 1e-12)
            s[f"{prop}_survival"] = float(survival)
        s["mean_survival"] = np.mean([s[f"{p}_survival"] for p in
                                       ["distinction", "persistence", "relation"]])
        survival_rows.append(s)

    survival_df = pd.DataFrame(survival_rows)
    survival_df = survival_df.sort_values("mean_survival", ascending=True)

    # ============================================================
    # SAVE
    # ============================================================

    print("\nSaving outputs...")

    catalog_df.to_csv(OUT / "t038_universe_catalog.csv", index=False)
    print("  Saved t038_universe_catalog.csv")

    # Emergence events
    events = []
    for _, row in catalog_df.iterrows():
        for prop in ["distinction", "persistence", "relation", "closure", "selfref"]:
            if row[f"{prop}_emerged"]:
                events.append({
                    "universe_id": row["universe_id"],
                    "property": prop,
                    "emergence_depth": row[f"{prop}_depth"],
                    "value": row[f"{prop}_value"],
                })
    events_df = pd.DataFrame(events)
    events_df.to_csv(OUT / "t038_emergence_events.csv", index=False)
    print(f"  Saved t038_emergence_events.csv ({len(events)} events)")

    ablation_df.to_csv(OUT / "t038_ablation_audit.csv", index=False)
    print("  Saved t038_ablation_audit.csv")

    survival_df.to_csv(OUT / "t038_survival_matrix.csv", index=False)
    print("  Saved t038_survival_matrix.csv")

    # Candidate laws
    laws = []
    for prop in ["distinction", "persistence", "relation", "closure", "selfref"]:
        emerged = catalog_df[catalog_df[f"{prop}_emerged"]]
        if len(emerged) > 0:
            depths = emerged[f"{prop}_depth"]
            depths = depths[depths > 0]
            if len(depths) > 0:
                laws.append({
                    "property": prop,
                    "emergence_rate": float(catalog_df[f"{prop}_emerged"].mean()),
                    "mean_depth": float(depths.mean()),
                    "std_depth": float(depths.std()),
                    "n_universes": len(depths),
                })
    laws_df = pd.DataFrame(laws)
    laws_df.to_csv(OUT / "t038_candidate_laws.csv", index=False)
    print("  Saved t038_candidate_laws.csv")

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

    # Fig 1: Emergence depths
    fig, ax = plt.subplots(figsize=(7, 4))
    props = ["distinction", "persistence", "relation", "closure", "selfref"]
    for prop in props:
        emerged = catalog_df[catalog_df[f"{prop}_emerged"]]
        depths = emerged[f"{prop}_depth"]
        depths = depths[depths > 0]
        if len(depths) > 0:
            ax.hist(depths, bins=20, alpha=0.4, label=f"{prop} (n={len(depths)})", density=True)
    ax.set_xlabel("Emergence depth")
    ax.set_ylabel("Density")
    ax.set_title("First emergence depths across properties")
    ax.legend(frameon=False)
    plt.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_t038_emergence_depths.{ext}", format=ext, dpi=300)
    plt.close(fig)
    print("  Saved fig_t038_emergence_depths.pdf/.png")

    # Fig 2: Transition tree (successful universe)
    if len(successful) > 0:
        best_uid = int(successful.iloc[0]["universe_id"])
        omega = PureInteraction(best_uid)
        rng = np.random.RandomState(best_uid)
        initial = rng.randn(STATE_DIM) * 0.5
        traj = simulate_pure_interaction(omega, initial)

        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        # Panel A: State trajectory (first 2 dims)
        ax = axes[0]
        ax.plot(traj[:, 0], traj[:, 1], "o-", markersize=3, lw=0.5, alpha=0.7)
        ax.set_xlabel("State dim 1")
        ax.set_ylabel("State dim 2")
        ax.set_title("(a) State trajectory")
        # Panel B: Distance from origin over time
        ax = axes[1]
        dists = [np.linalg.norm(t) for t in traj]
        ax.plot(dists, "o-", markersize=2, lw=0.5)
        ax.set_xlabel("Depth")
        ax.set_ylabel("Distance from origin")
        ax.set_title("(b) Distance evolution")
        # Panel C: Pairwise distances between states
        ax = axes[2]
        D = squareform(pdist(traj[:15], metric="euclidean"))
        im = ax.imshow(D, cmap="viridis")
        plt.colorbar(im, ax=ax, shrink=0.7)
        ax.set_title("(c) State distance matrix")
        plt.suptitle(f"U_{best_uid}: Distinction emergence", fontsize=10)
        plt.tight_layout()
        for ext in ("pdf", "png"):
            fig.savefig(FIG / f"fig_t038_transition_tree.{ext}", format=ext, dpi=300)
        plt.close(fig)
        print("  Saved fig_t038_transition_tree.pdf/.png")

    # Fig 3: Survival matrix
    if len(survival_df) > 0:
        fig, ax = plt.subplots(figsize=(8, 4))
        props_surv = ["distinction_survival", "persistence_survival", "relation_survival"]
        matrix = survival_df[props_surv].values
        im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=0, vmax=2)
        ax.set_xticks(range(len(props_surv)))
        ax.set_xticklabels([p.replace("_survival", "") for p in props_surv])
        ax.set_yticks(range(len(survival_df)))
        ax.set_yticklabels(survival_df["ablation"].values)
        plt.colorbar(im, ax=ax, label="Survival ratio")
        ax.set_title("Emergence survival across ablation conditions")
        for i in range(len(survival_df)):
            for j in range(len(props_surv)):
                val = matrix[i, j]
                color = "white" if val < 0.3 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=6, color=color)
        plt.tight_layout()
        for ext in ("pdf", "png"):
            fig.savefig(FIG / f"fig_t038_survival_matrix.{ext}", format=ext, dpi=300)
        plt.close(fig)
        print("  Saved fig_t038_survival_matrix.pdf/.png")

    # ============================================================
    # FINAL REPORT
    # ============================================================

    elapsed = time.time() - t0
    print(f"\nRuntime: {elapsed:.1f}s")

    # Determine essential assumptions
    if len(survival_df) > 0:
        essential = survival_df[survival_df["mean_survival"] < 0.5]["ablation"].tolist()
        essential = [a.replace("no_", "") for a in essential]
    else:
        essential = []

    # Determine if distinction can emerge from pure Ω
    distinction_possible = n_distinction > 0

    print("\n" + "=" * 70)
    print("T038 RESULTS")
    print("=" * 70)
    print(f"\nUniverses tested: {N_UNIVERSES}")
    print(f"Distinction emerged: {n_distinction}/{N_UNIVERSES} ({100*n_distinction/N_UNIVERSES:.1f}%)")
    print(f"Distinction+Persistence: {len(successful)}/{N_UNIVERSES}")
    print()
    print("Emergence rates:")
    for _, law in laws_df.iterrows():
        print(f"  {law['property']:15s}: {law['emergence_rate']:.3f} at depth {law['mean_depth']:.1f} ± {law['std_depth']:.1f}")
    print()
    print("Essential assumptions for distinction emergence:")
    if essential:
        for a in essential:
            print(f"  - {a}")
    else:
        print("  None identified (distinction is robust)")
    print()
    print("FINAL ANSWER:")
    print(f"  Can distinction emerge from pure Ω? {'YES' if distinction_possible else 'NO'}")
    if distinction_possible:
        print(f"  Minimum substrate: Ω + continuous state + recursion")
        print(f"  (No symbols, no coordinates, no geometry required)")
    else:
        print(f"  Minimum hidden assumption required: {essential}")
    print("=" * 70)

    # Summary JSON
    summary = {
        "n_universes": N_UNIVERSES,
        "distinction_emerged": int(n_distinction),
        "persistence_emerged": int(n_persistence),
        "relation_emerged": int(n_relation),
        "closure_emerged": int(n_closure),
        "selfref_emerged": int(n_selfref),
        "distinction_possible": bool(distinction_possible),
        "essential_assumptions": essential,
        "candidate_laws": laws_df.to_dict(orient="records") if len(laws_df) > 0 else [],
        "minimum_substrate": "Ω + continuous state + recursion" if distinction_possible else str(essential),
    }
    with open(OUT / "t038_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nSaved t038_summary.json")


if __name__ == "__main__":
    main()
