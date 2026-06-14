"""
RD-10B.R3: Fertile Interaction Audit

QUESTION:
What configuration of interaction produces fertility?

THE ACTUAL CLAIM:
Persistent novelty emerges when coherent structures can interact
without collapsing each other.

REQUIRED COMPONENTS:
1. Interaction — structures are in contact
2. Persistence — the interaction doesn't destroy the structures
3. Novelty — something new emerges from the interaction
4. Coherence — the structures are internally consistent

For every major success and every known failure, measure:
- Interaction present?
- Persistence present?
- Novelty present?
- Coherence present?
- Explanatory gain present?

Then ask: which combinations predict explanatory gain?
"""

import json

def build_fertility_data():
    """
    For each audit, measure the four components and gain.
    """
    audits = [
        # === SUCCESSES ===
        {
            'audit': 'RD-5',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'C is projection of MSE',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10A.8',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Topology more fundamental than constraint set',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10A.9',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Distinctions more fundamental than topology',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10A.10',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Preservation more fundamental than distinctions',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10A.12',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Distinctions realized through lenses',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10B.0',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Motifs are world-representation pairs',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10B.0A',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Correspondence varies widely',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10B.0B',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': False,  # Criteria disagree — no coherent resolution
            'gain': True,
            'gain_detail': 'Criteria disagree on "same world"',
            'config': 'I+P+N',
        },
        {
            'audit': 'RD-10B.0C',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Criteria are task-specific tools',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10B.0E',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Each criterion has domain',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10B.0F',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': False,  # Worlds have hidden assumptions — incoherent
            'gain': True,
            'gain_detail': 'Worlds have hidden assumptions',
            'config': 'I+P+N',
        },
        {
            'audit': 'RD-10B.J2',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Path independence confirmed',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10B.J3',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Vocabulary independence confirmed',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10B.J7',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Isomorphism class identified',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10B.J8',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Translation invariants identified',
            'config': 'I+P+N+C',
        },
        {
            'audit': 'RD-10B.M6b',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Viewpoint: 0% collapse; Claim: 100% collapse',
            'config': 'I+P+N+C',
        },

        # === FAILURES (falsifications that were productive) ===
        {
            'audit': 'RD-019',
            'interaction': True,
            'persistence': False,  # Density was destroyed as explanation
            'novelty': False,  # No new structure — just falsification
            'coherence': True,
            'gain': True,
            'gain_detail': 'Density does not cause C',
            'config': 'I+C',
        },
        {
            'audit': 'RD-020',
            'interaction': True,
            'persistence': False,
            'novelty': False,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Structural importance does not cause C',
            'config': 'I+C',
        },
        {
            'audit': 'RD-021',
            'interaction': True,
            'persistence': False,
            'novelty': False,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Velocity field does not cause C',
            'config': 'I+C',
        },
        {
            'audit': 'RD-9E',
            'interaction': True,
            'persistence': False,  # SP was destroyed as artifact
            'novelty': False,
            'coherence': True,
            'gain': True,
            'gain_detail': 'SP is binary artifact',
            'config': 'I+C',
        },
        {
            'audit': 'RD-10B.3',
            'interaction': True,
            'persistence': False,  # Detectors were destroyed as architectural
            'novelty': False,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Detectors measure time-series, not architecture',
            'config': 'I+C',
        },
        {
            'audit': 'RD-10B.J4',
            'interaction': True,
            'persistence': False,  # Junction independence was destroyed
            'novelty': True,  # Dependency chain is new structure
            'coherence': True,
            'gain': True,
            'gain_detail': 'Junctions are dependent',
            'config': 'I+N+C',
        },
        {
            'audit': 'RD-10B.J6',
            'interaction': True,
            'persistence': False,  # Unique generator was destroyed
            'novelty': True,  # Decomposition-dependence is new
            'coherence': True,
            'gain': True,
            'gain_detail': 'Compression is decomposition-dependent',
            'config': 'I+N+C',
        },
        {
            'audit': 'RD-10B.M1',
            'interaction': True,
            'persistence': False,  # Migration was destroyed as genuine
            'novelty': False,
            'coherence': True,
            'gain': True,
            'gain_detail': 'Migration is methodological artifact',
            'config': 'I+C',
        },

        # === ABANDONED (interaction_first experiments) ===
        {
            'audit': 'interaction_first',
            'interaction': True,
            'persistence': True,
            'novelty': True,
            'coherence': True,
            'gain': False,  # Never completed — no gain
            'gain_detail': 'Experiments coded but never completed',
            'config': 'I+P+N+C (but no gain)',
        },
    ]
    return audits

