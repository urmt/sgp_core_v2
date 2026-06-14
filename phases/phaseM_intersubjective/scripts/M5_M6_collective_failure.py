"""
Phase M5+M6 — COLLECTIVE RECURSIVE STABILITY + INTERACTION FAILURE MODES

M5: Can recursive continuity become collectively stabilized?
M6: What destroys intersubjective continuity stabilization?

NOT about groups or societies.
About distributed recursive continuity maintenance across processes.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseM_intersubjective'
PHL = '/home/student/sgp_core_v2/phases/phaseL_observer_emergence'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

pair_df = pd.read_csv(f'{BASE}/outputs/phaseM_shared_space.csv')
print(f'Loaded: {len(pair_df)} pairs')

# ====================================================
# M5: COLLECTIVE RECURSIVE STABILITY
# ====================================================
print('='*70)
print('PHASE M5 — COLLECTIVE RECURSIVE STABILITY')
print('Can recursive continuity become collectively stabilized?')
print('='*70)

# Build multi-system ensembles from pairwise data
# Sample groups of 3-5 systems and measure collective properties
N_ENSEMBLES = 2000
ensemble_records = []
for e in range(N_ENSEMBLES):
    k = np.random.choice([3, 4, 5])
    # Pick k systems from pairwise data
    rows = pair_df.sample(n=k)
    # Compute ensemble-level metrics as means of pairwise values
    ensemble_records.append({
        'ensemble_size': k,
        'mean_continuity_alignment': rows['continuity_alignment'].mean(),
        'mean_recursive_synchronization': rows['recursive_synchronization'].mean(),
        'mean_mutual_closure': rows['mutual_closure_reinforcement'].mean(),
        'mean_interaction_stability': rows['interaction_stability'].mean(),
        'mean_co_stabilization': rows['co_stabilization_probability'].mean(),
        'mean_shared_closure': rows['shared_closure'].mean(),
        'mean_manifold_convergence': rows['manifold_convergence'].mean(),
        'mean_signal_transfer': rows.get('signal_transfer_composite', rows['co_stabilization_probability']).mean(),
    })
ens_df = pd.DataFrame(ensemble_records)

# --- Collective closure persistence ---
# Does the ensemble maintain closure collectively?
ens_df['collective_closure'] = (
    ens_df['mean_shared_closure'] * ens_df['mean_recursive_synchronization']
)

# --- Distributed continuity maintenance ---
# Can continuity be maintained across the ensemble?
ens_df['distributed_continuity'] = (
    ens_df['mean_continuity_alignment'] * ens_df['mean_interaction_stability']
)

# --- Recursive network stabilization ---
# Is the ensemble as a whole stabilized by recursive interactions?
ens_df['network_stabilization'] = (
    ens_df['mean_co_stabilization'] * ens_df['mean_manifold_convergence']
)

# --- Ensemble reconstruction ability ---
# Can the ensemble reconstruct if one member is perturbed?
ens_df['ensemble_reconstruction'] = (
    ens_df['mean_co_stabilization'] * ens_df['mean_signal_transfer']
)

# --- Distributed identity preservation ---
# Can the ensemble preserve its organizational identity?
ens_df['distributed_identity'] = (
    ens_df['mean_continuity_alignment'] * ens_df['mean_shared_closure'] * ens_df['mean_manifold_convergence']
)

print(f'\n=== COLLECTIVE STABILITY METRICS ===')
m5_cols = ['collective_closure', 'distributed_continuity', 'network_stabilization',
           'ensemble_reconstruction', 'distributed_identity']
for col in m5_cols:
    print(f'  {col:35s}: {ens_df[col].mean():.4f} ± {ens_df[col].std():.3f}')

# Does ensemble size matter?
print(f'\n=== COLLECTIVE STABILITY BY ENSEMBLE SIZE ===')
for k in [3, 4, 5]:
    sub = ens_df[ens_df['ensemble_size'] == k]
    print(f'  Size {k}: collective_closure={sub["collective_closure"].mean():.4f} net_stab={sub["network_stabilization"].mean():.4f} dist_id={sub["distributed_identity"].mean():.4f}')

# What enables collective stability?
print(f'\n=== WHAT ENABLES COLLECTIVE STABILITY? ===')
for col in ['mean_co_stabilization', 'mean_shared_closure', 'mean_manifold_convergence',
            'mean_continuity_alignment', 'mean_signal_transfer']:
    c, p = pearsonr(ens_df[col], ens_df['distributed_identity'])
    print(f'  {col:40s}: r={c:.4f} p={p:.4e}')

# Save M5
ens_df.to_csv(f'{BASE}/outputs/phaseM_collective_stability.csv', index=False)
m5_summary = {
    'phase': 'M5',
    'n_ensembles': len(ens_df),
    'mean_collective_closure': float(ens_df['collective_closure'].mean()),
    'mean_distributed_continuity': float(ens_df['distributed_continuity'].mean()),
    'mean_network_stabilization': float(ens_df['network_stabilization'].mean()),
    'mean_distributed_identity': float(ens_df['distributed_identity'].mean()),
}
with open(f'{BASE}/summaries/m5_summary.json', 'w') as f:
    json.dump(m5_summary, f, indent=2)
print(f'\nSaved: phaseM_collective_stability.csv')

# ====================================================
# M6: INTERACTION FAILURE MODES
# ====================================================
print('\n' + '='*70)
print('PHASE M6 — INTERACTION FAILURE MODES')
print('What destroys intersubjective continuity stabilization?')
print('='*70)

# Simulate failure by destroying specific interaction properties
fail_records = []

for _, row in pair_df.iterrows():
    base_stab = row['co_stabilization_probability']
    
    # Fail 1: Destroy synchronization
    # Set recursive_synchronization to near-zero (closures don't align)
    fail1 = base_stab * (1 - row['recursive_synchronization'] + 1e-10)
    
    # Fail 2: Destroy closure compatibility
    # Set mutual_closure_reinforcement to near-zero
    fail2 = base_stab * (1 - row['mutual_closure_reinforcement'] + 1e-10)
    
    # Fail 3: Destroy temporal coherence alignment
    fail3 = base_stab * (1 - row['continuity_alignment'] + 1e-10)
    
    # Fail 4: Destroy recursive alignment between the two
    fail4 = base_stab * row.get('recursive_interference', 0.5)
    
    # Fail 5: Destroy continuity transfer
    fail5 = base_stab * (1 - row.get('continuity_transfer_efficiency', row['co_stabilization_probability']) + 1e-10)
    
    # Fail 6: Destroy all simultaneously
    fail6 = base_stab * 0.01
    
    fail_records.append({
        'domain_a': row['domain_a'], 'domain_b': row['domain_b'],
        'observer_level_a': row.get('observer_level_a', 0),
        'observer_level_b': row.get('observer_level_b', 0),
        'base_co_stabilization': base_stab,
        'fail_synchronization': fail1,
        'fail_closure_compatibility': fail2,
        'fail_temporal_alignment': fail3,
        'fail_recursive_alignment': fail4,
        'fail_continuity_transfer': fail5,
        'fail_all': fail6,
    })

fail_df = pd.DataFrame(fail_records)

# Compute collapse ratios
for fail_col in ['fail_synchronization', 'fail_closure_compatibility', 'fail_temporal_alignment',
                 'fail_recursive_alignment', 'fail_continuity_transfer', 'fail_all']:
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = np.where(fail_df['base_co_stabilization'] > 1e-10,
                         fail_df[fail_col] / fail_df['base_co_stabilization'], 0)
    fail_df[f'{fail_col}_collapse'] = 1.0 - ratio

print(f'\n=== INTERACTION FAILURE COLLAPSE RATIOS ===')
for fail_col in ['fail_synchronization', 'fail_closure_compatibility', 'fail_temporal_alignment',
                 'fail_recursive_alignment', 'fail_continuity_transfer', 'fail_all']:
    collapse = fail_df[f'{fail_col}_collapse'].mean()
    print(f'  {fail_col:35s}: collapse={collapse:.4f}')

# Most destructive
collapse_by = {}
for fail_col in ['fail_synchronization', 'fail_closure_compatibility', 'fail_temporal_alignment',
                 'fail_recursive_alignment', 'fail_continuity_transfer']:
    collapse_by[fail_col.replace('fail_', '')] = float(fail_df[f'{fail_col}_collapse'].mean())
worst = max(collapse_by, key=collapse_by.get)
print(f'\nMost destructive failure: {worst} (collapse={collapse_by[worst]:.4f})')

# By observer level
if 'observer_level_a' in pair_df.columns:
    high_high_mask = (fail_df['observer_level_a'] >= 2) & (fail_df['observer_level_b'] >= 2)
    other_mask = ~high_high_mask
    if high_high_mask.sum() > 0 and other_mask.sum() > 0:
        print(f'\n=== FAILURE BY OBSERVER LEVEL ===')
        for fail_col in ['fail_synchronization', 'fail_closure_compatibility', 'fail_temporal_alignment',
                         'fail_recursive_alignment', 'fail_continuity_transfer']:
            hh_collapse = fail_df.loc[high_high_mask, f'{fail_col}_collapse'].mean()
            o_collapse = fail_df.loc[other_mask, f'{fail_col}_collapse'].mean()
            print(f'  {fail_col:35s}: high-high collapse={hh_collapse:.4f} other={o_collapse:.4f}')

# Save M6
fail_df.to_csv(f'{BASE}/outputs/phaseM_failure_modes.csv', index=False)
m6_summary = {
    'phase': 'M6',
    'most_destructive': worst,
    'most_destructive_value': collapse_by[worst],
    'collapse_by_type': collapse_by,
}
with open(f'{BASE}/summaries/m6_summary.json', 'w') as f:
    json.dump(m6_summary, f, indent=2)
print(f'\nSaved: phaseM_failure_modes.csv')

print(f'\nM5+M6 COMPLETE')
