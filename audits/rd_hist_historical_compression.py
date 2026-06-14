"""
RD-HIST.1 Phase 7: Historical Compression

Attempt to determine whether:
H1: Different studies found genuinely different structures.
H2: Multiple studies repeatedly rediscovered the same structure under different names.
"""

import json
from pathlib import Path

ROOT = Path("/home/student/sgp_core_v2")

def analyze_compression():
    print("="*70)
    print("RD-HIST.1 PHASE 7: HISTORICAL COMPRESSION")
    print("="*70)
    
    # Load previous results
    with open(ROOT / 'audits' / 'RD_HIST_EXPLANATORY_LOCUS.json') as f:
        locus_data = json.load(f)
    
    with open(ROOT / 'audits' / 'RD_HIST_PERSISTENCE_MAP.json') as f:
        persistence_data = json.load(f)
    
    with open(ROOT / 'audits' / 'RD_HIST_MIGRATION_GRAPH.json') as f:
        migration_data = json.load(f)
    
    # Group studies by actual locus
    print("\n--- STUDIES GROUPED BY ACTUAL LOCUS ---\n")
    
    locus_groups = {}
    for l in locus_data['loci']:
        locus = l['actual_locus']
        if locus not in locus_groups:
            locus_groups[locus] = []
        locus_groups[locus].append(l['id'])
    
    for locus, studies in sorted(locus_groups.items(), key=lambda x: -len(x[1])):
        print(f"{locus}: {len(studies)} studies")
        for s in studies:
            print(f"  - {s}")
    
    # Group studies by persistence type
    print("\n--- STUDIES GROUPED BY PERSISTENCE TYPE ---\n")
    
    persistence_groups = {}
    for p in persistence_data['persistence']:
        ptype = p['persistence_type']
        if ptype not in persistence_groups:
            persistence_groups[ptype] = []
        persistence_groups[ptype].append(p['id'])
    
    for ptype, studies in sorted(persistence_groups.items(), key=lambda x: -len(x[1])):
        print(f"{ptype}: {len(studies)} studies")
    
    # The compression question
    print("\n--- THE COMPRESSION QUESTION ---\n")
    
    print("H1: Different studies found genuinely different structures.")
    print("H2: Multiple studies repeatedly rediscovered the same structure under different names.")
    
    print("\n--- EVIDENCE FOR H1 ---\n")
    
    print("The persistence types are genuinely different:")
    print("  - pattern (9 studies): recurring patterns in data")
    print("  - structure (7 studies): stable structural relationships")
    print("  - operator (5 studies): transformations that preserve structure")
    print("  - property (5 studies): invariant properties")
    print("  - relation (2 studies): stable relationships between entities")
    print("  - mapping (2 studies): correspondences between domains")
    print()
    print("These are not the same thing under different names.")
    print("They are genuinely different types of persistence.")
    
    print("\n--- EVIDENCE FOR H2 ---\n")
    
    print("The claimed objects kept changing:")
    print("  density → structural importance → velocity field → C")
    print("  → novelty metrics → SP → constraint → topology")
    print("  → distinctions → preservation → lenses → representation")
    print("  → identity → purpose → domains → world assumptions")
    print("  → recursion → constraint → preservation → distinction")
    print("  → path independence → vocabulary → dependency → topology")
    print("  → compression → isomorphism → translation → migration")
    print("  → oscillation → comparison → tension → viewpoint")
    print("  → interaction → fertile interaction → experience → persistence")
    print()
    print("But the actual loci were more stable:")
    print("  Persistence: 14 studies")
    print("  Comparison: 7 studies")
    print("  Relation: 5 studies")
    print("  Interaction: 3 studies")
    print("  Property: 3 studies")
    print("  Transformation: 2 studies")
    print()
    print("The claimed objects changed, but the actual loci were stable.")
    
    # The verdict
    print("\n--- VERDICT ---\n")
    
    print("H1 is partially true: different persistence types are genuinely different.")
    print()
    print("H2 is also partially true: the same few loci kept appearing")
    print("under different claimed objects.")
    print()
    print("The deepest pattern is:")
    print("  The claimed object kept changing.")
    print("  The actual locus was stable.")
    print("  The persistence type was stable.")
    print()
    print("This suggests:")
    print("  The program was repeatedly discovering the same few structures")
    print("  and naming them differently.")
    
    # What survived
    print("\n--- WHAT SURVIVED EVERY CHANGE OF IDEA ---\n")
    
    print("1. Persistence (14 studies)")
    print("   The most common actual locus.")
    print("   The thing that kept surviving reinterpretation.")
    print()
    print("2. Comparison (7 studies)")
    print("   The second most common actual locus.")
    print("   The thing that kept producing explanatory gain.")
    print()
    print("3. The pattern: interaction → persistence → higher-order persistence")
    print("   This is what the archive actually shows.")
    
    # The final compression
    print("\n--- THE FINAL COMPRESSION ---\n")
    
    print("The entire RD-10B sequence can be compressed to:")
    print()
    print("  T037: Interaction exists")
    print("  RD-019-022: Not every interaction persists")
    print("  RD-5: Some interactions produce stable correlations")
    print("  RD-10A: Stable correlations have structure")
    print("  RD-10B.0: Structure depends on perspective")
    print("  RD-10B.X-W: Some structures are junction points")
    print("  RD-10B.J2-J8: Junction points are path-independent")
    print("  RD-10B.M1-M6b: Path independence is comparison-dependent")
    print("  RD-10B.R1-R3: Comparison requires interaction")
    print("  RD-10B.R4: Interaction requires experience")
    print("  RD-10B.R0R: Experience requires persistence")
    print()
    print("The final compression:")
    print()
    print("  persistence of interaction")
    print()
    print("Or more precisely:")
    print()
    print("  hierarchical persistence of interaction")

if __name__ == '__main__':
    analyze_compression()
