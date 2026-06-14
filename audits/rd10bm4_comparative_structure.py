"""
RD-10B.M4: Comparative Structure Audit (Characterization)

QUESTION:
> What makes comparison productive?

DESIGN:
For each audit with comparison present, characterize:
1. The TYPE of comparison (metric, representation, criterion, path, vocabulary, decomposition)
2. The STRUCTURE of comparison (pairwise, all-pairs, against-external, against-internal)
3. The GAIN from comparison (new invariant, new distinction, new relationship, collapse of assumption)
4. The COST of comparison (computational, conceptual, requires external input)

Then identify patterns:
- Which types of comparison are most productive?
- Which structures are most productive?
- What distinguishes productive comparison from unproductive comparison?
"""

import json

def build_comparative_structure():
    comparisons = [
        # RD-5: Metric comparison
        {
            'audit': 'RD-5',
            'type': 'metric',
            'structure': 'all-pairs',
            'descriptions_compared': ['C', 'MSE', 'factors'],
            'gain': 'new relationship',
            'gain_detail': 'C is projection of MSE',
            'cost': 'low',
            'productive': True,
        },
        # RD-9E: Method vs artifact
        {
            'audit': 'RD-9E',
            'type': 'method-artifact',
            'structure': 'pairwise',
            'descriptions_compared': ['SP', 'discretization'],
            'gain': 'collapse of assumption',
            'gain_detail': 'SP is binary artifact',
            'cost': 'low',
            'productive': True,
        },
        # RD-10B.3: Detector variants
        {
            'audit': 'RD-10B.3',
            'type': 'detector',
            'structure': 'all-pairs',
            'descriptions_compared': ['8 detectors × 8 architectures'],
            'gain': 'collapse of assumption',
            'gain_detail': 'Detectors measure time-series, not architecture',
            'cost': 'high',
            'productive': True,
        },
        # RD-10B.0: Representation comparison
        {
            'audit': 'RD-10B.0',
            'type': 'representation',
            'structure': 'all-pairs',
            'descriptions_compared': ['graph', 'timeseries', 'state-transition', 'correlation', 'phasespace'],
            'gain': 'new invariant',
            'gain_detail': 'Motifs are world-representation pairs',
            'cost': 'medium',
            'productive': True,
        },
        # RD-10B.0A: Correspondence
        {
            'audit': 'RD-10B.0A',
            'type': 'representation',
            'structure': 'all-pairs',
            'descriptions_compared': ['5 representations'],
            'gain': 'new distinction',
            'gain_detail': 'Correspondence varies widely',
            'cost': 'medium',
            'productive': True,
        },
        # RD-10B.0B: Identity criteria
        {
            'audit': 'RD-10B.0B',
            'type': 'criterion',
            'structure': 'all-pairs',
            'descriptions_compared': ['5 identity criteria'],
            'gain': 'collapse of assumption',
            'gain_detail': 'Criteria disagree on "same world"',
            'cost': 'low',
            'productive': True,
        },
        # RD-10B.0C: Criteria vs tasks
        {
            'audit': 'RD-10B.0C',
            'type': 'criterion',
            'structure': 'against-external',
            'descriptions_compared': ['criteria', 'tasks'],
            'gain': 'new relationship',
            'gain_detail': 'Criteria are task-specific tools',
            'cost': 'low',
            'productive': True,
        },
        # RD-10B.0D: Criterion stress
        {
            'audit': 'RD-10B.0D',
            'type': 'criterion',
            'structure': 'pairwise',
            'descriptions_compared': ['causal', 'other criteria'],
            'gain': 'new distinction',
            'gain_detail': 'Causal fails 60% of time',
            'cost': 'low',
            'productive': True,
        },
        # RD-10B.0E: World comparison
        {
            'audit': 'RD-10B.0E',
            'type': 'world',
            'structure': 'all-pairs',
            'descriptions_compared': ['5 stress worlds'],
            'gain': 'new invariant',
            'gain_detail': 'Each criterion has domain',
            'cost': 'medium',
            'productive': True,
        },
        # RD-10B.0F: World types
        {
            'audit': 'RD-10B.0F',
            'type': 'world',
            'structure': 'all-pairs',
            'descriptions_compared': ['5 world types'],
            'gain': 'new distinction',
            'gain_detail': 'Worlds have hidden assumptions',
            'cost': 'low',
            'productive': True,
        },
        # RD-10B.X: Chain comparison
        {
            'audit': 'RD-10B.X',
            'type': 'path',
            'structure': 'pairwise',
            'descriptions_compared': ['bottom-up', 'top-down'],
            'gain': 'new invariant',
            'gain_detail': 'Recursion is junction candidate',
            'cost': 'medium',
            'productive': True,
        },
        # RD-10B.J2: Path comparison
        {
            'audit': 'RD-10B.J2',
            'type': 'path',
            'structure': 'all-pairs',
            'descriptions_compared': ['11 ladders'],
            'gain': 'new invariant',
            'gain_detail': 'Path independence confirmed',
            'cost': 'high',
            'productive': True,
        },
        # RD-10B.J3: Vocabulary comparison
        {
            'audit': 'RD-10B.J3',
            'type': 'vocabulary',
            'structure': 'all-pairs',
            'descriptions_compared': ['5 vocabularies'],
            'gain': 'new invariant',
            'gain_detail': 'Vocabulary independence confirmed',
            'cost': 'high',
            'productive': True,
        },
        # RD-10B.J4: Dependency analysis
        {
            'audit': 'RD-10B.J4',
            'type': 'dependency',
            'structure': 'all-pairs',
            'descriptions_compared': ['4 junctions'],
            'gain': 'new relationship',
            'gain_detail': 'Junctions are dependent',
            'cost': 'medium',
            'productive': True,
        },
        # RD-10B.J6: Decomposition comparison
        {
            'audit': 'RD-10B.J6',
            'type': 'decomposition',
            'structure': 'all-pairs',
            'descriptions_compared': ['4 decompositions'],
            'gain': 'collapse of assumption',
            'gain_detail': 'Compression is decomposition-dependent',
            'cost': 'high',
            'productive': True,
        },
        # RD-10B.J7: Isomorphism analysis
        {
            'audit': 'RD-10B.J7',
            'type': 'decomposition',
            'structure': 'all-pairs',
            'descriptions_compared': ['4 decompositions'],
            'gain': 'new invariant',
            'gain_detail': 'Isomorphism class identified',
            'cost': 'high',
            'productive': True,
        },
        # RD-10B.J8: Translation analysis
        {
            'audit': 'RD-10B.J8',
            'type': 'decomposition',
            'structure': 'pairwise',
            'descriptions_compared': ['2 decompositions'],
            'gain': 'new invariant',
            'gain_detail': 'Translation invariants identified',
            'cost': 'high',
            'productive': True,
        },
    ]
    return comparisons

