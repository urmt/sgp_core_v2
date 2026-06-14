"""
Phase J5+J6 — Organizational Symmetry + Null Program.

J5: Test composition symmetry, directional asymmetry, reversibility symmetry.
    Does CG emerge when symmetries partially break?

J6: Destroy recursive ordering. Preserve distributions. Do invariants vanish?
"""
import numpy as np, pandas as pd, os, json, warnings
from sklearn.utils import shuffle
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseJ_invariants'
PI = '/home/student/sgp_core_v2/phases/phaseI_operator_algebra'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

print('='*70)
print('PHASE J5 — ORGANIZATIONAL SYMMETRY')
print('Test symmetry properties of operator compositions')
print('='*70)

comp_df = pd.read_csv(f'{PI}/outputs/phaseI_composition_results.csv')
conserv_df = pd.read_csv(f'{BASE}/outputs/phaseJ_conservation_collapse.csv')
inv_df = pd.read_csv(f'{BASE}/outputs/phaseJ_transform_invariants.csv')

# ====================================================
# J5: SYMMETRY TESTS
# ====================================================

# 1. Composition symmetry: A∘B vs B∘A
# For each (domain_A, domain_B) pair, we have both orderings
# Measure correlation between A-first and B-first
symmetry_records = []

pairs = comp_df.groupby(['domain_A', 'domain_B'])
for (d1, d2), grp in pairs:
    if len(grp) < 2:
        # Only one ordering found, skip
        continue
    
    # Check if we have both orderings
    order_a = grp[grp['operator_A'] == grp['operator_A'].iloc[0]]
    order_b = grp[grp['operator_B'] == order_a['operator_A'].iloc[0]] if len(grp[grp['operator_B'] == order_a['operator_A'].iloc[0]]) > 0 else None
    
    if order_b is not None and len(order_b) > 0:
        cg_a = order_a['cg_preservation_ratio'].mean()
        cg_b = order_b['cg_preservation_ratio'].mean()
        symmetry = 1 - abs(cg_a - cg_b)  # 1 = perfect symmetry
    else:
        cg_a = grp['cg_preservation_ratio'].mean()
        cg_b = cg_a
        symmetry = 1.0  # assume symmetric if only one ordering found
    
    grp_conserv = conserv_df[(conserv_df['domain_A'] == d1) & (conserv_df['domain_B'] == d2)]
    classification = grp_conserv['classification'].iloc[0] if len(grp_conserv) > 0 else 'unknown'
    
    symmetry_records.append({
        'domain_A': d1, 'domain_B': d2,
        'cg_a_first': round(cg_a, 4),
        'cg_b_first': round(cg_b, 4),
        'composition_symmetry': round(symmetry, 4),
        'classification': classification,
    })

sym_df = pd.DataFrame(symmetry_records)
sym_df.to_csv(f'{BASE}/outputs/phaseJ_symmetry.csv', index=False)
print(f'Symmetry records: {len(sym_df)} domain pairs')

print('\n=== COMPOSITION SYMMETRY ===')
print(f'Mean symmetry: {sym_df["composition_symmetry"].mean():.4f}')
asym_pairs = sym_df[sym_df['composition_symmetry'] < 0.95]
print(f'Asymmetric pairs (symmetry < 0.95): {len(asym_pairs)}/{len(sym_df)}')
for _, r in asym_pairs.iterrows():
    print(f'  {r["domain_A"]:20s} + {r["domain_B"]:20s}: sym={r["composition_symmetry"]:.3f} '
          f'A={r["cg_a_first"]:.3f} B={r["cg_b_first"]:.3f}')

# 2. Directional asymmetry: does CG depend on composition direction?
print('\n=== DIRECTIONAL ASYMMETRY ===')
print(f'Mean A-first CG: {sym_df["cg_a_first"].mean():.4f}')
print(f'Mean B-first CG: {sym_df["cg_b_first"].mean():.4f}')

# 3. Reversibility symmetry: does CG correlate with reversibility?
print('\n=== REVERSIBILITY SYMMETRY ===')
# From conservation data: does geo_survival ≈ cg_survival?
gap = (conserv_df['geo_survival'] - conserv_df['cg_survival']).mean()
print(f'Mean geo-CG gap: {gap:.4f} (positive = geometry outlives generativity)')
corr, p = pearsonr(conserv_df['geo_survival'], conserv_df['cg_survival'])
print(f'Geometry-CG correlation: r={corr:.4f} p={p:.4f}')

