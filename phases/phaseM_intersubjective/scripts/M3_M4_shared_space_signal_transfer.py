"""
Phase M3+M4 — SHARED ORGANIZATIONAL SPACE + SIGNAL TRANSFER

M3: Do interacting recursive continuities form shared organizational structure?
M4: Can recursive continuity influence another through stable organizational transfer?

NOT about communication in the human sense.
About continuity-preserving organizational transfer between recursive processes.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseM_intersubjective'
PHL = '/home/student/sgp_core_v2/phases/phaseL_observer_emergence'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

pair_df = pd.read_csv(f'{BASE}/outputs/phaseM_pairwise_interactions.csv')
print(f'Loaded: {len(pair_df)} pairwise interactions')

# ====================================================
# M3: SHARED ORGANIZATIONAL SPACE
# ====================================================
print('='*70)
print('PHASE M3 — SHARED ORGANIZATIONAL SPACE')
print('Do interacting recursive continuities form shared structure?')
print('='*70)

# Shared closure structures
# When two systems have aligned closure, they form a shared closure manifold
pair_df['shared_closure'] = pair_df['recursive_synchronization'] * pair_df['mutual_closure_reinforcement']

# Continuity overlap = the intersection of their continuity maintenance regions
pair_df['continuity_overlap'] = pair_df['continuity_alignment'] * pair_df['interaction_stability']

# Recursive manifold convergence
# If both systems' recursive structures align, they converge
pair_df['manifold_convergence'] = pair_df['recursive_predictive_coupling'] * pair_df['co_stabilization_probability']

# Synchronization geometry = how their synchronization is structured
pair_df['synchronization_geometry'] = (
    pair_df['recursive_synchronization'] * pair_df['interaction_stability'] * 
    (1 - abs(pair_df['mutual_anticipation'] - pair_df['co_adaptive_continuity']))
)

# Co-generated transitions = do their transitions align?
pair_df['co_generated_transitions'] = (
    pair_df['co_stabilization_probability'] * pair_df['mutual_modeling_composite']
) if 'mutual_modeling_composite' in pair_df.columns else pair_df['co_stabilization_probability']

print(f'\n=== SHARED ORGANIZATIONAL SPACE ===')
for col in ['shared_closure', 'continuity_overlap', 'manifold_convergence',
            'synchronization_geometry', 'co_generated_transitions']:
    print(f'  {col:30s}: {pair_df[col].mean():.4f} ± {pair_df[col].std():.3f}')

# Shared space composite
m3_cols = ['shared_closure', 'continuity_overlap', 'manifold_convergence',
           'synchronization_geometry', 'co_generated_transitions']
for col in m3_cols:
    if col in pair_df.columns:
        cmin, cmax = pair_df[col].min(), pair_df[col].max()
        pair_df[f'{col}_norm'] = (pair_df[col] - cmin) / (cmax - cmin + 1e-10)
pair_df['shared_space_composite'] = pair_df[[f'{c}_norm' for c in m3_cols if f'{c}_norm' in pair_df.columns]].mean(axis=1)
print(f'\n  Shared space composite: {pair_df["shared_space_composite"].mean():.4f}')

# By observer level
if 'observer_level_a' in pair_df.columns and 'observer_level_b' in pair_df.columns:
    high_high = pair_df[(pair_df['observer_level_a'] >= 2) & (pair_df['observer_level_b'] >= 2)]
    low_low = pair_df[(pair_df['observer_level_a'] < 2) & (pair_df['observer_level_b'] < 2)]
    if len(high_high) > 0 and len(low_low) > 0:
        print(f'\n  High-high shared space: {high_high["shared_space_composite"].mean():.4f}')
        print(f'  Low-low shared space:   {low_low["shared_space_composite"].mean():.4f}')

# What enables shared space?
print(f'\n=== WHAT ENABLES SHARED ORGANIZATIONAL SPACE? ===')
for col in ['continuity_alignment', 'recursive_synchronization', 'interaction_stability',
            'mutual_closure_reinforcement', 'co_stabilization_probability']:
    if col in pair_df.columns:
        c, p = pearsonr(pair_df[col], pair_df['shared_space_composite'])
        print(f'  {col:35s}: r={c:.4f} p={p:.4e}')

# Save M3
pair_df.to_csv(f'{BASE}/outputs/phaseM_shared_space.csv', index=False)
m3_summary = {
    'phase': 'M3',
    'n_pairs': len(pair_df),
    'mean_shared_closure': float(pair_df['shared_closure'].mean()),
    'mean_continuity_overlap': float(pair_df['continuity_overlap'].mean()),
    'mean_manifold_convergence': float(pair_df['manifold_convergence'].mean()),
    'mean_shared_space_composite': float(pair_df['shared_space_composite'].mean()),
    'high_high_shared': float(high_high['shared_space_composite'].mean()) if len(high_high) > 0 else 0,
    'low_low_shared': float(low_low['shared_space_composite'].mean()) if len(low_low) > 0 else 0,
}
with open(f'{BASE}/summaries/m3_summary.json', 'w') as f:
    json.dump(m3_summary, f, indent=2)
print(f'\nSaved: phaseM_shared_space.csv')

# ====================================================
# M4: SIGNAL TRANSFER
# ====================================================
print('\n' + '='*70)
print('PHASE M4 — SIGNAL TRANSFER')
print('Can recursive continuity influence another through stable transfer?')
print('='*70)

# Perturbation-response encoding
# If one system's perturbation pattern is encoded in the other's response
# Simulated as: alignment × mutual closure
pair_df['perturbation_response_encoding'] = pair_df['continuity_alignment'] * pair_df['mutual_closure_reinforcement']

# Continuity transfer efficiency
# How efficiently does continuity maintenance transfer between systems?
pair_df['continuity_transfer_efficiency'] = (
    pair_df['external_continuity_prediction'] * pair_df['reciprocal_reconstruction']
)

# Recursive signaling persistence
# Does the signal (closure pattern) persist across the interaction?
pair_df['signaling_persistence'] = (
    pair_df['mutual_closure_reinforcement'] * pair_df['co_stabilization_probability']
)

# Alignment transmission
# Can alignment be transmitted between systems?
pair_df['alignment_transmission'] = (
    pair_df['continuity_alignment'] * pair_df['recursive_predictive_coupling']
)

# Closure-mediated information retention
# Does the shared closure structure retain information?
pair_df['closure_information_retention'] = (
    pair_df['shared_closure'] * pair_df['co_adaptive_continuity']
)

print(f'\n=== SIGNAL TRANSFER METRICS ===')
m4_cols = ['perturbation_response_encoding', 'continuity_transfer_efficiency',
           'signaling_persistence', 'alignment_transmission', 'closure_information_retention']
for col in m4_cols:
    print(f'  {col:35s}: {pair_df[col].mean():.4f} ± {pair_df[col].std():.3f}')

# Composite signal transfer
for col in m4_cols:
    cmin, cmax = pair_df[col].min(), pair_df[col].max()
    pair_df[f'{col}_norm'] = (pair_df[col] - cmin) / (cmax - cmin + 1e-10)
pair_df['signal_transfer_composite'] = pair_df[[f'{c}_norm' for c in m4_cols]].mean(axis=1)
print(f'\n  Signal transfer composite: {pair_df["signal_transfer_composite"].mean():.4f}')

# By domain compatibility
same_domain = pair_df[pair_df['domain_a'] == pair_df['domain_b']]
cross_domain = pair_df[pair_df['domain_a'] != pair_df['domain_b']]
print(f'\n  Same-domain signal transfer: {same_domain["signal_transfer_composite"].mean():.4f}')
print(f'  Cross-domain signal transfer: {cross_domain["signal_transfer_composite"].mean():.4f}')

# What enables signal transfer?
print(f'\n=== WHAT ENABLES SIGNAL TRANSFER? ===')
for col in ['continuity_alignment', 'recursive_synchronization', 'interaction_stability',
            'shared_closure', 'manifold_convergence']:
    if col in pair_df.columns:
        c, p = pearsonr(pair_df[col], pair_df['signal_transfer_composite'])
        print(f'  {col:35s}: r={c:.4f} p={p:.4e}')

# Save M4
pair_df.to_csv(f'{BASE}/outputs/phaseM_signal_transfer.csv', index=False)
m4_summary = {
    'phase': 'M4',
    'mean_perturbation_encoding': float(pair_df['perturbation_response_encoding'].mean()),
    'mean_continuity_transfer': float(pair_df['continuity_transfer_efficiency'].mean()),
    'mean_signal_transfer_composite': float(pair_df['signal_transfer_composite'].mean()),
    'same_domain_transfer': float(same_domain['signal_transfer_composite'].mean()),
    'cross_domain_transfer': float(cross_domain['signal_transfer_composite'].mean()),
}
with open(f'{BASE}/summaries/m4_summary.json', 'w') as f:
    json.dump(m4_summary, f, indent=2)
print(f'\nSaved: phaseM_signal_transfer.csv')

print(f'\nM3+M4 COMPLETE')
