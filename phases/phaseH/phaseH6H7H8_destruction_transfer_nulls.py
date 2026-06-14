"""
Phase H6+H7+H8 — Destruction Tests + Cross-Family Causality + Null Program.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from scipy.stats import ks_2samp, pearsonr
from sklearn.utils import shuffle
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseH'
PC = '/home/student/sgp_core_v2/phases/phaseC'
os.makedirs(f'{BASE}/processed', exist_ok=True)
os.makedirs(f'{BASE}/nulls', exist_ok=True)

int_df = pd.read_csv(f'{BASE}/interventions/intervention_results.csv')
df = pd.read_csv(f'{PC}/phaseC_metrics.csv')
domains = sorted(df['domain'].unique())
regime_order = ['constrained_generative','rigid_coherence','chaotic_fertility','collapse']

t0 = time.time()
print('='*70)
print('PHASE H6+H7+H8 — DESTRUCTION + TRANSFER + NULLS')
print('='*70)

# === H6: DESTRUCTION TESTS ===
print('\n--- H6: Destruction Tests ---')
# Which interventions DESTROY constrained generativity (CG → non-CG)?
cg_df = int_df[int_df['regime_from'] == 'constrained_generative']
dest_records = []

for domain in domains:
    dd = cg_df[cg_df['domain'] == domain]
    if len(dd) == 0: continue
    for desc in dd['desc_name'].unique():
        di = dd[dd['desc_name'] == desc]
        destroyed = len(di[di['regime_to'] != 'constrained_generative'])
        dest_type = di[di['regime_to'] != 'constrained_generative']['regime_to'].value_counts()
        top_dest = dest_type.index[0] if len(dest_type) > 0 else 'N/A'
        dest_records.append({
            'domain': domain, 'intervention': f'perturb_{desc}',
            'n_cg_systems': len(di),
            'n_destroyed': destroyed,
            'destruction_rate': round(destroyed / len(di), 4) if len(di) > 0 else 0,
            'top_destruction_mode': top_dest,
            'destruction_entropy': round(-np.sum([v/len(di)*np.log2(v/len(di)) for v in dest_type.values])/np.log2(3), 4) if len(dest_type) > 1 else 0,
        })

dest_df = pd.DataFrame(dest_records)
dest_df.to_csv(f'{BASE}/processed/destruction_tests.csv', index=False)
print(f'Destruction tests saved: {len(dest_df)} entries')

print('\nMost destructive interventions per domain:')
for domain in domains:
    dd = dest_df[dest_df['domain'] == domain]
    if len(dd) == 0: continue
    best = dd.loc[dd['destruction_rate'].idxmax()]
    print(f'  {domain:25s}: {best["intervention"]:15s} destroys {best["destruction_rate"]:.3f} of CG systems → {best["top_destruction_mode"]}')

# === H7: CROSS-FAMILY CAUSALITY TRANSFER ===
print('\n--- H7: Cross-Family Causality ---')
# Phase F found 4 geometry clusters. Test if causal patterns transfer within clusters.
geom = pd.read_csv('/home/student/sgp_core_v2/phases/phaseF/processed/family_geometry_classes.csv')
cluster_map = dict(zip(geom['domain'], geom['hierarchical_cluster']))
int_df['cluster'] = int_df['domain'].map(cluster_map)

# For each cluster, compute within-cluster correlation of intervention effectiveness
transfer_records = []
for cluster in sorted(int_df['cluster'].unique()):
    cd = int_df[int_df['cluster'] == cluster]
    cl_domains = cd['domain'].unique()
    if len(cl_domains) < 2: continue
    
    for desc in cd['desc_name'].unique():
        # Build transition rate per domain
        rates = {}
        for d in cl_domains:
            di = cd[(cd['domain'] == d) & (cd['desc_name'] == desc)]
            rates[d] = di['transitioned'].mean() if len(di) > 0 else 0.5
        
        rates_list = list(rates.values())
        if len(rates_list) >= 2:
            within_var = np.var(rates_list)
            between_corr = np.corrcoef(rates_list, rates_list)[0,1] if len(rates_list) >= 2 else 0
            
            # Compare with cross-cluster variance
            other_rates = []
            for other_cl in sorted(int_df['cluster'].unique()):
                if other_cl == cluster: continue
                oc = int_df[(int_df['cluster'] == other_cl) & (int_df['desc_name'] == desc)]
                for d in oc['domain'].unique():
                    di = oc[oc['domain'] == d]
                    other_rates.append(di['transitioned'].mean() if len(di) > 0 else 0.5)
            
            cross_var = np.var(other_rates) if len(other_rates) >= 2 else 0
            transfer_score = within_var / max(cross_var, 1e-10)
            
            transfer_records.append({
                'cluster': int(cluster),
                'intervention': f'perturb_{desc}',
                'n_domains': len(cl_domains),
                'within_cluster_variance': round(within_var, 4),
                'cross_cluster_variance': round(cross_var, 4),
                'transfer_ratio': round(transfer_score, 4),
                'within_split_corr': round(between_corr, 4),
                'domains': '+'.join(sorted(cl_domains)),
            })

transfer_df = pd.DataFrame(transfer_records)
transfer_df.to_csv(f'{BASE}/processed/causal_transfer.csv', index=False)
print(f'\nCross-family transfer saved: {len(transfer_df)} entries')

print('\nTransfer within geometry clusters:')
for _, r in transfer_df.iterrows():
    print(f'  Cluster {r["cluster"]} ({r["domains"]:40s}) {r["intervention"]:15s}: '
          f'WCV={r["within_cluster_variance"]:.3f} CCV={r["cross_cluster_variance"]:.3f} '
          f'ratio={r["transfer_ratio"]:.3f}')

# === H8: NULL PROGRAM ===
print('\n--- H8: Null Program ---')
NULL = f'{BASE}/nulls'
N_NULL = 100

# Null program: test whether descriptor-specific intervention effects
# are distinguishable from random perturbations.

COLS_DESC_LIST = ['CSR','RBS','ADI','RTP','SRD']
null_records = []
for null_idx in range(N_NULL):
    if null_idx % 25 == 0: print(f'  Null iteration {null_idx}/{N_NULL}')
    
    # N1: Shuffle regime labels within domain
    n1 = int_df.copy()
    for domain in domains:
        idx = n1['domain'] == domain
        n1.loc[idx, 'regime_from'] = shuffle(n1.loc[idx, 'regime_from'].values)
        n1.loc[idx, 'regime_to'] = shuffle(n1.loc[idx, 'regime_to'].values)
    tprob_n1 = n1.groupby('desc_name')['transitioned'].mean()
    
    # N2: Random desc assignments
    rand_desc = int_df.copy()
    rand_desc['desc_name'] = np.random.choice(COLS_DESC_LIST, len(rand_desc))
    tprob_n2 = rand_desc.groupby('desc_name')['transitioned'].mean()
    
    # N3: Random transition maps (shuffle regime_to within domain+desc groups)
    n3 = int_df.copy()
    for (domain, desc), grp in n3.groupby(['domain','desc_name'], observed=False):
        idx = grp.index
        n3.loc[idx, 'regime_to'] = shuffle(grp['regime_to'].values)
    tprob_n3 = n3.groupby('desc_name')['transitioned'].mean()
    
    null_records.append({
        'null_iteration': int(null_idx),
        'null_type': 'all',
        'n1_mean_transprob': float(tprob_n1.mean()),
        'n2_mean_transprob': float(tprob_n2.mean()),
        'n3_mean_transprob': float(tprob_n3.mean()),
        **{f'n1_{d}': float(tprob_n1.get(d, 0)) for d in COLS_DESC_LIST},
        **{f'n2_{d}': float(tprob_n2.get(d, 0)) for d in COLS_DESC_LIST},
        **{f'n3_{d}': float(tprob_n3.get(d, 0)) for d in COLS_DESC_LIST},
    })

null_df = pd.DataFrame(null_records)
null_df.to_csv(f'{BASE}/nulls/null_controls.csv', index=False)
print(f'Null controls saved: {len(null_df)} iterations')

# Test survival at descriptor level (not overall)
true_transprob = int_df.groupby('desc_name')['transitioned'].mean()
null_survival = {}
print('\nPer-descriptor null survival:')
for desc in COLS_DESC_LIST:
    true_p = float(true_transprob.loc[desc]) if desc in true_transprob.index else 0
    null_survival[desc] = {}
    for null_type, prefix in [('shuffle_labels','n1'), ('random_desc','n2'), ('random_transition','n3')]:
        col = f'{prefix}_{desc}'
        if col in null_df.columns:
            null_mean = float(null_df[col].mean())
            null_std = float(null_df[col].std())
            z = (true_p - null_mean) / max(null_std, 1e-10)
            survived = bool(abs(z) > 2)
            null_survival[desc][null_type] = {
                'true': true_p, 'null_mean': null_mean, 'null_std': null_std,
                'z': round(z, 3), 'survived': survived,
            }
            print(f'  {desc}: {null_type:20s} true={true_p:.4f} null={null_mean:.4f}±{null_std:.4f} z={z:.2f} {"SURVIVED" if survived else "FAILED"}')
        else:
            null_survival[desc][null_type] = {'true': true_p, 'survived': False}

n_survived = sum(1 for d in null_survival for t in null_survival[d] if null_survival[d][t]['survived'])
total_tests = sum(len(null_survival[d]) for d in null_survival)
all_survive = n_survived == total_tests

# === METASTABILITY METRICS ===
meta_records = []
for domain in domains:
    dd = int_df[int_df['domain'] == domain]
    all_tprob = dd.groupby(['regime_from','regime_to']).size().unstack(fill_value=0)
    # Compute off-diagonal entropy (higher = more metastable)
    off_diag = all_tprob.values.copy()
    np.fill_diagonal(off_diag, 0)
    row_sums = off_diag.sum(axis=1, keepdims=True)
    off_diag_norm = off_diag / np.maximum(row_sums, 1)
    off_ent = -np.nansum(off_diag_norm * np.log2(np.maximum(off_diag_norm, 1e-10))) / np.log2(3)
    
    # Hysteresis: asymmetry in forward vs reverse transitions
    # For each regime pair, compare (A→B) vs (B→A)
    fwd_vs_rev = []
    for i, r1 in enumerate(regime_order):
        for j, r2 in enumerate(regime_order):
            if i >= j: continue
            fwd = all_tprob.loc[r1, r2] if r2 in all_tprob.columns and r1 in all_tprob.index else 0
            rev = all_tprob.loc[r2, r1] if r1 in all_tprob.columns and r2 in all_tprob.index else 0
            ratio = fwd / max(rev, 1)
            fwd_vs_rev.append(ratio)
    hysteresis = np.log2(np.mean(fwd_vs_rev) if fwd_vs_rev else 1)
    
    meta_records.append({
        'domain': domain,
        'metastability_entropy': round(off_ent, 4),
        'hysteresis_asymmetry': round(hysteresis, 4),
        'n_transitions': len(dd),
    })

meta_df = pd.DataFrame(meta_records)
meta_df.to_csv(f'{BASE}/processed/metastability_metrics.csv', index=False)

h6h7h8_summary = {
    'phase': 'H6+H7+H8', 'seed': SEED,
    'n_destruction_entries': len(dest_df),
    'n_transfer_entries': len(transfer_df),
    'n_null_iterations': N_NULL,
    'null_survival': null_survival,
    'all_nulls_survived': bool(all_survive),
    'n_survived_nulls': int(n_survived),
    'global_hysteresis_mean': float(meta_df['hysteresis_asymmetry'].mean()),
    'global_metastability_mean': float(meta_df['metastability_entropy'].mean()),
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/h6h7h8_summary.json', 'w') as f:
    json.dump(h6h7h8_summary, f, indent=2)
print(f'\nH6+H7+H8 COMPLETE ({time.time()-t0:.1f}s)')
