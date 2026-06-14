"""
RD-10B.M6: Tension-Preservation Conditions Audit

QUESTION:
> What conditions allow tension to be maintained? What conditions cause collapse?

DESIGN:
For each audit, characterize:
1. What was held in tension (multiple descriptions, criteria, decompositions)
2. What caused collapse (premature identification, single-description thinking, external pressure)
3. What prevented collapse (methodological discipline, explicit comparison, pluralism)

Identify patterns in what enables vs destroys tension-preservation.
"""

import json

def build_conditions():
    conditions = [
        # RD-5: Metric comparison (no collapse)
        {
            'audit': 'RD-5',
            'in_tension': ['C', 'MSE', 'factors'],
            'collapse_cause': None,
            'prevention': 'explicit comparison',
            'tension_type': 'metric',
        },
        # RD-9E: SP collapsed
        {
            'audit': 'RD-9E',
            'in_tension': ['SP', 'discretization'],
            'collapse_cause': 'methodological artifact detected',
            'prevention': None,
            'tension_type': 'method-artifact',
        },
        # RD-10B.3: Detectors collapsed
        {
            'audit': 'RD-10B.3',
            'in_tension': ['8 detectors × 8 architectures'],
            'collapse_cause': 'systematic testing revealed artifact',
            'prevention': None,
            'tension_type': 'detector',
        },
        # RD-10B.0: No collapse
        {
            'audit': 'RD-10B.0',
            'in_tension': ['graph', 'timeseries', 'state-transition', 'correlation', 'phasespace'],
            'collapse_cause': None,
            'prevention': 'cross-representation comparison',
            'tension_type': 'representation',
        },
        # RD-10B.0A: No collapse
        {
            'audit': 'RD-10B.0A',
            'in_tension': ['5 representations'],
            'collapse_cause': None,
            'prevention': 'correspondence analysis',
            'tension_type': 'representation',
        },
        # RD-10B.0B: Criteria disagree
        {
            'audit': 'RD-10B.0B',
            'in_tension': ['5 identity criteria'],
            'collapse_cause': 'criteria disagreed',
            'prevention': None,
            'tension_type': 'criterion',
        },
        # RD-10B.0C: Criteria task-specific
        {
            'audit': 'RD-10B.0C',
            'in_tension': ['criteria', 'tasks'],
            'collapse_cause': 'mapping revealed task-dependence',
            'prevention': None,
            'tension_type': 'criterion',
        },
        # RD-10B.0D: Causal fails
        {
            'audit': 'RD-10B.0D',
            'in_tension': ['causal', 'other criteria'],
            'collapse_cause': 'stress test revealed failure',
            'prevention': None,
            'tension_type': 'criterion',
        },
        # RD-10B.0E: Worlds differ
        {
            'audit': 'RD-10B.0E',
            'in_tension': ['5 stress worlds'],
            'collapse_cause': None,
            'prevention': 'world comparison',
            'tension_type': 'world',
        },
        # RD-10B.0F: Worlds non-neutral
        {
            'audit': 'RD-10B.0F',
            'in_tension': ['5 world types'],
            'collapse_cause': 'hidden assumptions revealed',
            'prevention': None,
            'tension_type': 'world',
        },
        # RD-10B.X: Recursion junction
        {
            'audit': 'RD-10B.X',
            'in_tension': ['bottom-up', 'top-down'],
            'collapse_cause': None,
            'prevention': 'chain comparison',
            'tension_type': 'path',
        },
        # RD-10B.J2: Path independence
        {
            'audit': 'RD-10B.J2',
            'in_tension': ['11 ladders'],
            'collapse_cause': None,
            'prevention': 'multiple path comparison',
            'tension_type': 'path',
        },
        # RD-10B.J3: Vocabulary independence
        {
            'audit': 'RD-10B.J3',
            'in_tension': ['5 vocabularies'],
            'collapse_cause': None,
            'prevention': 'cross-vocabulary comparison',
            'tension_type': 'vocabulary',
        },
        # RD-10B.J4: Junctions dependent
        {
            'audit': 'RD-10B.J4',
            'in_tension': ['4 junctions as independent'],
            'collapse_cause': 'dependency analysis',
            'prevention': None,
            'tension_type': 'dependency',
        },
        # RD-10B.J6: Compression decomposition-dependent
        {
            'audit': 'RD-10B.J6',
            'in_tension': ['4 decompositions'],
            'collapse_cause': 'compression revealed decomposition-dependence',
            'prevention': None,
            'tension_type': 'decomposition',
        },
        # RD-10B.J7: Isomorphism class
        {
            'audit': 'RD-10B.J7',
            'in_tension': ['4 decompositions'],
            'collapse_cause': None,
            'prevention': 'isomorphism analysis',
            'tension_type': 'decomposition',
        },
        # RD-10B.J8: Translation invariants
        {
            'audit': 'RD-10B.J8',
            'in_tension': ['2 decompositions'],
            'collapse_cause': None,
            'prevention': 'explicit translation maps',
            'tension_type': 'decomposition',
        },
        # RD-10B.M1: Migration methodological
        {
            'audit': 'RD-10B.M1',
            'in_tension': ['migration as genuine'],
            'collapse_cause': 'null model showed methodological artifact',
            'prevention': None,
            'tension_type': 'methodology',
        },
        # RD-10B.M2: Progression oscillation
        {
            'audit': 'RD-10B.M2',
            'in_tension': ['hierarchical progression'],
            'collapse_cause': None,
            'prevention': None,
            'tension_type': 'meta',
        },
    ]
    return conditions

