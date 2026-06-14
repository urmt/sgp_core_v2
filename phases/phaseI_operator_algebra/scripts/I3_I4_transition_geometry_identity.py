"""
Phase I3+I4 (REVISED) — Operator Transition Geometry + Recursive Identity.

CORRECTED: 
- Operator transition geometry requires CROSS-DOMAIN neighborhoods
  to measure transitions BETWEEN operator types.
- Recursive identity tests chain preservation of organizational properties
  through multi-step compositions.
"""
import numpy as np, pandas as pd, os, json, warnings
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from scipy.stats import entropy
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseI_operator_algebra'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

op_df = pd.read_csv(f'{BASE}/outputs/phaseI_operator_signatures.csv')
comp_df = pd.read_csv(f'{BASE}/outputs/phaseI_composition_results.csv')
PC = '/home/student/sgp_core_v2/phases/phaseC'
PE = '/home/student/sgp_core_v2/phases/phaseE'
PG = '/home/student/sgp_core_v2/phases/phaseG'

df = pd.read_csv(f'{PC}/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
curv = pd.read_csv(f'{PE}/processed/curvature_metrics.csv')
poss = pd.read_csv(f'{PE}/processed/possibility_metrics.csv')
phaseG = pd.read_csv(f'{PG}/processed/coherence_fertility_phase_space.csv')
merged = df.merge(phaseG, on=['sys_idx','domain']).merge(curv, on=['sys_idx','domain']).merge(poss, on=['sys_idx','domain'])
merged['process_regime'] = merged['region'].map({'constrained_generative':'CG','rigid_coherence':'RG',
                                                   'chaotic_fertility':'CH','collapse':'CL'})

domains = sorted(merged['domain'].unique())
op_cols = [c for c in op_df.columns if c.startswith('op_')]
domain_op_map = dict(zip(op_df['domain'], [op_df[op_df['domain']==d][op_cols].values[0] for d in domains]))

STAB_COLS = ['stability_return_time','stability_recovery_rate','stability_final_dev','stability_max_dev']
FERT_COLS = ['fertility_state_diversity','fertility_novelty_rate','fertility_state_coverage','fertility_transition_entropy']

print('='*70)
print('PHASE I3 (REVISED) — CROSS-DOMAIN OPERATOR TRANSITION GEOMETRY')
print('Transitions between operators require cross-domain neighborhoods')
print('='*70)

# Build GLOBAL organizational state space across ALL domains
X_all = StandardScaler().fit_transform(merged[STAB_COLS + FERT_COLS].values)
y_regime_all = merged['process_regime'].values
domain_all = merged['domain'].values
sys_idx_all = merged['sys_idx'].values
N = len(merged)

# Operator score per system (from domain-level map)
op_matrix = np.array([domain_op_map[d] for d in domain_all])

# Global neighborhood graph (k=30)
K = min(30, N - 1)
nbrs = NearestNeighbors(n_neighbors=K + 1, metric='euclidean').fit(X_all)
_, global_indices = nbrs.kneighbors(X_all)

# Compute operator transition geometry for each system
trans_geo_records = []
for i in range(N):
    neigh_idx = global_indices[i, 1:]
    neigh_domains = domain_all[neigh_idx]
    neigh_regimes = y_regime_all[neigh_idx]
    
    # 1. Operator continuity: what fraction of neighbors share the same dominant operator?
    this_dom_op = op_df[op_df['domain'] == domain_all[i]]['dominant_operator'].values[0]
    neigh_dom_ops = []
    for d in neigh_domains:
        neigh_dom_ops.append(op_df[op_df['domain'] == d]['dominant_operator'].values[0])
    neigh_dom_ops = np.array(neigh_dom_ops)
    operator_continuity = np.mean(neigh_dom_ops == this_dom_op)
    
    # 2. Operator rupture: abrupt change in operator character
    operator_rupture = 1 - operator_continuity
    
    # 3. Operator curvature: variance of operator score vectors across neighbors
    neigh_op_sigs = op_matrix[neigh_idx]
    op_var = np.var(neigh_op_sigs, axis=0).mean()
    operator_curvature = float(op_var)
    
    # 4. Transition smoothness: variance of organizational properties across neighbors
    neigh_fert = merged.iloc[neigh_idx]['fertility'].values
    neigh_coh = merged.iloc[neigh_idx]['coherence'].values
    smoothness = 1 / (1 + np.sqrt(np.var(neigh_fert) * np.var(neigh_coh)))
    
    # 5. Recursive closure: stability-fertility coupling
    recursive_closure = merged.iloc[i]['poss_stability_fertility_coupling']
    
    # 6. Operator reversibility
    operator_reversibility = merged.iloc[i]['poss_stability_fertility_coupling']
    
    # 7. Compositional stability: coherence × fertility
    comp_stability = merged.iloc[i]['fertility'] * merged.iloc[i]['coherence']
    
    # 8. Operator diversity in neighborhood: entropy of dominant operators
    dom_op_unique, dom_op_counts = np.unique(neigh_dom_ops, return_counts=True)
    op_entropy = entropy(dom_op_counts / dom_op_counts.sum(), base=len(dom_op_unique)) if len(dom_op_unique) > 1 else 0
    
    trans_geo_records.append({
        'domain': domain_all[i],
        'sys_idx': int(sys_idx_all[i]),
        'process_regime': y_regime_all[i],
        'dominant_operator': str(this_dom_op),
        'operator_continuity': round(float(operator_continuity), 4),
        'operator_rupture': round(float(operator_rupture), 4),
        'operator_curvature': round(float(operator_curvature), 6),
        'transition_smoothness': round(float(smoothness), 4),
        'recursive_closure': round(float(recursive_closure), 4),
        'operator_reversibility': round(float(operator_reversibility), 4),
        'compositional_stability': round(float(comp_stability), 6),
        'operator_neighborhood_entropy': round(float(op_entropy), 4),
    })

trans_geo_df = pd.DataFrame(trans_geo_records)
trans_geo_df.to_csv(f'{BASE}/outputs/phaseI_transition_geometry.csv', index=False)
print(f'\nOperator transition geometry saved: {len(trans_geo_df)} systems (cross-domain)')

# Summary by regime
print('\nOperator transition geometry by organizational regime (mean):')
for col in ['operator_continuity','operator_rupture','operator_curvature',
            'transition_smoothness','recursive_closure','operator_reversibility',
            'compositional_stability','operator_neighborhood_entropy']:
    vals = {}
    for regime in sorted(trans_geo_df['process_regime'].unique()):
        vals[regime] = trans_geo_df[trans_geo_df['process_regime'] == regime][col].mean()
    cg_v = vals.get('CG', 0)
    nc_v = np.mean([v for k, v in vals.items() if k != 'CG'])
    print(f'  {col:40s}: CG={cg_v:.4f} nonCG={nc_v:.4f} ratio={cg_v/max(nc_v,1e-10):.3f}')
    for regime, v in vals.items():
        print(f'    {regime:4s}: {v:.4f}')

# Which operators have the smoothest transitions?
print('\nOperator transition smoothness by dominant operator type:')
for op_type in sorted(trans_geo_df['dominant_operator'].unique()):
    dd = trans_geo_df[trans_geo_df['dominant_operator'] == op_type]
    print(f'  {op_type[3:30]:30s}: continuity={dd["operator_continuity"].mean():.3f} '
          f'curvature={dd["operator_curvature"].mean():.6f} '
          f'entropy={dd["operator_neighborhood_entropy"].mean():.3f}')

# ====================================================
# SECTION I4: RECURSIVE IDENTITY (REVISED)
# ====================================================
print('\n' + '='*70)
print('PHASE I4 (REVISED) — RECURSIVE IDENTITY')
print('Test: do operator chains preserve organizational process identity?')
print('='*70)

# Recursive identity: for a chain of compositions A∘B∘C,
# does organizational process identity persist?
# 
# Identity retention = how much of the original CG process geometry
# survives a chain of operator compositions.
#
# Measure: compare the CG geometry of the composed domains
# to the original individual domains.

comp_df = pd.read_csv(f'{BASE}/outputs/phaseI_composition_results.csv')

# Build process geometry profile per domain (from I3 data)
domain_geo_profiles = {}
for domain in domains:
    dd = trans_geo_df[trans_geo_df['domain'] == domain]
    domain_geo_profiles[domain] = {
        'cg_rate': len(merged[(merged['domain']==domain) & (merged['process_regime']=='CG')]) / max(len(merged[merged['domain']==domain]), 1),
        'mean_continuity': dd['operator_continuity'].mean(),
        'mean_curvature': dd['operator_curvature'].mean(),
        'mean_reversibility': dd['operator_reversibility'].mean(),
        'mean_compositional_stability': dd['compositional_stability'].mean(),
    }

# Test recursive identity through chained compositions
# For a chain A → B → C, measure identity decay
identity_records = []
for idx, r in comp_df.iterrows():
    d1, d2 = r['domain_A'], r['domain_B']
    prof1 = domain_geo_profiles[d1]
    prof2 = domain_geo_profiles[d2]
    
    # Composition profile: weighted average
    comp_profile = {k: (prof1[k] + prof2[k]) / 2 for k in prof1}
    
    # For each third domain, test chain
    for d3 in domains:
        if d3 in [d1, d2]: continue
        prof3 = domain_geo_profiles[d3]
        
        # Chain composition: (A∘B)∘C
        chain_profile = {k: (comp_profile[k] + prof3[k]) / 2 for k in comp_profile}
        
        # Identity retention: compare chain profile to originals
        # High retention = chain closely matches the average of individual profiles
        orig_avg = {k: (prof1[k] + prof2[k] + prof3[k]) / 3 for k in prof1}
        
        # Geometric identity: cosine similarity between process geometry vectors
        chain_vec = np.array([chain_profile['mean_continuity'], 
                              chain_profile['mean_reversibility'],
                              chain_profile['mean_compositional_stability']])
        orig_vec = np.array([orig_avg['mean_continuity'],
                             orig_avg['mean_reversibility'],
                             orig_avg['mean_compositional_stability']])
        
        norm = np.linalg.norm(chain_vec) * np.linalg.norm(orig_vec)
        identity_sim = float(np.dot(chain_vec, orig_vec) / max(norm, 1e-10))
        
        # CG retention: how much CG rate survives in chain
        chain_cg = (prof1['cg_rate'] + prof2['cg_rate'] + prof3['cg_rate']) / 3
        max_single_cg = max(prof1['cg_rate'], prof2['cg_rate'], prof3['cg_rate'])
        cg_retention = chain_cg / max(max_single_cg, 0.001)
        
        identity_records.append({
            'chain': f'{d1}→{d2}→{d3}',
            'domain_A': d1, 'domain_B': d2, 'domain_C': d3,
            'operator_A': r['operator_A'], 'operator_B': r['operator_B'],
            'chain_identity_similarity': round(identity_sim, 4),
            'chain_cg_rate': round(chain_cg, 4),
            'chain_cg_retention': round(cg_retention, 4),
            'identity_preserved': int(identity_sim > 0.85),
            'cg_preserved': int(cg_retention >= 0.8),
        })

identity_df = pd.DataFrame(identity_records)
identity_df.to_csv(f'{BASE}/outputs/phaseI_recursive_identity.csv', index=False)
print(f'\nRecursive identity saved: {len(identity_df)} operator chains (3-step)')

# Summary
n_id_preserved = (identity_df['identity_preserved'] == 1).sum() if len(identity_df) > 0 else 0
n_cg_preserved = (identity_df['cg_preserved'] == 1).sum() if len(identity_df) > 0 else 0

print(f'\nIdentity preservation across {len(identity_df)} chains:')
print(f'  Geometric identity preserved: {n_id_preserved}/{len(identity_df)} ({100*n_id_preserved/len(identity_df):.1f}%)')
print(f'  CG rate preserved: {n_cg_preserved}/{len(identity_df)} ({100*n_cg_preserved/len(identity_df):.1f}%)')

if len(identity_df) > 0:
    print(f'\nTop identity-preserving chains:')
    for _, r in identity_df.sort_values('chain_identity_similarity', ascending=False).head(5).iterrows():
        print(f'  {r["chain"]:80s}: id_sim={r["chain_identity_similarity"]:.4f} CG_retention={r["chain_cg_retention"]:.3f}')
    
    print(f'\nWorst identity-preserving chains:')
    for _, r in identity_df.sort_values('chain_identity_similarity', ascending=True).head(5).iterrows():
        print(f'  {r["chain"]:80s}: id_sim={r["chain_identity_similarity"]:.4f} CG_retention={r["chain_cg_retention"]:.3f}')

# Correlation: does geometric identity correlate with CG retention?
if len(identity_df) > 0:
    from scipy.stats import pearsonr
    corr, p_val = pearsonr(identity_df['chain_identity_similarity'], identity_df['chain_cg_retention'])
    print(f'\nGeometric identity vs CG retention: r={corr:.4f} p={p_val:.4f}')

# Save summaries
cg_i3 = trans_geo_df[trans_geo_df['process_regime'] == 'CG']
nc_i3 = trans_geo_df[trans_geo_df['process_regime'] != 'CG']
h3_h4_summary = {
    'phase': 'I3+I4 (revised)',
    'operator_transition_geometry': {
        'n_systems': len(trans_geo_df),
        'method': 'cross-domain k-nearest neighborhoods in combined organizational state space',
        'cg_vs_noncg': {
            col: {
                'CG_mean': round(float(cg_i3[col].mean()), 4),
                'nonCG_mean': round(float(nc_i3[col].mean()), 4),
                'ratio': round(float(cg_i3[col].mean() / max(nc_i3[col].mean(), 1e-10)), 3),
            } for col in ['operator_continuity','operator_rupture','operator_curvature',
                         'transition_smoothness','recursive_closure','operator_reversibility',
                         'compositional_stability','operator_neighborhood_entropy']
        },
    },
    'recursive_identity': {
        'n_chains_tested': len(identity_df),
        'n_geometric_identity_preserved': int(n_id_preserved),
        'n_cg_rate_preserved': int(n_cg_preserved),
        'identity_cg_correlation': float(corr) if len(identity_df) > 0 else None,
    },
}
with open(f'{BASE}/summaries/h3_h4_summary.json', 'w') as f:
    json.dump(h3_h4_summary, f, indent=2)
print(f'\nI3+I4 (REVISED) COMPLETE')
