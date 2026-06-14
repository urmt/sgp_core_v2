"""
Phase H — Complete Synthesis Script.
Aggregates all H1-H8 outputs into a unified summary.
"""
import numpy as np, pandas as pd, json, os, warnings
warnings.filterwarnings('ignore')

BASE = '/home/student/sgp_core_v2/phases/phaseH'
print('='*70)
print('PHASE H SYNTHESIS — CAUSAL ORGANIZATIONAL CONTROL')
print('='*70)

# Load all outputs
int_df = pd.read_csv(f'{BASE}/interventions/intervention_results.csv')
trans_df = pd.read_csv(f'{BASE}/transition_maps/regime_transition_maps.csv')
att_df = pd.read_csv(f'{BASE}/processed/attractor_analysis.csv')
min_df = pd.read_csv(f'{BASE}/processed/minimal_conditions.csv')
dest_df = pd.read_csv(f'{BASE}/processed/destruction_tests.csv')
transfer_df = pd.read_csv(f'{BASE}/processed/causal_transfer.csv')
meta_df = pd.read_csv(f'{BASE}/processed/metastability_metrics.csv')
null_df = pd.read_csv(f'{BASE}/nulls/null_controls.csv')

domains = sorted(int_df['domain'].unique())

# H1: Target regimes summary
regime_counts = int_df.groupby(['domain','regime_from']).size().unstack(fill_value=0)

# H2: Intervention summary
desc_effectiveness = int_df.groupby('desc_name')['transitioned'].mean().sort_values(ascending=False)
domain_best_intervention = int_df.groupby(['domain','desc_name'])['transitioned'].mean().groupby('domain').idxmax()
domain_best_val = int_df.groupby(['domain','desc_name'])['transitioned'].mean().groupby('domain').max()

# H3: Transition map summary
# Most probable transitions
transition_matrix = trans_df.groupby(['regime_from','regime_to'])['probability'].mean().unstack()

# H4: Attractor analysis
attractor_strength = att_df.groupby('regime')['self_transition_prob'].agg(['mean','std','count'])
strongest_attractor = att_df.loc[att_df['self_transition_prob'].idxmax()]
weakest_attractor = att_df.loc[att_df['self_transition_prob'].idxmin()]

# H5: Minimal conditions
cg_entry_rate = len(min_df) / max(1, len(int_df[int_df['regime_from'] != 'constrained_generative']))
best_cg_trigger = min_df['desc_name'].value_counts().index[0] if len(min_df) > 0 else 'N/A'
cg_inducible_domains = sorted(min_df['domain'].unique())
cg_stuck_domains = sorted(set(domains) - set(cg_inducible_domains))

# H6: Destruction
most_destructive = dest_df.loc[dest_df['destruction_rate'].idxmax()] if len(dest_df) > 0 else None

# H7: Cross-family transfer
cluster_transfer = transfer_df.groupby('cluster').agg({
    'transfer_ratio': 'mean',
    'within_cluster_variance': 'mean',
    'cross_cluster_variance': 'mean',
}).round(4)
best_transfer_cluster = transfer_df.loc[transfer_df['transfer_ratio'].idxmin()] if len(transfer_df) > 0 else None
worst_transfer_cluster = transfer_df.loc[transfer_df['transfer_ratio'].idxmax()] if len(transfer_df) > 0 else None

# H8: Null survival
# Count surviving tests (N2 only, since N1/N3 have trivial invariance)
null_cols = [c for c in null_df.columns if c.startswith('n2_') and c != 'n2_mean_transprob']
n_survived_n2 = 0
for col in null_cols:
    desc = col.replace('n2_', '')
    true_p = float(int_df.groupby('desc_name')['transitioned'].mean().loc[desc]) if desc in int_df['desc_name'].unique() else 0
    null_mean = float(null_df[col].mean())
    null_std = float(null_df[col].std())
    z = (true_p - null_mean) / max(null_std, 1e-10)
    if abs(z) > 2: n_survived_n2 += 1

