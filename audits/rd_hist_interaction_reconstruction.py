"""
RD-HIST.1 Phase 3: Interaction Reconstruction

For each study identify:
- Number of descriptions involved (1, 2, 3+)
- Type (object-object, representation-representation, operator-operator, system-system, decomposition-decomposition, other)
- Did explanatory gain appear only after comparison became available? (YES, NO, UNKNOWN)
"""

import json
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")

def build_interaction_data():
    interactions = [
        # === T-series ===
        {
            'id': 'T037_primitive_interaction_genesis',
            'n_descriptions': 2,
            'type': 'operator-operator',
            'gain_after_comparison': 'YES',
            'detail': 'Interaction operators compared to find minimal substrate',
        },
        {
            'id': 'T041_interaction_distinction_genesis',
            'n_descriptions': 2,
            'type': 'operator-operator',
            'gain_after_comparison': 'YES',
            'detail': 'Interaction and distinction operators compared',
        },

        # === Phase-series ===
        {
            'id': 'phase398_interaction_framework',
            'n_descriptions': 3,
            'type': 'system-system',
            'gain_after_comparison': 'YES',
            'detail': 'Multiple network conditions compared',
        },

        # === RD-series ===
        {
            'id': 'RD-019',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'NO',
            'detail': 'Density and C compared (intervention)',
        },
        {
            'id': 'RD-020',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'NO',
            'detail': 'Structural importance and C compared (intervention)',
        },
        {
            'id': 'RD-021',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'NO',
            'detail': 'Velocity field and C compared (intervention)',
        },
        {
            'id': 'RD-022',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Estimators compared for C robustness',
        },
        {
            'id': 'RD-5',
            'n_descriptions': 7,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': '7 metrics compared pairwise',
        },
        {
            'id': 'RD-9E',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'SP and discretization compared',
        },
        {
            'id': 'RD-10A.1',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Stability and constraint types compared',
        },
        {
            'id': 'RD-10A.8',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Constraint set and topology compared',
        },
        {
            'id': 'RD-10A.9',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Topology and distinctions compared',
        },
        {
            'id': 'RD-10A.10',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Distinctions and preservation compared',
        },
        {
            'id': 'RD-10A.12',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Distinctions and lenses compared',
        },
        {
            'id': 'RD-10B.0',
            'n_descriptions': 5,
            'type': 'representation-representation',
            'gain_after_comparison': 'YES',
            'detail': '5 representations compared',
        },
        {
            'id': 'RD-10B.0A',
            'n_descriptions': 5,
            'type': 'representation-representation',
            'gain_after_comparison': 'YES',
            'detail': '5 representations compared for correspondence',
        },
        {
            'id': 'RD-10B.0B',
            'n_descriptions': 5,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': '5 identity criteria compared',
        },
        {
            'id': 'RD-10B.0C',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Criteria and tasks compared',
        },
        {
            'id': 'RD-10B.0D',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Causal and other criteria compared',
        },
        {
            'id': 'RD-10B.0E',
            'n_descriptions': 5,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': '5 worlds compared',
        },
        {
            'id': 'RD-10B.0F',
            'n_descriptions': 5,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': '5 world types compared',
        },
        {
            'id': 'RD-10B.X',
            'n_descriptions': 2,
            'type': 'operator-operator',
            'gain_after_comparison': 'YES',
            'detail': 'Bottom-up and top-down chains compared',
        },
        {
            'id': 'RD-10B.Y',
            'n_descriptions': 2,
            'type': 'operator-operator',
            'gain_after_comparison': 'YES',
            'detail': 'Bottom-up and top-down chains compared',
        },
        {
            'id': 'RD-10B.Z',
            'n_descriptions': 2,
            'type': 'operator-operator',
            'gain_after_comparison': 'YES',
            'detail': 'Bottom-up and top-down chains compared',
        },
        {
            'id': 'RD-10B.W',
            'n_descriptions': 2,
            'type': 'operator-operator',
            'gain_after_comparison': 'YES',
            'detail': 'Bottom-up and top-down chains compared',
        },
        {
            'id': 'RD-10B.J2',
            'n_descriptions': 11,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': '11 ladders compared',
        },
        {
            'id': 'RD-10B.J3',
            'n_descriptions': 5,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': '5 vocabularies compared',
        },
        {
            'id': 'RD-10B.J4',
            'n_descriptions': 4,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': '4 junctions compared for dependency',
        },
        {
            'id': 'RD-10B.J5',
            'n_descriptions': 4,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Dependencies compared for topology',
        },
        {
            'id': 'RD-10B.J6',
            'n_descriptions': 4,
            'type': 'decomposition-decomposition',
            'gain_after_comparison': 'YES',
            'detail': '4 decompositions compared for compression',
        },
        {
            'id': 'RD-10B.J7',
            'n_descriptions': 4,
            'type': 'decomposition-decomposition',
            'gain_after_comparison': 'YES',
            'detail': '4 decompositions compared for isomorphism',
        },
        {
            'id': 'RD-10B.J8',
            'n_descriptions': 2,
            'type': 'decomposition-decomposition',
            'gain_after_comparison': 'YES',
            'detail': '2 decompositions compared for translation',
        },
        {
            'id': 'RD-10B.M1',
            'n_descriptions': 20,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': '20 audits compared for migration',
        },
        {
            'id': 'RD-10B.M2',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Objects and mappings compared',
        },
        {
            'id': 'RD-10B.M3',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Comparison and translation compared',
        },
        {
            'id': 'RD-10B.M5',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Tension and collapse compared',
        },
        {
            'id': 'RD-10B.M6b',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Viewpoint and claim compared',
        },
        {
            'id': 'RD-10B.R1',
            'n_descriptions': 2,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Interaction and explanation compared',
        },
        {
            'id': 'RD-10B.R3',
            'n_descriptions': 4,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'I, P, N, C compared',
        },
        {
            'id': 'RD-10B.R4',
            'n_descriptions': 3,
            'type': 'object-object',
            'gain_after_comparison': 'YES',
            'detail': 'Object, interaction, experience models compared',
        },
        {
            'id': 'RD-10B.R0R',
            'n_descriptions': 1,
            'type': 'object-object',
            'gain_after_comparison': 'NO',
            'detail': 'Single description re-scored for persistence',
        },
    ]
    return interactions

