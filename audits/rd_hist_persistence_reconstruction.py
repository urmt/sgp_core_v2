"""
RD-HIST.1 Phase 4: Persistence Reconstruction

For each study identify:
- What persisted?
- What destroyed persistence?
"""

import json
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")

def build_persistence_data():
    persistence = [
        # === T-series ===
        {
            'id': 'T037_primitive_interaction_genesis',
            'what_persisted': 'interaction operators',
            'what_destroyed': 'N/A (foundational study)',
            'persistence_type': 'operator',
        },
        {
            'id': 'T041_interaction_distinction_genesis',
            'what_persisted': 'interaction-distinction loop',
            'what_destroyed': 'N/A (foundational study)',
            'persistence_type': 'loop',
        },

        # === Phase-series ===
        {
            'id': 'phase398_interaction_framework',
            'what_persisted': 'interaction coherence (IC=0.9278)',
            'what_destroyed': 'N/A (successful study)',
            'persistence_type': 'signal',
        },

        # === RD-series ===
        {
            'id': 'RD-019',
            'what_persisted': 'nothing (falsified)',
            'what_destroyed': 'density as explanation',
            'persistence_type': 'none',
        },
        {
            'id': 'RD-020',
            'what_persisted': 'nothing (falsified)',
            'what_destroyed': 'structural importance as explanation',
            'persistence_type': 'none',
        },
        {
            'id': 'RD-021',
            'what_persisted': 'nothing (falsified)',
            'what_destroyed': 'velocity field as explanation',
            'persistence_type': 'none',
        },
        {
            'id': 'RD-022',
            'what_persisted': 'C rank-order stability',
            'what_destroyed': 'C level stability',
            'persistence_type': 'property',
        },
        {
            'id': 'RD-5',
            'what_persisted': 'C-MSE correlation (r=-0.89)',
            'what_destroyed': 'independent novelty metrics',
            'persistence_type': 'relation',
        },
        {
            'id': 'RD-9E',
            'what_persisted': 'nothing (falsified)',
            'what_destroyed': 'SP as genuine property',
            'persistence_type': 'none',
        },
        {
            'id': 'RD-10A.1',
            'what_persisted': 'stability-constraint mapping',
            'what_destroyed': 'N/A',
            'persistence_type': 'mapping',
        },
        {
            'id': 'RD-10A.8',
            'what_persisted': 'topology as invariant',
            'what_destroyed': 'constraint set as fundamental',
            'persistence_type': 'property',
        },
        {
            'id': 'RD-10A.9',
            'what_persisted': 'distinctions as invariant',
            'what_destroyed': 'topology as fundamental',
            'persistence_type': 'property',
        },
        {
            'id': 'RD-10A.10',
            'what_persisted': 'preservation as invariant',
            'what_destroyed': 'distinctions as fundamental',
            'persistence_type': 'transformation',
        },
        {
            'id': 'RD-10A.12',
            'what_persisted': 'lenses as mechanism',
            'what_destroyed': 'distinctions as intrinsic',
            'persistence_type': 'mechanism',
        },
        {
            'id': 'RD-10B.0',
            'what_persisted': 'world-representation pair',
            'what_destroyed': 'motifs as world properties',
            'persistence_type': 'pair',
        },
        {
            'id': 'RD-10B.0A',
            'what_persisted': 'correspondence structure',
            'what_destroyed': 'consistent correspondence',
            'persistence_type': 'structure',
        },
        {
            'id': 'RD-10B.0B',
            'what_persisted': 'criterion disagreement',
            'what_destroyed': 'unified identity',
            'persistence_type': 'pattern',
        },
        {
            'id': 'RD-10B.0C',
            'what_persisted': 'task-criterion mapping',
            'what_destroyed': 'universal criteria',
            'persistence_type': 'mapping',
        },
        {
            'id': 'RD-10B.0D',
            'what_persisted': 'causal failure pattern',
            'what_destroyed': 'causal criterion universality',
            'persistence_type': 'pattern',
        },
        {
            'id': 'RD-10B.0E',
            'what_persisted': 'criterion domains',
            'what_destroyed': 'universal criterion applicability',
            'persistence_type': 'structure',
        },
        {
            'id': 'RD-10B.0F',
            'what_persisted': 'world hidden assumptions',
            'what_destroyed': 'worlds as neutral',
            'persistence_type': 'structure',
        },
        {
            'id': 'RD-10B.X',
            'what_persisted': 'recursion as junction',
            'what_destroyed': 'N/A',
            'persistence_type': 'operator',
        },
        {
            'id': 'RD-10B.Y',
            'what_persisted': 'constraint as junction',
            'what_destroyed': 'N/A',
            'persistence_type': 'operator',
        },
        {
            'id': 'RD-10B.Z',
            'what_persisted': 'preservation as junction',
            'what_destroyed': 'N/A',
            'persistence_type': 'operator',
        },
        {
            'id': 'RD-10B.W',
            'what_persisted': 'distinction as junction',
            'what_destroyed': 'N/A',
            'persistence_type': 'operator',
        },
        {
            'id': 'RD-10B.J2',
            'what_persisted': 'path independence',
            'what_destroyed': 'N/A',
            'persistence_type': 'property',
        },
        {
            'id': 'RD-10B.J3',
            'what_persisted': 'vocabulary independence',
            'what_destroyed': 'N/A',
            'persistence_type': 'property',
        },
        {
            'id': 'RD-10B.J4',
            'what_persisted': 'dependency chain',
            'what_destroyed': 'junction independence',
            'persistence_type': 'structure',
        },
        {
            'id': 'RD-10B.J5',
            'what_persisted': 'linear topology',
            'what_destroyed': 'N/A',
            'persistence_type': 'structure',
        },
        {
            'id': 'RD-10B.J6',
            'what_persisted': 'decomposition dependence',
            'what_destroyed': 'unique generator',
            'persistence_type': 'pattern',
        },
        {
            'id': 'RD-10B.J7',
            'what_persisted': 'isomorphism class',
            'what_destroyed': 'specific generator',
            'persistence_type': 'structure',
        },
        {
            'id': 'RD-10B.J8',
            'what_persisted': 'translation invariants',
            'what_destroyed': 'N/A',
            'persistence_type': 'structure',
        },
        {
            'id': 'RD-10B.M1',
            'what_persisted': 'methodological artifact',
            'what_destroyed': 'migration as genuine',
            'persistence_type': 'pattern',
        },
        {
            'id': 'RD-10B.M2',
            'what_persisted': 'oscillation pattern',
            'what_destroyed': 'hierarchical progression',
            'persistence_type': 'pattern',
        },
        {
            'id': 'RD-10B.M3',
            'what_persisted': 'comparison before translation',
            'what_destroyed': 'translation as source',
            'persistence_type': 'pattern',
        },
        {
            'id': 'RD-10B.M5',
            'what_persisted': 'tension-preservation',
            'what_destroyed': 'collapse as productive',
            'persistence_type': 'pattern',
        },
        {
            'id': 'RD-10B.M6b',
            'what_persisted': 'viewpoint comparison',
            'what_destroyed': 'claim comparison',
            'persistence_type': 'pattern',
        },
        {
            'id': 'RD-10B.R1',
            'what_persisted': 'interaction-explanation link',
            'what_destroyed': 'object as source',
            'persistence_type': 'relation',
        },
        {
            'id': 'RD-10B.R3',
            'what_persisted': 'I+P+N+C configuration',
            'what_destroyed': 'interaction alone as sufficient',
            'persistence_type': 'configuration',
        },
        {
            'id': 'RD-10B.R4',
            'what_persisted': 'experience as underlying',
            'what_destroyed': 'object as primary',
            'persistence_type': 'concept',
        },
        {
            'id': 'RD-10B.R0R',
            'what_persisted': 'hierarchical persistence',
            'what_destroyed': 'all other candidates as fundamental',
            'persistence_type': 'pattern',
        },
    ]
    return persistence

