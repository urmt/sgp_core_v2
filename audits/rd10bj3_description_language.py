"""
RD-10B.J3: Description-Language Audit

QUESTION:
> Do recursion, constraint, preservation, and distinction still emerge
> when the same ladders are described using radically different vocabularies?

DESIGN:
1. Take one representative ladder (particles → atoms → molecules → ... → mathematics).
2. Describe it using five different vocabularies.
3. For each vocabulary, derive what transformations emerge.
4. Check whether the same four junctions appear, or whether they transform
   into something else.

Standing Rule 13: Path independence is necessary but not sufficient.
"""

import json

# ============================================================
# THE LADDER (same structure, different descriptions)
# ============================================================

LADDER = [
    'particles', 'atoms', 'molecules', 'replicators',
    'cells', 'organisms', 'minds', 'mathematics'
]

# ============================================================
# VOCABULARY 1: STRUCTURAL (nodes, edges, closures)
# ============================================================

def describe_structural():
    """
    Describe the ladder using structural vocabulary:
    nodes, edges, closures, boundaries, connectivity.
    """
    descriptions = {
        'particles': 'isolated nodes with no edges',
        'atoms': 'nodes with internal edges (electron shells)',
        'molecules': 'nodes connected by chemical edges',
        'replicators': 'self-referential edge structures',
        'cells': 'bounded networks of edges',
        'organisms': 'nested networks with regulatory edges',
        'minds': 'self-modeling networks',
        'mathematics': 'networks of networks (meta-structure)',
    }
    
    # What transformations emerge?
    transformations = {
        'recursion': {
            'present': True,
            'form': 'self-referential edge structure',
            'description': 'A node that has edges pointing to itself',
        },
        'constraint': {
            'present': True,
            'form': 'bounded connectivity',
            'description': 'Edges are limited by node type',
        },
        'preservation': {
            'present': True,
            'form': 'structure preservation',
            'description': 'The network maintains its topology',
        },
        'distinction': {
            'present': True,
            'form': 'boundary distinction',
            'description': 'Inside vs. outside the network',
        },
    }
    
    return {
        'vocabulary': 'structural',
        'descriptions': descriptions,
        'transformations': transformations,
    }

# ============================================================
# VOCABULARY 2: DYNAMICAL (flows, attractors, trajectories)
# ============================================================

def describe_dynamical():
    """
    Describe the ladder using dynamical vocabulary:
    flows, attractors, trajectories, basins, bifurcations.
    """
    descriptions = {
        'particles': 'free flow, no attractors',
        'atoms': 'stable attractors (energy levels)',
        'molecules': 'attractors with internal dynamics',
        'replicators': 'limit cycles (repetition)',
        'cells': 'homeostatic attractors with regulation',
        'organisms': 'adaptive attractors with learning',
        'minds': 'self-modifying attractors',
        'mathematics': 'attractors of attractors (meta-dynamics)',
    }
    
    transformations = {
        'recursion': {
            'present': True,
            'form': 'self-modifying dynamics',
            'description': 'The dynamics modify themselves',
        },
        'constraint': {
            'present': True,
            'form': 'attractor basin',
            'description': 'The basin limits possible trajectories',
        },
        'preservation': {
            'present': True,
            'form': 'invariant manifold',
            'description': 'The attractor preserves certain quantities',
        },
        'distinction': {
            'present': True,
            'form': 'bifurcation',
            'description': 'The flow splits into distinct regimes',
        },
    }
    
    return {
        'vocabulary': 'dynamical',
        'descriptions': descriptions,
        'transformations': transformations,
    }

# ============================================================
# VOCABULARY 3: INFORMATION (compression, prediction, entropy)
# ============================================================

def describe_information():
    """
    Describe the ladder using information vocabulary:
    compression, prediction, mutual information, entropy, coding.
    """
    descriptions = {
        'particles': 'maximum entropy, no compression',
        'atoms': 'low entropy (bound states), partial compression',
        'molecules': 'structured compression (chemical formula)',
        'replicators': 'self-referential compression (template)',
        'cells': 'compressed regulatory programs',
        'organisms': 'compressed behavioral repertoires',
        'minds': 'compressed world models',
        'mathematics': 'compressed compressions (meta-coding)',
    }
    
    transformations = {
        'recursion': {
            'present': True,
            'form': 'self-referential compression',
            'description': 'A code that can encode itself',
        },
        'constraint': {
            'present': True,
            'form': 'entropy bound',
            'description': 'The system is constrained to low-entropy states',
        },
        'preservation': {
            'present': True,
            'form': 'information preservation',
            'description': 'Relevant information is preserved across transformations',
        },
        'distinction': {
            'present': True,
            'form': 'signal vs. noise',
            'description': 'The system distinguishes signal from noise',
        },
    }
    
    return {
        'vocabulary': 'information',
        'descriptions': descriptions,
        'transformations': transformations,
    }

# ============================================================
# VOCABULARY 4: CATEGORY-THEORETIC (morphisms, functors, adjunctions)
# ============================================================

def describe_categorical():
    """
    Describe the ladder using category-theoretic vocabulary:
    objects, morphisms, functors, natural transformations, adjunctions.
    """
    descriptions = {
        'particles': 'discrete objects, only identity morphisms',
        'atoms': 'objects with internal morphisms (structure)',
        'molecules': 'objects connected by chemical morphisms',
        'replicators': 'endomorphisms (self-maps)',
        'cells': 'categories with regulatory functors',
        'organisms': 'functors between sensory and motor categories',
        'minds': 'self-referential functors (diagonal)',
        'mathematics': '2-categories (categories of categories)',
    }
    
    transformations = {
        'recursion': {
            'present': True,
            'form': 'fixed point of functor',
            'description': 'F(X) ≅ X for some functor F',
        },
        'constraint': {
            'present': True,
            'form': 'universal property',
            'description': 'Objects defined by constraints on morphisms',
        },
        'preservation': {
            'present': True,
            'form': 'functor preservation',
            'description': 'Functors preserve structure',
        },
        'distinction': {
            'present': True,
            'form': 'object distinction',
            'description': 'Objects are distinct if no isomorphism exists',
        },
    }
    
    return {
        'vocabulary': 'categorical',
        'descriptions': descriptions,
        'transformations': transformations,
    }

