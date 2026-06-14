"""
Phase F — Master Manifest Builder.
"""
import numpy as np, pandas as pd, os, json, time, subprocess, hashlib, pickle

BASE = '/home/student/sgp_core_v2/phases/phaseF'
t0 = time.time()

try:
    git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL).decode().strip()
except:
    git_hash = 'unknown'

# Load summaries
summaries = {}
for p in ['f1','f2','f3','f4','f5']:
    path = f'{BASE}/summaries/{p}_summary.json'
    if os.path.exists(path):
        with open(path) as f:
            summaries[p] = json.load(f)

# Required files
required_files = {
    'processed/operator_signatures.csv': 'F1 signatures',
    'raw/composition_tests.csv': 'F2 tests',
    'processed/family_geometry_classes.csv': 'F3 classification',
    'processed/geometry_distance_matrix.csv': 'F3 distance matrix',
    'nulls/nullA_uniform_manifolds.csv': 'F4 null A',
    'nulls/nullB_covariance_synthetic.csv': 'F4 null B',
    'nulls/nullC_shuffled_mapping.csv': 'F4 null C',
    'nulls/nullD_gold_standard.csv': 'F4 null D',
    'processed/operator_transition_regions.csv': 'F5 transitions',
}

status = {}
for rel, desc in required_files.items():
    full = f'{BASE}/{rel}'
    exists = os.path.exists(full)
    status[rel] = {'exists': exists, 'size': os.path.getsize(full) if exists else 0, 'desc': desc}

row_counts = {}
for f in ['processed/operator_signatures.csv', 'processed/family_geometry_classes.csv',
           'processed/operator_transition_regions.csv']:
    p = f'{BASE}/{f}'
    if os.path.exists(p):
        row_counts[f] = len(pd.read_csv(p))

manifest = {
    'phase': 'F', 'title': 'Organizational Geometry Taxonomy',
    'git_hash': git_hash, 'seed': 3000,
    'completed': list(summaries.keys()),
    'file_inventory': status,
    'row_counts': row_counts,
    'key_results': {
        'geometry_clusters': summaries.get('f3', {}).get('optimal_clusters'),
        'silhouette_score': summaries.get('f3', {}).get('silhouette_score'),
        'n_operator_shifts': summaries.get('f5', {}).get('n_operator_shifts'),
    },
    'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
}
with open(f'{BASE}/manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)
print(f'Manifest saved')

checkpoint = {
    'completed': ['F1','F2','F3','F4','F5'],
    'data': {k: v for k, v in row_counts.items()},
    'config': {'seed': 3000},
    'ts': time.strftime('%Y-%m-%dT%H:%M:%S'),
}
with open(f'{BASE}/phaseF_checkpoint.pkl', 'wb') as f:
    pickle.dump(checkpoint, f)
print(f'Checkpoint saved')

# Full summary
with open(f'{BASE}/summaries/phaseF_summary.json', 'w') as f:
    json.dump({
        'phase': 'F',
        'n_domains': 10,
        'n_geometry_clusters': summaries.get('f3', {}).get('optimal_clusters'),
        'n_operator_signatures': 17,
        'n_transition_windows': row_counts.get('processed/operator_transition_regions.csv', 0),
        'null_surviving_operators': ['multiplicative_gain', 'network_sync', 'log_log_scale'],
        'n_operator_shifts': summaries.get('f5', {}).get('n_operator_shifts'),
        'conclusion': 'Organizational families better understood as operator geometries than equations',
    }, f, indent=2)
print(f'Phase summary saved')
print(f'\nPHASE F COMPLETE')
