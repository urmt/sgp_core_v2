"""
Phase J3+J4 — Recursive Conservation + Operator Conservation Laws.

J3: Apply repeated operator compositions recursively. Track invariant decay.
J4: Test whether some operators behave like organizational conservation laws.

Anti-drift: Conservation through transformation ≠ static equilibrium.
"""
import numpy as np, pandas as pd, os, json, warnings
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseJ_invariants'
PI = '/home/student/sgp_core_v2/phases/phaseI_operator_algebra'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

print('='*70)
print('PHASE J3 — RECURSIVE CONSERVATION')
print('Apply repeated compositions. Track invariant decay and convergence.')
print('='*70)

# Load data
comp_df = pd.read_csv(f'{PI}/outputs/phaseI_composition_results.csv')
identity_df = pd.read_csv(f'{PI}/outputs/phaseI_recursive_identity.csv')
inv_df = pd.read_csv(f'{BASE}/outputs/phaseJ_transform_invariants.csv')
conserv_df = pd.read_csv(f'{BASE}/outputs/phaseJ_conservation_collapse.csv')
op_df = pd.read_csv(f'{PI}/outputs/phaseI_operator_signatures.csv')
op_cols = [c for c in op_df.columns if c.startswith('op_')]
domains = sorted(comp_df['domain_A'].unique())

# Build domain property profiles from composition data
domain_profiles = {}
for domain in domains:
    dd = inv_df[(inv_df['domain_A'] == domain) | (inv_df['domain_B'] == domain)]
    domain_profiles[domain] = {
        'cg_rate': float(dd[dd['property'] == 'cg_rate']['val_A'].mean()) if len(dd[dd['property']=='cg_rate']) > 0 else 0,
        'mean_reversibility': float(dd[dd['property'] == 'mean_reversibility']['val_A'].mean()) if len(dd[dd['property']=='mean_reversibility']) > 0 else 0,
        'mean_recursive_closure': float(dd[dd['property'] == 'mean_recursive_closure']['val_A'].mean()) if len(dd[dd['property']=='mean_recursive_closure']) > 0 else 0,
        'mean_continuity': float(dd[dd['property'] == 'mean_continuity']['val_A'].mean()) if len(dd[dd['property']=='mean_continuity']) > 0 else 0,
    }

# ====================================================
# J3: RECURSIVE CONSERVATION
# ====================================================
# Simulate recursive composition chains of length L=5
# Each step: compose current profile with a new random domain
# Track how properties evolve and whether they converge

N_CHAINS = 200
CHAIN_LENGTH = 6
properties = ['cg_rate', 'mean_reversibility', 'mean_recursive_closure', 'mean_continuity']

chain_records = []
for chain_idx in range(N_CHAINS):
    if chain_idx % 50 == 0 and chain_idx > 0: print(f'  Chain {chain_idx}/{N_CHAINS}')
    
    # Random starting domain
    current = domains[np.random.randint(len(domains))]
    profile = dict(domain_profiles[current])
    profile['domain'] = current
    
    chain_history = [dict(profile)]
    
    for step in range(1, CHAIN_LENGTH):
        # Pick random next domain different from current
        next_domain = current
        while next_domain == current:
            next_domain = domains[np.random.randint(len(domains))]
        
        next_profile = domain_profiles[next_domain]
        
        # Compose: weighted average (the composition operator)
        for prop in properties:
            profile[prop] = (profile[prop] + next_profile[prop]) / 2
        
        profile['domain'] = f'{current}∘{next_domain}'
        chain_history.append(dict(profile))
        current = next_domain
    
    # Compute invariant decay: how much does each property change from step 0 to step N?
    for step_idx, hist in enumerate(chain_history):
        if step_idx == 0:
            decay = 0
        else:
            decay = abs(hist['cg_rate'] - chain_history[0]['cg_rate']) / max(chain_history[0]['cg_rate'], 0.001)
        
        chain_records.append({
            'chain_idx': int(chain_idx),
            'step': int(step_idx),
            'domain': str(hist['domain']),
            'cg_rate': round(hist['cg_rate'], 4),
            'mean_reversibility': round(hist['mean_reversibility'], 4),
            'mean_recursive_closure': round(hist['mean_recursive_closure'], 4),
            'mean_continuity': round(hist['mean_continuity'], 4),
            'cg_decay': round(decay, 4),
        })

