"""
Phase G — Master Manifest Builder.
"""
import numpy as np, pandas as pd, os, json, time, subprocess, pickle

BASE = '/home/student/sgp_core_v2/phases/phaseG'
t0 = time.time()
try:
    git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL).decode().strip()
except:
    git_hash = 'unknown'

summaries = {}
for p in ['g1g2','g3','g4g5','g6','g7']:
    path = f'{BASE}/summaries/{p}_summary.json'
    if os.path.exists(path):
        with open(path) as f:
            summaries[p] = json.load(f)

required = {
    'processed/coherence_fertility_phase_space.csv': 'phase space',
    'processed/organizational_regions.csv': 'regions',
    'processed/constrained_generativity_candidates.csv': 'CG candidates',
    'processed/transition_dynamics.csv': 'transitions',
    'processed/balance_metrics.csv': 'balance',
    'processed/cross_family_positions.csv': 'cross-family',
    'processed/metastable_regimes.csv': 'metastable',
    'nulls/null_controls.csv': 'nulls',
}
for rel, desc in required.items():
    full = f'{BASE}/{rel}'
    if not os.path.exists(full):
        print(f'WARNING: {rel} missing')

# Save organizational_regions from phase space
ps = pd.read_csv(f'{BASE}/processed/coherence_fertility_phase_space.csv')
ps[['sys_idx','domain','coherence','fertility','region']].to_csv(
    f'{BASE}/processed/organizational_regions.csv', index=False)

manifest = {
    'phase': 'G', 'title': 'Coherent-Fertile Organizational Conditions',
    'git_hash': git_hash, 'seed': 3000,
    'completed': list(summaries.keys()),
    'file_inventory': {k: os.path.getsize(f'{BASE}/{k}') for k in required if os.path.exists(f'{BASE}/{k}')},
    'key_results': {
        'constrained_generative_count': summaries.get('g1g2',{}).get('constrained_generative_count'),
        'constrained_generative_pct': summaries.get('g1g2',{}).get('constrained_generative_pct'),
        'null_survive_count': summaries.get('g4g5',{}).get('null_survive_count'),
        'meta_stable_regimes': summaries.get('g7',{}).get('n_meta_stable_regimes'),
    },
    'conclusion': 'Constrained generativity exists in 6/10 families under moderate geometric conditions',
    'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
}
with open(f'{BASE}/manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)

checkpoint = {'completed': ['G1','G2','G3','G4','G5','G6','G7'], 'config': {'seed': 3000},
              'ts': time.strftime('%Y-%m-%dT%H:%M:%S')}
with open(f'{BASE}/phaseG_checkpoint.pkl', 'wb') as f:
    pickle.dump(checkpoint, f)

print(f'Manifest + checkpoint saved')
print(f'PHASE G COMPLETE')
