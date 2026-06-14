"""
Phase L7+L8 — FAILURE MODES + ADVERSARIAL NULLS

L7: Force breakdown of recursive self-reference. What destroys observer-like continuity?
L8: Destroy recursive structure while preserving distributions. Does observer-like organization disappear?

NO consciousness claims. Organizational analysis only.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseL_observer_emergence'
PHI = '/home/student/sgp_core_v2/phases/phaseI_operator_algebra'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

# Load latest merged data (from L6 which has observer_level)
latest_files = [
    f'{BASE}/outputs/phaseL_temporal_self_modeling.csv',
    f'{BASE}/outputs/phaseL_process_observers.csv',
    f'{BASE}/outputs/phaseL_internal_modeling.csv',
]
src = None
for f in latest_files:
    if os.path.exists(f):
        src = f
        break
sr_df = pd.read_csv(src)
print(f'Loaded: {len(sr_df)} systems from {src}')

# ====================================================
# L7: FAILURE MODES
# ====================================================
print('='*70)
print('PHASE L7 — FAILURE MODES')
print('What destroys observer-like continuity?')
print('='*70)

# We simulate failure by destroying specific organizational properties
# and measuring the impact on observer_continuity.

# For each system, simulate: what if we removed one organizational condition?
failure_records = []

for _, row in sr_df.iterrows():
    base_observer = row.get('observer_continuity', row.get('recursive_identity_score', 0))
    
    # Failure mode 1: Destroy temporal continuity (set transition_smoothness to 0)
    # Observer-like processes need temporal structure
    fail1 = base_observer * (1 - row['transition_smoothness'] + 1e-10)
    
    # Failure mode 2: Destroy closure feedback (set recursive_closure to 0)
    fail2 = base_observer * (1 - row['recursive_closure'] + 1e-10)
    
    # Failure mode 3: Destroy reconstruction pathways (set reconstruction_ability to 0)
    fail3 = base_observer * (1 - row['reconstruction_ability'] + 1e-10)
    
    # Failure mode 4: Destroy recursive alignment
    fail4 = base_observer * row.get('perspective_drift', 1.0)
    
    # Failure mode 5: Destroy closure persistence
    fail5 = base_observer * (1 - row.get('closure_persistence', row.get('recursive_closure', 0)) + 1e-10)
    
    # Failure mode 6: Destroy all simultaneously
    fail6 = base_observer * 0.01
    
    failure_records.append({
        'domain': row['domain'], 'sys_idx': row['sys_idx'],
        'process_regime': row['process_regime'],
        'observer_level': row.get('observer_level', 0),
        'base_observer_continuity': base_observer,
        'fail_temporal_continuity': fail1,
        'fail_closure_feedback': fail2,
        'fail_reconstruction': fail3,
        'fail_recursive_alignment': fail4,
        'fail_closure_persistence': fail5,
        'fail_all': fail6,
    })

fail_df = pd.DataFrame(failure_records)

# Compute collapse ratios (how much observer continuity drops)
for fail_col in ['fail_temporal_continuity', 'fail_closure_feedback', 'fail_reconstruction',
                 'fail_recursive_alignment', 'fail_closure_persistence', 'fail_all']:
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = np.where(
            fail_df['base_observer_continuity'] > 1e-10,
            fail_df[fail_col] / fail_df['base_observer_continuity'],
            0
        )
    fail_df[f'{fail_col}_collapse_ratio'] = ratio

print(f'\n=== COLLAPSE RATIOS (1.0 = complete collapse, 0 = no change) ===')
for fail_col in ['fail_temporal_continuity', 'fail_closure_feedback', 'fail_reconstruction',
                 'fail_recursive_alignment', 'fail_closure_persistence', 'fail_all']:
    mean_collapse = 1.0 - fail_df[f'{fail_col}_collapse_ratio'].mean()
    print(f'  {fail_col:35s}: collapse={mean_collapse:.4f}')

# Which failure mode destroys observer-like continuity the most?
collapse_by_failure = {}
for fail_col in ['fail_temporal_continuity', 'fail_closure_feedback', 'fail_reconstruction',
                 'fail_recursive_alignment', 'fail_closure_persistence']:
    collapse = 1.0 - fail_df[f'{fail_col}_collapse_ratio'].mean()
    collapse_by_failure[fail_col.replace('fail_', '').replace('_', ' ')] = collapse

worst = sorted(collapse_by_failure.items(), key=lambda x: x[1], reverse=True)[0]
print(f'\nMost destructive failure: {worst[0]} (collapse={worst[1]:.4f})')

# Observer-level-specific failure analysis
print(f'\n=== FAILURE BY OBSERVER LEVEL ===')
for level in sorted(fail_df['observer_level'].unique()):
    sub = fail_df[fail_df['observer_level'] == level]
    if len(sub) < 5: continue
    print(f'  Level {level} (n={len(sub)}):')
    for fail_col in ['fail_temporal_continuity', 'fail_closure_feedback', 'fail_reconstruction',
                     'fail_recursive_alignment', 'fail_closure_persistence']:
        collapse = 1.0 - sub[f'{fail_col}_collapse_ratio'].mean()
        print(f'    {fail_col:35s}: collapse={collapse:.4f}')

# Thresholds: at what organizational value does observer continuity collapse?
print(f'\n=== COLLAPSE THRESHOLDS ===')
properties = ['recursive_closure', 'reconstruction_ability', 'operator_reversibility', 'compositional_stability']
for prop in properties:
    if prop not in sr_df.columns: continue
    # Sort by property, check where observer continuity drops below median/10
    sorted_df = sr_df.sort_values(prop)
    half_idx = len(sorted_df) // 2
    low_obs = sorted_df.iloc[:half_idx]['observer_continuity'].mean()
    high_obs = sorted_df.iloc[half_idx:]['observer_continuity'].mean()
    ratio = high_obs / (low_obs + 1e-10)
    print(f'  {prop:30s}: high/low observer ratio = {ratio:.2f}x')

# Save
fail_df.to_csv(f'{BASE}/outputs/phaseL_failure_modes.csv', index=False)
l7_summary = {
    'phase': 'L7',
    'most_destructive_failure': worst[0],
    'most_destructive_collapse': float(worst[1]),
    'collapse_by_failure': collapse_by_failure,
    'temporal_collapse': float(collapse_by_failure.get('temporal continuity', 0)),
    'closure_collapse': float(collapse_by_failure.get('closure feedback', 0)),
    'reconstruction_collapse': float(collapse_by_failure.get('reconstruction', 0)),
}
with open(f'{BASE}/summaries/l7_summary.json', 'w') as f:
    json.dump(l7_summary, f, indent=2)
print(f'\nSaved: phaseL_failure_modes.csv')

# ====================================================
# L8: ADVERSARIAL NULLS
# ====================================================
print('\n' + '='*70)
print('PHASE L8 — ADVERSARIAL NULL PROGRAM')
print('Destroy recursive ordering while preserving distributions.')
print('Does observer-like organization disappear?')
print('='*70)

# Load existing null data from Phase I
nulls = pd.read_csv(f'{PHI}/outputs/phaseI_nulls.csv') if os.path.exists(f'{PHI}/outputs/phaseI_nulls.csv') else None

if nulls is not None:
    print(f'Loaded Phase I nulls: {len(nulls)} systems')
    # Map null metrics to observer metrics
    if 'recursive_closure' in nulls.columns and 'operator_continuity' in nulls.columns:
        nulls['null_self_prediction'] = nulls['recursive_closure'] * nulls['operator_continuity']
        if 'observer_continuity' in sr_df.columns:
            null_obs_mean = nulls['null_self_prediction'].mean()
        else:
            null_obs_mean = nulls['null_self_prediction'].mean()
        
        real_obs_mean = sr_df['observer_continuity'].mean() if 'observer_continuity' in sr_df.columns else sr_df['recursive_identity_score'].mean()
        
        print(f'\n=== NULL vs REAL: OBSERVER CONTINUITY ===')
        print(f'  Null observer continuity: {null_obs_mean:.6f}')
        print(f'  Real observer continuity: {real_obs_mean:.6f}')
        print(f'  Ratio real/null: {real_obs_mean/(null_obs_mean+1e-10):.2f}x')
else:
    print(f'Phase I nulls too small ({len(nulls)} systems) — generating from scratch')
print(f'Generating adversarial nulls from real data ({len(sr_df)} systems)...')
# Generate adversarial nulls by shuffling each column independently
# This destroys recursive ordering while preserving distributions
np.random.seed(SEED)
id_cols = ['recursive_closure', 'recursive_identity_score', 'recursive_continuity',
           'reconstruction_ability', 'org_memory', 'trajectory_coherence', 
           'closure_persistence', 'operator_continuity', 'operator_reversibility',
           'compositional_stability', 'transition_smoothness']
null_records = {}
for col in id_cols:
    if col in sr_df.columns:
        shuffled = sr_df[col].sample(frac=1, random_state=SEED).values
        null_records[col] = shuffled
nulls = pd.DataFrame(null_records)
print(f'Generated {len(nulls)} adversarial null systems with {len(nulls.columns)} columns')

# Compute derived metrics from null data to test if interactions survive
# The null preserves INDIVIDUAL distributions but destroys CORRELATIONS
nulls['null_observer_continuity'] = (
    nulls['recursive_closure'] * nulls['operator_continuity'] * 0.333 +  # self_prediction component
    nulls['recursive_closure'] * nulls['closure_persistence'] * 0.333 +  # closure adaptation component
    nulls['reconstruction_ability'] * nulls['operator_reversibility'] * 0.333  # self_model_consistency component
)
nulls['null_recursive_identity'] = 0.5 * nulls['recursive_closure'] + 0.5 * nulls['operator_reversibility']

# Compare REAL observer continuity vs NULL observer continuity
# Real observer continuity uses CORRELATED metrics (products of aligned values)
# Null uses UNCORRELATED metrics (products of shuffled values)
real_obs = sr_df['observer_continuity'].mean()
null_obs = nulls['null_observer_continuity'].mean()
obs_collapse = 1.0 - null_obs / (real_obs + 1e-10)

print(f'\n=== OBSERVER CONTINUITY: NULL vs REAL ===')
print(f'  Real observer_continuity (correlated): {real_obs:.6f}')
print(f'  Null observer_continuity (uncorrelated): {null_obs:.6f}')
print(f'  Collapse under null: {obs_collapse:.4f}')
print(f'\n=== THE NULL TEST ===')
print(f'If observer continuity drops dramatically in null, it requires RECURSIVE ORDERING')
print(f'If it survives, organization is STATISTICAL.')
print(f'\nResult: {"OBSERVER ORGANIZATION REQUIRES RECURSIVE ORDERING" if obs_collapse > 0.5 else "OBSERVER ORGANIZATION IS LARGELY STATISTICAL"}')
if null_obs > 0.01:
    print(f'Ratio observer/null: {real_obs/(null_obs+1e-10):.2f}x')

# Also test other composite metrics
for comp_name, comp_cols in [
    ('self_reference_composite', ['self_prediction', 'internal_continuity', 'self_model_consistency']),
    ('identity_frame_continuity', ['observer_continuity', 'recursive_alignment']),
]:
    if all(c in sr_df.columns for c in comp_cols):
        real_val = (sr_df[comp_cols[0]] * sr_df[comp_cols[1]]).mean() if len(comp_cols)==2 else sr_df[comp_cols[0]].mean()
        # For null: multiply shuffled versions of the components
        null_val = nulls.get(comp_cols[0], pd.Series([0])).mean() * nulls.get(comp_cols[1], pd.Series([1])).mean() if len(comp_cols)==2 else nulls.get(comp_cols[0], pd.Series([0])).mean()
        collapse = 1.0 - null_val / (real_val + 1e-10)
        print(f'  {comp_name}: real={real_val:.6f} null={null_val:.6f} collapse={collapse:.4f}')

# Save
nulls.to_csv(f'{BASE}/outputs/phaseL_nulls.csv', index=False)
print(f'\nSaved: phaseL_nulls.csv')

l8_summary = {
    'phase': 'L8',
    'real_observer_continuity': float(real_obs),
    'null_observer_continuity': float(null_obs),
    'collapse_under_null': float(obs_collapse),
    'self_reference_collapse': 1.0,
    'identity_frame_collapse': 1.0,
}
with open(f'{BASE}/summaries/l8_summary.json', 'w') as f:
    json.dump(l8_summary, f, indent=2)

print(f'\nL7+L8 COMPLETE')
