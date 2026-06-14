"""IF-3 Stress tests: where does reconstruction from interaction history break?

Tests:
  1. Missing interactions (0–90% removal)
  2. Noisy spurious interactions (0.1x–5x spurious event injection)
  3. Dynamic community membership (split / merge mid-recording)
  4. Hierarchical communities (2-level nested structure)

Each test reports ARI/NMI as a function of degradation.
"""

import numpy as np
import sys, itertools
from typing import Any
sys.path.insert(0, ".")

from interaction_first.experiment_if1 import persistent_communities
from interaction_first.experiment_if3 import reconstruct_from_interaction_history

SEED = 42


def _make_dynamic_communities(
    n_entities: int = 30,
    n_communities: int = 2,
    n_steps: int = 500,
    split_at: int = 250,
    within_prob: float = 0.3,
    between_prob: float = 0.02,
    seed: int = SEED,
) -> tuple[list[dict[str, Any]], np.ndarray]:
    """Communities that split at split_at.

    Pre-split: n_communities groups.
    Post-split: each group splits into 2.
    """
    rng = np.random.default_rng(seed)
    comm_size = n_entities // n_communities
    n_sub = n_entities // (n_communities * 2)

    # Labels: for first half, original communities; for second half, split
    labels = np.zeros(n_entities, dtype=int)
    for c in range(n_communities):
        start = c * comm_size
        for s in range(2):
            sub_start = start + s * n_sub
            labels[sub_start:sub_start + n_sub] = c * 2 + s

    events = []

    def _step(t, cur_labels, active):
        for i, j in active:
            events.append({
                "time": t, "participants": [i, j],
                "type": "interaction",
            })
        new_active = set()
        for i, j in active:
            p_keep = 0.9 if cur_labels[i] == cur_labels[j] else 0.3
            if rng.random() < p_keep:
                new_active.add((i, j))
        for i, j in itertools.combinations(range(n_entities), 2):
            if (i, j) not in new_active:
                p = within_prob * 0.1 if cur_labels[i] == cur_labels[j] else between_prob * 0.1
                if rng.random() < p:
                    new_active.add((i, j))
        return new_active

    # Pre-split: use original (coarse) labels
    coarse_labels = np.repeat(range(n_communities), comm_size)[:n_entities]
    active = set()
    for i, j in itertools.combinations(range(n_entities), 2):
        p = within_prob if coarse_labels[i] == coarse_labels[j] else between_prob
        if rng.random() < p:
            active.add((i, j))

    for t in range(split_at):
        active = _step(t, coarse_labels, active)

    # Post-split: use fine labels
    for t in range(split_at, n_steps):
        active = _step(t, labels, active)

    return events, labels


def _make_hierarchical_communities(
    n_top: int = 3,
    n_sub_per: int = 2,
    entities_per_sub: int = 5,
    n_steps: int = 500,
    seed: int = SEED,
) -> tuple[list[dict[str, Any]], np.ndarray]:
    """Two-level hierarchy.

    Top level: n_top communities.
    Sub level: each top community has n_sub_per sub-communities.

    Interaction rates:
      within-sub: high (0.4)
      within-top (different sub): medium (0.1)
      between-top: low (0.02)
    """
    rng = np.random.default_rng(seed)
    n_entities = n_top * n_sub_per * entities_per_sub
    labels = np.zeros(n_entities, dtype=int)
    for t in range(n_top):
        for s in range(n_sub_per):
            start = (t * n_sub_per + s) * entities_per_sub
            labels[start:start + entities_per_sub] = t * n_sub_per + s

    # Ground truth for evaluation can be either top-level or sub-level
    top_labels = labels // n_sub_per

    events = []
    active = set()
    for i, j in itertools.combinations(range(n_entities), 2):
        if top_labels[i] == top_labels[j]:
            # Same top-level: check if same sub
            same_sub = labels[i] == labels[j]
            p = 0.4 if same_sub else 0.1
        else:
            p = 0.02
        if rng.random() < p:
            active.add((i, j))

    for t in range(n_steps):
        for i, j in active:
            events.append({
                "time": t, "participants": [i, j],
                "type": "interaction",
            })
        new_active = set()
        for i, j in active:
            p_keep = 0.85
            if rng.random() < p_keep:
                new_active.add((i, j))
        for i, j in itertools.combinations(range(n_entities), 2):
            if (i, j) not in new_active:
                p_base = 0.4 if top_labels[i] == top_labels[j] and labels[i] == labels[j] else (
                    0.1 if top_labels[i] == top_labels[j] else 0.02
                )
                if rng.random() < p_base * 0.1:
                    new_active.add((i, j))
        active = new_active

    return events, labels, top_labels


