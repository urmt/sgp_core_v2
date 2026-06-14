"""
RD-10B.M2: Migration Map

OBJECTIVE:
> Build a complete dependency graph of every explanatory migration in RD-10B.
> Determine whether the progression is genuine, methodological, or relational.

For every audit:
1. What was being explained?
2. What became explanatory?
3. What fixed variable was later exposed?
4. What mapping replaced it?

Then construct:
Object → Property → Relation → Transformation → Decomposition → Translation

And determine whether this is:
- A genuine empirical progression
- A methodological artifact
- A projection of a deeper translation structure
"""

import json

# ============================================================
# COMPLETE MIGRATION DEPENDENCY GRAPH
# ============================================================

def build_migration_graph():
    """
    For every audit in RD-10B, record:
    - What was being explained
    - What became explanatory
    - What fixed variable was exposed
    - What mapping replaced it
    """
    migrations = [
        {
            'audit': 'RD-10B.3',
            'what_was_explained': 'architectural motifs',
            'what_became_explanatory': 'detector time-series properties',
            'fixed_variable_exposed': 'detector choice',
            'mapping_replaced': 'world → detector → motif',
            'category': 'object → method',
        },
        {
            'audit': 'RD-10B.0',
            'what_was_explained': 'motifs',
            'what_became_explanatory': 'world-representation pair',
            'fixed_variable_exposed': 'representation choice',
            'mapping_replaced': 'world ↔ representation',
            'category': 'object → mapping',
        },
        {
            'audit': 'RD-10B.0A',
            'what_was_explained': 'world identity',
            'what_became_explanatory': 'correspondence quality',
            'fixed_variable_exposed': 'representation pair',
            'mapping_replaced': 'representation₁ ↔ representation₂',
            'category': 'object → mapping',
        },
        {
            'audit': 'RD-10B.0B',
            'what_was_explained': '"same world"',
            'what_became_explanatory': 'identity criteria',
            'fixed_variable_exposed': 'criterion choice',
            'mapping_replaced': 'criterion ↔ purpose',
            'category': 'object → tool',
        },
        {
            'audit': 'RD-10B.0C',
            'what_was_explained': 'identity criteria',
            'what_became_explanatory': 'task-purpose correspondence',
            'fixed_variable_exposed': 'task definition',
            'mapping_replaced': 'task ↔ criterion',
            'category': 'tool → pragmatics',
        },
        {
            'audit': 'RD-10B.0D',
            'what_was_explained': 'causal identity',
            'what_became_explanatory': 'failure modes',
            'fixed_variable_exposed': 'causal criterion',
            'mapping_replaced': 'criterion ↔ failure conditions',
            'category': 'tool → meta-tool',
        },
        {
            'audit': 'RD-10B.0E',
            'what_was_explained': 'criterion domains',
            'what_became_explanatory': 'domain specificity',
            'fixed_variable_exposed': 'domain boundaries',
            'mapping_replaced': 'criterion ↔ domain',
            'category': 'tool → structure',
        },
        {
            'audit': 'RD-10B.0F',
            'what_was_explained': 'world behavior',
            'what_became_explanatory': 'hidden world assumptions',
            'fixed_variable_exposed': 'world construction',
            'mapping_replaced': 'world ↔ assumptions',
            'category': 'object → meta-object',
        },
        {
            'audit': 'RD-10B.X',
            'what_was_explained': 'recursion as junction',
            'what_became_explanatory': 'vocabulary independence',
            'fixed_variable_exposed': 'vocabulary choice',
            'mapping_replaced': 'bottom-up chain ↔ top-down chain',
            'category': 'object → mapping',
        },
        {
            'audit': 'RD-10B.J4',
            'what_was_explained': 'four independent junctions',
            'what_became_explanatory': 'dependency structure',
            'fixed_variable_exposed': 'junction independence assumption',
            'mapping_replaced': 'junction ↔ junction',
            'category': 'objects → relations',
        },
        {
            'audit': 'RD-10B.J6',
            'what_was_explained': 'distinction as generator',
            'what_became_explanatory': 'decomposition dependence',
            'fixed_variable_exposed': 'decomposition choice',
            'mapping_replaced': 'decomposition₁ ↔ decomposition₂',
            'category': 'object → mapping',
        },
        {
            'audit': 'RD-10B.J7',
            'what_was_explained': 'isomorphism class',
            'what_became_explanatory': 'translation structure',
            'fixed_variable_exposed': 'isomorphism definition',
            'mapping_replaced': 'generator₁ ↔ generator₂',
            'category': 'structure → mapping',
        },
        {
            'audit': 'RD-10B.J8',
            'what_was_explained': 'translation invariants',
            'what_became_explanatory': 'translation itself',
            'fixed_variable_exposed': 'invariant definition',
            'mapping_replaced': 'decomposition ↔ invariants',
            'category': 'structure → mapping',
        },
        {
            'audit': 'RD-10B.M1',
            'what_was_explained': 'migration pattern',
            'what_became_explanatory': 'methodology changes',
            'fixed_variable_exposed': 'methodology',
            'mapping_replaced': 'methodology ↔ explanation',
            'category': 'pattern → method',
        },
    ]
    
    return migrations

