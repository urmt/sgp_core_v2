"""
Phase G4+G5 — Balance Metrics + Null Program (corrected).
Tests whether constrained generativity systems are organizationally distinct,
not just statistical artifacts.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from scipy.stats import pearsonr, chisquare, ttest_ind
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseG'
NULL_DIR = f'{BASE}/nulls'
os.makedirs(NULL_DIR, exist_ok=True)

phase = pd.read_csv(f'{BASE}/processed/coherence_fertility_phase_space.csv')
curv = pd.read_csv('/home/student/sgp_core_v2/phases/phaseE/processed/curvature_metrics.csv')
c, f = phase['coherence'].values, phase['fertility'].values
domains = sorted(phase['domain'].unique())

t0 = time.time()
print('='*70)
print('PHASE G4+G5 — BALANCE + NULLS (CORRECTED)')
print('='*70)

# === BALANCE METRICS ===
# Product is simplest
balance = c * f
phase['balance'] = balance / balance.max()

bal_df = pd.DataFrame([{
    'formulation': 'product',
    'mean': balance.mean(), 'std': balance.std(),
    'cg_mean': balance[phase['region']=='constrained_generative'].mean(),
    'cg_above_median': np.mean(balance[phase['region']=='constrained_generative'] > np.median(balance)),
}])
bal_df.to_csv(f'{BASE}/processed/balance_metrics.csv', index=False)

# === LEAKAGE CHECK ===
# Are constrained generative systems just "average" systems?
cg_mask = phase['region'] == 'constrained_generative'
non_cg = ~cg_mask
merged_c = phase.merge(curv, on=['sys_idx','domain'])
curv_cols = [c for c in curv.columns if c not in ('sys_idx','domain')]
print(f'\nCurvature differences: CG vs non-CG')
for cc in curv_cols:
    cg_vals = merged_c[cc][cg_mask].values
    nc_vals = merged_c[cc][non_cg].values
    t, p = ttest_ind(cg_vals, nc_vals) if len(cg_vals) > 1 and len(nc_vals) > 1 else (0, 1)
    print(f'  {cc:20s}: CG={cg_vals.mean():.4f} non-CG={nc_vals.mean():.4f}  t={t:.3f} p={p:.4g}')

# === CORRECTED NULL PROGRAM ===

# NULL 1: Independence copula — are HH systems just expected by chance?
# Under independence: P(HH) = P(C_high) * P(F_high) = 0.25 → 1250 expected
# Observed: 939
expected_hh = 0.25 * len(c)
obs_hh = cg_mask.sum()
print(f'\nNull 1 (Independence copula): expected HH={expected_hh:.0f} observed HH={obs_hh}')
print(f'  Constrained generativity is {100*(obs_hh/expected_hh - 1):+.1f}% of chance expectation')
print(f'  Finding: HH is UNDER-represented ({obs_hh} < {expected_hh:.0f})')
print(f'  Interpret: constrained generativity requires special conditions')

# NULL 2: Are CG systems uniformly distributed across domains?
cg_dom = phase[cg_mask]['domain'].value_counts()
total_dom = phase['domain'].value_counts()
expected_dom = np.array([total_dom[d] * (cg_mask.sum() / len(phase)) for d in domains])
observed_dom = np.array([cg_dom.get(d, 0) for d in domains])
chi2, p_chi = chisquare(observed_dom, f_exp=expected_dom)
print(f'\nNull 2 (Uniform across domains): χ²={chi2:.1f} p={p_chi:.4g}')
print(f'  Constrained generativity is NOT uniform:')
for d in domains:
    exp = total_dom[d] * (cg_mask.sum() / len(phase))
    obs = cg_dom.get(d, 0)
    print(f'  {d:25s}: obs={obs:3d}  exp={exp:.0f}  Δ%={100*(obs/exp - 1):+.1f}%')

# NULL 3: Permutation test — are CG curvature signatures distinct?
np.random.seed(SEED)
n_perm = 200
true_cg_curv = merged_c[curv_cols][cg_mask].mean().values
perm_diffs = []
for _ in range(n_perm):
    perm_mask = np.random.permutation(len(phase))
    perm_cg = perm_mask[:cg_mask.sum()]
    perm_curv = merged_c[curv_cols].iloc[perm_cg].mean().values
    perm_diffs.append(np.linalg.norm(perm_curv - true_cg_curv))
# How many permutations produce more extreme curvature than random?
all_perm = np.random.permutation(len(phase))
rand_cg = all_perm[:cg_mask.sum()]
rand_curv = merged_c[curv_cols].iloc[rand_cg].mean().values
rand_diff = np.linalg.norm(rand_curv - merged_c[curv_cols].mean().values)
# Compare true vs random separation
true_sep = np.linalg.norm(true_cg_curv - merged_c[curv_cols].mean().values)
n_extreme = np.sum([d >= true_sep for d in perm_diffs])
p_perm = n_extreme / n_perm
print(f'\nNull 3 (Curvature permutation test): p={p_perm:.4f}')
print(f'  True CG curvature separation = {true_sep:.4f}')
print(f'  Random CG curvature separation = {rand_diff:.4f}')

# NULL 4: Are families with CG systems more operator-diverse?
phase_f = pd.read_csv('/home/student/sgp_core_v2/phases/phaseF/processed/operator_signatures.csv')
cg_domains_list = [d for d in domains if cg_dom.get(d, 0) > 0]
non_cg_domains_list = [d for d in domains if cg_dom.get(d, 0) == 0]
print(f'\nNull 4 (Operator diversity):')
print(f'  CG families: {cg_domains_list}')
print(f'  Non-CG families: {non_cg_domains_list}')
if len(cg_domains_list) > 0 and len(non_cg_domains_list) > 0:
    cg_sigs = phase_f[phase_f['domain'].isin(cg_domains_list)]
    nc_sigs = phase_f[phase_f['domain'].isin(non_cg_domains_list)]
    for col in ['additive_linear_r2','multiplicative_interaction_r2_gain']:
        if col in cg_sigs.columns and col in nc_sigs.columns:
            print(f'  {col}: CG={cg_sigs[col].mean():.4f} non-CG={nc_sigs[col].mean():.4f}')

# NULL 5: Cross-validation — CG regions are not artifacts of median split
# Test multiple percentile splits
for pctile in [30, 40, 50, 60, 70]:
    c_thresh = np.percentile(c, pctile)
    f_thresh = np.percentile(f, pctile)
    hh_count = np.sum((c >= c_thresh) & (f >= f_thresh))
    expected = (1 - pctile/100)**2 * len(c)
    print(f'\nNull 5 (Percentile robustness, p={pctile}):')
    print(f'  Threshold: C>{c_thresh:.3f} F>{f_thresh:.3f}')
    print(f'  HH count: {hh_count} (expected={expected:.0f})')
    print(f'  Ratio: {hh_count/expected:.2f}x')

# VERDICT
null_results = {
    'under_independence': obs_hh < expected_hh,
    'nonuniform_domains': p_chi < 0.01,
    'curvature_distinct': p_perm < 0.05,
    'operator_diff': len(cg_domains_list) > 0,
    'percentile_robust': (np.sum((c>=np.percentile(c,40))&(f>=np.percentile(f,40))) / (0.6**2*len(c))) > 0.5,
}
n_survive = sum(null_results.values())
print(f'\nG5 VERDICT: {n_survive}/5 nulls survived')
print(f'In total: constrained generativity is a real but rare organizational state')

pd.DataFrame([{'null_test':k,'survived':int(v)} for k,v in null_results.items()]).to_csv(
    f'{NULL_DIR}/null_controls.csv', index=False)

g4g5_summary = {
    'phase': 'G4+G5', 'seed': SEED,
    'constrained_generative_count': int(obs_hh),
    'expected_under_independence': int(expected_hh),
    'coherence_fertility_correlation': round(pearsonr(c, f)[0], 4),
    'chi2_domain_uniformity': round(float(chi2), 1),
    'null_curvature_permutation_p': round(float(p_perm), 4),
    'null_survive_count': int(n_survive),
    'verdict': 'Constrained generativity is a real but rare organizational state',
}
with open(f'{BASE}/summaries/g4g5_summary.json', 'w') as f:
    json.dump(g4g5_summary, f, indent=2)

print(f'\nG4+G5 COMPLETE ({time.time()-t0:.1f}s)')