def analyze_conditions():
    print("="*70)
    print("RD-10B.M6: TENSION-PRESERVATION CONDITIONS AUDIT")
    print("="*70)
    
    conditions = build_conditions()
    
    # Collapse causes
    print("\n--- COLLAPSE CAUSES ---\n")
    collapsed = [c for c in conditions if c['collapse_cause'] is not None]
    not_collapsed = [c for c in conditions if c['collapse_cause'] is None]
    
    print(f"Collapsed: {len(collapsed)} audits")
    for c in collapsed:
        print(f"  {c['audit']}: {c['collapse_cause']}")
    
    print(f"\nNot collapsed: {len(not_collapsed)} audits")
    
    # Prevention methods
    print("\n--- PREVENTION METHODS ---\n")
    prevented = [c for c in conditions if c['prevention'] is not None]
    not_prevented = [c for c in conditions if c['prevention'] is None]
    
    print(f"Prevented: {len(prevented)} audits")
    for c in prevented:
        print(f"  {c['audit']}: {c['prevention']}")
    
    print(f"\nNot prevented: {len(not_prevented)} audits")
    for c in not_prevented:
        print(f"  {c['audit']}: collapsed={c['collapse_cause'] is not None}")
    
    # Tension types
    print("\n--- TENSION TYPES ---\n")
    types = {}
    for c in conditions:
        t = c['tension_type']
        if t not in types:
            types[t] = []
        types[t].append(c)
    
    for t, cs in sorted(types.items()):
        collapsed_count = sum(1 for c in cs if c['collapse_cause'] is not None)
        print(f"{t}: {len(cs)} audits, {collapsed_count} collapsed")
    
    # Key patterns
    print("\n--- KEY PATTERNS ---\n")
    
    print("1. Collapse occurs when:")
    print("   - Methodological artifacts are detected (RD-9E, RD-10B.3)")
    print("   - Systematic testing reveals failure (RD-10B.0D)")
    print("   - Dependency analysis reveals non-independence (RD-10B.J4)")
    print("   - Compression reveals decomposition-dependence (RD-10B.J6)")
    print("   - Null model shows methodological artifact (RD-10B.M1)")
    
    print()
    print("2. Tension is preserved when:")
    print("   - Explicit comparison is maintained (RD-5, RD-10B.0, RD-10B.0A)")
    print("   - Cross-representation mapping is used (RD-10B.X, RD-10B.J2)")
    print("   - Cross-vocabulary comparison is used (RD-10B.J3)")
    print("   - Isomorphism analysis is used (RD-10B.J7)")
    print("   - Explicit translation maps are constructed (RD-10B.J8)")
    
    print()
    print("3. The fundamental condition for tension-preservation:")
    print("   EXPLICIT COMPARISON STRUCTURE")
    print("   When comparison is structured and explicit, tension is preserved.")
    print("   When comparison is implicit or absent, collapse occurs.")

if __name__ == '__main__':
    analyze_conditions()
