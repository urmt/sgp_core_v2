"""
Phase K3+K4 — Identity vs Geometry + Reconstructive Self-Continuity.

K3: Can geometry survive without identity? Can identity survive geometry change?
K4: Test whether systems can reconstruct identity after organizational collapse.

Anti-drift: Identity is NOT geometry. Identity is THROUGH-transformation continuity.
"""
import numpy as np, pandas as pd, os, json, warnings
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseK_recursive_identity'
PH2 = '/home/student/sgp_core_v2/phases/phaseH2_process'
PI = '/home/student/sgp_core_v2/phases/phaseI_operator_algebra'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

print('='*70)
print('PHASE K3 — IDENTITY VS GEOMETRY')
print('Can geometry survive without identity? Can identity survive geometry change?')
print('='*70)

# Load data
id_metrics_df = pd.read_csv(f'{BASE}/outputs/phaseK_identity_metrics.csv')
trans_geo = pd.read_csv(f'{PI}/outputs/phaseI_transition_geometry.csv')
recovery_df = pd.read_csv(f'{PH2}/outputs/recovery_metrics.csv') if os.path.exists(f'{PH2}/outputs/recovery_metrics.csv') else None

# Merge identity metrics with transition geometry
merged = id_metrics_df.merge(trans_geo, on=['domain','sys_idx'], how='left', suffixes=('', '_tg'))

# ====================================================
# K3: IDENTITY VS GEOMETRY
# ====================================================
# Define geometry survival metrics
merged['geometry_survival'] = merged['operator_continuity']  # from trans_geo
# Define identity survival 
merged['identity_survival'] = merged['recursive_identity_score']

# Test 1: Can geometry survive without identity?
geo_without_id = merged[
    (merged['geometry_survival'] > merged['geometry_survival'].median()) &
    (merged['identity_survival'] < merged['identity_survival'].median())
]

# Test 2: Can identity survive geometry change?
id_without_geo = merged[
    (merged['identity_survival'] > merged['identity_survival'].median()) &
    (merged['geometry_survival'] < merged['geometry_survival'].median())
]

# Test 3: Both survive
both_survive = merged[
    (merged['geometry_survival'] > merged['geometry_survival'].median()) &
    (merged['identity_survival'] > merged['identity_survival'].median())
]

# Test 4: Neither survives
neither_survive = merged[
    (merged['geometry_survival'] < merged['geometry_survival'].median()) &
    (merged['identity_survival'] < merged['identity_survival'].median())
]

print(f'\n=== IDENTITY VS GEOMETRY SURVIVAL ===')
print(f'Total systems: {len(merged)}')
print(f'Geometry survives without identity: {len(geo_without_id)} ({100*len(geo_without_id)/len(merged):.1f}%)')
print(f'Identity survives geometry change: {len(id_without_geo)} ({100*len(id_without_geo)/len(merged):.1f}%)')
print(f'Both survive: {len(both_survive)} ({100*len(both_survive)/len(merged):.1f}%)')
print(f'Neither survives: {len(neither_survive)} ({100*len(neither_survive)/len(merged):.1f}%)')

# Correlation between geometry and identity
corr, p = pearsonr(merged['geometry_survival'], merged['identity_survival'])
print(f'\nGeometry-Identity correlation: r={corr:.4f} p={p:.4f}')

# What predicts identity better: static geometry or recursive continuity?
print('\n=== WHAT PREDICTS IDENTITY? ===')
predictors = ['operator_continuity', 'operator_curvature', 'operator_neighborhood_entropy',
              'transition_smoothness', 'recursive_closure', 'operator_reversibility']
for pred in predictors:
    if pred in merged.columns:
        c, p_val = pearsonr(merged[pred], merged['identity_survival'])
        print(f'  {pred:40s}: r={c:.4f} p={p_val:.4f}')
    else:
        print(f'  {pred:40s}: NOT FOUND')

# By regime
print('\n=== IDENTITY & GEOMETRY BY REGIME ===')
for regime in ['CG', 'CH', 'RG', 'CL']:
    rd = merged[merged['process_regime'] == regime]
    if len(rd) == 0: continue
    print(f'  {regime:4s}: identity={rd["identity_survival"].mean():.4f} geometry={rd["geometry_survival"].mean():.4f}')

