"""
Phase L1 — SELF-REFERENCE METRICS

Constructs operational metrics for whether a process
models aspects of its own continuity.

Approach: Uses EXISTING phase outputs (no raw trajectory generation).
Self-reference is measured as interactions between known organizational metrics.

Anti-drift: Self-reference is closure-referential continuity,
not philosophical introspection.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseL_observer_emergence'
PHK = '/home/student/sgp_core_v2/phases/phaseK_recursive_identity'
PHI = '/home/student/sgp_core_v2/phases/phaseI_operator_algebra'
PHJ = '/home/student/sgp_core_v2/phases/phaseJ_organizational_invariants'
PH2 = '/home/student/sgp_core_v2/phases/phaseH2_process'
os.makedirs(f'{BASE}/outputs', exist_ok=True)
os.makedirs(f'{BASE}/summaries', exist_ok=True)

print('='*70)
print('PHASE L1 — SELF-REFERENCE METRICS')
print('Organizational self-reference from existing phase outputs')
print('='*70)

# Load all existing data
id_metrics = pd.read_csv(f'{PHK}/outputs/phaseK_identity_metrics.csv')
trans_geo = pd.read_csv(f'{PHI}/outputs/phaseI_transition_geometry.csv')
recovery = pd.read_csv(f'{PH2}/outputs/recovery_metrics.csv') if os.path.exists(f'{PH2}/outputs/recovery_metrics.csv') else None
nulls = pd.read_csv(f'{PHI}/outputs/phaseI_nulls.csv') if os.path.exists(f'{PHI}/outputs/phaseI_nulls.csv') else None

print(f'Loaded: identity_metrics={len(id_metrics)}, transition_geometry={len(trans_geo)}')

# Merge into unified dataset
df = id_metrics.merge(trans_geo, on=['domain','sys_idx'], how='left', suffixes=('','_tg'))
if recovery is not None:
    df = df.merge(recovery, on=['domain','sys_idx'], how='left', suffixes=('','_rec'))
print(f'Merged: {len(df)} systems')

# ====================================================
# Construct Self-Reference Metrics
# ====================================================
# Each metric captures a DIFFERENT organizational condition
# for recursive identity to become self-referential.

print('\nConstructing self-reference metrics...')

# --- SR1: Recursive self-prediction ---
# Does the process predict its own continuity?
# = recursive_closure × operator_continuity
# High closure WITH high continuity = process that enforces its own trajectory
df['self_prediction'] = df['recursive_closure'] * df['operator_continuity']

# --- SR2: Internal continuity prediction ---
# Does the process maintain awareness of its own continuity?
# = recursive_continuity × transition_smoothness
# High continuity smoothness WITH recursive structure
df['internal_continuity'] = df['recursive_continuity'] * df['transition_smoothness']

# --- SR3: Self-model consistency ---
# Does the process model itself consistently through transformation?
# = reconstruction_ability × operator_reversibility
# Can reconstruct AND operator is reversible = self-model survives
df['self_model_consistency'] = df['reconstruction_ability'] * df['operator_reversibility']

# --- SR4: Closure-aware adaptation ---
# Does closure drive adaptation under perturbation?
# = closure_persistence × recovery_identity
# High persistence + high recovery = closure guides recovery
df['closure_adaptation'] = df['closure_persistence'] * df['recovery_identity']

# --- SR5: Recursive forecasting stability ---
# Does recursive structure remain stable under transformation?
# = recursive_closure × compositional_stability
# Closure does not break when composed
df['forecast_stability'] = df['recursive_closure'] * df['compositional_stability']

# --- SR6: Process self-alignment ---
# Are operator geometry and identity aligned?
# = |operator_continuity - recursive_identity_score|⁻ (inverted)
# Low gap = process "knows itself"
continuity_gap = np.abs(df['operator_continuity'] - df['recursive_identity_score'])
df['self_alignment'] = 1.0 - (continuity_gap - continuity_gap.min()) / (continuity_gap.max() - continuity_gap.min() + 1e-10)

# --- SR7: Temporal self-coherence ---
# Does identity persist coherently through time?
# = trajectory_coherence × org_memory
# Remembers coherent trajectory
df['temporal_self_coherence'] = df['trajectory_coherence'] * df['org_memory']

# --- SR8: Perturbation anticipation (from recovery data) ---
# Does the system show structured recovery?
# = recovery_probability × (1 - recovery_entropy)
if 'recovery_probability' in df.columns and 'recovery_entropy' in df.columns:
    df['perturbation_anticipation'] = df['recovery_probability'] * (1 - df['recovery_entropy'])
else:
    df['perturbation_anticipation'] = 0.0

# --- Composite self-reference score ---
sr_cols = ['self_prediction', 'internal_continuity', 'self_model_consistency',
           'closure_adaptation', 'forecast_stability', 'self_alignment',
           'temporal_self_coherence', 'perturbation_anticipation']

# Normalize each to [0,1]
for col in sr_cols:
    cmin, cmax = df[col].min(), df[col].max()
    df[f'{col}_norm'] = (df[col] - cmin) / (cmax - cmin + 1e-10)

df['self_reference_composite'] = df[[f'{c}_norm' for c in sr_cols]].mean(axis=1)

# Save
df.to_csv(f'{BASE}/outputs/phaseL_self_reference.csv', index=False)
print(f'Saved: phaseL_self_reference.csv ({len(df)} systems, {len(sr_cols)} metrics)')

# ====================================================
# Analysis: What organizational conditions drive self-reference?
# ====================================================
print(f'\n=== SELF-REFERENCE METRICS — MEANS ===')
for col in sr_cols:
    print(f'  {col:30s}: {df[col].mean():.6f}')

print(f'\n=== SELF-REFERENCE COMPOSITE BY REGIME ===')
for reg in ['CG', 'CH', 'RG', 'CL']:
    sub = df[df['process_regime'] == reg]
    print(f'  {reg}: composite={sub["self_reference_composite"].mean():.4f} ± {sub["self_reference_composite"].std():.3f}')

# What predicts self-reference?
print(f'\n=== ORGANIZATIONAL PREDICTORS OF SELF-REFERENCE ===')
predictors = ['recursive_closure', 'operator_continuity', 'recursive_identity_score',
              'reconstruction_ability', 'org_memory', 'operator_reversibility',
              'transition_smoothness', 'compositional_stability', 'recursive_continuity']
for col in predictors:
    if col in df.columns:
        c, p = pearsonr(df[col], df['self_reference_composite'])
        print(f'  {col:30s}: r={c:.4f} p={p:.4e}')
    else:
        print(f'  {col:30s}: NOT FOUND')

# Top predictor
top_pred = sorted([(col, abs(pearsonr(df[col], df['self_reference_composite'])[0]))
                    for col in predictors if col in df.columns],
                   key=lambda x: x[1], reverse=True)[0]
print(f'\nTop predictor: {top_pred[0]} (r={top_pred[1]:.4f})')

# Double-check which column has highest r
from scipy.stats import pearsonr as pr
best_col = None; best_r = -1
for col in predictors:
    if col in df.columns:
        r, _ = pr(df[col], df['self_reference_composite'])
        if abs(r) > best_r:
            best_r = abs(r)
            best_col = col
print(f'Best predictor: {best_col} (r={best_r:.4f})')

# Save summary
summary = {
    'phase': 'L1',
    'n_systems': len(df),
    'mean_self_reference_composite': float(df['self_reference_composite'].mean()),
    'top_organizational_predictor': best_col,
    'top_predictor_r': float(best_r),
    'sr_metrics': {col: float(df[col].mean()) for col in sr_cols},
    'regime_means': {reg: float(df[df['process_regime']==reg]['self_reference_composite'].mean()) for reg in ['CG','CH','RG','CL']},
}
with open(f'{BASE}/summaries/l1_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f'Saved: summaries/l1_summary.json')

print(f'\nL1 COMPLETE')
