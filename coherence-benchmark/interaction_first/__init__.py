"""Interaction-first experiments runner.

Tests whether stable objects can be reconstructed from interaction networks alone.
"""

import numpy as np

from .experiment_if1 import particle_collisions, game_of_life, persistent_communities
from .experiment_if2 import compute_persistence, compare_to_ground_truth
from .experiment_if3 import reconstruct_from_interaction_history

SEP = "=" * 78


def run_if1():
    """Construct systems with no predefined objects, only interaction events."""
    print(f"\n{SEP}")
    print("  IF-1: SYSTEMS FROM INTERACTION ONLY")
    print(f"{SEP}")

    results = {}

    print("\n  [1/3] Particle collisions (anonymous entities, no tracking) ...")
    evts = particle_collisions(n_entities=20, n_events=2000)
    print(f"        {len(evts)} collision events recorded")
    participants = set()
    for e in evts:
        for p in e.get("participants", []):
            participants.add(p)
    print(f"        {len(participants)} unique entities participated")
    results["collisions"] = {"n_events": len(evts), "n_participants": len(participants)}

    print("\n  [2/3] Game of Life (cell state changes as interaction events) ...")
    evts_gol = game_of_life(grid_size=20, n_steps=500)
    print(f"        {len(evts_gol)} state-change events recorded")
    types = {}
    for e in evts_gol:
        types[e.get("type", "")] = types.get(e.get("type", ""), 0) + 1
    for t, c in types.items():
        print(f"        {t}: {c}")
    results["gol"] = {"n_events": len(evts_gol), "types": types}

    print("\n  [3/3] Persistent communities (dynamic interaction graph) ...")
    evts_pc, labels = persistent_communities(
        n_entities=30, n_communities=3, n_steps=500
    )
    n_unique = len(set(
        p for e in evts_pc for p in e.get("participants", [])
    ))
    print(f"        {len(evts_pc)} interaction events")
    print(f"        {n_unique} entities involved")
    print(f"        Ground truth: {len(np.unique(labels))} communities")
    results["persistent_communities"] = {
        "n_events": len(evts_pc),
        "n_entities": n_unique,
        "n_communities": int(len(np.unique(labels))),
    }

    return results, evts_pc, labels


def run_if2(events, labels):
    """Measure objectness as persistence of interaction topology."""
    print(f"\n{SEP}")
    print("  IF-2: OBJECTNESS = PERSISTENCE OF INTERACTION TOPOLOGY")
    print(f"{SEP}")

    n_entities = len(labels)
    persistence = compute_persistence(events, n_entities, window_size=50)

    print(f"\n  Interaction windows scanned: {persistence['n_windows']}")
    print(f"  Mean pair persistence:       {persistence['mean_persistence']:.4f}")
    print(f"  Interaction sparsity:         {persistence['sparsity']:.4f}")
    print(f"  Objectness score:             {persistence['objectness_score']:.4f}")

    print(f"\n  Entity stability (top-3 partners):")
    stabilities = persistence["entity_stability"]
    for i in np.argsort(stabilities)[-5:]:
        print(f"    entity {i:3d}: {stabilities[i]:.4f}")

    gt = compare_to_ground_truth(persistence["pair_persistence"], labels)
    print(f"\n  [Validation vs ground truth]")
    print(f"    Within-community persistence:  {gt['within_community_persistence']:.4f}")
    print(f"    Between-community persistence: {gt['between_community_persistence']:.4f}")
    print(f"    Separation:                    {gt['separation']:.4f}")
    print(f"    Relative separation:           {gt['relative_separation']:.4f}")

    object_found = gt["separation"] > 0.01
    print(f"\n  -> Objects detectable from interaction persistence: {'YES' if object_found else 'NO'}")

    return persistence, gt, object_found


def run_if3(events, labels):
    """Reconstruct objects from interaction history only."""
    print(f"\n{SEP}")
    print("  IF-3: RECONSTRUCTION FROM INTERACTION HISTORY")
    print(f"{SEP}")

    n_entities = len(labels)
    result = reconstruct_from_interaction_history(
        events, n_entities, ground_truth_labels=labels,
    )

    if "error" in result:
        print(f"\n  Error: {result['error']}")
        return result, False

    print(f"\n  Discovered object-like groups: {result['n_discovered']}")
    print(f"  Requested clusters:              {result['n_clusters_requested']}")
    print(f"  Silhouette score:                {result.get('silhouette', 'N/A'):.4f}")

    if "ari" in result:
        print(f"  Adjusted Rand Index (vs truth):  {result['ari']:.4f}")
        print(f"  NMI (vs truth):                  {result['nmi']:.4f}")

    success = result.get("ari", -1) > 0.3 or result.get("silhouette", -1) > 0.3
    print(f"\n  -> Objects reconstructed from interaction alone: {'YES' if success else 'NO'}")

    return result, success


def run_all():
    """Run all interaction-first experiments and print unified report."""
    print(f"\n{'=' * 78}")
    print("  ONTOLOGY TRACK: DO OBJECTS EMERGE FROM INTERACTION?")
    print(f"{'=' * 78}")

    if1_results, pc_events, pc_labels = run_if1()
    if2_result, gt_result, object_found = run_if2(pc_events, pc_labels)
    if3_result, reconstructed = run_if3(pc_events, pc_labels)

    print(f"\n{'=' * 78}")
    print("  ONTOLOGY TRACK SUMMARY")
    print(f"{'=' * 78}")
    print(f"""
  IF-1: Systems with interaction only
    Particle collisions:           {if1_results['collisions']['n_events']} events
    Game of Life:                  {if1_results['gol']['n_events']} state changes
    Persistent communities:        {if1_results['persistent_communities']['n_events']} interactions

  IF-2: Objectness = persistence of interaction topology
    Objects detectable from interaction persistence:  {'PASS' if object_found else 'FAIL'}

  IF-3: Reconstruction from interaction history
    Objects reconstructed from interaction alone:     {'PASS' if reconstructed else 'FAIL'}

  Verdict:
    {'Interaction-first hypothesis is supported: objects are derivable from'
     ' persistent interaction patterns.' if (object_found or reconstructed)
     else 'Interaction-first hypothesis is NOT supported: objects require'
           ' additional information beyond interaction history.'}
""")


if __name__ == "__main__":
    run_all()
