"""
RD-HIST.1 Phase 2: Explanatory Locus Extraction

For every study extract:
- Claimed explanatory object
- Actual explanatory locus (Object/Property/Relation/Transformation/Interaction/Comparison/Persistence/Translation/Other)
- Confidence score
"""

import json
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")

def build_locus_data():
    """
    Manually extract explanatory loci for major studies.
    This is the ground truth for the reconstruction.
    """
    loci = [
        # === T-series ===
        {
            'id': 'T037_primitive_interaction_genesis',
            'series': 'T',
            'claimed_object': 'primitive interaction operator',
            'actual_locus': 'Interaction',
            'confidence': 0.8,
            'detail': 'Searched for minimum substrate from which distinction, persistence, arithmetic emerge',
        },
        {
            'id': 'T041_interaction_distinction_genesis',
            'series': 'T',
            'claimed_object': 'interaction-distinction genesis',
            'actual_locus': 'Interaction',
            'confidence': 0.8,
            'detail': 'Interaction produces distinction, distinction produces new interaction',
        },

        # === Phase-series ===
        {
            'id': 'phase398_interaction_framework',
            'series': 'Phase',
            'claimed_object': 'recursive interaction dynamics',
            'actual_locus': 'Persistence',
            'confidence': 0.7,
            'detail': 'P-A-N achieves INTERACTION-STABLE: IC=0.9278, CR=0.9104',
        },

        # === RD-series (RD-019 through RD-022) ===
        {
            'id': 'RD-019',
            'series': 'RD',
            'claimed_object': 'density',
            'actual_locus': 'Other (falsification)',
            'confidence': 0.9,
            'detail': 'Density does not cause C (R²=0.055)',
        },
        {
            'id': 'RD-020',
            'series': 'RD',
            'claimed_object': 'structural importance',
            'actual_locus': 'Other (falsification)',
            'confidence': 0.9,
            'detail': 'Structural importance does not cause C (p=0.09)',
        },
        {
            'id': 'RD-021',
            'series': 'RD',
            'claimed_object': 'velocity field',
            'actual_locus': 'Other (falsification)',
            'confidence': 0.9,
            'detail': 'Velocity field does not cause C (p=0.34)',
        },
        {
            'id': 'RD-022',
            'series': 'RD',
            'claimed_object': 'C measurement',
            'actual_locus': 'Property',
            'confidence': 0.7,
            'detail': 'C robust on rank-ordering, estimator-sensitive on level',
        },

        # === RD-5 through RD-9 ===
        {
            'id': 'RD-5',
            'series': 'RD',
            'claimed_object': 'novelty metrics',
            'actual_locus': 'Relation',
            'confidence': 0.9,
            'detail': 'C is projection of MSE (r=-0.89)',
        },
        {
            'id': 'RD-9E',
            'series': 'RD',
            'claimed_object': 'SP (surprise persistence)',
            'actual_locus': 'Other (falsification)',
            'confidence': 0.9,
            'detail': 'SP is binary artifact of discretization',
        },

        # === RD-10A ===
        {
            'id': 'RD-10A.1',
            'series': 'RD',
            'claimed_object': 'stability taxonomy',
            'actual_locus': 'Relation',
            'confidence': 0.6,
            'detail': 'Stability types mapped to constraint types',
        },
        {
            'id': 'RD-10A.8',
            'series': 'RD',
            'claimed_object': 'constraint topology',
            'actual_locus': 'Property',
            'confidence': 0.8,
            'detail': 'Topology more fundamental than constraint set',
        },
        {
            'id': 'RD-10A.9',
            'series': 'RD',
            'claimed_object': 'protected distinctions',
            'actual_locus': 'Property',
            'confidence': 0.8,
            'detail': 'Distinctions more fundamental than topology',
        },
        {
            'id': 'RD-10A.10',
            'series': 'RD',
            'claimed_object': 'distinction preservation',
            'actual_locus': 'Transformation',
            'confidence': 0.8,
            'detail': 'Preservation more fundamental than distinctions',
        },
        {
            'id': 'RD-10A.12',
            'series': 'RD',
            'claimed_object': 'lenses',
            'actual_locus': 'Transformation',
            'confidence': 0.7,
            'detail': 'Distinctions realized through lenses',
        },

        # === RD-10B.0 series ===
        {
            'id': 'RD-10B.0',
            'series': 'RD',
            'claimed_object': 'representation',
            'actual_locus': 'Comparison',
            'confidence': 0.9,
            'detail': 'Motifs are world-representation pairs',
        },
        {
            'id': 'RD-10B.0A',
            'series': 'RD',
            'claimed_object': 'correspondence',
            'actual_locus': 'Comparison',
            'confidence': 0.8,
            'detail': 'Correspondence varies widely',
        },
        {
            'id': 'RD-10B.0B',
            'series': 'RD',
            'claimed_object': 'identity criterion',
            'actual_locus': 'Comparison',
            'confidence': 0.9,
            'detail': 'Criteria disagree on "same world"',
        },
        {
            'id': 'RD-10B.0C',
            'series': 'RD',
            'claimed_object': 'purpose',
            'actual_locus': 'Relation',
            'confidence': 0.8,
            'detail': 'Criteria are task-specific tools',
        },
        {
            'id': 'RD-10B.0D',
            'series': 'RD',
            'claimed_object': 'failure mode',
            'actual_locus': 'Other (falsification)',
            'confidence': 0.8,
            'detail': 'Causal fails 60% of time',
        },
        {
            'id': 'RD-10B.0E',
            'series': 'RD',
            'claimed_object': 'domain',
            'actual_locus': 'Comparison',
            'confidence': 0.8,
            'detail': 'Each criterion has domain',
        },
        {
            'id': 'RD-10B.0F',
            'series': 'RD',
            'claimed_object': 'world assumptions',
            'actual_locus': 'Comparison',
            'confidence': 0.8,
            'detail': 'Worlds have hidden assumptions',
        },

        # === RD-10B.X-W ===
        {
            'id': 'RD-10B.X',
            'series': 'RD',
            'claimed_object': 'recursion',
            'actual_locus': 'Persistence',
            'confidence': 0.8,
            'detail': 'Fixed point of self-referential operator',
        },
        {
            'id': 'RD-10B.Y',
            'series': 'RD',
            'claimed_object': 'constraint',
            'actual_locus': 'Persistence',
            'confidence': 0.7,
            'detail': 'Reachable states under bounding rule',
        },
        {
            'id': 'RD-10B.Z',
            'series': 'RD',
            'claimed_object': 'preservation',
            'actual_locus': 'Persistence',
            'confidence': 0.8,
            'detail': 'Invariance under operation',
        },
        {
            'id': 'RD-10B.W',
            'series': 'RD',
            'claimed_object': 'distinction',
            'actual_locus': 'Persistence',
            'confidence': 0.7,
            'detail': 'Identity from differentiation',
        },

        # === RD-10B.J series ===
        {
            'id': 'RD-10B.J2',
            'series': 'RD',
            'claimed_object': 'path independence',
            'actual_locus': 'Persistence',
            'confidence': 0.9,
            'detail': 'Path independence confirmed across 11 ladders',
        },
        {
            'id': 'RD-10B.J3',
            'series': 'RD',
            'claimed_object': 'vocabulary independence',
            'actual_locus': 'Persistence',
            'confidence': 0.9,
            'detail': 'Vocabulary independence confirmed across 5 vocabularies',
        },
        {
            'id': 'RD-10B.J4',
            'series': 'RD',
            'claimed_object': 'junction dependency',
            'actual_locus': 'Relation',
            'confidence': 0.9,
            'detail': 'Junctions are dependent',
        },
        {
            'id': 'RD-10B.J5',
            'series': 'RD',
            'claimed_object': 'dependency topology',
            'actual_locus': 'Relation',
            'confidence': 0.8,
            'detail': 'Linear chain confirmed',
        },
        {
            'id': 'RD-10B.J6',
            'series': 'RD',
            'claimed_object': 'compression',
            'actual_locus': 'Other (falsification)',
            'confidence': 0.8,
            'detail': 'Compression is decomposition-dependent',
        },
        {
            'id': 'RD-10B.J7',
            'series': 'RD',
            'claimed_object': 'isomorphism class',
            'actual_locus': 'Persistence',
            'confidence': 0.9,
            'detail': 'Isomorphism class identified across decompositions',
        },
        {
            'id': 'RD-10B.J8',
            'series': 'RD',
            'claimed_object': 'translation invariants',
            'actual_locus': 'Persistence',
            'confidence': 0.9,
            'detail': 'Translation invariants identified',
        },

        # === RD-10B.M series ===
        {
            'id': 'RD-10B.M1',
            'series': 'RD',
            'claimed_object': 'migration pattern',
            'actual_locus': 'Other (falsification)',
            'confidence': 0.8,
            'detail': 'Migration is methodological artifact',
        },
        {
            'id': 'RD-10B.M2',
            'series': 'RD',
            'claimed_object': 'oscillation pattern',
            'actual_locus': 'Persistence',
            'confidence': 0.9,
            'detail': 'Progression is oscillation',
        },
        {
            'id': 'RD-10B.M3',
            'series': 'RD',
            'claimed_object': 'comparison vs translation',
            'actual_locus': 'Comparison',
            'confidence': 0.9,
            'detail': 'Translation comes after comparison',
        },
        {
            'id': 'RD-10B.M5',
            'series': 'RD',
            'claimed_object': 'tension-preservation',
            'actual_locus': 'Persistence',
            'confidence': 0.9,
            'detail': 'Tension-preservation is distinguishing factor',
        },
        {
            'id': 'RD-10B.M6b',
            'series': 'RD',
            'claimed_object': 'viewpoint vs claim',
            'actual_locus': 'Comparison',
            'confidence': 0.9,
            'detail': 'Viewpoint: 0% collapse; Claim: 100% collapse',
        },

        # === RD-10B.R series ===
        {
            'id': 'RD-10B.R1',
            'series': 'RD',
            'claimed_object': 'interaction',
            'actual_locus': 'Interaction',
            'confidence': 0.8,
            'detail': 'Every gain involved interaction',
        },
        {
            'id': 'RD-10B.R3',
            'series': 'RD',
            'claimed_object': 'fertile interaction',
            'actual_locus': 'Persistence',
            'confidence': 0.9,
            'detail': 'I+P+N+C configuration for persistent novelty',
        },
        {
            'id': 'RD-10B.R4',
            'series': 'RD',
            'claimed_object': 'experience',
            'actual_locus': 'Persistence',
            'confidence': 0.7,
            'detail': 'Objects are frozen experience',
        },
        {
            'id': 'RD-10B.R0R',
            'series': 'RD',
            'claimed_object': 'persistence ladder',
            'actual_locus': 'Persistence',
            'confidence': 0.9,
            'detail': 'Hierarchical persistence of interaction',
        },
    ]
    return loci

