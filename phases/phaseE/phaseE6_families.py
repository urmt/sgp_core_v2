"""
Phase E6 — Organizational Family Discovery.
Tests cross-domain transfer with proper within-domain standardization,
geometry similarity analysis, and regime alignment.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
from scipy.stats import pearsonr, spearmanr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseE'
t0 = time.time()

curv = pd.read_csv(f'{BASE}/processed/curvature_metrics.csv')
poss = pd.read_csv(f'{BASE}/processed/possibility_metrics.csv')
phaseC = pd.read_csv('/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv')
phaseC['sys_idx'] = phaseC.groupby('domain').cumcount()
df = curv.merge(poss, on=['sys_idx','domain']).merge(
    phaseC[['sys_idx','domain','CSR','RBS','ADI','RTP','SRD']], on=['sys_idx','domain'])
domains = sorted(df['domain'].unique())

COLS_CURV = ['tangent_rotation','local_curvature','predictive_shear',
             'geodesic_instab','jacobian_vol','desc_switch_vel']
COLS_POSS = ['poss_reachable_volume','poss_branching_diversity',
             'poss_adaptive_recovery','poss_future_entropy',
             'poss_divergence_capacity','poss_stability_fertility_coupling']
COLS_DESC = ['CSR','RBS','ADI','RTP','SRD']

print('='*70)
print('PHASE E6 — ORGANIZATIONAL FAMILY DISCOVERY')
print('='*70)

# Pre-compute within-domain standardized curvature for each domain
dom_data = {}
for d in domains:
    dm = df[df['domain'] == d].reset_index(drop=True)
    dom_data[d] = {
        'curv_raw': dm[COLS_CURV].values,
        'curv_z': StandardScaler().fit_transform(dm[COLS_CURV].values),
        'poss': dm[COLS_POSS].values,
        'N': len(dm),
    }

# ============================================================
# E6.1: Family Transfer (within-domain standardized cross-prediction)
# ============================================================
print('\n--- E6.1: Cross-Domain Curvature Transfer ---')
transfer_records = []

for src_d in domains:
    X_src = dom_data[src_d]['curv_z']  # already standardized within source
    y_src = dom_data[src_d]['poss']

    for tgt_d in domains:
        X_tgt = StandardScaler().fit_transform(dom_data[tgt_d]['curv_raw'])  # standardize within target
        y_tgt = dom_data[tgt_d]['poss']

        for pj, pc in enumerate(COLS_POSS):
            y_src_v = y_src[:, pj]
            y_tgt_v = y_tgt[:, pj]

            if src_d == tgt_d:
                # LOOCV within-domain
                N = len(y_src_v)
                yp = np.zeros(N)
                for i in range(N):
                    tr = np.arange(N) != i
                    yp[i] = Ridge(alpha=1.0).fit(X_src[tr], y_src_v[tr]).predict(X_src[i:i+1])[0]
            else:
                # Cross-domain: train on full source
                model = Ridge(alpha=1.0).fit(X_src, y_src_v)
                yp = model.predict(X_tgt)

            r2 = r2_score(y_tgt_v, yp) if np.std(y_tgt_v) > 1e-10 else 0.0
            sr, _ = spearmanr(y_tgt_v, yp) if np.std(y_tgt_v) > 1e-10 and np.std(yp) > 1e-10 else (0, 1)
            transfer_records.append({
                'source': src_d, 'target': tgt_d,
                'same_domain': src_d == tgt_d,
                'possibility_metric': pc, 'transfer_R2': r2, 'spearman_r': sr,
            })

    print(f'  Source={src_d}: {len(domains)} domains ({time.time()-t0:.1f}s)')

transfer_df = pd.DataFrame(transfer_records)
transfer_df.to_csv(f'{BASE}/processed/family_transfer.csv', index=False)
print(f'  Family transfer saved: {len(transfer_df)} rows')

# Transfer matrix
pivot_r2 = transfer_df.groupby(['source','target'])['transfer_R2'].mean().unstack()
print('\nTransfer matrix (mean R², within-domain standardized):')
print(pivot_r2.round(4))

# ============================================================
# E6.2: Geometry Similarity
# ============================================================
print('\n--- E6.2: Geometry Similarity ---')
sim_records = []

for d1 in domains:
    for d2 in domains:
        if d2 < d1: continue
        # Compare mean curvature vectors
        c1_m = dom_data[d1]['curv_raw'].mean(axis=0)
        c2_m = dom_data[d2]['curv_raw'].mean(axis=0)
        c1_s = dom_data[d1]['curv_raw'].std(axis=0)
        c2_s = dom_data[d2]['curv_raw'].std(axis=0)

        # Cosine similarity of mean profiles
        cs = np.dot(c1_m, c2_m) / (np.linalg.norm(c1_m) * np.linalg.norm(c2_m) + 1e-10)
        # Correlation of mean profiles
        r_m, _ = pearsonr(c1_m, c2_m) if len(c1_m) > 1 else (0, 1)
        # L2 distance between mean profiles
        l2 = np.sqrt(np.sum((c1_m - c2_m)**2))

        # Correlation of distributions (stack all systems)
        all_c1 = dom_data[d1]['curv_raw'].T.flatten()
        all_c2 = dom_data[d2]['curv_raw'].T.flatten()
        r_dist, _ = pearsonr(all_c1, all_c2) if len(all_c1) > 1 else (0, 1)

        sim_records.append({
            'domain1': d1, 'domain2': d2,
            'cosine_sim_mean': cs, 'pearson_r_mean': r_m,
            'l2_mean': l2, 'distribution_corr': r_dist,
        })

sim_df = pd.DataFrame(sim_records)
sim_df.to_csv(f'{BASE}/processed/geometry_similarity.csv', index=False)
print(f'  Geometry similarity saved: {len(sim_df)} pairs')

# Best matched pairs
print('\nClosest domain pairs (by cosine similarity):')
best = sim_df[sim_df['domain1'] != sim_df['domain2']].sort_values('cosine_sim_mean', ascending=False)
for _, r in best.head(5).iterrows():
    print(f'  {r["domain1"]} ↔ {r["domain2"]}: cos={r["cosine_sim_mean"]:.4f}')

print('\nFarthest domain pairs:')
worst = sim_df[sim_df['domain1'] != sim_df['domain2']].sort_values('cosine_sim_mean')
for _, r in worst.head(5).iterrows():
    print(f'  {r["domain1"]} ↔ {r["domain2"]}: cos={r["cosine_sim_mean"]:.4f}')

# ============================================================
# E6.3: Regime Alignment
# ============================================================
print('\n--- E6.3: Regime Alignment ---')
# Check if domains with similar curvature profiles also have similar 
# curvature → possibility transfer quality
align_records = []

for d1 in domains:
    for d2 in domains:
        if d2 >= d1: continue
        # Get transfer quality between d1 and d2 (average both directions)
        fwd = transfer_df[(transfer_df['source']==d1)&(transfer_df['target']==d2)]['transfer_R2'].mean()
        rev = transfer_df[(transfer_df['source']==d2)&(transfer_df['target']==d1)]['transfer_R2'].mean()
        mutual_xfer = (fwd + rev) / 2

        # Geometry similarity
        g = sim_df[(sim_df['domain1']==d1)&(sim_df['domain2']==d2)]
        if len(g) == 0:
            g = sim_df[(sim_df['domain1']==d2)&(sim_df['domain2']==d1)]
        cos_sim = g['cosine_sim_mean'].values[0] if len(g) > 0 else 0

        align_records.append({
            'domain1': d1, 'domain2': d2,
            'mutual_transfer_R2': mutual_xfer,
            'cosine_sim': cos_sim,
        })

align_df = pd.DataFrame(align_records)
align_df.to_csv(f'{BASE}/processed/regime_alignment.csv', index=True)
print(f'  Regime alignment saved: {len(align_df)} pairs')

if len(align_df) > 0:
    r_align, _ = pearsonr(align_df['cosine_sim'], align_df['mutual_transfer_R2'])
    print(f'  Curvature similarity → transfer quality correlation: r={r_align:.4f}')

# ============================================================
# E6 Summary
# ============================================================
# Best source domain (best average cross-domain transferer)
src_scores = transfer_df[transfer_df['same_domain']==False].groupby('source')['transfer_R2'].mean()
tgt_scores = transfer_df[transfer_df['same_domain']==False].groupby('target')['transfer_R2'].mean()

best_src = src_scores.idxmax()
best_tgt = tgt_scores.idxmax()
within_r2 = transfer_df[transfer_df['same_domain']==True]['transfer_R2'].mean()
cross_r2 = transfer_df[transfer_df['same_domain']==False]['transfer_R2'].mean()

print(f'\n--- E6 Summary ---')
print(f'Within-domain transfer R²: {within_r2:.4f}')
print(f'Cross-domain transfer R²:  {cross_r2:.4f}')
print(f'Best source domain:        {best_src} ({src_scores[best_src]:.4f})')
print(f'Best target domain:        {best_tgt} ({tgt_scores[best_tgt]:.4f})')
print(f'Geometry→transfer corr:    {r_align:.4f}')

e6_summary = {
    'phase': 'E6', 'seed': SEED,
    'n_transfer_pairs': len(transfer_df),
    'n_geometry_pairs': len(sim_df),
    'n_alignment_pairs': len(align_df),
    'within_domain_R2': round(within_r2, 6),
    'cross_domain_R2': round(cross_r2, 6),
    'best_source_domain': str(best_src),
    'best_source_R2': round(src_scores[best_src], 6),
    'best_target_domain': str(best_tgt),
    'best_target_R2': round(tgt_scores[best_tgt], 6),
    'geometry_transfer_correlation': round(r_align, 6) if len(align_df) > 0 else 0,
    'runtime': round(time.time() - t0),
}
with open(f'{BASE}/summaries/e6_summary.json', 'w') as f:
    json.dump(e6_summary, f, indent=2)
print(f'\nE6 summary saved')
print(f'E6 COMPLETE ({time.time()-t0:.0f}s)')