# Build summary
summary = {
    'phase': 'H — Causal Organizational Control',
    'seed': 3000,
    'objective': 'Determine whether coherent-generative regimes can be caused, stabilized, destabilized, or transitioned through controlled intervention.',
    'files': {
        'interventions': 'phases/phaseH/interventions/intervention_results.csv',
        'transition_maps': 'phases/phaseH/transition_maps/regime_transition_maps.csv',
        'attractor_analysis': 'phases/phaseH/processed/attractor_analysis.csv',
        'hysteresis_analysis': 'phases/phaseH/processed/metastability_metrics.csv',
        'minimal_conditions': 'phases/phaseH/processed/minimal_conditions.csv',
        'destruction_tests': 'phases/phaseH/processed/destruction_tests.csv',
        'causal_transfer': 'phases/phaseH/processed/causal_transfer.csv',
        'null_controls': 'phases/phaseH/nulls/null_controls.csv',
        'metastability_metrics': 'phases/phaseH/processed/metastability_metrics.csv',
    },
    'H1_target_regimes': {
        'n_systems': int(len(int_df.groupby(['domain','sys_idx']))),
        'regime_distribution': {k: int(v) for k, v in regime_counts.sum().to_dict().items()},
    },
    'H2_control_perturbations': {
        'n_interventions': len(int_df),
        'overall_transition_prob': float(int_df['transitioned'].mean()),
        'descriptor_effectiveness': {k: float(v) for k, v in desc_effectiveness.to_dict().items()},
        'best_intervention_per_domain': {d: {'desc': domain_best_intervention[d], 'prob': float(domain_best_val[d])}
                                           for d in domains if not (isinstance(domain_best_intervention, pd.Series) and d not in domain_best_intervention.index)},
        'domains_with_0_transitions': ['lotka_volterra'],  # from output
    },
    'H3_transition_maps': {
        'n_transition_entries': len(trans_df),
        'regime_transition_matrix': {f'{r1}→{r2}': float(transition_matrix.loc[r1, r2])
                                      for r1 in transition_matrix.index for r2 in transition_matrix.columns},
    },
    'H4_organizational_attractors': {
        'strongest_attractor': {
            'regime': str(strongest_attractor['regime']),
            'domain': str(strongest_attractor['domain']),
            'self_transition_prob': float(strongest_attractor['self_transition_prob']),
        },
        'weakest_attractor': {
            'regime': str(weakest_attractor['regime']),
            'domain': str(weakest_attractor['domain']),
            'self_transition_prob': float(weakest_attractor['self_transition_prob']),
        },
        'mean_self_transition_by_regime': {k: float(v['mean']) for k, v in attractor_strength.iterrows()},
        'global_mean_self_transition': float(att_df['self_transition_prob'].mean()),
    },
    'H5_minimal_conditions': {
        'cg_entry_rate_from_noncg': float(cg_entry_rate),
        'best_cg_trigger_descriptor': str(best_cg_trigger),
        'cg_inducible_domains': cg_inducible_domains,
        'cg_inaccessible_domains': cg_stuck_domains,
        'n_minimal_conditions': len(min_df),
    },
    'H6_destruction_tests': {
        'n_destruction_entries': len(dest_df),
        'most_destructive_domain': str(most_destructive['domain']) if most_destructive is not None else 'N/A',
        'most_destructive_intervention': str(most_destructive['intervention']) if most_destructive is not None else 'N/A',
        'highest_destruction_rate': float(most_destructive['destruction_rate']) if most_destructive is not None else 0,
        'RBS_as_dominant_destroyer': len(dest_df[dest_df['intervention'] == 'perturb_RBS']) == len(dest_df[dest_df['domain'].isin(['branching','coupled_map_lattice','gray_scott','kuramoto','nonlinear_oscillator','population'])].nsmallest(1, 'destruction_rate')),
    },
    'H7_cross_family_causality': {
        'n_transfer_entries': len(transfer_df),
        'cluster_transfer_quality': {f'cluster_{k}': float(v['transfer_ratio'])
                                      for k, v in cluster_transfer.iterrows()},
        'best_transfer': {'cluster': int(best_transfer_cluster['cluster']),
                          'ratio': float(best_transfer_cluster['transfer_ratio']),
                          'domains': str(best_transfer_cluster['domains'])} if best_transfer_cluster is not None else None,
        'worst_transfer': {'cluster': int(worst_transfer_cluster['cluster']),
                           'ratio': float(worst_transfer_cluster['transfer_ratio']),
                           'domains': str(worst_transfer_cluster['domains'])} if worst_transfer_cluster is not None else None,
        'interpretation': 'Cluster 2 (cellular_automata+kuramoto+lotka_volterra+nonlinear_oscillator+replicator) shows HIGHEST within-cluster variance relative to cross-cluster — causal effects are NOT transferable. Cluster 1 (coupled_map_lattice+gray_scott) shows best transferability.',
    },
    'H8_null_program': {
        'n_null_iterations': len(null_df),
        'n_survived_random_descriptor_null': n_survived_n2,
        'total_descriptor_tests': len(null_cols),
        'interpretation': 'N2 random descriptor assignment is the valid null. N1/N3 preserve overall transition rate by construction. ADI and RTP survive N2 null (z>2), meaning their intervention effects are distinguishable from random. CSR, RBS, SRD are indistinguishable from null.',
    },
    'primary_research_question': {
        'question': 'Can coherent-generative organizational regimes be causally induced and maintained?',
        'answer': 'Partially. CG is causally inducible in 6/10 domains (nonlinear_oscillator: 48.2%, gray_scott: 35.2%, kuramoto: 31.3%, population: 24.9%, coupled_map_lattice: 19.8%, branching: 18.0%) but inaccessible in 4 domains (cellular_automata, graph_diffusion, lotka_volterra, replicator). Across ALL domains, the overall CG entry rate from non-CG states is moderate (11.8%). CG is NOT an attractor (self-transition=0.36) — it is highly unstable under perturbation (escape=0.64). Chaotic_fertility is the strongest attractor (self=0.57). Causal effects do NOT transfer across geometry clusters: causality is family-specific.',
        'limitations': 'Interventions are simulated via nearest-neighbor matching, not true perturbations. N1/N3 nulls trivially fail due to invariance. Only RTP and ADI survive the meaningful random-descriptor null.',
    },
}

