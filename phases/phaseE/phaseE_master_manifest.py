"""
Phase E — Master Manifest Builder.
Aggregates all sub-phase summaries into one master manifest.
Saves pipeline checkpoint.
"""
import numpy as np, pandas as pd, os, json, time, subprocess, pickle, hashlib

BASE = '/home/student/sgp_core_v2/phases/phaseE'
t0 = time.time()

# Get git hash
try:
    git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL).decode().strip()
except:
    git_hash = 'unknown'

# Load all summaries
summaries = {}
for phase in ['e1','e2','e3','e4','e5','e6']:
    path = f'{BASE}/summaries/{phase}_summary.json'
    if os.path.exists(path):
        with open(path) as f:
            summaries[phase] = json.load(f)
    else:
        summaries[phase] = {'error': f'{path} not found'}

# Verify all required files exist
required_files = {
    'raw/local_coeff_vectors.csv': 'E1 coefficient vectors',
    'raw/neighborhood_graph.csv': 'E1 neighborhood graph',
    'raw/curvature_tensors.npz': 'E1 curvature tensors',
    'raw/leakage_audit.csv': 'E2 leakage audit',
    'processed/curvature_metrics.csv': 'E1 curvature metrics',
    'processed/possibility_metrics.csv': 'E2 possibility metrics',
    'processed/prediction_results.csv': 'E3 prediction results',
    'processed/per_domain_r2.csv': 'E3 per-domain R²',
    'raw/model_comparisons.csv': 'E3 model comparisons',
    'processed/curvature_regions.csv': 'E4 curvature regions',
    'processed/concentration_regions.csv': 'E4 concentration regions',
    'nulls/null1_covariance_synthetic.csv': 'E5 null 1',
    'nulls/null2_k_sensitivity.csv': 'E5 null 2',
    'nulls/null3_scaling_sensitivity.csv': 'E5 null 3',
    'nulls/null4_random_manifold_controls.csv': 'E5 null 4',
    'nulls/null5_cross_domain_persistence.csv': 'E5 null 5',
    'nulls/null_all_distributions.npz': 'E5 null distributions',
    'processed/family_transfer.csv': 'E6 family transfer',
    'processed/geometry_similarity.csv': 'E6 geometry similarity',
    'processed/regime_alignment.csv': 'E6 regime alignment',
}

file_status = {}
for rel_path, desc in required_files.items():
    full_path = f'{BASE}/{rel_path}'
    exists = os.path.exists(full_path)
    size = os.path.getsize(full_path) if exists else 0
    file_status[rel_path] = {'exists': exists, 'size_bytes': size, 'description': desc}

missing = [k for k, v in file_status.items() if not v['exists']]
if missing:
    print(f'WARNING: {len(missing)} files missing:')
    for m in missing:
        print(f'  {m}')

# Count rows in key files
row_counts = {}
for rel_path in ['raw/local_coeff_vectors.csv', 'raw/neighborhood_graph.csv',
                  'processed/curvature_metrics.csv', 'processed/possibility_metrics.csv',
                  'processed/prediction_results.csv', 'processed/curvature_regions.csv',
                  'processed/family_transfer.csv']:
    full = f'{BASE}/{rel_path}'
    if os.path.exists(full):
        try:
            row_counts[rel_path] = len(pd.read_csv(full))
        except:
            row_counts[rel_path] = 'error'

# Master manifest
manifest = {
    'phase': 'E',
    'title': 'Organizational Curvature & Possibility Space',
    'git_hash': git_hash,
    'seed': 3000,
    'k_neighbors_default': 30,
    'completed_phases': list(summaries.keys()),
    'total_runtime_seconds': sum(
        s.get('runtime', s.get('runtime_seconds', 0)) for s in summaries.values() if 'runtime' in s or 'runtime_seconds' in s
    ),
    'file_inventory': file_status,
    'row_counts': row_counts,
    'key_results': {
        'E1_curvature_metrics': list(summaries.get('e1', {}).get('curvature_metrics', [])),
        'E2_possibility_metrics': list(summaries.get('e2', {}).get('possibility_metrics', [])),
        'E3_mean_R2_curvature': summaries.get('e3', {}).get('mean_R2_curvature', None),
        'E3_mean_R2_raw_descriptors': summaries.get('e3', {}).get('mean_R2_raw_descriptors', None),
        'E3_curvature_wins': summaries.get('e3', {}).get('n_curv_wins', None),
        'E5_verdict': summaries.get('e5', {}).get('verdict', None),
        'E5_null_survive_count': summaries.get('e5', {}).get('null_survive_count', None),
        'E6_within_domain_R2': summaries.get('e6', {}).get('within_domain_R2', None),
        'E6_cross_domain_R2': summaries.get('e6', {}).get('cross_domain_R2', None),
    },
    'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
}

with open(f'{BASE}/manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)
print(f'Master manifest saved: {len(manifest)} keys')

# Pipeline checkpoint
checkpoint = {
    'completed_phases': ['E1','E2','E3','E4','E5','E6'],
    'data_loaded': {
        'curvature_metrics': len(pd.read_csv(f'{BASE}/processed/curvature_metrics.csv')),
        'possibility_metrics': len(pd.read_csv(f'{BASE}/processed/possibility_metrics.csv')),
        'combined': len(pd.read_csv(f'{BASE}/processed/prediction_results.csv')),
    },
    'config': {'seed': 3000, 'k': 30, 'descriptors': ['CSR','RBS','ADI','RTP','SRD']},
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
    'manifest_hash': hashlib.md5(json.dumps(manifest, sort_keys=True).encode()).hexdigest(),
}
with open(f'{BASE}/phaseE_checkpoint.pkl', 'wb') as f:
    pickle.dump(checkpoint, f)
print(f'Checkpoint saved')

print(f'\nMaster manifest + checkpoint COMPLETE ({time.time()-t0:.1f}s)')
print(f'\n=== PHASE E COMPLETE ===')
