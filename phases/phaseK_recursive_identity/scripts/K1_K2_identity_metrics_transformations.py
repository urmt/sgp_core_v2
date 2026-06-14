"""
Phase K1+K2 — Recursive Identity Metrics + Identity Under Transformation.

CRITICAL DISTINCTION:
  Statistical persistence (crystal) — stays same because nothing changes.
  Recursive identity persistence (mind) — maintains self THROUGH change.

Anti-drift check: Am I measuring identity-through-transformation, 
or just similarity-after-transformation?
"""
import numpy as np, pandas as pd, os, json, warnings
from sklearn.preprocessing import StandardScaler, MinMaxScaler
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseK_recursive_identity'
PC = '/home/student/sgp_core_v2/phases/phaseC'
PE = '/home/student/sgp_core_v2/phases/phaseE'
PG = '/home/student/sgp_core_v2/phases/phaseG'
PI = '/home/student/sgp_core_v2/phases/phaseI_operator_algebra'
PH2 = '/home/student/sgp_core_v2/phases/phaseH2_process'
PJ = '/home/student/sgp_core_v2/phases/phaseJ_invariants'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

print('='*70)
print('PHASE K1 — RECURSIVE IDENTITY METRICS')
print('Distinguishing statistical persistence from recursive identity')
print('='*70)

