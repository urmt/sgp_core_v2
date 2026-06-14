"""
Phase I1+I2 — Operator Extraction + Composition Tests.

Analyzing organizational TRANSFORMATION classes, not equations.
Operators are organizational operation types that transform coherence-fertility geometry.

Anti-drift check: Am I analyzing PROCESS or collapsing PROCESS into STATIC STATE?
Answer: Operators describe how organizational processes TRANSFORM, not what states they occupy.
"""
import numpy as np, pandas as pd, os, json, warnings
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseI_operator_algebra'
PC = '/home/student/sgp_core_v2/phases/phaseC'
PE = '/home/student/sgp_core_v2/phases/phaseE'
PG = '/home/student/sgp_core_v2/phases/phaseG'
PF = '/home/student/sgp_core_v2/phases/phaseF'
PH2 = '/home/student/sgp_core_v2/phases/phaseH2_process'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

# Load all relevant data
df = pd.read_csv(f'{PC}/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
curv = pd.read_csv(f'{PE}/processed/curvature_metrics.csv')
poss = pd.read_csv(f'{PE}/processed/possibility_metrics.csv')
phaseG = pd.read_csv(f'{PG}/processed/coherence_fertility_phase_space.csv')
op_sig = pd.read_csv(f'{PF}/processed/operator_signatures.csv')
geom = pd.read_csv(f'{PF}/processed/family_geometry_classes.csv')

merged = df.merge(phaseG, on=['sys_idx','domain']).merge(curv, on=['sys_idx','domain']).merge(poss, on=['sys_idx','domain'])
merged['process_regime'] = merged['region'].map({'constrained_generative':'CG','rigid_coherence':'RG',
                                                   'chaotic_fertility':'CH','collapse':'CL'})

# Load H2 outputs if available
h2_path = f'{PH2}/outputs/transition_geometry.csv'
h2_bnd = f'{PH2}/outputs/transition_boundary_metrics.csv'
h2_persist = f'{PH2}/outputs/persistence_metrics.csv'
h2_recovery = f'{PH2}/outputs/recovery_metrics.csv'
geo_df = pd.read_csv(h2_path) if os.path.exists(h2_path) else None
bnd_df = pd.read_csv(h2_bnd) if os.path.exists(h2_bnd) else None
persist_df = pd.read_csv(h2_persist) if os.path.exists(h2_persist) else None
recovery_df = pd.read_csv(h2_recovery) if os.path.exists(h2_recovery) else None

domains = sorted(merged['domain'].unique())
N_DOMAINS = len(domains)

print('='*70)
print('PHASE I1 — ORGANIZATIONAL OPERATOR EXTRACTION')
print('Operators: organizational transformation classes, not equations')
print('='*70)
print(f'\nLoading data across {N_DOMAINS} domains')

# ====================================================
# SECTION I1: OPERATOR EXTRACTION
# ====================================================
# Each operator is scored per domain as a continuous value [0,1]
# representing how strongly that transformation type characterizes the domain.

operator_records = []

for domain in domains:
    dm = merged[merged['domain'] == domain]
    
    # --- Operator 1: ADDITIVE (linear composition) ---
    # Phase F additive_linear_r2 measures how well linear model predicts behavior
    f_row = op_sig[op_sig['domain'] == domain]
    additive_score = float(f_row['additive_linear_r2'].iloc[0]) if len(f_row) > 0 else 0
    
    # --- Operator 2: MULTIPLICATIVE (nonlinear gain) ---
    # Phase F multiplicative_log_log_slope magnitude — log-log slope ≠ 0 = multiplicative
    mult_slope = float(f_row['multiplicative_log_log_slope'].iloc[0]) if len(f_row) > 0 else 0
    multiplicative_score = min(1.0, abs(mult_slope) / 10.0)
    
    # --- Operator 3: BRANCHING (diversification) ---
    # Mean poss_branching_diversity across all systems in domain
    branching_score = float(dm['poss_branching_diversity'].mean())
    # Also from H2 if available
    if geo_df is not None:
        gd = geo_df[geo_df['domain'] == domain]
        if len(gd) > 0:
            branching_score = float(gd['transition_branching'].mean())
    
    # --- Operator 4: SYNCHRONIZATION (phase locking) ---
    # From Phase F network_sync_coupling
    sync_score = float(f_row['network_sync_coupling'].iloc[0]) if len(f_row) > 0 else 0
    
    # --- Operator 5: RECURSIVE FEEDBACK (self-referential) ---
    # High transition reversibility + stability-fertility coupling = recursive closure
    feedback_score = float(dm['poss_stability_fertility_coupling'].mean())
    # Also from H2 if available
    if geo_df is not None:
        gd = geo_df[geo_df['domain'] == domain]
        if len(gd) > 0:
            feedback_score = float(gd['transition_reversibility'].mean())
    
    # --- Operator 6: COMPETITIVE EXCLUSION (selection/elimination) ---
    # Low novelty rate + low diversity = strong exclusion
    # Inversely related to fertility_novelty_rate (low novelty = strong exclusion)
    exclusion_score = 1.0 - float(dm['fertility_novelty_rate'].mean())
    # Also incorporate stability_fertility_coupling (tight coupling = exclusion)
    exclusion_score = 0.5 * exclusion_score + 0.5 * (1.0 - float(dm['poss_reachable_volume'].mean()))
    
    # --- Operator 7: DIFFUSION (spread across space) ---
    # High geodesic_instab = high sensitivity to path = diffusion-like spreading
    diffusion_score = float(np.log1p(dm['geodesic_instab'].mean())) / 5.0
    diffusion_score = min(1.0, diffusion_score)
    
    # --- Operator 8: HIERARCHICAL NESTING ---
    # From Phase F: tree_depth and tree_r2
    tree_depth = float(f_row['hierarchical_tree_depth'].iloc[0]) if len(f_row) > 0 else 0
    tree_r2 = float(f_row['hierarchical_tree_r2'].iloc[0]) if len(f_row) > 0 else 0
    hierarchy_score = float(np.sqrt(tree_r2 * (tree_depth / 20.0)))
    
    # --- Operator 9: CONSTRAINT PROPAGATION (rigidity transmission) ---
    # High process_rigidity = constraint propagates through system
    constraint_score = float(np.log1p(dm['jacobian_vol'].mean())) / 10.0
    constraint_score = min(1.0, constraint_score)
    
    # --- Operator 10: RESONANCE LOCKING ---
    # Tight stability-fertility coupling that persists across perturbations
    resonance_score = float(dm['poss_stability_fertility_coupling'].mean())
    # Weighted by how consistently this holds (low std = stable resonance)
    coupling_std = float(dm['poss_stability_fertility_coupling'].std())
    resonance_score = resonance_score * (1.0 / (1.0 + coupling_std))
    
    # Normalize all scores to [0, 1] via their global distributions
    operator_records.append({
        'domain': domain,
        'op_additive': additive_score,
        'op_multiplicative': multiplicative_score,
        'op_branching': branching_score,
        'op_synchronization': sync_score,
        'op_recursive_feedback': feedback_score,
        'op_competitive_exclusion': exclusion_score,
        'op_diffusion': diffusion_score,
        'op_hierarchical_nesting': hierarchy_score,
        'op_constraint_propagation': constraint_score,
        'op_resonance_locking': resonance_score,
    })

op_df = pd.DataFrame(operator_records)

# Normalize each operator column to [0, 1] across domains
op_cols = [c for c in op_df.columns if c.startswith('op_')]
scaler = MinMaxScaler()
op_df[op_cols] = scaler.fit_transform(op_df[op_cols])
op_df['dominant_operator'] = op_df[op_cols].idxmax(axis=1)

op_df.to_csv(f'{BASE}/outputs/phaseI_operator_signatures.csv', index=False)
print(f'\nOperator signatures saved: {len(op_df)} domains × {len(op_cols)} operators')

print('\n=== OPERATOR TAXONOMY ===')
for _, r in op_df.iterrows():
    dominant = r['dominant_operator']
    top_ops = r[op_cols].sort_values(ascending=False).head(3)
    print(f'\n{str(r["domain"]):25s} [DOMINANT: {dominant[3:16]}]')
    for op, score in top_ops.items():
        print(f'  {op[3:30]:30s}: {score:.3f}')

# ====================================================
# SECTION I2: OPERATOR COMPOSITION TESTS
# ====================================================
print('\n' + '='*70)
print('PHASE I2 — OPERATOR COMPOSITION')
print('Test whether compositions preserve CG')
print('='*70)

# Composition: Combine two domains' operators. 
# Treat each domain as an "operator bundle."
# Composition test: does the UNION of two domains' organizational processes
# preserve CG better than either individually?

# Define per-domain CG metrics
cg_by_domain = {}
for domain in domains:
    dm = merged[merged['domain'] == domain]
    cg = dm[dm['process_regime'] == 'CG']
    cg_by_domain[domain] = {
        'cg_count': len(cg),
        'cg_rate': len(cg) / len(dm),
        'cg_continuity': float(geo_df[geo_df['domain']==domain]['transition_continuity'].mean()) if geo_df is not None and len(geo_df[geo_df['domain']==domain]) > 0 else None,
        'cg_reversibility': float(geo_df[geo_df['domain']==domain]['transition_reversibility'].mean()) if geo_df is not None and len(geo_df[geo_df['domain']==domain]) > 0 else None,
    }

# For each operator pair, test composition effect
from itertools import combinations
comp_records = []

for op_a, op_b in combinations(op_cols, 2):
    # Find top-2 domains for each operator
    top_a = op_df.nlargest(2, op_a)
    top_b = op_df.nlargest(2, op_b)
    
    # Can't compose same domain with itself
    for i, d1 in top_a.iterrows():
        for j, d2 in top_b.iterrows():
            if d1['domain'] == d2['domain']:
                continue
            
            domain_a = d1['domain']
            domain_b = d2['domain']
            
            # Composition metric: do paired domains produce higher CG properties
            # than either alone? Use CG rate + continuity as indicators.
            ca = cg_by_domain[domain_a]
            cb = cg_by_domain[domain_b]
            
            # Composition: average of both domains' CG rates (union proxy)
            comp_cg_rate = (ca['cg_rate'] + cb['cg_rate']) / 2
            
            # Continuity retention under composition
            if ca['cg_continuity'] is not None and cb['cg_continuity'] is not None:
                comp_continuity = (ca['cg_continuity'] + cb['cg_continuity']) / 2
            else:
                comp_continuity = None
            
            if ca['cg_reversibility'] is not None and cb['cg_reversibility'] is not None:
                comp_reversibility = (ca['cg_reversibility'] + cb['cg_reversibility']) / 2
            else:
                comp_reversibility = None
            
            # Preservation ratio: does composition maintain CG better than individual?
            max_single_cg = max(ca['cg_rate'], cb['cg_rate'])
            preservation = comp_cg_rate / max(max_single_cg, 0.001)
            
            comp_records.append({
                'operator_A': op_a[3:],
                'operator_B': op_b[3:],
                'domain_A': domain_a,
                'domain_B': domain_b,
                'cg_rate_A': round(ca['cg_rate'], 4),
                'cg_rate_B': round(cb['cg_rate'], 4),
                'comp_cg_rate': round(comp_cg_rate, 4),
                'comp_continuity': round(comp_continuity, 4) if comp_continuity is not None else None,
                'comp_reversibility': round(comp_reversibility, 4) if comp_reversibility is not None else None,
                'cg_preservation_ratio': round(preservation, 4),
                'preserves_CG': int(preservation >= 0.8),
            })

comp_df = pd.DataFrame(comp_records)
comp_df.to_csv(f'{BASE}/outputs/phaseI_composition_results.csv', index=False)
print(f'\nComposition tests saved: {len(comp_df)} domain-operator pairs')

# Which operator compositions best preserve CG?
print('\nTop operator compositions preserving CG:')
preserving = comp_df[comp_df['preserves_CG'] == 1]
if len(preserving) > 0:
    for _, r in preserving.sort_values('cg_preservation_ratio', ascending=False).head(10).iterrows():
        print(f'  {r["operator_A"]:20s} + {r["operator_B"]:20s}: {r["domain_A"]:25s} + {r["domain_B"]:25s} '
              f'preservation={r["cg_preservation_ratio"]:.3f} CG_rate={r["comp_cg_rate"]:.3f}')

# By operator pair type (aggregating across domain pairs)
print('\nAggregate by operator pair type:')
op_pair_summary = comp_df.groupby(['operator_A', 'operator_B']).agg({
    'cg_preservation_ratio': ['mean', 'std', 'count'],
    'preserves_CG': 'sum',
}).round(4)

for (op_a, op_b), row in op_pair_summary.iterrows():
    n_preserved = row[('preserves_CG', 'sum')]
    n_total = row[('cg_preservation_ratio', 'count')]
    print(f'  {op_a:20s} + {op_b:20s}: '
          f'preservation={row[("cg_preservation_ratio", "mean")]:.3f}±{row[("cg_preservation_ratio", "std")]:.3f} '
          f'{int(n_preserved)}/{int(n_total)} preserved')

# Summary
h1_h2_summary = {
    'phase': 'I1+I2',
    'operators_extracted': op_cols,
    'per_domain_operators': {
        str(r['domain']): {
            'dominant': str(r['dominant_operator']),
            'top3': {c[3:]: round(float(r[c]), 3) for c in r[op_cols].sort_values(ascending=False).head(3).index}
        } for _, r in op_df.iterrows()
    },
    'composition_tests': {
        'n_pairs_tested': len(comp_df),
        'n_preserving_CG': int(len(preserving)),
        'best_composition': str(comp_df.loc[comp_df['cg_preservation_ratio'].idxmax(), ['operator_A','operator_B']].to_dict()) if len(comp_df) > 0 else None,
    },
}
with open(f'{BASE}/summaries/h1_h2_summary.json', 'w') as f:
    json.dump(h1_h2_summary, f, indent=2)
print(f'\nI1+I2 COMPLETE')