def analyze_fertility():
    print("="*70)
    print("RD-10B.R3: FERTILE INTERACTION AUDIT")
    print("="*70)
    
    audits = build_fertility_data()
    
    # Count configurations
    print("\n--- CONFIGURATION COUNTS ---\n")
    
    configs = {}
    for a in audits:
        c = a['config']
        if c not in configs:
            configs[c] = {'total': 0, 'gain': 0, 'no_gain': 0}
        configs[c]['total'] += 1
        if a['gain']:
            configs[c]['gain'] += 1
        else:
            configs[c]['no_gain'] += 1
    
    for c, counts in sorted(configs.items()):
        rate = counts['gain'] / counts['total'] if counts['total'] > 0 else 0
        print(f"{c}: {counts['total']} audits, {counts['gain']} gain, {counts['no_gain']} no gain, rate={rate:.2%}")
    
    # Which combinations predict gain?
    print("\n--- WHICH COMBINATIONS PREDICT GAIN? ---\n")
    
    # Test each component
    components = ['interaction', 'persistence', 'novelty', 'coherence']
    
    for comp in components:
        with_comp = [a for a in audits if a[comp]]
        without_comp = [a for a in audits if not a[comp]]
        
        with_gain = sum(1 for a in with_comp if a['gain'])
        without_gain = sum(1 for a in without_comp if a['gain'])
        
        rate_with = with_gain / len(with_comp) if len(with_comp) > 0 else 0
        rate_without = without_gain / len(without_comp) if len(without_comp) > 0 else 0
        
        print(f"{comp}:")
        print(f"  With: {len(with_comp)} audits, {with_gain} gain, rate={rate_with:.2%}")
        print(f"  Without: {len(without_comp)} audits, {without_gain} gain, rate={rate_without:.2%}")
        print()
    
    # Test combinations
    print("--- COMBINATION ANALYSIS ---\n")
    
    # I+P+N+C
    ipnc = [a for a in audits if a['interaction'] and a['persistence'] and a['novelty'] and a['coherence']]
    ipnc_gain = sum(1 for a in ipnc if a['gain'])
    print(f"I+P+N+C: {len(ipnc)} audits, {ipnc_gain} gain, rate={ipnc_gain/len(ipnc):.2%}" if len(ipnc) > 0 else "I+P+N+C: 0 audits")
    
    # I+P+N (without C)
    ipn = [a for a in audits if a['interaction'] and a['persistence'] and a['novelty'] and not a['coherence']]
    ipn_gain = sum(1 for a in ipn if a['gain'])
    print(f"I+P+N (no C): {len(ipn)} audits, {ipn_gain} gain, rate={ipn_gain/len(ipn):.2%}" if len(ipn) > 0 else "I+P+N (no C): 0 audits")
    
    # I+C (without P or N)
    ic = [a for a in audits if a['interaction'] and a['coherence'] and not a['persistence'] and not a['novelty']]
    ic_gain = sum(1 for a in ic if a['gain'])
    print(f"I+C (no P, no N): {len(ic)} audits, {ic_gain} gain, rate={ic_gain/len(ic):.2%}" if len(ic) > 0 else "I+C (no P, no N): 0 audits")
    
    # I+N+C (without P)
    inc = [a for a in audits if a['interaction'] and a['novelty'] and a['coherence'] and not a['persistence']]
    inc_gain = sum(1 for a in inc if a['gain'])
    print(f"I+N+C (no P): {len(inc)} audits, {inc_gain} gain, rate={inc_gain/len(inc):.2%}" if len(inc) > 0 else "I+N+C (no P): 0 audits")
    
    # The key question
    print("\n--- THE KEY QUESTION ---\n")
    
    print("Does I+P+N+C predict gain better than I+C alone?")
    print()
    
    if len(ipnc) > 0 and len(ic) > 0:
        rate_ipnc = ipnc_gain / len(ipnc)
        rate_ic = ic_gain / len(ic)
        print(f"I+P+N+C rate: {rate_ipnc:.2%}")
        print(f"I+C rate: {rate_ic:.2%}")
        
        if rate_ipnc > rate_ic:
            print("P+N adds value beyond I+C alone.")
        else:
            print("P+N does NOT add value beyond I+C alone.")
    
    # The abandoned experiment
    print("\n--- THE ABANDONED EXPERIMENT ---\n")
    
    print("interaction_first had I+P+N+C but NO GAIN.")
    print("Why?")
    print()
    print("Because the experiments were never completed.")
    print("The code exists. The results don't.")
    print()
    print("This is the crucial counterexample:")
    print("I+P+N+C is necessary but not sufficient.")
    print("You also need to actually run the experiment.")
    print()
    print("Or more precisely:")
    print("You need the interaction to actually occur.")
    print("Not just be possible.")

if __name__ == '__main__':
    analyze_fertility()
