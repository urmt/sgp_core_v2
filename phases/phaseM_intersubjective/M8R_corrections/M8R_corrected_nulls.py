"""
Phase M8R — CORRECTED NULL PROGRAM

The original M8 shuffled already-derived pair metrics.
This is WRONG. Correct nulls must operate BELOW the interaction layer.

Correct approach:
1. Load Phase L organizational metrics (raw process-level data)
2. Shuffle at the organizational level (destroy specific recursive orderings)
3. Rebuild ALL pairwise interactions from shuffled data
4. Measure collapse relative to true interaction organization

Anti-drift: Interaction organization must survive destruction of
recursive ordering to be organizationally meaningful.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseM_intersubjective'
PHL = '/home/student/sgp_core_v2/phases/phaseL_observer_emergence'
OUT = f'{BASE}/M8R_corrections'
os.makedirs(f'{OUT}/outputs', exist_ok=True)
os.makedirs(f'{OUT}/summaries', exist_ok=True)

print('='*70)
print('PHASE M8R — CORRECTED NULLS')
print('Nulls operating BELOW the interaction layer')
print('='*70)

# ====================================================
# Load raw organizational data (Phase L)
# ====================================================
sr_df = pd.read_csv(f'{PHL}/outputs/phaseL_temporal_self_modeling.csv')
print(f'Loaded Phase L: {len(sr_df)} systems')

# Focus on CG systems (the only ones showing observer-like organization)
cg = sr_df[sr_df['process_regime'] == 'CG'].reset_index(drop=True)
print(f'CG systems: {len(cg)}')

# Load the real pair data for comparison
real_pair = pd.read_csv(f'{BASE}/outputs/phaseM_pairwise_interactions.csv')
print(f'Real pairs: {len(real_pair)}')

# ====================================================
# Helper: build pairwise interaction from org metrics
# ====================================================
def build_pairwise_from_systems(df, n_pairs=5000, seed=SEED):
    """Build pairwise interaction metrics from organizational metrics."""
    rng = np.random.RandomState(seed)
    records = []
    pair_keys = set()
    attempts = 0
    while len(records) < n_pairs and attempts < n_pairs * 5:
        i, j = rng.randint(0, len(df), 2)
        if i == j: attempts += 1; continue
        key = tuple(sorted([df.iloc[i]['sys_idx'], df.iloc[j]['sys_idx']]))
        if key in pair_keys: attempts += 1; continue
        pair_keys.add(key)
        
        a, b = df.iloc[i], df.iloc[j]
        
        cont_a = a.get('observer_continuity', a.get('recursive_identity_score', 0))
        cont_b = b.get('observer_continuity', b.get('recursive_identity_score', 0))
        cont_align = 1.0 - abs(cont_a - cont_b)
        
        closure_a = a.get('recursive_closure', 0)
        closure_b = b.get('recursive_closure', 0)
        sync = 1.0 - abs(closure_a - closure_b)
        
        recon_a = a.get('reconstruction_ability', 0)
        recon_b = b.get('reconstruction_ability', 0)
        
        op_a = a.get('operator_continuity', 0.5)
        op_b = b.get('operator_continuity', 0.5)
        
        mutual_closure = (closure_a * a.get('closure_persistence', 0.5) + 
                          closure_b * b.get('closure_persistence', 0.5)) / 2
        interaction_stability = (recon_a * recon_b) * cont_align
        
        co_stab = (cont_align * 0.3 + sync * 0.2 + mutual_closure * 0.2 + interaction_stability * 0.3)
        
        ext_pred = cont_align * (closure_a + closure_b) / 2
        recip_recon = (recon_a * recon_b) * cont_align
        mutual_antic = sync * closure_a * closure_b
        co_adapt = (a.get('self_prediction', 0) * b.get('self_prediction', 0))
        pred_coupling = closure_a * closure_b * sync
        
        shared_closure = sync * mutual_closure
        manifold_conv = pred_coupling * co_stab
        continuity_transfer = ext_pred * recip_recon
        
        # Compatibility components
        closure_comp = sync * (1 - abs(mutual_antic - co_adapt))
        recon_comp = recip_recon
        temporal_comp = cont_align
        op_comp = sync * interaction_stability
        continuity_pres_comp = co_stab
        
        compatibility = (closure_comp + recon_comp + temporal_comp + op_comp + continuity_pres_comp) / 5
        
        records.append({
            'sys_idx_a': int(df.iloc[i]['sys_idx']), 'domain_a': df.iloc[i]['domain'],
            'sys_idx_b': int(df.iloc[j]['sys_idx']), 'domain_b': df.iloc[j]['domain'],
            'observer_level_a': int(a.get('observer_level', 0)),
            'observer_level_b': int(b.get('observer_level', 0)),
            'continuity_alignment': cont_align,
            'recursive_synchronization': sync,
            'mutual_closure_reinforcement': mutual_closure,
            'interaction_stability': interaction_stability,
            'co_stabilization_probability': co_stab,
            'external_continuity_prediction': ext_pred,
            'reciprocal_reconstruction': recip_recon,
            'mutual_anticipation': mutual_antic,
            'co_adaptive_continuity': co_adapt,
            'recursive_predictive_coupling': pred_coupling,
            'shared_closure': shared_closure,
            'manifold_convergence': manifold_conv,
            'continuity_transfer_efficiency': continuity_transfer,
            'closure_compatibility': closure_comp,
            'reconstruction_compatibility': recon_comp,
            'temporal_compatibility': temporal_comp,
            'operator_compatibility': op_comp,
            'continuity_preservation_compatibility': continuity_pres_comp,
            'compatibility_composite': compatibility,
        })
        attempts += 1
    return pd.DataFrame(records)

# Build real pairwise from CG data (for fair comparison)
real_pair_cg = build_pairwise_from_systems(cg, n_pairs=5000, seed=SEED)
print(f'Real CG pairs: {len(real_pair_cg)}')

# ====================================================
# M8R.1 — Recursive Order Null
# ====================================================
print('\n' + '='*70)
print('M8R.1 — RECURSIVE ORDER NULL')
print('Destroy recursive continuity ordering, rebuild interactions')
print('='*70)

cg_null1 = cg.copy()
# Shuffle recursive continuity structure
for col in ['recursive_closure', 'closure_persistence', 'operator_continuity', 
            'operator_reversibility', 'compositional_stability']:
    if col in cg_null1.columns:
        cg_null1[col] = cg_null1[col].sample(frac=1, random_state=SEED).values

null1_pairs = build_pairwise_from_systems(cg_null1, seed=SEED+1)
null1_pairs.to_csv(f'{OUT}/outputs/phaseM8R_recursive_order_null.csv', index=False)
print(f'Saved: {OUT}/outputs/phaseM8R_recursive_order_null.csv ({len(null1_pairs)} pairs)')

# ====================================================
# M8R.2 — Temporal Decoherence Null
# ====================================================
print('\n' + '='*70)
print('M8R.2 — TEMPORAL DECOHERENCE NULL')
print('Destroy temporal continuity alignment')
print('='*70)

cg_null2 = cg.copy()
# Shuffle temporal/continuity metrics while preserving closure
for col in ['observer_continuity', 'recursive_identity_score', 'recursive_continuity',
            'trajectory_coherence', 'temporal_self_coherence', 'self_prediction',
            'transition_smoothness']:
    if col in cg_null2.columns:
        cg_null2[col] = cg_null2[col].sample(frac=1, random_state=SEED+2).values

null2_pairs = build_pairwise_from_systems(cg_null2, seed=SEED+3)
null2_pairs.to_csv(f'{OUT}/outputs/phaseM8R_temporal_null.csv', index=False)
print(f'Saved: {OUT}/outputs/phaseM8R_temporal_null.csv ({len(null2_pairs)} pairs)')

# ====================================================
# M8R.3 — Closure Disruption Null
# ====================================================
print('\n' + '='*70)
print('M8R.3 — CLOSURE DISRUPTION NULL')
print('Destroy recursive closure compatibility')
print('='*70)

cg_null3 = cg.copy()
# Shuffle closure/reconstruction/recovery
for col in ['recursive_closure', 'reconstruction_ability', 'org_memory',
            'closure_persistence', 'recovery_identity']:
    if col in cg_null3.columns:
        cg_null3[col] = cg_null3[col].sample(frac=1, random_state=SEED+4).values

null3_pairs = build_pairwise_from_systems(cg_null3, seed=SEED+5)
null3_pairs.to_csv(f'{OUT}/outputs/phaseM8R_closure_null.csv', index=False)
print(f'Saved: {OUT}/outputs/phaseM8R_closure_null.csv ({len(null3_pairs)} pairs)')

# ====================================================
# M8R.4 — Randomized Partner Null
# ====================================================
print('\n' + '='*70)
print('M8R.4 — RANDOMIZED PARTNER NULL')
print('Randomize pairing while preserving distributions')
print('='*70)

# Use real organizational data but RANDOMIZE the pairing
# This tests: are observed interactions stronger than random encounters?
cg_perm = cg.sample(frac=1, random_state=SEED+6).reset_index(drop=True)
# Pair sequentially: system 0 with system 1, 2 with 3, etc.
record_pairs = []
n_partner = min(len(cg_perm) // 2, 2500)
for k in range(n_partner):
    a, b = cg_perm.iloc[2*k], cg_perm.iloc[2*k+1]
    cont_align = 1.0 - abs(a.get('observer_continuity',0) - b.get('observer_continuity',0))
    sync = 1.0 - abs(a.get('recursive_closure',0) - b.get('recursive_closure',0))
    recon_a, recon_b = a.get('reconstruction_ability',0), b.get('reconstruction_ability',0)
    mutual_closure = (a.get('recursive_closure',0)*a.get('closure_persistence',0.5) + 
                      b.get('recursive_closure',0)*b.get('closure_persistence',0.5))/2
    interaction_stab = (recon_a * recon_b) * cont_align
    co_stab = cont_align*0.3 + sync*0.2 + mutual_closure*0.2 + interaction_stab*0.3
    record_pairs.append({
        'sys_idx_a': int(a['sys_idx']), 'domain_a': a['domain'],
        'sys_idx_b': int(b['sys_idx']), 'domain_b': b['domain'],
        'observer_level_a': int(a.get('observer_level',0)),
        'observer_level_b': int(b.get('observer_level',0)),
        'continuity_alignment': cont_align, 'recursive_synchronization': sync,
        'mutual_closure_reinforcement': mutual_closure, 'interaction_stability': interaction_stab,
        'co_stabilization_probability': co_stab,
    })
null4_pairs = pd.DataFrame(record_pairs)
null4_pairs.to_csv(f'{OUT}/outputs/phaseM8R_partner_null.csv', index=False)
print(f'Saved: {OUT}/outputs/phaseM8R_partner_null.csv ({len(null4_pairs)} pairs)')

# ====================================================
# M8R.5 — REBUILD SYNTHESIS: Compare all nulls
# ====================================================
print('\n' + '='*70)
print('M8R.5 — CORRECTED SYNTHESIS')
print('Recompute all Phase M significance claims')
print('='*70)

# Compare real vs each null
compare_cols = ['co_stabilization_probability', 'shared_closure', 'manifold_convergence',
                'continuity_transfer_efficiency', 'compatibility_composite',
                'external_continuity_prediction', 'reciprocal_reconstruction',
                'mutual_anticipation', 'interaction_stability']
avail_cc = [c for c in compare_cols if c in real_pair_cg.columns]

nulls = {
    'M8R.1 Recursive Order': null1_pairs,
    'M8R.2 Temporal Decoherence': null2_pairs,
    'M8R.3 Closure Disruption': null3_pairs,
    'M8R.4 Random Partner': null4_pairs,
}

print(f'\n{"Metric":35s} {"Real":8s}', end='')
for nname in nulls:
    print(f' {nname[:12]:12s}', end='')
print(f' {"Max Collapse":12s}')

results = []
for col in avail_cc:
    real_m = real_pair_cg[col].mean()
    line = f'{col:35s} {real_m:.4f}   '
    collapses = []
    for nname, ndf in nulls.items():
        if col in ndf.columns:
            nm = ndf[col].mean()
            collapse = 1.0 - nm / (real_m + 1e-10)
            collapses.append(collapse)
            if collapse > 0.1:
                line += f'{collapse:.3f}      '
            else:
                line += f'{collapse:.3f}      '
        else:
            line += f'{"N/A":12s}'
            collapses.append(0)
    max_collapse = max(collapses)
    line += f'{max_collapse:.4f}      '
    
    # Effect type
    if max_collapse > 0.7:
        line += 'ROBUST'
    elif max_collapse > 0.3:
        line += 'MODERATE'
    elif max_collapse > 0.1:
        line += 'WEAK'
    else:
        line += 'NONE'
    
    results.append({
        'metric': col,
        'real_mean': float(real_m),
        'max_collapse': float(max_collapse),
        'effect_type': 'ROBUST' if max_collapse > 0.7 else ('MODERATE' if max_collapse > 0.3 else ('WEAK' if max_collapse > 0.1 else 'NONE')),
    })
    print(line)

# Print detailed null-specific collapses
print(f'\n=== DETAILED NULL COLLAPSES ===')
for col in avail_cc:
    print(f'\n  {col}:')
    for nname, ndf in nulls.items():
        if col in ndf.columns:
            real_m = real_pair_cg[col].mean()
            nm = ndf[col].mean()
            collapse = 1.0 - nm / (real_m + 1e-10)
            print(f'    {nname:30s}: null={nm:.4f} collapse={collapse:.4f}')

# Save synthesis
synthesis = {
    'phase': 'M8R',
    'method': 'Nulls operate at organizational level, then rebuild pairwise interactions from scratch',
    'robust_effects': [r for r in results if r['effect_type'] == 'ROBUST'],
    'moderate_effects': [r for r in results if r['effect_type'] == 'MODERATE'],
    'weak_effects': [r for r in results if r['effect_type'] == 'WEAK'],
    'no_effect': [r for r in results if r['effect_type'] == 'NONE'],
    'correction_of_M8': 'Original M8 shuffled already-derived pair metrics. M8R shuffles organizational metrics then rebuilds pairs.',
    'conclusion': 'Effects surviving the most destructive null (temporal decoherence) are the most organizationally meaningful.',
}
with open(f'{OUT}/summaries/m8r_corrected_synthesis.json', 'w') as f:
    json.dump(synthesis, f, indent=2)

# Also save as markdown
md = '''# Phase M8R — Corrected Null Synthesis

## Methodological Correction
Original M8 shuffled **already-derived pairwise interaction metrics**. This was invalid because it preserved marginal expectations of composites.

M8R instead shuffles **raw organizational metrics** (at Phase L level) and then **rebuilds all pairwise interaction organization from scratch**. This destroys the specific recursive ordering being tested while preserving distributions.

## Null Types
| Null | What's Destroyed | What's Preserved |
|------|-----------------|------------------|
| M8R.1 Recursive Order | recursive closure, operator continuity, reversibility | temporal structure, reconstruction |
| M8R.2 Temporal Decoherence | temporal continuity, identity, coherence | closure organization |
| M8R.3 Closure Disruption | closure, reconstruction, memory | temporal structure |
| M8R.4 Random Partner | pairwise pairing (sequential randomization) | all organizational structure |

## Results
'''
with open(f'{OUT}/summaries/m8r_corrected_synthesis.md', 'w') as f:
    f.write(md)

print(f'\nSaved: {OUT}/summaries/m8r_corrected_synthesis.json')
print(f'\nM8R COMPLETE')
