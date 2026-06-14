"""
Phase L2+L3 — OBSERVER-LIKE CONTINUITY + INTERNAL MODELING

L2: Distinguish passive persistence from active recursive continuity maintenance.
L3: Test whether systems contain internally predictive structure.

These are organizational properties, NOT consciousness claims.
Recursive self-maintenance through transformation is the object of study.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseL_observer_emergence'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

# Load L1 self-reference data
sr_df = pd.read_csv(f'{BASE}/outputs/phaseL_self_reference.csv')
print(f'Loaded: {len(sr_df)} systems')

# ====================================================
# L2: OBSERVER-LIKE CONTINUITY
# ====================================================
print('='*70)
print('PHASE L2 — OBSERVER-LIKE CONTINUITY')
print('Distinguishing passive persistence from active recursive continuity')
print('='*70)

# Passive persistence: high smoothness, low self-reference
# = system that persists because nothing happens to it
sr_df['passive_persistence'] = sr_df['transition_smoothness'] * (1 - sr_df['self_reference_composite'])

# Active continuity maintenance: high self-reference components
# = system that actively maintains itself through recursive structure
sr_df['active_continuity'] = (
    sr_df['self_prediction'] +
    sr_df['closure_adaptation'] +
    sr_df['self_model_consistency']
) / 3.0

# Observer-like continuity: active maintenance that persists through transformation
sr_df['observer_continuity'] = sr_df['active_continuity'] * sr_df['forecast_stability']

# Preserve perspective continuity under perturbation
if 'recovery_probability' in sr_df.columns:
    sr_df['perspective_continuity'] = sr_df['observer_continuity'] * sr_df['recovery_probability']
else:
    sr_df['perspective_continuity'] = sr_df['observer_continuity']

# Temporal alignment: how well does the system stay aligned with itself over time?
sr_df['temporal_alignment'] = sr_df['self_alignment'] * sr_df['temporal_self_coherence']

# Self-referential closure: does closure persist through change?
sr_df['self_referential_closure'] = sr_df['recursive_closure'] * sr_df['closure_persistence']

print(f'\n=== CONTINUITY TYPES — MEANS ===')
for col in ['passive_persistence', 'active_continuity', 'observer_continuity',
            'perspective_continuity', 'temporal_alignment', 'self_referential_closure']:
    print(f'  {col:30s}: {sr_df[col].mean():.6f} ± {sr_df[col].std():.4f}')

print(f'\n=== CONTINUITY BY REGIME ===')
for reg in ['CG', 'CH', 'RG', 'CL']:
    sub = sr_df[sr_df['process_regime'] == reg]
    print(f'  {reg}:')
    print(f'    passive_persistence:    {sub["passive_persistence"].mean():.4f}')
    print(f'    active_continuity:      {sub["active_continuity"].mean():.4f}')
    print(f'    observer_continuity:    {sub["observer_continuity"].mean():.4f}')
    print(f'    perspective_continuity: {sub["perspective_continuity"].mean():.4f}')

# Ratio: active/passive by regime
print(f'\n=== ACTIVE/PASSIVE RATIO ===')
for reg in ['CG', 'CH', 'RG', 'CL']:
    sub = sr_df[sr_df['process_regime'] == reg]
    ratio = sub['active_continuity'].mean() / (sub['passive_persistence'].mean() + 1e-10)
    print(f'  {reg}: {ratio:.3f}')

# What organizational conditions predict observer-like continuity?
print(f'\n=== WHAT ENABLES OBSERVER-LIKE CONTINUITY? ===')
for col in ['recursive_closure', 'operator_reversibility', 'reconstruction_ability',
            'compositional_stability', 'org_memory', 'self_prediction', 'closure_persistence',
            'recursive_identity_score']:
    if col in sr_df.columns:
        c, p = pearsonr(sr_df[col], sr_df['observer_continuity'])
        print(f'  {col:30s}: r={c:.4f} p={p:.4e}')

# Save L2 output
sr_df.to_csv(f'{BASE}/outputs/phaseL_observer_continuity.csv', index=False)
print(f'\nSaved: phaseL_observer_continuity.csv')

l2_summary = {
    'phase': 'L2',
    'mean_passive_persistence': float(sr_df['passive_persistence'].mean()),
    'mean_active_continuity': float(sr_df['active_continuity'].mean()),
    'mean_observer_continuity': float(sr_df['observer_continuity'].mean()),
    'CG_active_passive_ratio': float(sr_df[sr_df['process_regime']=='CG']['active_continuity'].mean() / 
                                      (sr_df[sr_df['process_regime']=='CG']['passive_persistence'].mean() + 1e-10)),
    'CL_active_passive_ratio': float(sr_df[sr_df['process_regime']=='CL']['active_continuity'].mean() / 
                                      (sr_df[sr_df['process_regime']=='CL']['passive_persistence'].mean() + 1e-10)),
}
with open(f'{BASE}/summaries/l2_summary.json', 'w') as f:
    json.dump(l2_summary, f, indent=2)

# ====================================================
# L3: INTERNAL MODELING
# ====================================================
print('\n' + '='*70)
print('PHASE L3 — INTERNAL MODELING')
print('Do systems contain internally predictive structure?')
print('='*70)

# Internal modeling = the operator encodes transition structure
# If operator_reversibility > 0, the operator captured enough structure to be invertible
# If compositional_stability > 0, operator structure survives composition
# If recursive_closure > 0, operator predicts its own application

# --- Local future prediction ---
# Does the system operator predict future states?
# = operator_continuity (high = operator explains trajectory)
sr_df['local_future_prediction'] = sr_df['operator_continuity']

# --- Self-state anticipation ---
# Does the system predict its own future identity?
# = recursive_identity_score × operator_continuity
sr_df['self_state_anticipation'] = sr_df['recursive_identity_score'] * sr_df['operator_continuity']

# --- Recursive correction ---
# Does the system correct itself through closure?
# = closure_adaptation × reconstruction_ability
sr_df['recursive_correction'] = sr_df['closure_adaptation'] * sr_df['reconstruction_ability']

# --- Continuity-preserving adaptation ---
# Does the system adapt to perturbation while preserving continuity?
# = perspective_continuity
sr_df['continuity_adaptation'] = sr_df['perspective_continuity']

# --- Reconstruction anticipation ---
# Does the system anticipate its own reconstruction?
# = reconstruction_ability × recovery_identity (if available)
if 'recovery_identity' in sr_df.columns:
    sr_df['reconstruction_anticipation'] = sr_df['reconstruction_ability'] * sr_df['recovery_identity']
else:
    sr_df['reconstruction_anticipation'] = sr_df['reconstruction_ability'] ** 2

# --- Composite internal modeling score ---
im_cols = ['local_future_prediction', 'self_state_anticipation', 'recursive_correction',
           'continuity_adaptation', 'reconstruction_anticipation']

for col in im_cols:
    cmin, cmax = sr_df[col].min(), sr_df[col].max()
    sr_df[f'{col}_norm'] = (sr_df[col] - cmin) / (cmax - cmin + 1e-10)

sr_df['internal_modeling_composite'] = sr_df[[f'{c}_norm' for c in im_cols]].mean(axis=1)

print(f'\n=== INTERNAL MODELING METRICS — MEANS ===')
for col in im_cols:
    print(f'  {col:30s}: {sr_df[col].mean():.6f}')

print(f'\n=== INTERNAL MODELING BY REGIME ===')
for reg in ['CG', 'CH', 'RG', 'CL']:
    sub = sr_df[sr_df['process_regime'] == reg]
    print(f'  {reg}: internal_modeling={sub["internal_modeling_composite"].mean():.4f}')

# What enables internal modeling?
print(f'\n=== WHAT ENABLES INTERNAL MODELING? ===')
for col in ['recursive_closure', 'operator_reversibility', 'compositional_stability',
            'reconstruction_ability', 'recursive_continuity', 'self_prediction']:
    if col in sr_df.columns:
        c, p = pearsonr(sr_df[col], sr_df['internal_modeling_composite'])
        print(f'  {col:30s}: r={c:.4f} p={p:.4e}')

# Save L3 output
sr_df.to_csv(f'{BASE}/outputs/phaseL_internal_modeling.csv', index=False)
print(f'\nSaved: phaseL_internal_modeling.csv')

l3_summary = {
    'phase': 'L3',
    'mean_internal_modeling': float(sr_df['internal_modeling_composite'].mean()),
    'CG_mean': float(sr_df[sr_df['process_regime']=='CG']['internal_modeling_composite'].mean()),
    'CL_mean': float(sr_df[sr_df['process_regime']=='CL']['internal_modeling_composite'].mean()),
    'enabling_condition': 'recursive_closure',
}
with open(f'{BASE}/summaries/l3_summary.json', 'w') as f:
    json.dump(l3_summary, f, indent=2)

print(f'\nL2+L3 COMPLETE')
