"""
Phase M7+M8 — ORGANIZATIONAL COMPATIBILITY + ADVERSARIAL NULLS

M7: Which recursive organizations can sustain one another?
M8: Does mutual recursive stabilization disappear when ordering is destroyed?

NOT about compatibility in the social sense.
About whether recursive continuity processes can co-stabilize given their organizational structure.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseM_intersubjective'
PHL = '/home/student/sgp_core_v2/phases/phaseL_observer_emergence'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

pair_df = pd.read_csv(f'{BASE}/outputs/phaseM_shared_space.csv')
print(f'Loaded: {len(pair_df)} pairs')

# ====================================================
# M7: ORGANIZATIONAL COMPATIBILITY
# ====================================================
print('='*70)
print('PHASE M7 — ORGANIZATIONAL COMPATIBILITY')
print('Which recursive organizations can sustain one another?')
print('='*70)

# --- Closure compatibility ---
# Can two closure structures coexist without conflict?
pair_df['closure_compatibility'] = (
    pair_df['recursive_synchronization'] * (1 - abs(pair_df['mutual_anticipation'] - pair_df['co_adaptive_continuity']))
)

# --- Reconstruction compatibility ---
# Can both systems support each other's reconstruction?
pair_df['reconstruction_compatibility'] = pair_df['reciprocal_reconstruction']

# --- Temporal compatibility ---
# Do their temporal structures align?
pair_df['temporal_compatibility'] = pair_df['continuity_alignment']

# --- Operator compatibility ---
# Can their operator structures interoperate?
pair_df['operator_compatibility'] = (
    pair_df['recursive_synchronization'] * pair_df['interaction_stability']
)

# --- Continuity preservation compatibility ---
# Can they preserve each other's continuity?
pair_df['continuity_preservation_compatibility'] = pair_df['co_stabilization_probability']

# Composite compatibility
comp_cols = ['closure_compatibility', 'reconstruction_compatibility', 'temporal_compatibility',
             'operator_compatibility', 'continuity_preservation_compatibility']
for col in comp_cols:
    cmin, cmax = pair_df[col].min(), pair_df[col].max()
    pair_df[f'{col}_norm'] = (pair_df[col] - cmin) / (cmax - cmin + 1e-10)
pair_df['compatibility_composite'] = pair_df[[f'{c}_norm' for c in comp_cols]].mean(axis=1)

print(f'\n=== COMPATIBILITY METRICS ===')
for col in comp_cols:
    print(f'  {col:35s}: {pair_df[col].mean():.4f} ± {pair_df[col].std():.3f}')
print(f'  Compatibility composite: {pair_df["compatibility_composite"].mean():.4f}')

# How many pairs are highly compatible?
high_comp = (pair_df['compatibility_composite'] > pair_df['compatibility_composite'].quantile(0.9)).sum()
low_comp = (pair_df['compatibility_composite'] < pair_df['compatibility_composite'].quantile(0.1)).sum()
print(f'\n  Highly compatible pairs (>90th pct): {high_comp}')
print(f'  Low compatibility pairs (<10th pct):  {low_comp}')

# Profile highly compatible pairs
print(f'\n=== PROFILE: HIGHLY COMPATIBLE vs INCOMPATIBLE ===')
mask_high = pair_df['compatibility_composite'] > pair_df['compatibility_composite'].quantile(0.9)
mask_low = pair_df['compatibility_composite'] < pair_df['compatibility_composite'].quantile(0.1)
profile_cols = ['co_stabilization_probability', 'shared_closure', 'manifold_convergence',
                'signal_transfer_composite', 'mutual_modeling_composite']
for col in profile_cols:
    if col in pair_df.columns:
        h = pair_df.loc[mask_high, col].mean()
        l = pair_df.loc[mask_low, col].mean()
        print(f'  {col:35s}: high={h:.4f} low={l:.4f} ratio={h/(l+1e-10):.2f}x')

# By domain
print(f'\n=== COMPATIBILITY BY DOMAIN PAIR ===')
cross = pair_df[pair_df['domain_a'] != pair_df['domain_b']]
same = pair_df[pair_df['domain_a'] == pair_df['domain_b']]
print(f'  Same domain: {same["compatibility_composite"].mean():.4f}')
print(f'  Cross domain: {cross["compatibility_composite"].mean():.4f}')

# Most compatible domain pairs
print(f'\n=== MOST COMPATIBLE DOMAIN PAIRS ===')
domain_comp = pair_df.groupby(['domain_a', 'domain_b'])['compatibility_composite'].agg(['mean','count'])
domain_comp = domain_comp[domain_comp['count'] > 10].sort_values('mean', ascending=False)
for (da, db), row in domain_comp.head(5).iterrows():
    print(f'  {da:20s} x {db:20s}: compat={row["mean"]:.4f} (n={int(row["count"])})')

# Save M7
pair_df.to_csv(f'{BASE}/outputs/phaseM_compatibility.csv', index=False)
m7_summary = {
    'phase': 'M7',
    'n_pairs': len(pair_df),
    'mean_compatibility': float(pair_df['compatibility_composite'].mean()),
    'same_domain_comp': float(same['compatibility_composite'].mean()),
    'cross_domain_comp': float(cross['compatibility_composite'].mean()),
    'n_highly_compatible': int(high_comp),
    'n_incompatible': int(low_comp),
}
with open(f'{BASE}/summaries/m7_summary.json', 'w') as f:
    json.dump(m7_summary, f, indent=2)
print(f'\nSaved: phaseM_compatibility.csv')

# ====================================================
# M8: ADVERSARIAL NULLS
# ====================================================
print('\n' + '='*70)
print('PHASE M8 — ADVERSARIAL NULL PROGRAM')
print('Does mutual recursive stabilization disappear under null?')
print('='*70)

# Generate adversarial null interactions by shuffling RAW components
# This destroys recursive coupling while preserving marginal distributions
np.random.seed(SEED)

# Use the rawest available components to reconstruct composites under null
raw_cols = ['continuity_alignment', 'recursive_synchronization', 'mutual_closure_reinforcement',
            'interaction_stability', 'external_continuity_prediction', 'reciprocal_reconstruction',
            'mutual_anticipation', 'co_adaptive_continuity', 'recursive_predictive_coupling']
avail_raw = [c for c in raw_cols if c in pair_df.columns]

null_raw = {}
for col in ['observer_level_a', 'observer_level_b', 'domain_a', 'domain_b']:
    if col in pair_df.columns:
        null_raw[col] = pair_df[col].values  # Keep identities (used only for grouping)
for col in avail_raw:
    null_raw[col] = pair_df[col].sample(frac=1, random_state=SEED).values
nulls = pd.DataFrame(null_raw)

# Recompute all composite metrics from shuffled components
nulls['null_co_stabilization'] = (
    nulls['continuity_alignment'] * 0.3 + nulls['recursive_synchronization'] * 0.2 +
    nulls['mutual_closure_reinforcement'] * 0.2 + nulls['interaction_stability'] * 0.3
)
nulls['null_shared_closure'] = nulls['recursive_synchronization'] * nulls['mutual_closure_reinforcement']
nulls['null_manifold_convergence'] = nulls['recursive_predictive_coupling'] * nulls['mutual_anticipation']
nulls['null_continuity_transfer'] = nulls['external_continuity_prediction'] * nulls['reciprocal_reconstruction']
nulls['null_mutual_modeling'] = (
    nulls['external_continuity_prediction'] + nulls['reciprocal_reconstruction'] +
    nulls['mutual_anticipation'] + nulls['co_adaptive_continuity'] + nulls['recursive_predictive_coupling']
) / 5
nulls['null_compatibility'] = (
    nulls['recursive_synchronization'] * nulls['interaction_stability'] + nulls['null_co_stabilization']
) / 2

# Compare real vs null
print(f'\n=== INTERACTION METRICS: NULL vs REAL ===')
comparison = {}
for real_col, null_col in [
    ('co_stabilization_probability', 'null_co_stabilization'),
    ('shared_closure', 'null_shared_closure'),
    ('manifold_convergence', 'null_manifold_convergence'),
    ('mutual_modeling_composite', 'null_mutual_modeling'),
    ('compatibility_composite', 'null_compatibility'),
]:
    if real_col in pair_df.columns and null_col in nulls.columns:
        real_m = pair_df[real_col].mean()
        null_m = nulls[null_col].mean()
        collapse = 1.0 - null_m / (real_m + 1e-10)
        comparison[real_col] = {'real': float(real_m), 'null': float(null_m), 'collapse': float(collapse)}
        print(f'  {real_col:40s}: real={real_m:.6f} null={null_m:.6f} collapse={collapse:.4f}')

print(f'\n=== THE NULL TEST ===')
print(f'Do co-stabilization metrics collapse under null?')
for col, vals in comparison.items():
    print(f'  {col}: {"REQUIRES RECURSIVE ORDERING" if vals["collapse"] > 0.5 else "LARGELY STATISTICAL"}')

# Save
nulls.to_csv(f'{BASE}/outputs/phaseM_nulls.csv', index=False)
m8_summary = {
    'phase': 'M8',
    'null_comparison': comparison,
    'co_stabilization_collapse': comparison.get('co_stabilization_probability', {}).get('collapse', 0),
}
with open(f'{BASE}/summaries/m8_summary.json', 'w') as f:
    json.dump(m8_summary, f, indent=2)
print(f'\nSaved: phaseM_nulls.csv')

print(f'\nM7+M8 COMPLETE')