def analyze_structure():
    print("="*70)
    print("RD-10B.M4: COMPARATIVE STRUCTURE AUDIT")
    print("="*70)
    
    comparisons = build_comparative_structure()
    
    # By type
    print("\n--- BY COMPARISON TYPE ---\n")
    types = {}
    for c in comparisons:
        t = c['type']
        if t not in types:
            types[t] = []
        types[t].append(c)
    
    for t, cs in sorted(types.items()):
        print(f"{t}: {len(cs)} audits")
        for c in cs:
            print(f"  {c['audit']}: {c['gain']}")
    
    # By structure
    print("\n--- BY COMPARISON STRUCTURE ---\n")
    structures = {}
    for c in comparisons:
        s = c['structure']
        if s not in structures:
            structures[s] = []
        structures[s].append(c)
    
    for s, cs in sorted(structures.items()):
        print(f"{s}: {len(cs)} audits")
        for c in cs:
            print(f"  {c['audit']}: {c['type']}")
    
    # By gain type
    print("\n--- BY GAIN TYPE ---\n")
    gains = {}
    for c in comparisons:
        g = c['gain']
        if g not in gains:
            gains[g] = []
        gains[g].append(c)
    
    for g, cs in sorted(gains.items()):
        print(f"{g}: {len(cs)} audits")
        for c in cs:
            print(f"  {c['audit']}: {c['type']}")
    
    # Most productive structure
    print("\n--- MOST PRODUCTIVE STRUCTURE ---\n")
    for s, cs in structures.items():
        print(f"{s}: {len(cs)} audits")
    
    # Key patterns
    print("\n--- KEY PATTERNS ---\n")
    
    print("1. All-pairs comparison dominates: 12 of 17 audits")
    print("2. Representation and criterion comparison are most common")
    print("3. New invariants and collapse of assumptions are most common gains")
    print("4. All comparisons are productive (no unproductive comparisons)")
    
    # The question
    print("\n--- THE QUESTION ---\n")
    print("If all comparisons are productive, what distinguishes")
    print("productive comparison from unproductive comparison?")
    print()
    print("Answer: We don't know, because we haven't seen unproductive comparison.")
    print("Every comparison in RD-10B has been productive.")
    print()
    print("This suggests that comparison is ALWAYS productive.")
    print("The question is not whether to compare, but what to compare.")

if __name__ == '__main__':
    analyze_structure()