def analyze_migration_map():
    print("="*70)
    print("RD-10B.M2: MIGRATION MAP")
    print("="*70)
    
    migrations = build_migration_graph()
    
    print("\n--- COMPLETE MIGRATION DEPENDENCY GRAPH ---\n")
    
    for m in migrations:
        print(f"AUDIT: {m['audit']}")
        print(f"  Was explaining: {m['what_was_explained']}")
        print(f"  Became explanatory: {m['what_became_explanatory']}")
        print(f"  Fixed variable exposed: {m['fixed_variable_exposed']}")
        print(f"  Mapping replaced: {m['mapping_replaced']}")
        print(f"  Category: {m['category']}")
        print()
    
    # Pattern analysis
    print("--- PATTERN ANALYSIS ---\n")
    
    # Count categories
    from collections import Counter
    categories = Counter(m['category'] for m in migrations)
    print("Category frequencies:")
    for cat, count in categories.most_common():
        print(f"  {cat}: {count}")
    
    # What became explanatory most often?
    print("\nWhat became explanatory:")
    became = Counter(m['what_became_explanatory'] for m in migrations)
    for item, count in became.most_common():
        print(f"  {item}: {count}")
    
    # What fixed variables were exposed?
    print("\nFixed variables exposed:")
    fixed = Counter(m['fixed_variable_exposed'] for m in migrations)
    for item, count in fixed.most_common():
        print(f"  {item}: {count}")
    
    # What mappings replaced?
    print("\nMappings that replaced:")
    for m in migrations:
        print(f"  {m['audit']}: {m['mapping_replaced']}")
    
    # The progression
    print("\n--- THE PROGRESSION ---\n")
    
    print("Object → Property → Relation → Transformation → Decomposition → Translation")
    print()
    print("Observed in RD-10B:")
    print("  RD-10B.3:  object → method (detector)")
    print("  RD-10B.0:  object → mapping (world-representation)")
    print("  RD-10B.0A: object → mapping (representation correspondence)")
    print("  RD-10B.0B: object → tool (identity criterion)")
    print("  RD-10B.0C: tool → pragmatics (purpose)")
    print("  RD-10B.0D: tool → meta-tool (failure modes)")
    print("  RD-10B.0E: tool → structure (domain)")
    print("  RD-10B.0F: object → meta-object (assumptions)")
    print("  RD-10B.X:  object → mapping (vocabulary)")
    print("  RD-10B.J4: objects → relations (dependency)")
    print("  RD-10B.J6: object → mapping (decomposition)")
    print("  RD-10B.J7: structure → mapping (translation)")
    print("  RD-10B.J8: structure → mapping (invariants)")
    print("  RD-10B.M1: pattern → method (methodology)")
    print()
    
    # Verdict
    print("--- VERDICT ---\n")
    
    print("The progression is NOT:")
    print("  Object → Property → Relation → Transformation → Decomposition → Translation")
    print()
    print("The progression IS:")
    print("  Object → Mapping → Object → Mapping → ...")
    print()
    print("Each time an object becomes explanatory, it is later revealed")
    print("to be a mapping. Then the mapping becomes the new object.")
    print("Then the new object is revealed to be a mapping.")
    print()
    print("This is not a hierarchy.")
    print("This is a oscillation between objects and mappings.")
    print()
    print("The strongest conclusion:")
    print("  RD-10B is not converging toward a deepest level.")
    print("  RD-10B is converging toward a translation structure.")
    print("  Not: what is fundamental?")
    print("  But: what remains invariant when descriptions are translated?")
    print()
    print("This is Path B: the Translation Program.")
    print()
    
    return {
        'migrations': migrations,
        'categories': dict(categories),
        'verdict': 'oscillation_objects_mappings',
    }

if __name__ == '__main__':
    result = analyze_migration_map()
    
    with open('/home/student/sgp_core_v2/audits/rd10bm2_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Saved to audits/rd10bm2_results.json")
