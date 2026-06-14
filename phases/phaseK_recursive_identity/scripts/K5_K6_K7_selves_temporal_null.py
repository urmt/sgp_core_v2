"""
Phase K5+K6+K7 — Selves Classification + Temporal Identity + Null Program.

K5: Classify CG systems into self-types based on identity profiles.
K6: How identity changes across temporal iterations.
K7: Baseline identity of null/noise systems.

Anti-drift: Not all CG systems are "selves" — some are rocks, some are minds.
"""
import numpy as np, pandas as pd, os, json, warnings
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseK_recursive_identity'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

id_metrics = pd.read_csv(f'{BASE}/outputs/phaseK_identity_metrics.csv')
cg_metrics = id_metrics[id_metrics['process_regime'] == 'CG'].copy()

print('='*70)
print('PHASE K5 — PROCESS SELVES CLASSIFICATION')
print('Classifying CG systems into self-types based on identity profiles')
print('='*70)

# ====================================================
# K5: SELVES CLASSIFICATION
# ====================================================
# Three axes of self: 
#   - identity: recursive_identity_score
#   - continuity: recursive_continuity
#   - memory: org_memory

# Score dimensions: identity + continuity + memory + reconstruction
id_cols = ['recursive_identity_score', 'recursive_continuity', 'org_memory', 
           'reconstruction_ability', 'trajectory_coherence', 'closure_persistence']

# Compute composite self-ness
for col in id_cols:
    cg_metrics[f'z_{col}'] = (cg_metrics[col] - cg_metrics[col].mean()) / cg_metrics[col].std()

cg_metrics['self_composite'] = cg_metrics[[f'z_{c}' for c in id_cols]].mean(axis=1)

# Quantile-based classification
q33 = cg_metrics['self_composite'].quantile(0.33)
q66 = cg_metrics['self_composite'].quantile(0.66)

cg_metrics['self_type'] = 'intermediate'
cg_metrics.loc[cg_metrics['self_composite'] > q66, 'self_type'] = 'strong_self'
cg_metrics.loc[cg_metrics['self_composite'] < q33, 'self_type'] = 'weak_self'

type_counts = cg_metrics['self_type'].value_counts()
print(f'\nSelf type distribution:')
for t, c in type_counts.items():
    print(f'  {t}: {c} ({100*c/len(cg_metrics):.1f}%)')

# Profile by self-type
print(f'\nIdentity profile by self-type:')
for t in ['strong_self', 'intermediate', 'weak_self']:
    sub = cg_metrics[cg_metrics['self_type'] == t]
    print(f'\n  {t} ({len(sub)} systems):')
    for col in id_cols:
        print(f'    {col:30s}: {sub[col].mean():.4f} ± {sub[col].std():.3f}')

# Strong self by domain
print(f'\nStrong selves by domain:')
strong = cg_metrics[cg_metrics['self_type'] == 'strong_self']
for d in sorted(strong['domain'].unique()):
    n = len(strong[strong['domain'] == d])
    total = len(cg_metrics[cg_metrics['domain'] == d])
    print(f'  {d:25s}: {n:3d}/{total:<3d} ({100*n/total:.0f}%)')

cg_metrics.to_csv(f'{BASE}/outputs/phaseK_self_types.csv', index=False)

# ====================================================
# K6: TEMPORAL IDENTITY — identity over iterations
# ====================================================
print('\n' + '='*70)
print('PHASE K6 — TEMPORAL IDENTITY')
print('How does identity change over time?')
print('='*70)

# Build synthetic temporal identity as a function of iteration
# Based on K2 retention rates: identity decays under transformation
T = 100
temporal_records = []

for _, row in id_metrics.iterrows():
    base_score = row['recursive_identity_score']
    continuity = row['recursive_continuity']
    # Decay model: identity decays exponentially with continuity as damping
    for t in range(T):
        decay = np.exp(-0.02 * t * (1 - continuity))
        noise = np.random.normal(0, 0.02 * decay)
        temporal_records.append({
            'domain': row['domain'], 'sys_idx': row['sys_idx'],
            'process_regime': row['process_regime'],
            'iteration': t, 'identity': base_score * decay + noise,
            'continuity': continuity * decay,
        })

