"""
Phase J1+J2 — Transformational Invariants + Conservation vs Collapse.

J1: Which organizational properties remain invariant under recursive transformation?
J2: Classify transformations by what survives and what collapses.

Anti-drift: Persistent geometry ≠ persistent generativity. They are SEPARATE invariants.
"""
import numpy as np, pandas as pd, os, json, warnings
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseJ_invariants'
PI = '/home/student/sgp_core_v2/phases/phaseI_operator_algebra'
PC = '/home/student/sgp_core_v2/phases/phaseC'
PE = '/home/student/sgp_core_v2/phases/phaseE'
PG = '/home/student/sgp_core_v2/phases/phaseG'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

print('='*70)
print('PHASE J1 — TRANSFORMATIONAL INVARIANTS')
print('What organizational properties remain conserved under transformation?')
print('='*70)

# Load Phase I data
comp_df = pd.read_csv(f'{PI}/outputs/phaseI_composition_results.csv')
identity_df = pd.read_csv(f'{PI}/outputs/phaseI_recursive_identity.csv')
op_df = pd.read_csv(f'{PI}/outputs/phaseI_operator_signatures.csv')
trans_geo = pd.read_csv(f'{PI}/outputs/phaseI_transition_geometry.csv')

# Load per-domain properties
df = pd.read_csv(f'{PC}/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
curv = pd.read_csv(f'{PE}/processed/curvature_metrics.csv')
poss = pd.read_csv(f'{PE}/processed/possibility_metrics.csv')
phaseG = pd.read_csv(f'{PG}/processed/coherence_fertility_phase_space.csv')
merged = df.merge(phaseG, on=['sys_idx','domain']).merge(curv, on=['sys_idx','domain']).merge(poss, on=['sys_idx','domain'])
merged['process_regime'] = merged['region'].map({'constrained_generative':'CG','rigid_coherence':'RG',
                                                   'chaotic_fertility':'CH','collapse':'CL'})
domains = sorted(merged['domain'].unique())

# Per-domain baseline properties
domain_props = {}
for domain in domains:
    dm = merged[merged['domain'] == domain]
    cg = dm[dm['process_regime'] == 'CG']
    domain_props[domain] = {
        'cg_rate': len(cg) / len(dm),
        'mean_coherence': dm['coherence'].mean(),
        'mean_fertility': dm['fertility'].mean(),
        'mean_reversibility': dm['poss_stability_fertility_coupling'].mean(),
        'mean_recursive_closure': dm['poss_stability_fertility_coupling'].mean(),
        'mean_continuity': trans_geo[trans_geo['domain']==domain]['operator_continuity'].mean() if len(trans_geo[trans_geo['domain']==domain]) > 0 else 0,
        'mean_reconstruction': None,  # will fill from H2 recovery if available
    }

# Load H2 recovery data for reconstruction ability
H2 = '/home/student/sgp_core_v2/phases/phaseH2_process'
recovery_path = f'{H2}/outputs/recovery_metrics.csv'
persist_path = f'{H2}/outputs/persistence_metrics.csv'
if os.path.exists(recovery_path) and os.path.exists(persist_path):
    recovery_df = pd.read_csv(recovery_path)
    persist_df = pd.read_csv(persist_path)
    for domain in domains:
        rdf = recovery_df[recovery_df['domain'] == domain]
        pdf = persist_df[persist_df['domain'] == domain]
        if len(rdf) > 0 and rdf['recovery_possible'].max() >= 0:
            domain_props[domain]['mean_reconstruction'] = rdf[rdf['recovery_possible']==1]['recovery_probability'].mean() if len(rdf[rdf['recovery_possible']==1]) > 0 else 0
        else:
            domain_props[domain]['mean_reconstruction'] = 0
        domain_props[domain]['persistence_half_life'] = pdf['persistence_half_life'].mean() if len(pdf) > 0 else 0
else:
    for domain in domains:
        domain_props[domain]['mean_reconstruction'] = 0
        domain_props[domain]['persistence_half_life'] = 0

# ====================================================
# J1: TRANSFORMATIONAL INVARIANTS
# ====================================================
# For each composition, measure what properties are invariant
# (survive the transformation from A to A∘B)

invariant_records = []
for _, r in comp_df.iterrows():
    d1, d2 = r['domain_A'], r['domain_B']
    p1, p2 = domain_props[d1], domain_props[d2]
    
    # How much does each property change under composition?
    # Composition value = average of the two domains
    # Invariance = 1 - relative_change (1 = perfectly invariant, 0 = completely transformed)
    
    props_to_check = ['cg_rate', 'mean_coherence', 'mean_fertility', 'mean_reversibility',
                      'mean_recursive_closure', 'mean_continuity', 'mean_reconstruction']
    
    for prop in props_to_check:
        v1 = p1.get(prop, 0) or 0
        v2 = p2.get(prop, 0) or 0
        comp_val = (v1 + v2) / 2
        
        # Invariance: how much does composition differ from the ORIGINAL domain values?
        # If both domains have similar values, composition preserves the property.
        # If they differ, composition transforms it.
        max_val = max(v1, v2, 0.001)
        change = abs(comp_val - v1) / max_val + abs(comp_val - v2) / max_val
        invariance = max(0, 1 - change / 2)
        
        invariant_records.append({
            'domain_A': d1, 'domain_B': d2,
            'operator_A': r['operator_A'], 'operator_B': r['operator_B'],
            'property': prop,
            'val_A': round(v1, 4),
            'val_B': round(v2, 4),
            'comp_val': round(comp_val, 4),
            'invariance': round(invariance, 4),
        })

inv_df = pd.DataFrame(invariant_records)
inv_df.to_csv(f'{BASE}/outputs/phaseJ_transform_invariants.csv', index=False)
print(f'\nInvariant records: {len(inv_df)}')

# Which properties are most invariant under composition?
print('\n=== PROPERTY INVARIANCE RANKING ===')
prop_means = inv_df.groupby('property')['invariance'].agg(['mean','std','count'])
for prop in sorted(prop_means.index, key=lambda p: prop_means.loc[p, 'mean'], reverse=True):
    m = prop_means.loc[prop]
    print(f'  {prop:30s}: invariance={m["mean"]:.4f}±{m["std"]:.4f}')

# ====================================================
# J2: CONSERVATION VS COLLAPSE CLASSIFICATION
# ====================================================
print('\n' + '='*70)
print('PHASE J2 — CONSERVATION VS COLLAPSE')
print('Identify transformations where geometry survives but generativity collapses')
print('='*70)

# For each chain, classify into:
# 1. dead_coherence: geometry preserved, CG collapsed
# 2. chaotic_fertility: fertility preserved, coherence collapsed
# 3. maintained_CG: both preserved
# 4. dissolving_identity: geometry collapsed, but CG preserved
# 5. reconstructive: CG recovers after initial collapse

# Use composition + identity data
conservation_records = []
for _, r in comp_df.iterrows():
    d1, d2 = r['domain_A'], r['domain_B']
    p1, p2 = domain_props[d1], domain_props[d2]
    
    # Geometry survival: does reversibility survive composition?
    v1_r = p1.get('mean_reversibility', 0) or 0
    v2_r = p2.get('mean_reversibility', 0) or 0
    comp_r = (v1_r + v2_r) / 2
    geo_survival = min(comp_r / max(max(v1_r, v2_r), 0.01), 1.0) if max(v1_r, v2_r) > 0 else 0
    
    # Generativity survival: does CG rate survive composition?
    v1_cg = p1.get('cg_rate', 0)
    v2_cg = p2.get('cg_rate', 0)
    comp_cg = (v1_cg + v2_cg) / 2
    cg_survival = min(comp_cg / max(max(v1_cg, v2_cg), 0.01), 1.0) if max(v1_cg, v2_cg) > 0 else 0
    
    # Coherence survival
    v1_coh = p1.get('mean_coherence', 0)
    v2_coh = p2.get('mean_coherence', 0)
    comp_coh = (v1_coh + v2_coh) / 2
    coh_survival = min(comp_coh / max(max(v1_coh, v2_coh), 0.01), 1.0) if max(v1_coh, v2_coh) > 0 else 0
    
    # Fertility survival
    v1_fer = p1.get('mean_fertility', 0)
    v2_fer = p2.get('mean_fertility', 0)
    comp_fer = (v1_fer + v2_fer) / 2
    fer_survival = min(comp_fer / max(max(v1_fer, v2_fer), 0.01), 1.0) if max(v1_fer, v2_fer) > 0 else 0
    
    # Classification
    geo_ok = geo_survival > 0.5
    cg_ok = cg_survival > 0.5
    coh_ok = coh_survival > 0.5
    fer_ok = fer_survival > 0.5
    
    if geo_ok and cg_ok and coh_ok and fer_ok:
        classification = 'maintained_CG'
    elif geo_ok and not cg_ok and coh_ok and not fer_ok:
        classification = 'dead_coherence'
    elif geo_ok and not cg_ok and not coh_ok and fer_ok:
        classification = 'chaotic_fertility'
    elif not geo_ok and cg_ok:
        classification = 'dissolving_identity'
    elif not geo_ok and not cg_ok and coh_ok and fer_ok:
        classification = 'reconstructive_potential'
    else:
        classification = 'mixed_collapse'
    
    conservation_records.append({
        'domain_A': d1, 'domain_B': d2,
        'operator_A': r['operator_A'], 'operator_B': r['operator_B'],
        'classification': classification,
        'geo_survival': round(geo_survival, 4),
        'cg_survival': round(cg_survival, 4),
        'coh_survival': round(coh_survival, 4),
        'fer_survival': round(fer_survival, 4),
        'comp_cg_rate': round(r['cg_preservation_ratio'], 4),
    })

conserv_df = pd.DataFrame(conservation_records)
conserv_df.to_csv(f'{BASE}/outputs/phaseJ_conservation_collapse.csv', index=False)
print(f'\nConservation records: {len(conserv_df)}')

# Classification distribution
print('\n=== CONSERVATION VS COLLAPSE CLASSIFICATION ===')
class_counts = conserv_df['classification'].value_counts()
for cls, cnt in class_counts.items():
    pct = 100 * cnt / len(conserv_df)
    print(f'  {cls:25s}: {cnt} ({pct:.1f}%)')

# Which compositions produce each class?
print('\n=== MAINTAINED CG COMPOSITIONS ===')
mc = conserv_df[conserv_df['classification'] == 'maintained_CG']
for _, r in mc.iterrows():
    print(f'  {r["domain_A"]:20s} + {r["domain_B"]:20s} ({r["operator_A"]:15s}+{r["operator_B"]:15s}) '
          f'geo={r["geo_survival"]:.3f} cg={r["cg_survival"]:.3f}')

print('\n=== DEAD COHERENCE COMPOSITIONS ===')
dc = conserv_df[conserv_df['classification'] == 'dead_coherence']
for _, r in dc.iterrows():
    print(f'  {r["domain_A"]:20s} + {r["domain_B"]:20s} ({r["operator_A"]:15s}+{r["operator_B"]:15s}) '
          f'geo={r["geo_survival"]:.3f} coh={r["coh_survival"]:.3f} fer={r["fer_survival"]:.3f}')

# The key finding: geometry surviving while generativity collapses
print('\n=== FORM-FUNCTION UNCOUPLING (geometry survives, CG collapses) ===')
ff_uncoupled = conserv_df[(conserv_df['geo_survival'] > 0.7) & (conserv_df['cg_survival'] < 0.3)]
print(f'  {len(ff_uncoupled)}/{len(conserv_df)} compositions ({100*len(ff_uncoupled)/len(conserv_df):.1f}%)')
for _, r in ff_uncoupled.iterrows():
    print(f'  {r["domain_A"]:20s} + {r["domain_B"]:20s}: geo={r["geo_survival"]:.3f} cg={r["cg_survival"]:.3f}')

print('\n=== CG-GEOMETRY COUPLED (both survive) ===')
cg_geo_coupled = conserv_df[(conserv_df['geo_survival'] > 0.7) & (conserv_df['cg_survival'] > 0.7)]
print(f'  {len(cg_geo_coupled)}/{len(conserv_df)} compositions ({100*len(cg_geo_coupled)/len(conserv_df):.1f}%)')

# Summary
h1_h2_summary = {
    'phase': 'J1+J2',
    'property_invariance_ranking': {str(k): float(v['mean']) for k, v in prop_means.iterrows()},
    'most_invariant_property': str(prop_means['mean'].idxmax()),
    'least_invariant_property': str(prop_means['mean'].idxmin()),
    'conservation_classification': {str(k): int(v) for k, v in class_counts.items()},
    'form_function_uncoupling_rate': round(100 * len(ff_uncoupled) / len(conserv_df), 1),
    'form_function_coupling_rate': round(100 * len(cg_geo_coupled) / len(conserv_df), 1),
}
with open(f'{BASE}/summaries/h1_h2_summary.json', 'w') as f:
    json.dump(h1_h2_summary, f, indent=2)
print(f'\nJ1+J2 COMPLETE')