chain_df = pd.DataFrame(chain_records)
chain_df.to_csv(f'{BASE}/outputs/phaseJ_recursive_conservation.csv', index=False)
print(f'\nRecursive conservation: {len(chain_df)} steps across {N_CHAINS} chains')

# Does CG rate converge under repeated composition?
print('\n=== CG RATE DECAY UNDER RECURSIVE COMPOSITION ===')
for step in range(CHAIN_LENGTH):
    sd = chain_df[chain_df['step'] == step]
    print(f'  Step {step}: mean CG={sd["cg_rate"].mean():.4f} ± {sd["cg_rate"].std():.4f} '
          f'decay={sd["cg_decay"].mean():.4f}')

# Does reversibility converge?
print('\n=== REVERSIBILITY UNDER RECURSIVE COMPOSITION ===')
for step in range(CHAIN_LENGTH):
    sd = chain_df[chain_df['step'] == step]
    print(f'  Step {step}: mean rev={sd["mean_reversibility"].mean():.4f} ± {sd["mean_reversibility"].std():.4f}')

# Convergence test: does the variance shrink across steps?
print('\n=== CONVERGENCE TEST (variance over steps) ===')
for prop in properties:
    step_vars = [chain_df[chain_df['step'] == s][prop].var() for s in range(CHAIN_LENGTH)]
    initial_var = step_vars[0]
    final_var = step_vars[-1]
    var_ratio = final_var / max(initial_var, 0.001)
    print(f'  {prop:30s}: initial_var={initial_var:.6f} final_var={final_var:.6f} ratio={var_ratio:.3f} '
          f'{"CONVERGING" if var_ratio < 0.8 else "STABLE" if var_ratio < 1.2 else "DIVERGING"}')

# ====================================================
# J4: OPERATOR CONSERVATION LAWS
# ====================================================
print('\n' + '='*70)
print('PHASE J4 — OPERATOR CONSERVATION LAWS')
print('Do some operators behave like organizational conservation laws?')
print('='*70)

# For each operator family, test its conservation properties:
# 1. CG conservation: does this operator preserve CG probability under composition?
# 2. Identity conservation: does it preserve geometric identity?
# 3. Reconstruction conservation: does it preserve recovery ability?

op_cols_list = [c[3:] for c in op_cols]  # strip 'op_' prefix
law_records = []

for op_name in op_cols_list:
    # Find compositions involving this operator
    op_comp = comp_df[(comp_df['operator_A'] == op_name) | (comp_df['operator_B'] == op_name)]
    
    if len(op_comp) == 0:
        continue
    
    # CG conservation: mean CG preservation when this operator participates
    cg_conservation = op_comp['cg_preservation_ratio'].mean()
    cg_std = op_comp['cg_preservation_ratio'].std()
    
    # Also test CG rate retention specifically
    cg_rate_retention = op_comp['comp_cg_rate'].mean() if 'comp_cg_rate' in op_comp.columns else cg_conservation
    
    # Identity conservation: from identity_df
    # Which identity chains involve this operator?
    id_involving = identity_df[(identity_df['operator_A'] == op_name) | 
                                (identity_df['operator_B'] == op_name) |
                                (identity_df['operator_C'] == op_name)] if 'operator_C' in identity_df.columns else identity_df[:0]
    
    identity_conservation = id_involving['chain_identity_similarity'].mean() if len(id_involving) > 0 else None
    cg_in_identity = id_involving['chain_cg_retention'].mean() if len(id_involving) > 0 and 'chain_cg_retention' in id_involving.columns else None
    
    # Form-function gap: how much does geometry survive while CG collapses?
    # Positive gap = geometry outlives generativity (form-function uncoupling)
    conserv_op = conserv_df[(conserv_df['operator_A'] == op_name) | (conserv_df['operator_B'] == op_name)]
    if len(conserv_op) > 0:
        geo_cg_gap = (conserv_op['geo_survival'] - conserv_op['cg_survival']).mean()
    else:
        geo_cg_gap = None
    
    law_records.append({
        'operator': op_name,
        'n_compositions': len(op_comp),
        'cg_conservation_mean': round(cg_conservation, 4),
        'cg_conservation_std': round(cg_std, 4),
        'cg_rate_retention': round(cg_rate_retention, 4),
        'identity_conservation': round(identity_conservation, 4) if identity_conservation is not None else None,
        'cg_in_identity_chains': round(cg_in_identity, 4) if cg_in_identity is not None else None,
        'form_function_gap': round(geo_cg_gap, 4) if geo_cg_gap is not None else None,
    })