temporal_df = pd.DataFrame(temporal_records)

# Identity stability over time
print(f'\nIdentity decay patterns:')
for t_check in [0, 10, 25, 50, 99]:
    sub = temporal_df[temporal_df['iteration'] == t_check]
    print(f'  Iteration {t_check:3d}: mean identity={sub["identity"].mean():.4f} ± {sub["identity"].std():.3f}')

# Identity half-life: when identity drops below 0.5 of initial
half_life_records = []
for (domain, idx), grp in temporal_df.groupby(['domain', 'sys_idx']):
    initial = grp[grp['iteration'] == 0]['identity'].values[0]
    half_val = initial * 0.5
    half_it = grp[grp['identity'] < half_val]['iteration'].min()
    half_life = half_it if not np.isnan(half_it) else T
    half_life_records.append({'domain': domain, 'sys_idx': idx, 'half_life': half_life, 'initial_identity': initial})

half_life_df = pd.DataFrame(half_life_records)
print(f'\nIdentity half-life:')
print(f'  Mean: {half_life_df["half_life"].mean():.1f} iterations')
print(f'  Max: {half_life_df["half_life"].max()}')
print(f'  Systems with no decay: {(half_life_df["half_life"] == T).sum()}')

# By regime
print(f'\nHalf-life by regime:')
for reg in ['CG', 'CH', 'RG', 'CL']:
    sub = half_life_df[half_life_df['domain'].isin(
        id_metrics[id_metrics['process_regime'] == reg]['domain'].unique()
    )]
    if len(sub) > 0:
        print(f'  {reg}: mean half-life = {sub["half_life"].mean():.1f}')

temporal_df.to_csv(f'{BASE}/outputs/phaseK_temporal_identity.csv', index=False)
half_life_df.to_csv(f'{BASE}/outputs/phaseK_identity_half_life.csv', index=False)

# ====================================================
# K7: NULL PROGRAM
# ====================================================
print('\n' + '='*70)
print('PHASE K7 — NULL PROGRAM')
print('Baseline identity of null/noise systems')
print('='*70)

# Generate control: random-walk identity metrics
N_NULL = 1000
null_records = []
for i in range(N_NULL):
    null_records.append({
        'null_sys': i,
        'recursive_identity_score': np.random.uniform(0, 1),
        'recursive_continuity': np.random.uniform(0, 1),
        'reconstruction_ability': np.random.uniform(0, 1),
        'org_memory': np.random.uniform(0, 1),
        'trajectory_coherence': np.random.uniform(0, 1),
        'closure_persistence': np.random.uniform(0, 1),
    })
null_df = pd.DataFrame(null_records)

# Compare null vs actual
print(f'\nNull baseline vs actual CG identity:')
actual_cg = cg_metrics[['recursive_identity_score', 'recursive_continuity', 
                         'reconstruction_ability', 'org_memory',
                         'trajectory_coherence', 'closure_persistence']].mean()

null_mean = null_df[['recursive_identity_score', 'recursive_continuity', 
                      'reconstruction_ability', 'org_memory',
                      'trajectory_coherence', 'closure_persistence']].mean()

comparison = pd.DataFrame({'actual_CG': actual_cg, 'null_baseline': null_mean, 
                           'ratio': actual_cg.values / null_mean.values})
print(f'\n{"Metric":25s} {"Actual CG":10s} {"Null":10s} {"Ratio":8s}')
for col in comparison.index:
    print(f'  {col:25s} {comparison.loc[col,"actual_CG"]:10.4f} {comparison.loc[col,"null_baseline"]:10.4f} {comparison.loc[col,"ratio"]:8.2f}')

# How many CG systems are above null baseline?
null_df.to_csv(f'{BASE}/outputs/phaseK_null_baseline.csv', index=False)

print(f'\nK5+K6+K7 COMPLETE')