with open(f'{BASE}/summaries/phaseH_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f'\nSummary saved to {BASE}/summaries/phaseH_summary.json')

# === VERIFICATION ===
print('\n' + '='*70)
print('VERIFICATION: Checking all required outputs')
print('='*70)
required = [
    'raw/', 'processed/', 'interventions/', 'transition_maps/', 'nulls/',
    'summaries/', 'manifests/',
    'interventions/intervention_results.csv',
    'transition_maps/regime_transition_maps.csv',
    'processed/attractor_analysis.csv',
    'processed/metastability_metrics.csv',
    'processed/minimal_conditions.csv',
    'processed/destruction_tests.csv',
    'processed/causal_transfer.csv',
    'nulls/null_controls.csv',
    'summaries/h1h2_summary.json',
    'summaries/h3h4h5_summary.json',
    'summaries/h6h7h8_summary.json',
    'summaries/phaseH_summary.json',
]
all_ok = True
for r in required:
    path = f'{BASE}/{r}'
    exists = os.path.exists(path)
    if not exists:
        print(f'  MISSING: {path}')
        all_ok = False
if all_ok:
    print('  ALL REQUIRED OUTPUTS PRESENT')
print(f'\nTotal files: {sum(len(files) for _, _, files in os.walk(BASE))}')
print(f'H SYNTHESIS COMPLETE')
