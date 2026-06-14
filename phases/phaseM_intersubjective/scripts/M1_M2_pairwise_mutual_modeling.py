"""
Phase M1+M2 — PAIRWISE CONTINUITY INTERACTION + MUTUAL MODELING

M1: Do some recursive continuities stabilize each other?
M2: Can recursive systems internally model other recursive continuities?

The primary object is recursive continuity interaction processes.
NOT entities. NOT agents. NOT minds.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseM_intersubjective'
PHL = '/home/student/sgp_core_v2/phases/phaseL_observer_emergence'
PHI = '/home/student/sgp_core_v2/phases/phaseI_operator_algebra'
os.makedirs(f'{BASE}/outputs', exist_ok=True)
os.makedirs(f'{BASE}/summaries', exist_ok=True)

print('='*70)
print('PHASE M1 — PAIRWISE CONTINUITY INTERACTION')
print('Do recursive continuities stabilize each other?')
print('='*70)

# Load observer-like systems from Phase L
sr_df = pd.read_csv(f'{PHL}/outputs/phaseL_temporal_self_modeling.csv')
print(f'Loaded: {len(sr_df)} systems')

# Focus on CG systems with observer-level data
obs = sr_df[sr_df['observer_level'] >= 2].copy() if 'observer_level' in sr_df.columns else sr_df[sr_df['process_regime'] == 'CG'].copy()
print(f'Observer-like systems: {len(obs)}')
# If too few Level 3, use CG systems with high self-reference
if len(obs) < 50:
    obs = sr_df[sr_df['process_regime'] == 'CG'].nlargest(100, 'self_reference_composite')
    print(f'Using top-100 CG by self-reference: {len(obs)}')

# ====================================================
# Construct pairwise interactions
# ====================================================
N_PAIRS = min(5000, len(obs)**2 // 2)
print(f'\nSampling {N_PAIRS} pairwise interactions...')

pair_records = []
pair_keys = set()
attempts = 0
while len(pair_records) < N_PAIRS and attempts < N_PAIRS * 3:
    i, j = np.random.randint(0, len(obs), 2)
    if i == j: attempts += 1; continue
    key = tuple(sorted([obs.iloc[i]['sys_idx'], obs.iloc[j]['sys_idx']]))
    if key in pair_keys: attempts += 1; continue
    pair_keys.add(key)
    
    a, b = obs.iloc[i], obs.iloc[j]
    
    # --- Continuity alignment ---
    # How well do their continuity patterns match?
    cont_a = a.get('observer_continuity', a.get('recursive_identity_score', 0))
    cont_b = b.get('observer_continuity', b.get('recursive_identity_score', 0))
    cont_align = 1.0 - abs(cont_a - cont_b)
    
    # --- Recursive synchronization ---
    # Do their closure structures align?
    closure_a = a.get('recursive_closure', 0)
    closure_b = b.get('recursive_closure', 0)
    sync = 1.0 - abs(closure_a - closure_b)
    
    # --- Mutual closure reinforcement ---
    # Does each system's closure support the other?
    # Simulated as: combined closure effect under interaction
    mutual_closure = (closure_a * a.get('closure_persistence', 0.5) + 
                      closure_b * b.get('closure_persistence', 0.5)) / 2
    
    # --- Interaction stability ---
    # Combined reconstruction ability + alignment
    recon_a = a.get('reconstruction_ability', 0)
    recon_b = b.get('reconstruction_ability', 0)
    combo_recon = recon_a * recon_b  # Both must reconstruct
    interaction_stability = combo_recon * cont_align
    
    # --- Perturbation sharing ---
    # If one is perturbed, can the other help stabilize?
    # = combined recovery probability
    rec_a = a.get('recovery_probability', recon_a)
    rec_b = b.get('recovery_probability', recon_b)
    if isinstance(rec_a, str) or np.isnan(float(rec_a)) if not isinstance(rec_a, str) else True:
        rec_a = recon_a
    if isinstance(rec_b, str) or np.isnan(float(rec_b)) if not isinstance(rec_b, str) else True:
        rec_b = recon_b
    rec_a = float(rec_a) if not isinstance(rec_a, str) else recon_a
    rec_b = float(rec_b) if not isinstance(rec_b, str) else recon_b
    pert_sharing = (rec_a + rec_b) / 2
    
    # --- Recursive continuity interference ---
    # If closures are incompatible, interaction degrades both
    # = 1 - |difference in operator structure|
    op_a = a.get('operator_continuity', 0.5)
    op_b = b.get('operator_continuity', 0.5)
    interference = 1.0 - abs(op_a - op_b)
    # If both have high operator continuity but different closure, interference is negative
    if abs(closure_a - closure_b) > 0.5 and op_a > 0.5 and op_b > 0.5:
        interference *= 0.3  # Strong incompatibility penalty
    
    # --- Co-stabilization probability ---
    # How likely are they to stabilize each other's continuity?
    co_stab = (cont_align * 0.3 + sync * 0.2 + mutual_closure * 0.2 + 
               interaction_stability * 0.3)
    
    # --- M2: Mutual modeling metrics ---
    
    # External continuity prediction
    # Can A predict B's continuity?
    ext_pred_a = cont_align * closure_a  # A's closure helps it predict B
    ext_pred_b = cont_align * closure_b  # B's closure helps it predict A
    ext_pred = (ext_pred_a + ext_pred_b) / 2
    
    # Reciprocal reconstruction
    # Can A help B reconstruct after perturbation?
    recip_recon = combo_recon * cont_align
    
    # Mutual anticipation
    # Does alignment allow anticipation?
    mutual_anticipation = sync * closure_a * closure_b
    
    # Co-adaptive continuity
    # Can both adapt together?
    co_adaptive = (a.get('adaptive_continuity', a.get('self_prediction', 0)) * 
                   b.get('adaptive_continuity', b.get('self_prediction', 0)))
    
    # Recursive predictive coupling
    # Do their recursive structures enable mutual prediction?
    pred_coupling = closure_a * closure_b * sync
    
    pair_records.append({
        'sys_idx_a': int(a['sys_idx']), 'domain_a': a['domain'],
        'sys_idx_b': int(b['sys_idx']), 'domain_b': b['domain'],
        'process_regime_a': a['process_regime'], 'process_regime_b': b['process_regime'],
        'observer_level_a': int(a.get('observer_level', 0)),
        'observer_level_b': int(b.get('observer_level', 0)),
        # M1 metrics
        'continuity_alignment': cont_align,
        'recursive_synchronization': sync,
        'mutual_closure_reinforcement': mutual_closure,
        'interaction_stability': interaction_stability,
        'perturbation_sharing': pert_sharing,
        'recursive_interference': interference,
        'co_stabilization_probability': co_stab,
        # M2 metrics
        'external_continuity_prediction': ext_pred,
        'reciprocal_reconstruction': recip_recon,
        'mutual_anticipation': mutual_anticipation,
        'co_adaptive_continuity': co_adaptive,
        'recursive_predictive_coupling': pred_coupling,
    })
    attempts += 1

pair_df = pd.DataFrame(pair_records)
print(f'Generated {len(pair_df)} unique pairwise interactions')

# ====================================================
# ANALYSIS
# ====================================================

# M1: Do some continuities stabilize each other?
print(f'\n=== M1: PAIRWISE INTERACTION ANALYSIS ===')
print(f'  Mean continuity_alignment:          {pair_df["continuity_alignment"].mean():.4f}')
print(f'  Mean recursive_synchronization:     {pair_df["recursive_synchronization"].mean():.4f}')
print(f'  Mean mutual_closure_reinforcement:  {pair_df["mutual_closure_reinforcement"].mean():.4f}')
print(f'  Mean interaction_stability:         {pair_df["interaction_stability"].mean():.4f}')
print(f'  Mean perturbation_sharing:          {pair_df["perturbation_sharing"].mean():.4f}')
print(f'  Mean recursive_interference:        {pair_df["recursive_interference"].mean():.4f}')
print(f'  Mean co_stabilization_probability:  {pair_df["co_stabilization_probability"].mean():.4f}')

# Compare same-domain vs cross-domain interactions
same_domain = pair_df[pair_df['domain_a'] == pair_df['domain_b']]
cross_domain = pair_df[pair_df['domain_a'] != pair_df['domain_b']]
print(f'\n  Same-domain pairs: {len(same_domain)}')
print(f'    Co-stabilization: {same_domain["co_stabilization_probability"].mean():.4f}')
print(f'  Cross-domain pairs: {len(cross_domain)}')
print(f'    Co-stabilization: {cross_domain["co_stabilization_probability"].mean():.4f}')

# Observer Level 3 vs Level 0 interactions
if 'observer_level_a' in pair_df.columns:
    high_high = pair_df[(pair_df['observer_level_a'] >= 2) & (pair_df['observer_level_b'] >= 2)]
    low_low = pair_df[(pair_df['observer_level_a'] < 2) & (pair_df['observer_level_b'] < 2)]
    if len(high_high) > 0 and len(low_low) > 0:
        print(f'\n  High-high pairs: {len(high_high)} — co-stab={high_high["co_stabilization_probability"].mean():.4f}')
        print(f'  Low-low pairs: {len(low_low)} — co-stab={low_low["co_stabilization_probability"].mean():.4f}')

# What predicts co-stabilization?
print(f'\n=== WHAT PREDICTS CO-STABILIZATION? ===')
preds = ['continuity_alignment', 'recursive_synchronization', 'mutual_closure_reinforcement',
         'interaction_stability', 'recursive_interference']
for col in preds:
    if col in pair_df.columns:
        c, p = pearsonr(pair_df[col], pair_df['co_stabilization_probability'])
        print(f'  {col:40s}: r={c:.4f} p={p:.4e}')

# ====================================================
# M2: Mutual modeling
# ====================================================
print(f'\n' + '='*70)
print('PHASE M2 — MUTUAL MODELING')
print('Can recursive systems internally model other recursive continuities?')
print('='*70)

print(f'\n=== M2: MUTUAL MODELING ANALYSIS ===')
print(f'  Mean external_continuity_prediction:  {pair_df["external_continuity_prediction"].mean():.4f}')
print(f'  Mean reciprocal_reconstruction:       {pair_df["reciprocal_reconstruction"].mean():.4f}')
print(f'  Mean mutual_anticipation:             {pair_df["mutual_anticipation"].mean():.4f}')
print(f'  Mean co_adaptive_continuity:          {pair_df["co_adaptive_continuity"].mean():.4f}')
print(f'  Mean recursive_predictive_coupling:   {pair_df["recursive_predictive_coupling"].mean():.4f}')

# Composite mutual modeling score
mm_cols = ['external_continuity_prediction', 'reciprocal_reconstruction', 
           'mutual_anticipation', 'co_adaptive_continuity', 'recursive_predictive_coupling']
for col in mm_cols:
    pair_df[f'{col}_norm'] = (pair_df[col] - pair_df[col].min()) / (pair_df[col].max() - pair_df[col].min() + 1e-10)
pair_df['mutual_modeling_composite'] = pair_df[[f'{c}_norm' for c in mm_cols]].mean(axis=1)

print(f'\n  Mutual modeling composite (mean): {pair_df["mutual_modeling_composite"].mean():.4f}')

# When does mutual modeling emerge?
print(f'\n=== WHEN DOES MUTUAL MODELING EMERGE? ===')
for col in ['continuity_alignment', 'recursive_synchronization', 'interaction_stability',
            'co_stabilization_probability']:
    if col in pair_df.columns:
        c, p = pearsonr(pair_df[col], pair_df['mutual_modeling_composite'])
        print(f'  {col:40s}: r={c:.4f} p={p:.4e}')

# Save M1+M2
pair_df.to_csv(f'{BASE}/outputs/phaseM_pairwise_interactions.csv', index=False)
print(f'\nSaved: phaseM_pairwise_interactions.csv ({len(pair_df)} pairs)')

# Save M2-specific output
mm_cols_save = mm_cols + ['mutual_modeling_composite'] + \
    [f'{c}_norm' for c in mm_cols] + \
    ['sys_idx_a', 'domain_a', 'sys_idx_b', 'domain_b', 'process_regime_a', 'process_regime_b',
     'observer_level_a', 'observer_level_b', 'co_stabilization_probability', 'continuity_alignment']
mm_save_cols = [c for c in mm_cols_save if c in pair_df.columns]
pair_df[mm_save_cols].to_csv(f'{BASE}/outputs/phaseM_mutual_modeling.csv', index=False)
print(f'Saved: phaseM_mutual_modeling.csv')

# Summaries
m1_summary = {
    'phase': 'M1',
    'n_pairs': len(pair_df),
    'mean_co_stabilization': float(pair_df['co_stabilization_probability'].mean()),
    'same_domain_co_stab': float(same_domain['co_stabilization_probability'].mean()) if len(same_domain) > 0 else 0,
    'cross_domain_co_stab': float(cross_domain['co_stabilization_probability'].mean()) if len(cross_domain) > 0 else 0,
    'best_predictor': str(sorted(
        [(col, pearsonr(pair_df[col], pair_df['co_stabilization_probability'])[0]) for col in preds if col in pair_df.columns],
        key=lambda x: abs(x[1]), reverse=True
    )[0]),
}
m2_summary = {
    'phase': 'M2',
    'mean_mutual_modeling': float(pair_df['mutual_modeling_composite'].mean()),
    'mean_external_prediction': float(pair_df['external_continuity_prediction'].mean()),
    'mean_reciprocal_reconstruction': float(pair_df['reciprocal_reconstruction'].mean()),
}
with open(f'{BASE}/summaries/m1_summary.json', 'w') as f:
    json.dump(m1_summary, f, indent=2)
with open(f'{BASE}/summaries/m2_summary.json', 'w') as f:
    json.dump(m2_summary, f, indent=2)

print(f'\nM1+M2 COMPLETE')
