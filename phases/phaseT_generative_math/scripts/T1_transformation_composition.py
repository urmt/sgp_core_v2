"""
T1 — TRANSFORMATION COMPOSITION AUDIT
"""
import sys, os, json, numpy as np, pandas as pd
BASE = '/home/student/sgp_core_v2/phases/phaseT_generative_math'
os.makedirs(f'{BASE}/outputs', exist_ok=True)
os.makedirs(f'{BASE}/summaries', exist_ok=True)

# Load data
comp = pd.read_csv('/home/student/sgp_core_v2/phases/phaseI_operator_algebra/outputs/phaseI_composition_results.csv')
chains = pd.read_csv('/home/student/sgp_core_v2/phases/phaseI_operator_algebra/outputs/phaseI_recursive_identity.csv')

# Test associativity: A∘(B∘C) vs (A∘B)∘C
triples = []
for _, row in chains.iterrows():
    if 'operator_A' in row and 'operator_B' in row and 'operator_C' in row:
        triples.append({
            'operator_A': row['operator_A'],
            'operator_B': row['operator_B'],
            'operator_C': row['operator_C'],
            'cg_A': float(row.get('cg_rate_A', 0)),
            'cg_B': float(row.get('cg_rate_B', 0)),
            'cg_C': float(row.get('cg_rate_C', 0)),
            'comp_cg': float(row.get('chain_cg_rate', 0)),
        })

if len(triples) < 10:
    print('ERROR: insufficient triples')
    exit(1)

errors = []
for t in triples:
    errors.append(abs(t['comp_cg'] - t['cg_A']))

mean_error = float(np.mean(errors)) if errors else 0
std_error = float(np.std(errors)) if len(errors) > 1 else 0

# Null tests: shuffle operator identities
n_trials = 100
null_errors = []
for _ in range(n_trials):
    null_chains = chains.copy()
    for c in ['operator_A', 'operator_B', 'operator_C']:
        if c in null_chains.columns:
            vals = null_chains[c].values.copy()
            np.random.shuffle(vals)
            null_chains[c] = vals
    # Compute error on shuffled data
    null_triples = []
    for _, row in null_chains.iterrows():
        if 'operator_A' in row and 'operator_B' in row and 'operator_C' in row:
            null_triples.append({
                'cg_A': float(row.get('cg_rate_A', 0)),
                'comp_cg': float(row.get('chain_cg_rate', 0)),
            })
    if len(null_triples) > 0:
        null_error = np.mean([abs(t['comp_cg'] - t['cg_A']) for t in null_triples])
        null_errors.append(null_error)

null_mean = float(np.mean(null_errors)) if null_errors else 0
collapse = mean_error - null_mean

# Save outputs
pd.DataFrame(triples).to_csv(f'{BASE}/outputs/T1_transformation_composition.csv', index=False)
with open(f'{BASE}/summaries/t1_summary.json','w') as f:
    json.dump({
        'phase': 'T1',
        'n_triples': len(triples),
        'mean_assoc_error': mean_error,
        'null_mean_error': null_mean,
        'collapse': collapse,
        'significant': collapse > 0.05,
    }, f, indent=2)

print(f'T1 complete: {len(triples)} triples, error={mean_error:.4f}, null={null_mean:.4f}, collapse={collapse:.4f}')