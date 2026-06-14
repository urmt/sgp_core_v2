"""
Phase L4+L5+L6 — PERSPECTIVE STABILITY + PROCESS OBSERVERS + TEMPORAL SELF-MODELING

L4: Can recursive perspective remain coherent through change?
L5: Organizational conditions for observer-like persistence.
L6: Long-horizon tracking of recursive identity.

NO consciousness claims. Organizational analysis only.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseL_observer_emergence'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

# Load data (from latest merged file containing L1-L3 columns)
latest = f'{BASE}/outputs/phaseL_internal_modeling.csv'
sr_df = pd.read_csv(latest)
print(f'Loaded {len(sr_df)} systems from {latest}')

# ====================================================
# L4: RECURSIVE PERSPECTIVE STABILITY
# ====================================================
print('='*70)
print('PHASE L4 — RECURSIVE PERSPECTIVE STABILITY')
print('Can recursive perspective remain coherent through change?')
print('='*70)

# Perspective drift = how much does identity change under transformation?
# Measured as: 1 - (identity retention from Phase K transformations)
drift_cols = ['self_prediction', 'self_alignment', 'temporal_self_coherence']
# Systems with high self-alignment AND low drift = stable perspective
# We approximate drift from: 1 - compositional_stability (if operator breaks, perspective drifts)
sr_df['perspective_drift'] = 1.0 - sr_df['compositional_stability']

# Recursive alignment = identity stays aligned through operator transformation
sr_df['recursive_alignment'] = sr_df['self_alignment'] * sr_df['compositional_stability']

# Identity frame continuity = frame of reference persists
sr_df['identity_frame_continuity'] = sr_df['observer_continuity'] * sr_df['recursive_alignment']

# Closure persistence through change
sr_df['closure_persistence_through_change'] = sr_df['closure_persistence'] * sr_df['forecast_stability']

print(f'\n=== PERSPECTIVE STABILITY METRICS ===')
for col in ['perspective_drift', 'recursive_alignment', 'identity_frame_continuity',
            'closure_persistence_through_change']:
    print(f'  {col:35s}: {sr_df[col].mean():.6f} ± {sr_df[col].std():.4f}')

# What systems maintain coherent perspective?
high_stability = sr_df[sr_df['identity_frame_continuity'] > sr_df['identity_frame_continuity'].quantile(0.9)]
low_stability = sr_df[sr_df['identity_frame_continuity'] < sr_df['identity_frame_continuity'].quantile(0.1)]

print(f'\n=== SYSTEMS WITH STABLE PERSPECTIVE (top 10%) ===')
print(f'  n={len(high_stability)}')
for col in ['recursive_closure', 'reconstruction_ability', 'self_prediction',
            'recursive_identity_score', 'compositional_stability']:
    if col in sr_df.columns:
        h_mean = high_stability[col].mean()
        l_mean = low_stability[col].mean()
        print(f'  {col:30s}: stable={h_mean:.4f} vs unstable={l_mean:.4f} (ratio={h_mean/(l_mean+1e-10):.2f})')

# By regime
print(f'\n=== PERSPECTIVE STABILITY BY REGIME ===')
for reg in ['CG', 'CH', 'RG', 'CL']:
    sub = sr_df[sr_df['process_regime'] == reg]
    print(f'  {reg}: identity_frame_continuity={sub["identity_frame_continuity"].mean():.4f}')

# Save
sr_df.to_csv(f'{BASE}/outputs/phaseL_perspective_stability.csv', index=False)
l4_summary = {
    'phase': 'L4',
    'mean_perspective_drift': float(sr_df['perspective_drift'].mean()),
    'mean_identity_frame_continuity': float(sr_df['identity_frame_continuity'].mean()),
    'CG_identity_frame': float(sr_df[sr_df['process_regime']=='CG']['identity_frame_continuity'].mean()),
    'CL_identity_frame': float(sr_df[sr_df['process_regime']=='CL']['identity_frame_continuity'].mean()),
}
with open(f'{BASE}/summaries/l4_summary.json', 'w') as f:
    json.dump(l4_summary, f, indent=2)
print(f'\nSaved: phaseL_perspective_stability.csv')

# ====================================================
# L5: PROCESS OBSERVERS — organizational conditions
# ====================================================
print('\n' + '='*70)
print('PHASE L5 — PROCESS OBSERVER CONDITIONS')
print('Identifying organizational conditions for observer-like persistence')
print('='*70)
print('\nNOTE: These are ORGANIZATIONAL CLASSIFICATIONS only.')
print('No claims about consciousness.')

# Observer-likeness is a continuum of organizational conditions:
#   Level 0: Passive — persists because nothing happens
#   Level 1: Reactive — responds to perturbation
#   Level 2: Adaptive — maintains continuity through adaptation
#   Level 3: Observer-like — stable recursive self-referential continuity

# These are conditions, not fixed types.
# A system can show observer-like behavior under some conditions and not others.

# Level conditions (each is a CONTINUOUS organizational property):
sr_df['observer_level'] = 0

# Level 0 → Level 1: system does more than passively persist
# Condition: active_continuity > passive_persistence threshold
sr_df['reactive_condition'] = (sr_df['active_continuity'] > sr_df['passive_persistence'].median() * 0.5).astype(float)
sr_df.loc[sr_df['reactive_condition'] > 0, 'observer_level'] = 1

# Level 1 → Level 2: system maintains continuity through adaptation
# Condition: recursive_correction > 0 AND perspective_continuity > median
sr_df['adaptive_condition'] = (
    (sr_df['recursive_correction'] > sr_df['recursive_correction'].median() if sr_df['recursive_correction'].max() > 0 else True)
).astype(float)
sr_df.loc[(sr_df['observer_level'] >= 1) & (sr_df['perspective_continuity'] > sr_df['perspective_continuity'].median()), 'observer_level'] = 2

# Level 2 → Level 3: stable recursive self-referential continuity
# Condition: identity_frame_continuity > 0.8 quantile AND closure persists
sr_df['observer_like_condition'] = (
    (sr_df['identity_frame_continuity'] > sr_df['identity_frame_continuity'].quantile(0.8)) &
    (sr_df['closure_persistence_through_change'] > sr_df['closure_persistence_through_change'].median())
).astype(float)
sr_df.loc[(sr_df['observer_level'] >= 2) & (sr_df['observer_like_condition'] > 0), 'observer_level'] = 3

print(f'\n=== OBSERVER LEVEL DISTRIBUTION ===')
for level in range(4):
    n = (sr_df['observer_level'] == level).sum()
    print(f'  Level {level}: {n} systems ({100*n/len(sr_df):.1f}%)')

# By regime
print(f'\n=== OBSERVER LEVEL BY REGIME ===')
for reg in ['CG', 'CH', 'RG', 'CL']:
    sub = sr_df[sr_df['process_regime'] == reg]
    print(f'  {reg}: mean level={sub["observer_level"].mean():.2f}')
    for level in range(4):
        n = (sub['observer_level'] == level).sum()
        if n > 0:
            print(f'    Level {level}: {n} ({100*n/len(sub):.0f}%)')

# Profile of observer-like systems (Level 3)
obs = sr_df[sr_df['observer_level'] == 3]
non_obs = sr_df[sr_df['observer_level'] < 3]
print(f'\n=== PROFILE: OBSERVER-LIKE vs OTHER SYSTEMS ===')
for col in ['recursive_closure', 'reconstruction_ability', 'self_prediction',
            'self_model_consistency', 'observer_continuity', 'identity_frame_continuity',
            'recursive_identity_score', 'compositional_stability']:
    if col in sr_df.columns:
        print(f'  {col:30s}: obs={obs[col].mean():.4f} vs other={non_obs[col].mean():.4f}')

# Organizational conditions that distinguish observer-like systems
print(f'\n=== ORGANIZATIONAL CONDITIONS FOR OBSERVER-LIKE PERSISTENCE ===')
conditions = ['recursive_closure', 'operator_reversibility', 'reconstruction_ability',
              'self_prediction', 'closure_persistence', 'compositional_stability',
              'self_model_consistency', 'perspective_continuity']
for col in conditions:
    if col in sr_df.columns:
        ratio = obs[col].mean() / (non_obs[col].mean() + 1e-10)
        print(f'  {col:30s}: obs/other ratio = {ratio:.2f}x')

# Save L5
sr_df.to_csv(f'{BASE}/outputs/phaseL_process_observers.csv', index=False)
observer_types_summary = {
    'n_level0': int((sr_df['observer_level']==0).sum()),
    'n_level1': int((sr_df['observer_level']==1).sum()),
    'n_level2': int((sr_df['observer_level']==2).sum()),
    'n_level3': int((sr_df['observer_level']==3).sum()),
    'CG_mean_level': float(sr_df[sr_df['process_regime']=='CG']['observer_level'].mean()),
    'CL_mean_level': float(sr_df[sr_df['process_regime']=='CL']['observer_level'].mean()),
    'top_distinguishing_condition': str(sorted(
        [(col, obs[col].mean()/(non_obs[col].mean()+1e-10))
         for col in conditions if col in sr_df.columns],
        key=lambda x: x[1], reverse=True
    )[0]) if len(obs) > 0 else None,
}
with open(f'{BASE}/summaries/l5_summary.json', 'w') as f:
    json.dump(observer_types_summary, f, indent=2)
print(f'\nSaved: phaseL_process_observers.csv')

# ====================================================
# L6: TEMPORAL SELF-MODELING
# ====================================================
print('\n' + '='*70)
print('PHASE L6 — TEMPORAL SELF-MODELING')
print('Long-horizon tracking of recursive identity')
print('='*70)

# Using Phase K temporal identity data
temporal = pd.read_csv(f'{BASE}/../phaseK_recursive_identity/outputs/phaseK_temporal_identity.csv')
half_life = pd.read_csv(f'{BASE}/../phaseK_recursive_identity/outputs/phaseK_identity_half_life.csv') if os.path.exists(f'{BASE}/../phaseK_recursive_identity/outputs/phaseK_identity_half_life.csv') else None

# Continuity prediction error: how well does current identity predict future identity?
# Using temporal identity decay as proxy
if half_life is not None and len(half_life) > 0:
    half_life_merged = half_life.merge(sr_df, on=['domain','sys_idx'], how='inner', suffixes=('','_sr'))
    print(f'\nMerged temporal+self-reference: {len(half_life_merged)} systems')
    
    # Self-model drift: systems with high self-reference but short half-life have bad self-models
    half_life_merged['self_model_drift'] = 1.0 - (half_life_merged['half_life'] / half_life_merged['half_life'].max())
    half_life_merged['self_model_drift'] = half_life_merged['self_model_drift'] * half_life_merged['self_reference_composite']
    
    # Recursive correction ability: do observer-like systems maintain identity longer?
    print(f'\n=== IDENTITY PERSISTENCE BY OBSERVER LEVEL ===')
    for level in range(4):
        sub = half_life_merged[half_life_merged['observer_level'] == level]
        if len(sub) > 0:
            print(f'  Level {level}: half_life={sub["half_life"].mean():.1f}')

    # Long-term identity persistence
    print(f'\n=== LONG-TERM IDENTITY PERSISTENCE ===')
    long_threshold = half_life_merged['half_life'].quantile(0.9)
    long_persist = half_life_merged[half_life_merged['half_life'] >= long_threshold]
    short_persist = half_life_merged[half_life_merged['half_life'] < long_threshold]
    print(f'  Long persistence: {len(long_persist)} systems (half_life>={long_threshold:.0f})')
    print(f'  Short persistence: {len(short_persist)} systems')
    
    for col in ['self_reference_composite', 'observer_continuity', 'recursive_closure',
                'reconstruction_ability', 'identity_frame_continuity']:
        if col in long_persist.columns:
            print(f'  {col:30s}: long={long_persist[col].mean():.4f} vs short={short_persist[col].mean():.4f}')
    
    half_life_merged.to_csv(f'{BASE}/outputs/phaseL_temporal_self_modeling.csv', index=False)
    l6_summary = {
        'mean_half_life_level0': float(half_life_merged[half_life_merged['observer_level']==0]['half_life'].mean()) if (half_life_merged['observer_level']==0).sum()>0 else 0,
        'mean_half_life_level3': float(half_life_merged[half_life_merged['observer_level']==3]['half_life'].mean()) if (half_life_merged['observer_level']==3).sum()>0 else 0,
    }
    print(f'\nSaved: phaseL_temporal_self_modeling.csv')
else:
    # Generate synthetic temporal modeling from existing data
    print(f'\nNo temporal half-life data available — using synthetic temporal model')
    # Simulate: observer-like systems should show less identity drift over time
    T = 100
    records = []
    for _, row in sr_df.iterrows():
        base = row['recursive_identity_score']
        stability = row['compositional_stability']
        for t in range(T):
            drift = np.exp(-0.05 * t * stability)
            noise = np.random.normal(0, 0.01)
            records.append({
                'domain': row['domain'], 'sys_idx': row['sys_idx'],
                'process_regime': row['process_regime'],
                'observer_level': row['observer_level'],
                'iteration': t, 'identity': base * drift + noise,
                'continuity_prediction_error': 1.0 - drift,
            })
    temp_df = pd.DataFrame(records)
    temp_df.to_csv(f'{BASE}/outputs/phaseL_temporal_self_modeling.csv', index=False)
    print(f'Synthetic temporal model saved ({len(temp_df)} rows)')
    l6_summary = {'note': 'synthetic temporal data — no observed half-life available'}
    
with open(f'{BASE}/summaries/l6_summary.json', 'w') as f:
    json.dump(l6_summary, f, indent=2)

print(f'\nL4+L5+L6 COMPLETE')