law_df = pd.DataFrame(law_records)
law_df.to_csv(f'{BASE}/outputs/phaseJ_operator_laws.csv', index=False)
print(f'\nOperator conservation laws: {len(law_df)} operators')

print('\n=== OPERATOR CONSERVATION RANKING ===')
for _, r in law_df.sort_values('cg_conservation_mean', ascending=False).iterrows():
    print(f'  {r["operator"]:25s}: CG_conservation={r["cg_conservation_mean"]:.4f} '
          f'identity={r["identity_conservation"]} '
          f'form_func_gap={r["form_function_gap"]}')

print('\n=== STRONGEST CONSERVATION LAWS (CG_conservation > 0.7) ===')
strong = law_df[law_df['cg_conservation_mean'] > 0.7]
for _, r in strong.sort_values('cg_conservation_mean', ascending=False).iterrows():
    print(f'  {r["operator"]:25s}: CG={r["cg_conservation_mean"]:.3f} '
          f'CG_in_id={r["cg_in_identity_chains"]} gap={r["form_function_gap"]}')

print('\n=== WEAKEST CONSERVATION LAWS (CG_conservation < 0.4) ===')
weak = law_df[law_df['cg_conservation_mean'] < 0.4]
for _, r in weak.sort_values('cg_conservation_mean').iterrows():
    print(f'  {r["operator"]:25s}: CG={r["cg_conservation_mean"]:.3f} '
          f'CG_in_id={r["cg_in_identity_chains"]} gap={r["form_function_gap"]}')

# Summary: do any operators act as strict conservation laws (CG > 0.85)?
print(f'\n=== CONSERVATION LAW SUMMARY ===')
print(f'  Strict conservation laws (CG > 0.85): {len(law_df[law_df["cg_conservation_mean"] > 0.85])}/{len(law_df)} operators')
print(f'  Moderate (0.6-0.85): {len(law_df[(law_df["cg_conservation_mean"] > 0.6) & (law_df["cg_conservation_mean"] <= 0.85)])}/{len(law_df)}')
print(f'  Weak (< 0.6): {len(law_df[law_df["cg_conservation_mean"] <= 0.6])}/{len(law_df)}')

h3_h4_summary = {
    'phase': 'J3+J4',
    'recursive_conservation': {
        'n_chains': N_CHAINS,
        'n_steps': CHAIN_LENGTH,
        'cg_rate_convergence': {
            'step_0_mean': float(chain_df[chain_df['step']==0]['cg_rate'].mean()),
            f'step_{CHAIN_LENGTH-1}_mean': float(chain_df[chain_df['step']==CHAIN_LENGTH-1]['cg_rate'].mean()),
        },
    },
    'operator_conservation_laws': {
        'strongest': str(law_df.loc[law_df['cg_conservation_mean'].idxmax(), 'operator']),
        'strongest_value': float(law_df['cg_conservation_mean'].max()),
        'weakest': str(law_df.loc[law_df['cg_conservation_mean'].idxmin(), 'operator']),
        'weakest_value': float(law_df['cg_conservation_mean'].min()),
        'n_strict_laws': int(len(law_df[law_df['cg_conservation_mean'] > 0.85])),
        'n_total_operators': int(len(law_df)),
    }
}
with open(f'{BASE}/summaries/h3_h4_summary.json', 'w') as f:
    json.dump(h3_h4_summary, f, indent=2)
print(f'\nJ3+J4 COMPLETE')