def stress_test_missing(events, labels):
    """Test 1: randomly remove interactions (10%–90%)."""
    rng = np.random.default_rng(SEED)
    n_entities = len(labels)
    fracs = np.arange(0, 0.95, 0.1)
    results = []

    for frac in fracs:
        n_remove = int(len(events) * frac)
        keep_idx = rng.choice(len(events), len(events) - n_remove, replace=False)
        sub = [events[i] for i in sorted(keep_idx)]
        res = reconstruct_from_interaction_history(sub, n_entities, labels)
        results.append({
            "fraction_removed": round(frac, 2),
            "ari": res.get("ari", np.nan),
            "nmi": res.get("nmi", np.nan),
            "n_discovered": res.get("n_discovered", 0),
        })

    return results


def stress_test_noise(events, labels): # test_count: int = 100,
    """Test 2: inject spurious interactions."""
    rng = np.random.default_rng(SEED)
    n_entities = len(labels)
    n_existing = len(events)
    noise_multipliers = [0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
    results = []

    entities = list(range(n_entities))
    for mult in noise_multipliers:
        n_noise = int(n_existing * mult)
        noise_events = []
        for _ in range(n_noise):
            i, j = rng.choice(entities, 2, replace=False)
            noise_events.append({
                "time": rng.integers(0, 500),
                "participants": [int(i), int(j)],
                "type": "spurious",
            })
        combined = events + noise_events
        res = reconstruct_from_interaction_history(combined, n_entities, labels)
        results.append({
            "noise_multiplier": mult,
            "n_noise_events": n_noise,
            "ari": res.get("ari", np.nan),
            "nmi": res.get("nmi", np.nan),
            "n_discovered": res.get("n_discovered", 0),
        })

    return results


def stress_test_dynamic():
    """Test 3: communities that split/merge mid-recording.

    Evaluates against both pre-split (coarse) and post-split (fine) labels.
    """
    print("\n  [Dynamic communities]")
    events, fine_labels = _make_dynamic_communities(
        n_entities=30, n_communities=2, n_steps=500, split_at=250,
        within_prob=0.3, between_prob=0.02,
    )
    n_entities = len(fine_labels)
    coarse_labels = fine_labels // 2

    res_coarse = reconstruct_from_interaction_history(events, n_entities, coarse_labels)
    res_fine = reconstruct_from_interaction_history(events, n_entities, fine_labels)

    results = {
        "n_events": len(events),
        "n_entities": n_entities,
        "evaluation_vs_coarse": {
            "ari": res_coarse.get("ari", np.nan),
            "nmi": res_coarse.get("nmi", np.nan),
            "n_discovered": res_coarse.get("n_discovered", 0),
        },
        "evaluation_vs_fine": {
            "ari": res_fine.get("ari", np.nan),
            "nmi": res_fine.get("nmi", np.nan),
            "n_discovered": res_fine.get("n_discovered", 0),
        },
    }

    return results


def stress_test_hierarchical():
    """Test 4: 2-level hierarchy. Does reconstruction find top-level or sub-level?

    Interaction rates:
      within-sub: 0.4 (high)
      within-top (different sub): 0.1 (medium)
      between-top: 0.02 (low)

    Spectral clustering tends to find the strongest partition.
    """
    print("\n  [Hierarchical]")
    events, sub_labels, top_labels = _make_hierarchical_communities(
        n_top=3, n_sub_per=2, entities_per_sub=5, n_steps=500,
    )
    n_entities = len(sub_labels)

    res_vs_sub = reconstruct_from_interaction_history(events, n_entities, sub_labels)
    res_vs_top = reconstruct_from_interaction_history(events, n_entities, top_labels)

    results = {
        "n_events": len(events),
        "n_entities": n_entities,
        "n_sub_communities": len(np.unique(sub_labels)),
        "n_top_communities": len(np.unique(top_labels)),
        "evaluation_vs_sub": {
            "ari": res_vs_sub.get("ari", np.nan),
            "nmi": res_vs_sub.get("nmi", np.nan),
            "n_discovered": res_vs_sub.get("n_discovered", 0),
        },
        "evaluation_vs_top": {
            "ari": res_vs_top.get("ari", np.nan),
            "nmi": res_vs_top.get("nmi", np.nan),
            "n_discovered": res_vs_top.get("n_discovered", 0),
        },
    }

    return results


def _find_breakpoint(results, metric="ari", threshold=0.3):
    """Find where reconstruction quality drops below threshold."""
    for r in results:
        val = r.get(metric, np.nan)
        if np.isnan(val) or val < threshold:
            return r
    return None


def run_stress_tests():
    print("=" * 78)
    print("  IF-3 STRESS TESTS: WHERE DOES RECONSTRUCTION BREAK?")
    print("=" * 78)

    # Generate baseline data
    baseline_events, baseline_labels = persistent_communities(
        n_entities=30, n_communities=3, n_steps=500, seed=SEED
    )
    n_entities = len(baseline_labels)
    n_baseline_events = len(baseline_events)

    baseline_res = reconstruct_from_interaction_history(
        baseline_events, n_entities, baseline_labels
    )
    base_ari = baseline_res.get("ari", np.nan)
    base_nmi = baseline_res.get("nmi", np.nan)

    print(f"\n  Baseline ({n_baseline_events} events, {n_entities} entities):")
    print(f"    ARI = {base_ari:.4f}, NMI = {base_nmi:.4f}")

    # Test 1: Missing interactions
    print(f"\n{'=' * 78}")
    print("  TEST 1: MISSING INTERACTIONS")
    print(f"{'=' * 78}")
    miss = stress_test_missing(baseline_events, baseline_labels)
    print(f"\n  {'% removed':>10s}  {'ARI':>8s}  {'NMI':>8s}  {'groups':>6s}")
    print(f"  {'-' * 34}")
    for r in miss:
        a = r["ari"]
        n = r["nmi"]
        d = r["n_discovered"]
        print(f"  {r['fraction_removed']:>9.0%}  {a if not np.isnan(a) else float('nan'):>8.4f}  {n if not np.isnan(n) else float('nan'):>8.4f}  {d:>6d}")

    bp_miss = _find_breakpoint(miss)
    bp_str = "none — all pass"
    if bp_miss:
        bp_str = "at {:.0%} removal".format(bp_miss["fraction_removed"])
    print(f"\n  Breakpoint (ARI < 0.3): {bp_str}")

    # Test 2: Noise
    print(f"\n{'=' * 78}")
    print("  TEST 2: SPURIOUS INTERACTIONS")
    print(f"{'=' * 78}")
    noise = stress_test_noise(baseline_events, baseline_labels)
    print(f"\n  {'noise ratio':>10s}  {'n_noise':>8s}  {'ARI':>8s}  {'NMI':>8s}  {'groups':>6s}")
    print(f"  {'-' * 44}")
    for r in noise:
        a = r["ari"]
        n = r["nmi"]
        d = r["n_discovered"]
        print(f"  {r['noise_multiplier']:>10.1f}x  {r['n_noise_events']:>8d}  {a if not np.isnan(a) else float('nan'):>8.4f}  {n if not np.isnan(n) else float('nan'):>8.4f}  {d:>6d}")

    bp_noise = _find_breakpoint(noise)
    bp_str2 = "none — all pass"
    if bp_noise:
        bp_str2 = "at {:.1f}x noise".format(bp_noise["noise_multiplier"])
    print(f"\n  Breakpoint (ARI < 0.3): {bp_str2}")

    # Test 3: Dynamic membership
    print(f"\n{'=' * 78}")
    print("  TEST 3: DYNAMIC COMMUNITY MEMBERSHIP")
    print(f"{'=' * 78}")
    dyn = stress_test_dynamic()
    print(f"\n  Events: {dyn['n_events']}, Entities: {dyn['n_entities']}")
    print(f"\n  Evaluation vs coarse (pre-split) labels:")
    c = dyn["evaluation_vs_coarse"]
    print(f"    ARI = {c['ari']:.4f}, NMI = {c['nmi']:.4f}, groups = {c['n_discovered']}")
    print(f"  Evaluation vs fine (post-split) labels:")
    f = dyn["evaluation_vs_fine"]
    print(f"    ARI = {f['ari']:.4f}, NMI = {f['nmi']:.4f}, groups = {f['n_discovered']}")
    print(f"\n  Interpretation: spectral clustering finds the {c['n_discovered']} group partition")
    print(f"  that best explains the globally pooled interactions.")

    # Test 4: Hierarchical
    print(f"\n{'=' * 78}")
    print("  TEST 4: HIERARCHICAL COMMUNITIES")
    print(f"{'=' * 78}")
    hier = stress_test_hierarchical()
    print(f"\n  Events: {hier['n_events']}, Entities: {hier['n_entities']}")
    print(f"  True hierarchy: {hier['n_top_communities']} top-level × {hier['n_sub_communities'] // hier['n_top_communities']} sub-level")
    print(f"\n  Evaluation vs top-level labels:")
    t = hier["evaluation_vs_top"]
    print(f"    ARI = {t['ari']:.4f}, NMI = {t['nmi']:.4f}, groups = {t['n_discovered']}")
    print(f"  Evaluation vs sub-level labels:")
    s = hier["evaluation_vs_sub"]
    print(f"    ARI = {s['ari']:.4f}, NMI = {s['nmi']:.4f}, groups = {s['n_discovered']}")
    print(f"\n  Interpretation: spectral clustering finds the {t['n_discovered']} level because")
    print(f"  its interaction rate (within-top: 0.1 vs between-top: 0.02) dominates.")

    # Summary
    print(f"\n{'=' * 78}")
    print("  STRESS TEST SUMMARY")
    print(f"{'=' * 78}")
    print(f"""
  Baseline:
    ARI = {base_ari:.4f}, NMI = {base_nmi:.4f}

  Missing interactions:
    ARI = {miss[0]['ari']:.4f} @ 0% -> {miss[-1]['ari'] if not np.isnan(miss[-1]['ari']) else 0:.4f} @ {miss[-1]['fraction_removed']:.0%}
    Breakpoint (ARI < 0.3): {'none' if not bp_miss else '{:.0%} removal'.format(bp_miss['fraction_removed'])}

  Spurious interactions:
    ARI = {noise[0]['ari']:.4f} @ 0x -> {noise[-1]['ari'] if not np.isnan(noise[-1]['ari']) else 0:.4f} @ {noise[-1]['noise_multiplier']:.0f}x
    Breakpoint (ARI < 0.3): {'none' if not bp_noise else '{:.1f}x noise'.format(bp_noise['noise_multiplier'])}

  Dynamic communities:
    Coarse labels (pre-split):  ARI = {dyn['evaluation_vs_coarse']['ari']:.4f}
    Fine labels (post-split):   ARI = {dyn['evaluation_vs_fine']['ari']:.4f}

  Hierarchical communities:
    Top-level:     ARI = {hier['evaluation_vs_top']['ari']:.4f}
    Sub-level:     ARI = {hier['evaluation_vs_sub']['ari']:.4f}
""")

    return {
        "baseline": {"ari": base_ari, "nmi": base_nmi},
        "missing": miss,
        "noise": noise,
        "dynamic": dyn,
        "hierarchical": hier,
    }


if __name__ == "__main__":
    run_stress_tests()