# ─── Load all available data ───
df = pd.read_csv(f'{PC}/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
curv = pd.read_csv(f'{PE}/processed/curvature_metrics.csv')
poss = pd.read_csv(f'{PE}/processed/possibility_metrics.csv')
phaseG = pd.read_csv(f'{PG}/processed/coherence_fertility_phase_space.csv')
merged = df.merge(phaseG, on=['sys_idx','domain']).merge(curv, on=['sys_idx','domain']).merge(poss, on=['sys_idx','domain'])
merged['process_regime'] = merged['region'].map({'constrained_generative':'CG','rigid_coherence':'RG',
                                                   'chaotic_fertility':'CH','collapse':'CL'})
domains = sorted(merged['domain'].unique())

# Load Phase I operator transition geometry
trans_geo = pd.read_csv(f'{PI}/outputs/phaseI_transition_geometry.csv')

# Load H2 persistence and recovery
persist_df = pd.read_csv(f'{PH2}/outputs/persistence_metrics.csv') if os.path.exists(f'{PH2}/outputs/persistence_metrics.csv') else None
recovery_df = pd.read_csv(f'{PH2}/outputs/recovery_metrics.csv') if os.path.exists(f'{PH2}/outputs/recovery_metrics.csv') else None

# Load J invariants
inv_df = pd.read_csv(f'{PJ}/outputs/phaseJ_transform_invariants.csv')
conserv_df = pd.read_csv(f'{PJ}/outputs/phaseJ_conservation_collapse.csv')

STAB_COLS = ['stability_return_time','stability_recovery_rate','stability_final_dev','stability_max_dev']
FERT_COLS = ['fertility_state_diversity','fertility_novelty_rate','fertility_state_coverage','fertility_transition_entropy']

# ====================================================
# K1: RECURSIVE IDENTITY METRICS
# ====================================================
# For each SYSTEM, construct 8 recursive identity metrics.

identity_metrics = []

for domain in domains:
    dm = merged[merged['domain'] == domain].copy().reset_index(drop=True)
    tg = trans_geo[trans_geo['domain'] == domain] if len(trans_geo) > 0 else None
    
    # H2 data for this domain
    p_df = persist_df[persist_df['domain'] == domain] if persist_df is not None else None
    r_df = recovery_df[recovery_df['domain'] == domain] if recovery_df is not None else None
    
    for i in range(len(dm)):
        sys = dm.iloc[i]
        sys_idx_val = int(sys['sys_idx'])
        regime = sys['process_regime']
        
        # Get corresponding data from other sources
        tg_row = tg[tg['sys_idx'] == sys_idx_val] if tg is not None else None
        p_row = p_df[p_df['sys_idx'] == sys_idx_val] if p_df is not None else None
        r_row = r_df[r_df['sys_idx'] == sys_idx_val] if r_df is not None else None
        
        # ─── Metric 1: Recursive Continuity ───
        # How consistent is the operator identity across neighboring states?
        # From trans_geo: operator_continuity (cross-domain)
        if tg_row is not None and len(tg_row) > 0:
            recursive_continuity = float(tg_row['operator_continuity'].iloc[0])
        else:
            recursive_continuity = 0.5
        
        # ─── Metric 2: Self-Reconstruction Ability ───
        # Can system return to CG after forced collapse?
        # From recovery: recovery_probability (0-1)
        if r_row is not None and len(r_row) > 0:
            recov_possible = int(r_row['recovery_possible'].iloc[0])
            if recov_possible == 1:
                reconstruction_ability = float(r_row['recovery_probability'].iloc[0])
            elif recov_possible == -1:
                reconstruction_ability = 0.0  # no collapse neighbor available
            else:
                reconstruction_ability = 0.0  # can't recover
        else:
            reconstruction_ability = 0.0
        
        # ─── Metric 3: Organizational Memory ───
        # Stability-fertility coupling measures how tightly the system's
        # organizational properties are bound together.
        # High coupling = changes in one property predict changes in others = memory.
        org_memory = float(sys['poss_stability_fertility_coupling'])
        
        # ─── Metric 4: Transition Continuity ───
        # How smooth are the system's transitions between organizational states?
        transition_continuity = float(sys['fertility']) * float(sys['coherence'])
        # Also use transition_smoothness from trans_geo
        if tg_row is not None and len(tg_row) > 0:
            transition_smoothness = float(tg_row['transition_smoothness'].iloc[0])
        else:
            transition_smoothness = 0.5
        
        # ─── Metric 5: Closure Persistence ───
        # Does recursive closure (reversibility) persist?
        closure_persistence = float(sys['poss_stability_fertility_coupling'])
        
        # ─── Metric 6: Adaptive Continuity ───
        # Can the system adjust without losing identity?
        # High persistence tolerance + high recovery = adaptive continuity
        if p_row is not None and len(p_row) > 0:
            persistence_tolerance = float(p_row['perturbation_tolerance'].iloc[0])
        else:
            persistence_tolerance = 0.0
        # If tolerance is inf, treat as very high
        if np.isinf(persistence_tolerance) or persistence_tolerance > 100:
            persistence_tolerance = 10.0
        adaptive_continuity = persistence_tolerance * reconstruction_ability
        
        # ─── Metric 7: Perturbation Recovery Identity ───
        # After recovery, does the system return to similar organization?
        # Low recovery steps = fast return = strong recovery identity
        if r_row is not None and len(r_row) > 0 and recov_possible == 1:
            recovery_speed = max(0, 1.0 - float(r_row['recovery_steps_mean'].iloc[0]) / 100.0)
            recovery_quality = float(r_row['recovery_probability'].iloc[0])
            recovery_identity = recovery_quality * recovery_speed
        else:
            recovery_identity = 0.0
        
        # ─── Metric 8: Process Trajectory Coherence ───
        # How coherent is the system's path through organizational space?
        # Low persistence variance = coherent trajectory
        if p_row is not None and len(p_row) > 0:
            persistence_half_life = float(p_row['persistence_half_life'].iloc[0])
            trajectory_coherence = min(1.0, persistence_half_life / 50.0)  # normalize
        else:
            trajectory_coherence = 0.0
        
        # ─── COMPOSITE: Recursive Identity Score ───
        # True recursive identity = system that maintains itself THROUGH change:
        # High reconstruction_ability + high org_memory + high trajectory_coherence
        recursive_identity_score = (
            0.25 * reconstruction_ability + 
            0.25 * org_memory + 
            0.20 * recursive_continuity + 
            0.15 * trajectory_coherence + 
            0.15 * recovery_identity
        )
        
        identity_metrics.append({
            'domain': domain,
            'sys_idx': sys_idx_val,
            'process_regime': regime,
            'recursive_continuity': round(recursive_continuity, 4),
            'reconstruction_ability': round(reconstruction_ability, 4),
            'org_memory': round(org_memory, 4),
            'transition_continuity': round(transition_continuity, 6),
            'transition_smoothness': round(transition_smoothness, 4),
            'closure_persistence': round(closure_persistence, 4),
            'adaptive_continuity': round(adaptive_continuity, 4),
            'recovery_identity': round(recovery_identity, 4),
            'trajectory_coherence': round(trajectory_coherence, 4),
            'recursive_identity_score': round(recursive_identity_score, 4),
        })

id_metrics_df = pd.DataFrame(identity_metrics)
id_metrics_df.to_csv(f'{BASE}/outputs/phaseK_identity_metrics.csv', index=False)
print(f'Recursive identity metrics: {len(id_metrics_df)} systems, 8 metrics + composite')

# ─── Distinguish statistical from recursive persistence ───
# Statistical: high trajectory_coherence but low reconstruction_ability
# Recursive: high trajectory_coherence AND high reconstruction_ability
cg_systems = id_metrics_df[id_metrics_df['process_regime'] == 'CG']

statistical_cg = cg_systems[
    (cg_systems['trajectory_coherence'] > np.median(cg_systems['trajectory_coherence'])) &
    (cg_systems['reconstruction_ability'] < np.median(cg_systems['reconstruction_ability']))
]
recursive_cg = cg_systems[
    (cg_systems['trajectory_coherence'] > np.median(cg_systems['trajectory_coherence'])) &
    (cg_systems['reconstruction_ability'] > np.median(cg_systems['reconstruction_ability']))
]

print(f'\n=== STATISTICAL vs RECURSIVE IDENTITY ===')
print(f'CG systems total: {len(cg_systems)}')
print(f'Statistical persistence (crystal-like): {len(statistical_cg)}')
print(f'Recursive identity persistence (mind-like): {len(recursive_cg)}')
print(f'Ratio recursive/statistical: {len(recursive_cg)/max(len(statistical_cg),1):.2f}')

# Per-domain breakdown
print('\nPer-domain identity types:')
for domain in domains:
    cgd = cg_systems[cg_systems['domain'] == domain]
    if len(cgd) == 0:
        print(f'  {domain:25s}: no CG systems')
        continue
    sc = len(statistical_cg[statistical_cg['domain'] == domain])
    rc = len(recursive_cg[recursive_cg['domain'] == domain])
    print(f'  {domain:25s}: {len(cgd):3d} CG — {sc:3d} statistical, {rc:3d} recursive ({100*rc/len(cgd):.0f}%)')

# ====================================================
# K2: IDENTITY UNDER TRANSFORMATION
# ====================================================
print('\n' + '='*70)
print('PHASE K2 — IDENTITY UNDER TRANSFORMATION')
print('Which properties preserve recursive identity through transformation?')
print('='*70)

# Use Phase J invariant data to test which properties predict identity retention
# Identity retention = ability to maintain identity through composition

# For each composition, track identity-related metrics
comp_df = pd.read_csv(f'{PI}/outputs/phaseI_composition_results.csv')
identity_trans_records = []

for _, r in comp_df.iterrows():
    d1, d2 = r['domain_A'], r['domain_B']
    
    # Compute identity retention for this composition
    # Using domain-level averages from id_metrics_df
    id1 = id_metrics_df[id_metrics_df['domain'] == d1]
    id2 = id_metrics_df[id_metrics_df['domain'] == d2]
    
    if len(id1) == 0 or len(id2) == 0:
        continue
    
    # Compare identity properties across the composition
    for prop in ['recursive_continuity', 'reconstruction_ability', 'org_memory',
                 'transition_smoothness', 'closure_persistence', 'trajectory_coherence',
                 'recursive_identity_score']:
        v1 = id1[prop].mean()
        v2 = id2[prop].mean()
        comp_val = (v1 + v2) / 2
        
        # Identity retention = how much does composition preserve each property?
        identity_retention = 1 - abs(v1 - v2) / max(max(v1, v2, 0.001), 0.001)
        identity_retention = max(0, min(1, identity_retention))
        
        identity_trans_records.append({
            'domain_A': d1, 'domain_B': d2,
            'operator_A': r['operator_A'], 'operator_B': r['operator_B'],
            'property': prop,
            'val_A': round(v1, 4),
            'val_B': round(v2, 4),
            'identity_retention': round(identity_retention, 4),
        })

id_trans_df = pd.DataFrame(identity_trans_records)
id_trans_df.to_csv(f'{BASE}/outputs/phaseK_identity_transformations.csv', index=False)
print(f'\nIdentity transformations saved: {len(id_trans_df)}')

# Which properties retain identity best under transformation?
print('\n=== IDENTITY RETENTION UNDER TRANSFORMATION ===')
prop_retention = id_trans_df.groupby('property')['identity_retention'].agg(['mean','std']).sort_values('mean', ascending=False)
for prop, row in prop_retention.iterrows():
    print(f'  {prop:35s}: retention={row["mean"]:.4f}±{row["std"]:.4f}')

# Which operator compositions best preserve identity?
print('\n=== COMPOSITIONS PRESERVING RECURSIVE IDENTITY (top 5) ===')
id_score_ret = id_trans_df[id_trans_df['property'] == 'recursive_identity_score'].sort_values('identity_retention', ascending=False)
for _, r in id_score_ret.head(5).iterrows():
    print(f'  {r["domain_A"]:20s} + {r["domain_B"]:20s}: identity_retention={r["identity_retention"]:.4f}')

print('\n=== WORST COMPOSITIONS FOR RECURSIVE IDENTITY (bottom 5) ===')
for _, r in id_score_ret.tail(5).iterrows():
    print(f'  {r["domain_A"]:20s} + {r["domain_B"]:20s}: identity_retention={r["identity_retention"]:.4f}')

h1_h2_summary = {
    'phase': 'K1+K2',
    'recursive_identity_distribution': {
        'total_cg': int(len(cg_systems)),
        'statistical_persistence': int(len(statistical_cg)),
        'recursive_identity': int(len(recursive_cg)),
        'ratio': round(len(recursive_cg) / max(len(statistical_cg), 1), 2),
    },
    'identity_retention_ranking': {str(k): float(v['mean']) for k, v in prop_retention.iterrows()},
    'best_identity_preserver': str(id_score_ret.iloc[0][['domain_A','domain_B']].to_dict()) if len(id_score_ret) > 0 else None,
}
with open(f'{BASE}/summaries/h1_h2_summary.json', 'w') as f:
    json.dump(h1_h2_summary, f, indent=2)
print(f'\nK1+K2 COMPLETE')