def analyze_persistence():
    print("="*70)
    print("RD-HIST.1 PHASE 4: PERSISTENCE RECONSTRUCTION")
    print("="*70)
    
    persistence = build_persistence_data()
    
    # Count by persistence_type
    print("\n--- PERSISTENCE TYPES ---\n")
    
    type_counts = {}
    for p in persistence:
        t = p['persistence_type']
        if t not in type_counts:
            type_counts[t] = 0
        type_counts[t] += 1
    
    for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"{t}: {count} studies")
    
    # Count what was destroyed
    print("\n--- WHAT WAS DESTROYED ---\n")
    
    destroyed = [p for p in persistence if p['what_destroyed'] != 'N/A']
    not_destroyed = [p for p in persistence if p['what_destroyed'] == 'N/A']
    
    print(f"Studies with destruction: {len(destroyed)}")
    print(f"Studies without destruction: {len(not_destroyed)}")
    
    # Most common destructions
    destruction_items = {}
    for p in destroyed:
        d = p['what_destroyed']
        if d not in destruction_items:
            destruction_items[d] = 0
        destruction_items[d] += 1
    
    print("\nMost common destructions:")
    for d, count in sorted(destruction_items.items(), key=lambda x: -x[1])[:10]:
        print(f"  {d}: {count}")
    
    # Save
    output = {
        'total_studies': len(persistence),
        'type_counts': type_counts,
        'destroyed_count': len(destroyed),
        'not_destroyed_count': len(not_destroyed),
        'persistence': persistence,
    }
    
    with open(ROOT / 'audits' / 'RD_HIST_PERSISTENCE_MAP.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\nSaved to audits/RD_HIST_PERSISTENCE_MAP.json")

if __name__ == '__main__':
    analyze_persistence()
