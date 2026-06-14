"""
RD-10B.M3: Comparative Structure Audit

QUESTION:
> Does explanatory power scale with comparison or with translation?

DESIGN:
For every audit from RD-5 onward, record:
- Number of descriptions available
- Whether comparison is present
- Whether translation is present
- Explanatory gain

Test three hypotheses:
H1: Explanation scales with translation
H2: Explanation scales with comparison
H3: Translation only becomes possible after explanatory gains from comparison
"""

import json

# ============================================================
# AUDIT DATA
# ============================================================

def build_audit_data():
    """
    For every audit, record descriptions, comparison, translation, gain.
    """
    audits = [
        {
            'audit': 'RD-5',
            'descriptions': ['C', 'MSE', 'factors'],
            'n_descriptions': 3,
            'comparison_present': True,
            'comparison_type': 'metric comparison',
            'translation_present': False,
            'translation_type': None,
            'explanatory_gain': 'C is projection of MSE',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-9E',
            'descriptions': ['SP', 'discretization'],
            'n_descriptions': 2,
            'comparison_present': True,
            'comparison_type': 'method vs artifact',
            'translation_present': False,
            'translation_type': None,
            'explanatory_gain': 'SP is binary artifact',
            'gain_magnitude': 'medium',
        },
        {
            'audit': 'RD-10B.3',
            'descriptions': ['world', 'detector', 'motif'],
            'n_descriptions': 3,
            'comparison_present': True,
            'comparison_type': 'detector variants',
            'translation_present': False,
            'translation_type': None,
            'explanatory_gain': 'Detectors measure time-series, not architecture',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.0',
            'descriptions': ['graph', 'timeseries', 'state-transition', 'correlation', 'phasespace'],
            'n_descriptions': 5,
            'comparison_present': True,
            'comparison_type': 'representation comparison',
            'translation_present': True,
            'translation_type': 'cross-representation mapping',
            'explanatory_gain': 'Motifs are world-representation pairs',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.0A',
            'descriptions': ['rep1', 'rep2', 'rep3', 'rep4', 'rep5'],
            'n_descriptions': 5,
            'comparison_present': True,
            'comparison_type': 'correspondence analysis',
            'translation_present': True,
            'translation_type': 'representation correspondence',
            'explanatory_gain': 'Correspondence varies widely',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.0B',
            'descriptions': ['predictive', 'intervention', 'counterfactual', 'information', 'causal'],
            'n_descriptions': 5,
            'comparison_present': True,
            'comparison_type': 'identity criteria comparison',
            'translation_present': False,
            'translation_type': None,
            'explanatory_gain': 'Criteria disagree on "same world"',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.0C',
            'descriptions': ['criteria', 'tasks', 'purposes'],
            'n_descriptions': 3,
            'comparison_present': True,
            'comparison_type': 'criteria vs tasks',
            'translation_present': True,
            'translation_type': 'criteria-task mapping',
            'explanatory_gain': 'Criteria are task-specific tools',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.0D',
            'descriptions': ['causal', 'other criteria'],
            'n_descriptions': 2,
            'comparison_present': True,
            'comparison_type': 'criterion stress test',
            'translation_present': False,
            'translation_type': None,
            'explanatory_gain': 'Causal fails 60% of time',
            'gain_magnitude': 'medium',
        },
        {
            'audit': 'RD-10B.0E',
            'descriptions': ['stress worlds'],
            'n_descriptions': 5,
            'comparison_present': True,
            'comparison_type': 'world comparison',
            'translation_present': False,
            'translation_type': None,
            'explanatory_gain': 'Each criterion has domain',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.0F',
            'descriptions': ['world types'],
            'n_descriptions': 5,
            'comparison_present': True,
            'comparison_type': 'world comparison',
            'translation_present': False,
            'translation_type': None,
            'explanatory_gain': 'Worlds have hidden assumptions',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.X',
            'descriptions': ['bottom-up', 'top-down'],
            'n_descriptions': 2,
            'comparison_present': True,
            'comparison_type': 'chain comparison',
            'translation_present': True,
            'translation_type': 'cross-chain mapping',
            'explanatory_gain': 'Recursion is junction candidate',
            'gain_magnitude': 'medium',
        },
        {
            'audit': 'RD-10B.J2',
            'descriptions': ['11 ladders'],
            'n_descriptions': 11,
            'comparison_present': True,
            'comparison_type': 'path comparison',
            'translation_present': False,
            'translation_type': None,
            'explanatory_gain': 'Path independence confirmed',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.J3',
            'descriptions': ['5 vocabularies'],
            'n_descriptions': 5,
            'comparison_present': True,
            'comparison_type': 'vocabulary comparison',
            'translation_present': True,
            'translation_type': 'cross-vocabulary mapping',
            'explanatory_gain': 'Vocabulary independence confirmed',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.J4',
            'descriptions': ['junctions'],
            'n_descriptions': 4,
            'comparison_present': True,
            'comparison_type': 'dependency analysis',
            'translation_present': False,
            'translation_type': None,
            'explanatory_gain': 'Junctions are dependent',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.J6',
            'descriptions': ['decompositions'],
            'n_descriptions': 4,
            'comparison_present': True,
            'comparison_type': 'decomposition comparison',
            'translation_present': True,
            'translation_type': 'cross-decomposition mapping',
            'explanatory_gain': 'Compression is decomposition-dependent',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.J7',
            'descriptions': ['decompositions'],
            'n_descriptions': 4,
            'comparison_present': True,
            'comparison_type': 'isomorphism analysis',
            'translation_present': True,
            'translation_type': 'cross-decomposition translation',
            'explanatory_gain': 'Isomorphism class identified',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.J8',
            'descriptions': ['decompositions'],
            'n_descriptions': 2,
            'comparison_present': True,
            'comparison_type': 'translation analysis',
            'translation_present': True,
            'translation_type': 'explicit translation maps',
            'explanatory_gain': 'Translation invariants identified',
            'gain_magnitude': 'high',
        },
        {
            'audit': 'RD-10B.M1',
            'descriptions': ['migration pattern'],
            'n_descriptions': 1,
            'comparison_present': False,
            'comparison_type': None,
            'translation_present': False,
            'translation_type': None,
            'explanatory_gain': 'Migration is methodological',
            'gain_magnitude': 'medium',
        },
        {
            'audit': 'RD-10B.M2',
            'descriptions': ['migration graph'],
            'n_descriptions': 1,
            'comparison_present': False,
            'comparison_type': None,
            'translation_present': False,
            'translation_type': None,
            'explanatory_gain': 'Progression is oscillation',
            'gain_magnitude': 'high',
        },
    ]
    
    return audits