# 4. Recursive symmetry: does A∘B∘A ≈ A?
# Use identity_df chain data
identity_df = pd.read_csv(f'{PI}/outputs/phaseI_recursive_identity.csv')
if len(identity_df) > 0 and 'chain_identity_similarity' in identity_df.columns:
    print(f'\n=== RECURSIVE SYMMETRY (A∘B∘A ≈ A) ===')
    # Find chains where domain_A = domain_C (recursive closure)
    recursive_chains = identity_df[identity_df['domain_A'] == identity_df['domain_C']]
    if len(recursive_chains) > 0:
        mean_id = recursive_chains['chain_identity_similarity'].mean()
        print(f'  Chains with A=C: {len(recursive_chains)}')
        print(f'  Mean identity retention: {mean_id:.4f}')
        # CG retention in recursive chains
        if 'chain_cg_retention' in recursive_chains.columns:
            print(f'  Mean CG retention: {recursive_chains["chain_cg_retention"].mean():.4f}')
    else:
        print(f'  No chains found with A=C (recursive closure)')

# 5. Symmetry breaking and CG emergence
print('\n=== SYMMETRY BREAKING AND CG EMERGENCE ===')
# Does CG emerge preferentially when symmetries partially break?
# Test: is CG rate higher for asymmetric compositions?
for label, subset in [('All', sym_df), ('Asymmetric (<0.95)', asym_pairs)]:
    cg_rates = []
    for _, r in subset.iterrows():
        # Find CG_rate for this composition
        cr = conserv_df[(conserv_df['domain_A'] == r['domain_A']) & (conserv_df['domain_B'] == r['domain_B'])]
        if len(cr) > 0:
            cg_rates.append(cr['cg_survival'].mean())
    if cg_rates:
        print(f'  {label:25s}: mean CG survival={np.mean(cg_rates):.4f} (n={len(cg_rates)})')

# Correlation: symmetry vs CG survival
sym_vs_cg = []
for _, r in sym_df.iterrows():
    cr = conserv_df[(conserv_df['domain_A'] == r['domain_A']) & (conserv_df['domain_B'] == r['domain_B'])]
    if len(cr) > 0:
        sym_vs_cg.append({'symmetry': r['composition_symmetry'], 'cg_survival': cr['cg_survival'].mean()})
if sym_vs_cg:
    svc = pd.DataFrame(sym_vs_cg)
    corr2, p2 = pearsonr(svc['symmetry'], svc['cg_survival'])
    print(f'\n  Symmetry-CG correlation: r={corr2:.4f} p={p2:.4f}')
    if corr2 < 0:
        print(f'  Interpretation: CG emerges when symmetry BREAKS (negative correlation)')
    elif corr2 > 0:
        print(f'  Interpretation: CG associates with symmetry PRESERVATION')
    else:
        print(f'  Interpretation: No relationship between symmetry and CG')

# ====================================================
# J6: NULL PROGRAM
# ====================================================
print('\n' + '='*70)
print('PHASE J6 — NULL PROGRAM')
print('Destroy recursive ordering. Preserve distributions.')
print('='*70)

N_NULL = 30

# Build domain_profiles first (needed by nulls)
all_comp_domains = list(set(comp_df['domain_A'].tolist() + comp_df['domain_B'].tolist()))
domains = sorted(all_comp_domains)
domain_profiles = {}
for domain in all_comp_domains:
    dd = inv_df[(inv_df['domain_A'] == domain) | (inv_df['domain_B'] == domain)]
    cg_vals = dd[dd['property'] == 'cg_rate']['val_A'].tolist() + dd[dd['property'] == 'cg_rate']['val_B'].tolist()
    domain_profiles[domain] = {'cg_rate': float(np.mean(cg_vals)) if cg_vals else 0.1}

# Reference values
ref_cg_invariance = inv_df[inv_df['property'] == 'cg_rate']['invariance'].mean()
ref_continuity_invariance = inv_df[inv_df['property'] == 'mean_continuity']['invariance'].mean()

