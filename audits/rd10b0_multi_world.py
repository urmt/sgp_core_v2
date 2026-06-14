"""
RD-10B.0: Representation Audit — Multi-World Version

Test representation dependence across multiple worlds.
"""

import numpy as np
import json
from collections import defaultdict
import sys

# Import from single-world version
sys.path.insert(0, '/home/student/sgp_core_v2/audits')
from rd10b0_representation_audit import (
    run_world, representation_graph, representation_timeseries,
    representation_state_transition, representation_correlation,
    representation_phasespace, detect_in_graph, detect_in_timeseries,
    detect_in_state_transition, detect_in_correlation, detect_in_phasespace
)

def run_multi_world(n_worlds=10, n_steps=200):
    """Run representation audit across multiple worlds."""
    
    detector_map = {
        'graph': detect_in_graph,
        'timeseries': detect_in_timeseries,
        'state_transition': detect_in_state_transition,
        'correlation': detect_in_correlation,
        'phasespace': detect_in_phasespace,
    }
    
    representation_funcs = {
        'graph': representation_graph,
        'timeseries': representation_timeseries,
        'state_transition': representation_state_transition,
        'correlation': representation_correlation,
        'phasespace': representation_phasespace,
    }
    
    all_results = []
    
    for world_id in range(n_worlds):
        print(f"World {world_id+1}/{n_worlds}...", end='', flush=True)
        
        # Run world
        trajectory, world = run_world(n_steps=n_steps, seed=world_id * 100)
        
        # Create representations
        representations = {}
        for name, func in representation_funcs.items():
            representations[name] = func(trajectory, world)
        
        # Apply detectors
        world_motifs = {}
        for repr_name, repr_data in representations.items():
            detector = detector_map[repr_name]
            motifs = detector(repr_data)
            world_motifs[repr_name] = motifs
        
        all_results.append(world_motifs)
        
        # Quick summary
        motif_counts = defaultdict(int)
        for repr_name, motifs in world_motifs.items():
            for m, v in motifs.items():
                if v > 0.1:
                    motif_counts[m] += 1
        print(f" {dict(motif_counts)}")
    
    return all_results

def analyze_multi_world(results):
    """Analyze representation dependence across worlds."""
    
    print("\n" + "="*70)
    print("MULTI-WORLD REPRESENTATION DEPENDENCE ANALYSIS")
    print("="*70)
    
    # Collect all motif values across worlds and representations
    motif_values = defaultdict(lambda: defaultdict(list))
    
    for world_result in results:
        for repr_name, motifs in world_result.items():
            for motif, value in motifs.items():
                motif_values[motif][repr_name].append(value)
    
    # For each motif, compute representation dependence
    print("\nRepresentation dependence (across all worlds):")
    print(f"\n{'Motif':<15} {'Repr Dep (CV)':<15} {'Present In':<15} {'Verdict'}")
    print("-"*60)
    
    for motif in sorted(motif_values.keys()):
        repr_data = motif_values[motif]
        
        # Collect all values across representations
        all_values = []
        present_in = []
        
        for repr_name, values in repr_data.items():
            if values:
                all_values.extend(values)
                if np.mean(values) > 0.1:
                    present_in.append(repr_name)
        
        if all_values:
            cv = np.std(all_values) / (np.mean(all_values) + 1e-10)
            
            if cv > 1.0:
                verdict = "HIGHLY REPR-DEPENDENT"
            elif cv > 0.5:
                verdict = "MODERATELY REPR-DEPENDENT"
            elif cv > 0.2:
                verdict = "WEAKLY REPR-DEPENDENT"
            else:
                verdict = "REPR-INVARIANT"
            
            print(f"{motif:<15} {cv:<15.3f} {len(present_in)}/5{'':<10} {verdict}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    repr_dependent = 0
    repr_invariant = 0
    
    for motif in motif_values:
        all_values = []
        for repr_name, values in motif_values[motif].items():
            all_values.extend(values)
        
        if all_values:
            cv = np.std(all_values) / (np.mean(all_values) + 1e-10)
            if cv > 0.5:
                repr_dependent += 1
            else:
                repr_invariant += 1
    
    print(f"\nRepresentation-dependent motifs: {repr_dependent}")
    print(f"Representation-invariant motifs: {repr_invariant}")
    
    if repr_dependent > repr_invariant:
        print("\nCONCLUSION: Most motifs are representation-dependent.")
        print("The representation matters more than the world.")
    else:
        print("\nCONCLUSION: Some motifs survive representation changes.")
        print("There may be world-level properties.")

if __name__ == '__main__':
    n_worlds = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    print(f"RD-10B.0: Multi-World Representation Audit")
    print(f"Worlds: {n_worlds}")
    
    results = run_multi_world(n_worlds=n_worlds)
    analyze_multi_world(results)
    
    with open('/home/student/sgp_core_v2/audits/rd10b0_multi_world_results.json', 'w') as f:
        json.dump({'n_worlds': n_worlds, 'motif_values': {
            motif: {repr_name: values for repr_name, values in repr_data.items()}
            for motif, repr_data in motif_values.items()
        }}, f, indent=2, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
    
    print("\nSaved to audits/rd10b0_multi_world_results.json")