def analyze_comparative():
    print("="*70)
    print("RD-10B.M3: COMPARATIVE STRUCTURE AUDIT")
    print("="*70)
    
    audits = build_audit_data()
    
    print("\n--- AUDIT TABLE ---\n")
    print(f"{'Audit':<12} {'#Desc':<7} {'Compare':<10} {'Translate':<11} {'Gain':<8}")
    print("-" * 55)
    
    for a in audits:
        compare = "YES" if a['comparison_present'] else "NO"
        translate = "YES" if a['translation_present'] else "NO"
        print(f"{a['audit']:<12} {a['n_descriptions']:<7} {compare:<10} {translate:<11} {a['gain_magnitude']:<8}")
    
    # Test H1: Explanation scales with translation
    print("\n--- H1: EXPLANATION SCALES WITH TRANSLATION ---\n")
    
    with_translation = [a for a in audits if a['translation_present']]
    without_translation = [a for a in audits if not a['translation_present']]
    
    high_gain_with = sum(1 for a in with_translation if a['gain_magnitude'] == 'high')
    high_gain_without = sum(1 for a in without_translation if a['gain_magnitude'] == 'high')
    
    print(f"With translation: {len(with_translation)} audits, {high_gain_with} high gain")
    print(f"Without translation: {len(without_translation)} audits, {high_gain_without} high gain")
    
    if len(with_translation) > 0:
        rate_with = high_gain_with / len(with_translation)
    else:
        rate_with = 0
    if len(without_translation) > 0:
        rate_without = high_gain_without / len(without_translation)
    else:
        rate_without = 0
    
    print(f"High gain rate with translation: {rate_with:.2%}")
    print(f"High gain rate without translation: {rate_without:.2%}")
    
    # Test H2: Explanation scales with comparison
    print("\n--- H2: EXPLANATION SCALES WITH COMPARISON ---\n")
    
    with_comparison = [a for a in audits if a['comparison_present']]
    without_comparison = [a for a in audits if not a['comparison_present']]
    
    high_gain_with_c = sum(1 for a in with_comparison if a['gain_magnitude'] == 'high')
    high_gain_without_c = sum(1 for a in without_comparison if a['gain_magnitude'] == 'high')
    
    print(f"With comparison: {len(with_comparison)} audits, {high_gain_with_c} high gain")
    print(f"Without comparison: {len(without_comparison)} audits, {high_gain_without_c} high gain")
    
    if len(with_comparison) > 0:
        rate_with_c = high_gain_with_c / len(with_comparison)
    else:
        rate_with_c = 0
    if len(without_comparison) > 0:
        rate_without_c = high_gain_without_c / len(without_comparison)
    else:
        rate_without_c = 0
    
    print(f"High gain rate with comparison: {rate_with_c:.2%}")
    print(f"High gain rate without comparison: {rate_without_c:.2%}")
    
    # Test H3: Translation only after comparison gains
    print("\n--- H3: TRANSLATION ONLY AFTER COMPARISON GAINS ---\n")
    
    # Check order: do comparison gains precede translation?
    comparison_first = 0
    translation_first = 0
    
    for i, a in enumerate(audits):
        if a['translation_present']:
            # Check if any earlier audit had comparison but no translation
            earlier_comparison = any(
                audits[j]['comparison_present'] and not audits[j]['translation_present']
                for j in range(i)
            )
            if earlier_comparison:
                comparison_first += 1
            else:
                translation_first += 1
    
    print(f"Translation after comparison: {comparison_first}")
    print(f"Translation without prior comparison: {translation_first}")
    
    # Verdict
    print("\n--- VERDICT ---\n")
    
    print("H1 (Explanation scales with translation):")
    print(f"  Rate with translation: {rate_with:.2%}")
    print(f"  Rate without translation: {rate_without:.2%}")
    if rate_with > rate_without:
        print("  SUPPORTED")
    else:
        print("  NOT SUPPORTED")
    
    print()
    print("H2 (Explanation scales with comparison):")
    print(f"  Rate with comparison: {rate_with_c:.2%}")
    print(f"  Rate without comparison: {rate_without_c:.2%}")
    if rate_with_c > rate_without_c:
        print("  SUPPORTED")
    else:
        print("  NOT SUPPORTED")
    
    print()
    print("H3 (Translation after comparison gains):")
    if comparison_first > translation_first:
        print(f"  SUPPORTED ({comparison_first} vs {translation_first})")
    else:
        print(f"  NOT SUPPORTED ({comparison_first} vs {translation_first})")
    
    print()
    print("STRONGEST CONCLUSION:")
    if rate_with_c > rate_with:
        print("  Comparison is more strongly associated with explanation than translation.")
        print("  Translation may be a downstream effect of comparison.")
    else:
        print("  Translation is more strongly associated with explanation than comparison.")
    
    return {
        'audits': audits,
        'h1': {'rate_with': rate_with, 'rate_without': rate_without},
        'h2': {'rate_with': rate_with_c, 'rate_without': rate_without_c},
        'h3': {'comparison_first': comparison_first, 'translation_first': translation_first},
    }

if __name__ == '__main__':
    result = analyze_comparative()
    
    with open('/home/student/sgp_core_v2/audits/rd10bm3_results.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print("\nSaved to audits/rd10bm3_results.json")
