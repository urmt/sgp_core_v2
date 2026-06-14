"""
Phase H1+H2 — Target Regime Identification + Control Perturbations.
Uses nearest-neighbor matching to simulate causal descriptor interventions.
For each system, finds matched neighbor differing primarily on one descriptor,
then measures regime transition.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseH'
OUT = '/home/student/sgp_core_v2/phases/phaseE'
os.makedirs(f'{BASE}/processed', exist_ok=True)
os.makedirs(f'{BASE}/interventions', exist_ok=True)

# Load data
df = pd.read_csv('/home/student/sgp_core_v2/phases/phaseC/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
phase = pd.read_csv('/home/student/sgp_core_v2/phases/phaseG/processed/coherence_fertility_phase_space.csv')
curv = pd.read_csv(f'{OUT}/processed/curvature_metrics.csv')
poss = pd.read_csv(f'{OUT}/processed/possibility_metrics.csv')

merged = df.merge(phase, on=['sys_idx','domain']).merge(curv, on=['sys_idx','domain']).merge(poss, on=['sys_idx','domain'])
domains = sorted(merged['domain'].unique())
COLS_DESC = ['CSR','RBS','ADI','RTP','SRD']
COLS_CURV = ['tangent_rotation','local_curvature','predictive_shear','geodesic_instab','jacobian_vol','desc_switch_vel']

t0 = time.time()
print('='*70)
print('PHASE H1+H2 — TARGET REGIMES + CONTROL PERTURBATIONS')
print('='*70)

# H1: Label regime sets
regime_labels = {'constrained_generative': 'CG', 'rigid_coherence': 'RG',
                 'chaotic_fertility': 'CH', 'collapse': 'CL'}
merged['regime_label'] = merged['region'].map(regime_labels)
print(f'\nRegime counts: {merged["region"].value_counts().to_dict()}')

# H2: Simulated interventions via matched pairs
# For each system, find neighbor that differs most in a single descriptor
# This simulates "what if this descriptor were different?"
intervention_records = []

for domain in domains:
    dm = merged[merged['domain'] == domain].copy().reset_index(drop=True)
    N = len(dm)
    X_desc = StandardScaler().fit_transform(dm[COLS_DESC].values)
    covars = dm[COLS_CURV].values  # control variables
    
    for di, desc_name in enumerate(COLS_DESC):
        # For each system, find the neighbor with most different desc_name value
        # while controlling for curvature (matching on similar curvature)
        X_covar = StandardScaler().fit_transform(covars)
        X_full = np.column_stack([X_covar * 2.0, X_desc])  # weight covariates higher
        
        nbrs = NearestNeighbors(n_neighbors=min(31, N)).fit(X_full)
        _, indices = nbrs.kneighbors(X_full)
        
        for i in range(N):
            sys_row = dm.iloc[i]
            desc_i = sys_row[desc_name]
            regime_i = sys_row['region']
            
            # Find neighbor with maximally different desc_name
            max_diff = 0
            best_j = None
            for j in indices[i, 1:]:  # exclude self
                if j >= N: continue
                desc_j = dm.iloc[j][desc_name]
                diff = abs(desc_j - desc_i) / (abs(desc_i) + 1e-10)
                if diff > max_diff:
                    max_diff = diff
                    best_j = j
            
            if best_j is None or max_diff < 0.01: continue
            
            j = best_j
            sys_j = dm.iloc[j]
            regime_j = sys_j['region']
            
            # Record intervention
            desc_change = sys_j[desc_name] - desc_i
            
            # Effect on coherence, fertility
            delta_c = sys_j['coherence'] - sys_row['coherence']
            delta_f = sys_j['fertility'] - sys_row['fertility']
            
            intervention_records.append({
                'domain': domain, 'sys_idx': int(sys_row['sys_idx']),
                'intervention': f'perturb_{desc_name}',
                'desc_name': desc_name,
                'desc_original': desc_i,
                'desc_target': sys_j[desc_name],
                'desc_change': desc_change,
                'regime_from': regime_i,
                'regime_to': regime_j,
                'transitioned': regime_i != regime_j,
                'delta_coherence': delta_c,
                'delta_fertility': delta_f,
                'matched_sys_idx': int(sys_j['sys_idx']),
            })
    
    print(f'  {domain}: {sum(1 for r in intervention_records if r["domain"]==domain)} interventions')

int_df = pd.DataFrame(intervention_records)
int_path = f'{BASE}/interventions/intervention_results.csv'
int_df.to_csv(int_path, index=False)
print(f'\nH2 saved: {int_path} ({len(int_df)} interventions)')

# Which interventions cause regime transitions?
print('\nTransition probabilities P(regime_B | intervention_A):')
for domain in domains:
    dd = int_df[int_df['domain'] == domain]
    if len(dd) == 0: continue
    for desc in COLS_DESC:
        di = dd[dd['desc_name'] == desc]
        if len(di) == 0: continue
        trans_prob = di['transitioned'].mean()
        print(f'  {domain:25s} {desc:5s}: P(transition | perturb) = {trans_prob:.3f} ({di["transitioned"].sum()}/{len(di)})')

# Most effective intervention per domain
print('\nMost effective intervention per domain:')
for domain in domains:
    dd = int_df[int_df['domain'] == domain]
    if len(dd) == 0: continue
    best = dd.groupby('desc_name')['transitioned'].mean().idxmax()
    best_prob = dd.groupby('desc_name')['transitioned'].mean().max()
    print(f'  {domain:25s}: {best:5s} ({best_prob:.3f})')

# Transition matrix
print('\nRegime transition matrix (all interventions):')
transitions = int_df.groupby(['regime_from','regime_to']).size().unstack(fill_value=0)
print(transitions)

# Per-intervention-type effectiveness
print('\nIntervention effectiveness by descriptor:')
for desc in COLS_DESC:
    di = int_df[int_df['desc_name'] == desc]
    trans_prob = di['transitioned'].mean()
    print(f'  Perturb {desc:5s}: P(transition)={trans_prob:.4f} (n={len(di)})')

h1h2_summary = {
    'phase': 'H1+H2', 'seed': SEED,
    'n_interventions': len(int_df),
    'n_domains': len(domains),
    'overall_transition_probability': float(int_df['transitioned'].mean()),
    'best_intervention_per_domain': {
        d: {
            'desc': str(int_df[int_df['domain']==d].groupby('desc_name')['transitioned'].mean().idxmax()),
            'prob': float(int_df[int_df['domain']==d].groupby('desc_name')['transitioned'].mean().max())
        } for d in domains if len(int_df[int_df['domain']==d]) > 0
    },
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/h1h2_summary.json', 'w') as f:
    json.dump(h1h2_summary, f, indent=2)
print(f'\nH1+H2 COMPLETE ({time.time()-t0:.1f}s)')