def analyze_interactions():
    print("="*70)
    print("RD-HIST.1 PHASE 3: INTERACTION RECONSTRUCTION")
    print("="*70)
    
    interactions = build_interaction_data()
    
    # Count by gain_after_comparison
    print("\n--- GAIN AFTER COMPARISON ---\n")
    
    gain_counts = {}
    for i in interactions:
        g = i['gain_after_comparison']
        if g not in gain_counts:
            gain_counts[g] = 0
        gain_counts[g] += 1
    
    for g, count in sorted(gain_counts.items()):
        print(f"{g}: {count} studies")
    
    # Count by type
    print("\n--- INTERACTION TYPES ---\n")
    
    type_counts = {}
    for i in interactions:
        t = i['type']
        if t not in type_counts:
            type_counts[t] = 0
        type_counts[t] += 1
    
    for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"{t}: {count} studies")
    
    # Count by n_descriptions
    print("\n--- NUMBER OF DESCRIPTIONS ---\n")
    
    desc_counts = {}
    for i in interactions:
        n = i['n_descriptions']
        if n not in desc_counts:
            desc_counts[n] = 0
        desc_counts[n] += 1
    
    for n, count in sorted(desc_counts.items()):
        print(f"{n} descriptions: {count} studies")
    
    # Save
    output = {
        'total_studies': len(interactions),
        'gain_counts': gain_counts,
        'type_counts': type_counts,
        'desc_counts': desc_counts,
        'interactions': interactions,
    }
    
    with open(ROOT / 'audits' / 'RD_HIST_INTERACTION_MAP.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\nSaved to audits/RD_HIST_INTERACTION_MAP.json")

if __name__ == '__main__':
    analyze_interactions()