null_records = []
for null_idx in range(N_NULL):
    if null_idx % 10 == 0: print(f'  Null {null_idx}/{N_NULL}')
    
    # N1: Shuffle domain labels in composition (destroy operator identity)
    n1_comp = comp_df.copy()
    all_domains = list(set(n1_comp['domain_A'].tolist() + n1_comp['domain_B'].tolist()))
    shuffled_domains = shuffle(all_domains)
    domain_map = dict(zip(all_domains, shuffled_domains))
    n1_comp['domain_A'] = n1_comp['domain_A'].map(domain_map)
    n1_comp['domain_B'] = n1_comp['domain_B'].map(domain_map)
    
    # Recompute invariance under shuffled labels
    n1_inv = []
    for _, r in n1_comp.iterrows():
        d1, d2 = r['domain_A'], r['domain_B']
        # Get properties from original domain data but with SHUFFLED labels
        v1_cg = domain_profiles[d1]['cg_rate'] if d1 in domain_profiles else 0.1
        v2_cg = domain_profiles[d2]['cg_rate'] if d2 in domain_profiles else 0.1
        inv = 1 - abs(v1_cg - v2_cg) / max(max(v1_cg, v2_cg), 0.001)
        n1_inv.append(inv)
    
    # N2: Shuffle composition property values while preserving marginals
    n2_inv = []
    for _, r in comp_df.iterrows():
        d1, d2 = r['domain_A'], r['domain_B']
        # Random permutation of domain properties
        v1 = np.random.permutation([domain_profiles[d]['cg_rate'] for d in domains])[0]
        v2 = np.random.permutation([domain_profiles[d]['cg_rate'] for d in domains])[0]
        inv = 1 - abs(v1 - v2) / max(max(v1, v2), 0.001)
        n2_inv.append(inv)
    
    # N3: Shuffle the composition pairs themselves (random pairings)
    n3_comp = comp_df.copy()
    random_as = shuffle(n3_comp['domain_A'].values)
    random_bs = shuffle(n3_comp['domain_B'].values)
    n3_comp['domain_A'] = random_as
    n3_comp['domain_B'] = random_bs
    
    n3_inv = []
    for _, r in n3_comp.iterrows():
        d1, d2 = r['domain_A'], r['domain_B']
        v1 = domain_profiles[d1]['cg_rate'] if d1 in domain_profiles else 0.1
        v2 = domain_profiles[d2]['cg_rate'] if d2 in domain_profiles else 0.1
        inv = 1 - abs(v1 - v2) / max(max(v1, v2), 0.001)
        n3_inv.append(inv)
    
    null_records.append({
        'null_iteration': int(null_idx),
        'n1_shuffled_labels_cg_invariance': float(np.mean(n1_inv)),
        'n2_shuffled_properties_cg_invariance': float(np.mean(n2_inv)),
        'n3_shuffled_pairs_cg_invariance': float(np.mean(n3_inv)),
    })

null_df = pd.DataFrame(null_records)
null_df.to_csv(f'{BASE}/outputs/phaseJ_nulls.csv', index=False)
print(f'\nNull program saved: {len(null_df)} iterations')

# Verification
print('\n=== NULL VERIFICATION ===')
true_cg_inv = float(inv_df[inv_df['property'] == 'cg_rate']['invariance'].mean())
true_cont_inv = float(inv_df[inv_df['property'] == 'mean_continuity']['invariance'].mean())

for null_label, col in [('Shuffled labels', 'n1_shuffled_labels_cg_invariance'),
                         ('Shuffled properties', 'n2_shuffled_properties_cg_invariance'),
                         ('Shuffled pairs', 'n3_shuffled_pairs_cg_invariance')]:
    n_mean = null_df[col].mean()
    n_std = null_df[col].std()
    z = (true_cg_inv - n_mean) / max(n_std, 1e-10)
    print(f'  {null_label:25s}: true={true_cg_inv:.4f} null={n_mean:.4f}±{n_std:.4f} z={z:.2f} {"SURVIVED" if abs(z) > 2 else "FAILED"}')

h5_h6_summary = {
    'phase': 'J5+J6',
    'symmetry': {
        'mean_composition_symmetry': float(sym_df['composition_symmetry'].mean()),
        'n_asymmetric_pairs': int(len(asym_pairs)),
        'geometry_cg_correlation': float(corr),
        'symmetry_cg_correlation': float(corr2) if sym_vs_cg else None,
    },
    'nulls': {
        'n_iterations': N_NULL,
        'true_cg_invariance': float(true_cg_inv),
        'shuffled_labels_z': float((true_cg_inv - null_df['n1_shuffled_labels_cg_invariance'].mean()) / max(null_df['n1_shuffled_labels_cg_invariance'].std(), 1e-10)),
        'shuffled_properties_z': float((true_cg_inv - null_df['n2_shuffled_properties_cg_invariance'].mean()) / max(null_df['n2_shuffled_properties_cg_invariance'].std(), 1e-10)),
        'shuffled_pairs_z': float((true_cg_inv - null_df['n3_shuffled_pairs_cg_invariance'].mean()) / max(null_df['n3_shuffled_pairs_cg_invariance'].std(), 1e-10)),
    },
}
with open(f'{BASE}/summaries/h5_h6_summary.json', 'w') as f:
    json.dump(h5_h6_summary, f, indent=2)
print(f'\nJ5+J6 COMPLETE')