def analyze_loci():
    print("="*70)
    print("RD-HIST.1 PHASE 2: EXPLANATORY LOCUS EXTRACTION")
    print("="*70)
    
    loci = build_locus_data()
    
    # Count by actual locus
    print("\n--- STUDIES BY ACTUAL LOCUS ---\n")
    
    locus_counts = {}
    for l in loci:
        locus = l['actual_locus']
        if locus not in locus_counts:
            locus_counts[locus] = 0
        locus_counts[locus] += 1
    
    for locus, count in sorted(locus_counts.items(), key=lambda x: -x[1]):
        print(f"{locus}: {count} studies")
    
    # Count by series
    print("\n--- STUDIES BY SERIES ---\n")
    
    series_counts = {}
    for l in loci:
        series = l['series']
        if series not in series_counts:
            series_counts[series] = 0
        series_counts[series] += 1
    
    for series, count in sorted(series_counts.items()):
        print(f"{series}: {count} studies")
    
    # Save
    output = {
        'total_studies': len(loci),
        'locus_counts': locus_counts,
        'series_counts': series_counts,
        'loci': loci,
    }
    
    with open(ROOT / 'audits' / 'RD_HIST_EXPLANATORY_LOCUS.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\nSaved to audits/RD_HIST_EXPLANATORY_LOCUS.json")

if __name__ == '__main__':
    analyze_loci()