# Identity vs geometry scatter statistics
id_vs_geo_df = merged[['domain', 'sys_idx', 'process_regime', 'geometry_survival', 
                        'identity_survival', 'recursive_continuity', 'reconstruction_ability',
                        'org_memory', 'trajectory_coherence']].copy()
id_vs_geo_df['geo_without_id'] = (merged['geometry_survival'] > merged['geometry_survival'].median()) & \
                                  (merged['identity_survival'] < merged['identity_survival'].median())
id_vs_geo_df['id_without_geo'] = (merged['identity_survival'] > merged['identity_survival'].median()) & \
                                  (merged['geometry_survival'] < merged['geometry_survival'].median())

id_vs_geo_df.to_csv(f'{BASE}/outputs/phaseK_identity_vs_geometry.csv', index=False)
print(f'\nIdentity vs geometry saved: {len(id_vs_geo_df)} systems')

# ====================================================
# K4: RECONSTRUCTIVE SELF-CONTINUITY
# ====================================================
print('\n' + '='*70)
print('PHASE K4 — RECONSTRUCTIVE SELF-CONTINUITY')
print('Can systems reconstruct identity after organizational collapse?')
print('='*70)

if recovery_df is not None:
    # Merge recovery data with identity metrics
    rec_merged = recovery_df.merge(id_metrics_df, on=['domain', 'sys_idx'], how='inner', suffixes=('', '_im'))
    
    # For each recoverable CG system, test reconstructability
    recov_systems = rec_merged[rec_merged['recovery_possible'] == 1]
    
    print(f'\nRecoverable CG systems: {len(recov_systems)}')
    
    # Test: do recursive-identity systems reconstruct differently?
    if len(recov_systems) > 0:
        rec_median = recov_systems['recursive_identity_score'].median()
        high_id = recov_systems[recov_systems['recursive_identity_score'] > rec_median]
        low_id = recov_systems[recov_systems['recursive_identity_score'] <= rec_median]
        
        print(f'\n  High recursive identity: {len(high_id)} systems')
        print(f'    Recovery probability: {high_id["recovery_probability"].mean():.3f}')
        print(f'    Recovery steps: {high_id["recovery_steps_mean"].mean():.1f}')
        print(f'    Recovery entropy: {high_id["recovery_entropy"].mean():.3f}')
        
        print(f'\n  Low recursive identity: {len(low_id)} systems')
        print(f'    Recovery probability: {low_id["recovery_probability"].mean():.3f}')
        print(f'    Recovery steps: {low_id["recovery_steps_mean"].mean():.1f}')
        print(f'    Recovery entropy: {low_id["recovery_entropy"].mean():.3f}')
        
        # What predicts reconstruction quality?
        print('\n=== PREDICTORS OF RECONSTRUCTION QUALITY ===')
        for pred in ['recursive_continuity', 'reconstruction_ability', 'org_memory',
                     'closure_persistence', 'trajectory_coherence', 'recursive_identity_score']:
            c, p_val = pearsonr(recov_systems[pred], recov_systems['recovery_probability'])
            print(f'  {pred:35s}: r={c:.4f} p={p_val:.4f}')
    
    # Save full reconstruction data
    rec_merged.to_csv(f'{BASE}/outputs/phaseK_reconstruction.csv', index=False)
    print(f'\nReconstruction analysis saved: {len(rec_merged)} systems')
else:
    print(f'  No H2 recovery data available — skipping K4')
    pd.DataFrame().to_csv(f'{BASE}/outputs/phaseK_reconstruction.csv', index=False)

h3_h4_summary = {
    'phase': 'K3+K4',
    'identity_vs_geometry': {
        'n_total': len(merged),
        'geo_without_id': int(len(geo_without_id)),
        'id_without_geo': int(len(id_without_geo)),
        'both_survive': int(len(both_survive)),
        'correlation': float(corr),
        'best_identity_predictor': str(sorted(
            [(p, pearsonr(merged[p], merged['identity_survival'])[0]) for p in predictors if p in merged.columns],
            key=lambda x: abs(x[1]), reverse=True
        )[0]) if any(p in merged.columns for p in predictors) else None,
    },
    'reconstruction': {
        'n_recoverable': int(len(recov_systems)) if recovery_df is not None else 0,
    },
}
with open(f'{BASE}/summaries/h3_h4_summary.json', 'w') as f:
    json.dump(h3_h4_summary, f, indent=2)
print(f'\nK3+K4 COMPLETE')