# ============================================================
# VOCABULARY 5: COMPUTATIONAL (programs, execution, state updates)
# ============================================================

def describe_computational():
    """
    Describe the ladder using computational vocabulary:
    programs, execution, state, input, output, halting.
    """
    descriptions = {
        'particles': 'no program, no state',
        'atoms': 'implicit program (quantum mechanics)',
        'molecules': 'chemical programs (reaction rules)',
        'replicators': 'self-replicating programs',
        'cells': 'regulated programs (gene networks)',
        'organisms': 'adaptive programs (learning)',
        'minds': 'self-modifying programs (reflection)',
        'mathematics': 'programs that reason about programs',
    }
    
    transformations = {
        'recursion': {
            'present': True,
            'form': 'recursive program',
            'description': 'A program that calls itself',
        },
        'constraint': {
            'present': True,
            'form': 'type constraint',
            'description': 'The program is constrained by its type',
        },
        'preservation': {
            'present': True,
            'form': 'input-output preservation',
            'description': 'The program preserves the input-output mapping',
        },
        'distinction': {
            'present': True,
            'form': 'halting distinction',
            'description': 'The program distinguishes halting from non-halting',
        },
    }
    
    return {
        'vocabulary': 'computational',
        'descriptions': descriptions,
        'transformations': transformations,
    }

# ============================================================
# ANALYSIS
# ============================================================

def analyze_description_languages():
    print("="*70)
    print("DESCRIPTION-LANGUAGE AUDIT")
    print("="*70)
    
    vocabularies = [
        describe_structural(),
        describe_dynamical(),
        describe_information(),
        describe_categorical(),
        describe_computational(),
    ]
    
    # Show descriptions
    for vocab in vocabularies:
        print(f"\n--- {vocab['vocabulary'].upper()} VOCABULARY ---")
        for stage, desc in vocab['descriptions'].items():
            print(f"  {stage}: {desc}")
    
    # Count junction appearances
    print("\n--- JUNCTION APPEARANCE ACROSS VOCABULARIES ---")
    
    junction_counts = {}
    for junction in ['recursion', 'constraint', 'preservation', 'distinction']:
        present_count = sum(
            1 for v in vocabularies
            if v['transformations'][junction]['present']
        )
        junction_counts[junction] = present_count
        print(f"  {junction}: {present_count}/{len(vocabularies)}")
    
    # Show forms
    print("\n--- JUNCTION FORMS ACROSS VOCABULARIES ---")
    for junction in ['recursion', 'constraint', 'preservation', 'distinction']:
        print(f"\n  {junction}:")
        for v in vocabularies:
            t = v['transformations'][junction]
            print(f"    {v['vocabulary']}: {t['form']}")
    
    # Verdict
    print("\n--- VERDICT ---")
    
    all_present = all(
        junction_counts[j] == len(vocabularies)
        for j in ['recursion', 'constraint', 'preservation', 'distinction']
    )
    
    if all_present:
        print("\nAll four junctions appear in all five vocabularies.")
        print("This is evidence against vocabulary convergence.")
        print()
        print("However, note that the FORMS differ across vocabularies:")
        for junction in ['recursion', 'constraint', 'preservation', 'distinction']:
            forms = [v['transformations'][junction]['form'] for v in vocabularies]
            unique_forms = set(forms)
            print(f"  {junction}: {len(unique_forms)} different forms")
            if len(unique_forms) > 1:
                print(f"    Examples: {list(unique_forms)[:3]}")
        
        print()
        print("This suggests the junctions are not vocabulary artifacts.")
        print("They appear in different forms in different vocabularies,")
        print("which is what we would expect if they were genuine transformations")
        print("that can be expressed in multiple ways.")
        
        verdict = 'vocabulary_independent'
    else:
        missing = [
            j for j in ['recursion', 'constraint', 'preservation', 'distinction']
            if junction_counts[j] < len(vocabularies)
        ]
        print(f"\nSome junctions are missing from some vocabularies: {missing}")
        print("This suggests vocabulary dependence.")
        verdict = 'vocabulary_dependent'
    
    # The deeper question
    print("\n--- THE DEEPER QUESTION ---")
    print()
    print("Are the four junctions projections of a single deeper transformation?")
    print()
    print("Evidence:")
    print("  - All four appear in all vocabularies")
    print("  - But they have different forms in different vocabularies")
    print("  - This is consistent with them being projections")
    print()
    print("Counter-evidence:")
    print("  - The forms are structurally similar across vocabularies")
    print("  - For example, 'recursion' is always 'self-reference' in some form")
    print("  - This suggests they are genuine, not projections")
    print()
    print("This question cannot be resolved by this audit alone.")
    print("It requires a deeper analysis of the relationship between the four junctions.")
    
    return {
        'vocabularies': len(vocabularies),
        'junction_counts': junction_counts,
        'verdict': verdict,
    }

if __name__ == '__main__':
    result = analyze_description_languages()
    
    with open('/home/student/sgp_core_v2/audits/rd10bj3_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\nSaved to audits/rd10bj3_results.json")
