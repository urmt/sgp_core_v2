"""
Phase Q1+Q2 — CANDIDATE INVARIANT EXTRACTION + TRAJECTORY/DISTRIBUTION SPLIT

Q1: Extract candidate invariants from all prior phases (K→P).
Q2: Separate trajectory-dependent from distribution-dependent properties.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')

BASE = '/home/student/sgp_core_v2/phases/phaseQ_recursive_invariants'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

# ====================================================
# LOAD DATA FROM ALL PHASES
# ====================================================
print('='*70)
print('PHASE Q1 — CANDIDATE INVARIANT EXTRACTION')
print('='*70)

data_sources = {}

# Phase K
try:
    k_id = pd.read_csv(f'{BASE}/../phaseK_recursive_identity/outputs/phaseK_identity_metrics.csv')
    k_vg = pd.read_csv(f'{BASE}/../phaseK_recursive_identity/outputs/phaseK_identity_vs_geometry.csv')
    k_null = pd.read_csv(f'{BASE}/../phaseK_recursive_identity/outputs/phaseK_null_baseline.csv')
    data_sources['K'] = {'identity': k_id, 'geometry': k_vg, 'null': k_null}
    print(f'  Phase K: {len(k_id)} identity metrics, {len(k_vg)} geometry, {len(k_null)} null')
except Exception as e: print(f'  Phase K: NOT FOUND ({e})')

# Phase N
try:
    n_tax = pd.read_csv(f'{BASE}/../phaseN_dynamical_coupling/outputs/phaseN_coupling_taxonomy.csv')
    n_null = pd.read_csv(f'{BASE}/../phaseN_dynamical_coupling/outputs/phaseN_dynamical_nulls.csv')
    n_fail = pd.read_csv(f'{BASE}/../phaseN_dynamical_coupling/outputs/phaseN_failure_modes.csv')
    data_sources['N'] = {'taxonomy': n_tax, 'null': n_null, 'failure': n_fail}
    print(f'  Phase N: {len(n_tax)} taxonomy, {len(n_null)} nulls, {len(n_fail)} failures')
except Exception as e: print(f'  Phase N: NOT FOUND ({e})')

# Phase O
try:
    o_cont = pd.read_csv(f'{BASE}/../phaseO_shared_recursive_identity/outputs/phaseO_shared_continuity.csv')
    o_closure = pd.read_csv(f'{BASE}/../phaseO_shared_recursive_identity/outputs/phaseO_collective_closure.csv')
    o_stable = pd.read_csv(f'{BASE}/../phaseO_shared_recursive_identity/outputs/phaseO_higher_order_stabilization.csv')
    o_null = pd.read_csv(f'{BASE}/../phaseO_shared_recursive_identity/outputs/phaseO_nulls.csv')
    data_sources['O'] = {'continuity': o_cont, 'closure': o_closure, 'stable': o_stable, 'null': o_null}
    print(f'  Phase O: {len(o_cont)} continuity, {len(o_closure)} closure, {len(o_stable)} stable, {len(o_null)} nulls')
except Exception as e: print(f'  Phase O: NOT FOUND ({e})')

# Phase P
try:
    p_cont = pd.read_csv(f'{BASE}/../phaseP_transition_persistence/outputs/phaseP_transition_continuity.csv')
    p_recon = pd.read_csv(f'{BASE}/../phaseP_transition_persistence/outputs/phaseP_reconstruction.csv')
    p_shared = pd.read_csv(f'{BASE}/../phaseP_transition_persistence/outputs/phaseP_shared_transition.csv')
    p_null = pd.read_csv(f'{BASE}/../phaseP_transition_persistence/outputs/phaseP_nulls.csv')
    data_sources['P'] = {'continuity': p_cont, 'recon': p_recon, 'shared': p_shared, 'null': p_null}
    print(f'  Phase P: {len(p_cont)} continuity, {len(p_recon)} recon, {len(p_shared)} shared, {len(p_null)} nulls')
except Exception as e: print(f'  Phase P: NOT FOUND ({e})')

print(f'\n  Total data sources: {len(data_sources)} phases')

# ====================================================
# Q1: CANDIDATE INVARIANT EXTRACTION
# ====================================================
print(f'\n=== CANDIDATE INVARIANTS ===')

candidates = []

# From Phase N: null survival (trajectory vs distribution)
if 'N' in data_sources:
    nd = data_sources['N']['taxonomy']
    nn = data_sources['N']['null']
    # Get real values from taxonomy data
    real_sync = float(nd['final_synchronization'].mean()) if 'final_synchronization' in nd.columns else None
    real_closure_corr = float(nd['closure_correlation'].mean()) if 'closure_correlation' in nd.columns else None
    null_sync = float(nn['null_final_sync'].mean()) if 'null_final_sync' in nn.columns else None
    null_closure_corr = float(nn['null_closure_corr'].mean()) if 'null_closure_corr' in nn.columns else None

    candidates.append({
        'candidate': 'synchronization_value',
        'phase': 'N', 'source': 'dynamical_nulls',
        'real': real_sync, 'null': null_sync,
        'collapse': float(1.0 - null_sync / real_sync) if real_sync and null_sync and real_sync > 1e-10 else None,
        'property_type': 'distribution_dependent',
    })
    candidates.append({
        'candidate': 'closure_correlation',
        'phase': 'N', 'source': 'dynamical_nulls',
        'real': real_closure_corr, 'null': null_closure_corr,
        'collapse': float(1.0 - null_closure_corr / real_closure_corr) if real_closure_corr and null_closure_corr and real_closure_corr > 1e-10 else None,
        'property_type': 'trajectory_dependent',
    })

# From Phase O: shared continuity
if 'O' in data_sources:
    od = data_sources['O']['null']
    candidates.append({
        'candidate': 'shared_closure_value',
        'phase': 'O', 'source': 'nulls',
        'real': float(od['real_shared_c'].mean()) if 'real_shared_c' in od.columns else None,
        'null': float(od['null1_shared_c'].mean()) if 'null1_shared_c' in od.columns else None,
        'collapse': float(1.0 - od['null1_shared_c'].mean() / od['real_shared_c'].mean()) if 'real_shared_c' in od.columns and 'null1_shared_c' in od.columns else None,
        'property_type': 'distribution_dependent',
    })
    candidates.append({
        'candidate': 'shared_cross_corr',
        'phase': 'O', 'source': 'nulls',
        'real': float(od['real_cross_corr'].mean()) if 'real_cross_corr' in od.columns else None,
        'null': float(od['null1_cross_corr'].mean()) if 'null1_cross_corr' in od.columns else None,
        'collapse': float(1.0 - od['null1_cross_corr'].mean() / od['real_cross_corr'].mean()) if 'real_cross_corr' in od.columns and 'null1_cross_corr' in od.columns else None,
        'property_type': 'trajectory_dependent',
    })
    candidates.append({
        'candidate': 'closure_convergence_value',
        'phase': 'O', 'source': 'nulls',
        'real': float(od['real_c_convergence'].mean()) if 'real_c_convergence' in od.columns else None,
        'null': float(od['null1_c_convergence'].mean()) if 'null1_c_convergence' in od.columns else None,
        'collapse': float(1.0 - od['null1_c_convergence'].mean() / od['real_c_convergence'].mean()) if 'real_c_convergence' in od.columns and 'null1_c_convergence' in od.columns else None,
        'property_type': 'mixed',
    })
    # Stability
    os_d = data_sources['O']['stable']
    candidates.append({
        'candidate': 'persistence_gain',
        'phase': 'O', 'source': 'stabilization',
        'real': float(os_d['persistence_gain'].mean()),
        'null': None,
        'collapse': None,
        'property_type': 'transition_invariant',
    })
    candidates.append({
        'candidate': 'buffering',
        'phase': 'O', 'source': 'stabilization',
        'real': float(os_d['buffering'].mean()),
        'null': None,
        'collapse': None,
        'property_type': 'transition_invariant',
    })

# From Phase P: transition persistence
if 'P' in data_sources:
    pc = data_sources['P']['continuity']
    pr = data_sources['P']['recon']
    ps = data_sources['P']['shared']
    pn = data_sources['P']['null']
    
    candidates.append({
        'candidate': 'individual_transition_survival',
        'phase': 'P', 'source': 'continuity',
        'real': float(pc['continuity_survives'].mean()),
        'null': float(pn['null1_continuity'].mean()) if 'null1_continuity' in pn.columns else None,
        'collapse': float(1.0 - pn['null1_continuity'].mean() / pc['continuity_survives'].mean()) if 'null1_continuity' in pn.columns else None,
        'property_type': 'transition_invariant',
    })
    candidates.append({
        'candidate': 'shared_transition_survival',
        'phase': 'P', 'source': 'shared_transition',
        'real': float(ps['shared_survives'].mean()),
        'null': None,
        'collapse': None,
        'property_type': 'transition_invariant',
    })
    candidates.append({
        'candidate': 'closure_recovery_under_transition',
        'phase': 'P', 'source': 'continuity',
        'real': float(pc['c_recovery'].mean()),
        'null': None,
        'collapse': None,
        'property_type': 'transition_invariant',
    })
    candidates.append({
        'candidate': 'reconstruction_probability',
        'phase': 'P', 'source': 'reconstruction',
        'real': float(pr['rec_probability'].mean()),
        'null': None,
        'collapse': None,
        'property_type': 'transition_invariant',
    })
    candidates.append({
        'candidate': 'reconstruction_fidelity',
        'phase': 'P', 'source': 'reconstruction',
        'real': float(pr['rec_fidelity'].mean()),
        'null': None,
        'collapse': None,
        'property_type': 'transition_invariant',
    })

cand_df = pd.DataFrame(candidates)
cand_df.to_csv(f'{BASE}/outputs/phaseQ_candidate_invariants.csv', index=False)

print(f'\n  Extracted {len(candidates)} candidate invariants')
print(f'\n  {"Candidate":40s} {"Real":>8s} {"Null":>8s} {"Collapse":>8s} {"Type":>25s}')
print(f'  {"-"*89}')
for _, c in cand_df.iterrows():
    r = f'{c["real"]:.4f}' if pd.notna(c['real']) else 'N/A'
    n = f'{c["null"]:.4f}' if pd.notna(c['null']) else 'N/A'
    col = f'{c["collapse"]:.4f}' if pd.notna(c['collapse']) else 'N/A'
    print(f'  {c["candidate"]:40s} {r:>8s} {n:>8s} {col:>8s} {c["property_type"]:>25s}')

# Save Q1 summary
q1 = {'phase': 'Q1', 'n_candidates': len(candidates),
      'candidates': [c['candidate'] for c in candidates]}
with open(f'{BASE}/summaries/q1_summary.json','w') as f: json.dump(q1,f,indent=2)

# ====================================================
# Q2: TRAJECTORY VS DISTRIBUTION SEPARATION
# ====================================================
print('\n' + '='*70)
print('PHASE Q2 — TRAJECTORY VS DISTRIBUTION SEPARATION')
print('Which properties require temporal sequencing vs survive as statistics?')
print('='*70)

# Build comparison from null data across phases
all_properties = []

if 'N' in data_sources:
    nd = data_sources['N']['taxonomy']
    nn = data_sources['N']['null']
    real_sync = float(nd['final_synchronization'].mean()) if 'final_synchronization' in nd.columns else 0
    real_cc = float(nd['closure_correlation'].mean()) if 'closure_correlation' in nd.columns else 0
    null_sync = float(nn['null_final_sync'].mean())
    null_cc = float(nn['null_closure_corr'].mean())
    all_properties.append({'property': 'synchronization', 'phase': 'N',
                           'real_mean': real_sync, 'null_mean': null_sync,
                           'collapse': float(1.0 - null_sync / real_sync) if real_sync > 1e-10 else 1.0,
                           'dependency': 'distribution'})
    all_properties.append({'property': 'closure_correlation', 'phase': 'N',
                           'real_mean': real_cc, 'null_mean': null_cc,
                           'collapse': float(1.0 - null_cc / real_cc) if real_cc > 1e-10 else 1.0,
                           'dependency': 'trajectory'})

if 'O' in data_sources:
    od = data_sources['O']['null']
    for col, real_col, null_col, label in [
        ('shared_closure', 'real_shared_c', 'null1_shared_c', 'shared_closure_value'),
        ('closure_convergence', 'real_c_convergence', 'null1_c_convergence', 'closure_convergence'),
        ('cross_corr', 'real_cross_corr', 'null1_cross_corr', 'cross_correlation'),
    ]:
        if real_col in od.columns and null_col in od.columns:
            r = float(od[real_col].mean())
            n = float(od[null_col].mean())
            coll = 1.0 - n / r if r > 1e-10 else 0
            dep = 'trajectory' if coll > 0.5 else 'distribution'
            all_properties.append({
                'property': label, 'phase': 'O',
                'real_mean': r, 'null_mean': n, 'collapse': coll,
                'dependency': dep,
            })

if 'P' in data_sources:
    pn = data_sources['P']['null']
    for col, label in [
        ('real_continuity', 'continuity_survival'),
        ('null1_continuity', 'continuity_survival_null1'),
        ('null2_survives', 'continuity_survival_null2'),
        ('null3_continuity', 'continuity_survival_null3'),
    ]:
        pass
    if 'real_continuity' in pn.columns and 'null1_continuity' in pn.columns:
        r = float(pn['real_continuity'].mean())
        n1 = float(pn['null1_continuity'].mean())
        coll = 1.0 - n1 / r if r > 1e-10 else 0
        dep = 'distribution' if coll < 0.1 else 'trajectory'
        all_properties.append({
            'property': 'continuity_through_transition', 'phase': 'P',
            'real_mean': r, 'null_mean': n1, 'collapse': coll,
            'dependency': dep,
        })

q2_df = pd.DataFrame(all_properties)
q2_df.to_csv(f'{BASE}/outputs/phaseQ_trajectory_distribution_split.csv', index=False)

print(f'\n  {"Property":40s} {"Phase":>6s} {"Real":>8s} {"Null":>8s} {"Collapse":>10s} {"Dependency":>15s}')
print(f'  {"-"*87}')
for _, r in q2_df.iterrows():
    print(f'  {r["property"]:40s} {r["phase"]:>6s} {r["real_mean"]:>8.4f} {r["null_mean"]:>8.4f} {r["collapse"]:>10.4f} {r["dependency"]:>15s}')

print(f'\n  TRAJECTORY-DEPENDENT (collapse > 0.5):')
for _, r in q2_df[q2_df['collapse'] > 0.5].iterrows():
    print(f'    {r["property"]:40s} (collapse={r["collapse"]:.4f})')

print(f'\n  DISTRIBUTION-DEPENDENT (collapse < 0.5):')
for _, r in q2_df[q2_df['collapse'] < 0.5].iterrows():
    print(f'    {r["property"]:40s} (collapse={r["collapse"]:.4f})')

q2 = {'phase': 'Q2', 'n_properties': len(all_properties),
      'trajectory_dependent': [r['property'] for _, r in q2_df[q2_df['collapse'] > 0.5].iterrows()],
      'distribution_dependent': [r['property'] for _, r in q2_df[q2_df['collapse'] < 0.5].iterrows()]}
with open(f'{BASE}/summaries/q2_summary.json','w') as f: json.dump(q2,f,indent=2)

print(f'\nQ1+Q2 COMPLETE')
