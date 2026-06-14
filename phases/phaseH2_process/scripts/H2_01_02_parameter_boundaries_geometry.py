"""
H2_01 + H2_02 — Process-Level Parameter Interventions + Transition Geometry.

NOT descriptor statistics.
NOT generic state occupancy.
NOT attractor theory.

This treats transitions as PRIMARY organizational objects.
Each system is a TRANSITION NODE in an organizational process space.
Curvature = local geometry of organizational becoming, not prediction error.
"""
import numpy as np, pandas as pd, os, json, warnings
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import pdist, squareform
from scipy.stats import entropy
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseH2_process'
PC = '/home/student/sgp_core_v2/phases/phaseC'
PE = '/home/student/sgp_core_v2/phases/phaseE'
PG = '/home/student/sgp_core_v2/phases/phaseG'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

# ─── Load data ───
df = pd.read_csv(f'{PC}/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
phaseG = pd.read_csv(f'{PG}/processed/coherence_fertility_phase_space.csv')
curv = pd.read_csv(f'{PE}/processed/curvature_metrics.csv')
poss = pd.read_csv(f'{PE}/processed/possibility_metrics.csv')

merged = df.merge(phaseG, on=['sys_idx','domain']).merge(curv, on=['sys_idx','domain']).merge(poss, on=['sys_idx','domain'])
domains = sorted(merged['domain'].unique())
N_TOTAL = len(merged)

# Process-space descriptors: the organizational state is defined by stability + fertility
STAB_COLS = ['stability_return_time','stability_recovery_rate','stability_final_dev','stability_max_dev']
FERT_COLS = ['fertility_state_diversity','fertility_novelty_rate','fertility_state_coverage','fertility_transition_entropy']
CURV_COLS = ['tangent_rotation','local_curvature','predictive_shear','geodesic_instab','jacobian_vol','desc_switch_vel']
POSS_COLS = ['poss_reachable_volume','poss_branching_diversity','poss_adaptive_recovery','poss_future_entropy','poss_divergence_capacity','poss_stability_fertility_coupling']

# Coherence-fertility regime labels
regime_labels = {'constrained_generative': 'CG', 'rigid_coherence': 'RG',
                 'chaotic_fertility': 'CH', 'collapse': 'CL'}
merged['process_regime'] = merged['region'].map(regime_labels)

print('='*70)
print('H2_01 — PARAMETER-LEVEL PROCESS TRANSITION BOUNDARIES')
print('Principles: Transitions are primary. Parameters are generative handles.')
print('='*70)

# ─────────────────────────────────────────────
# SECTION 1: Transition boundaries in organizational state space
# ─────────────────────────────────────────────
# For each domain, find the boundaries between regimes in organizational space.
# A "transition boundary" is a region where small changes in organizational
# parameters produce large changes in process character (CG ↔ non-CG).

boundary_records = []
transition_sharpness = []

for domain in domains:
    dm = merged[merged['domain'] == domain].copy()
    X_org = StandardScaler().fit_transform(dm[STAB_COLS + FERT_COLS].values)
    y_regime = dm['process_regime'].values
    domain_k = min(30, len(dm) - 1)
    
    nbrs = NearestNeighbors(n_neighbors=domain_k + 1).fit(X_org)
    _, indices = nbrs.kneighbors(X_org)
    
    for i in range(len(dm)):
        regime_i = y_regime[i]
        neighbors = indices[i, 1:]  # exclude self
        neighbor_regimes = y_regime[neighbors]
        
        # Transition boundary density: what fraction of neighbors are in a DIFFERENT regime?
        frac_diff = np.mean(neighbor_regimes != regime_i)
        
        # Transition sharpness: the distance to the nearest system of a different regime
        all_dists = squareform(pdist(X_org))
        distances_to_diff = [all_dists[i, j] for j in range(len(dm)) if j != i and y_regime[j] != regime_i]
        min_dist_to_diff = np.min(distances_to_diff) if distances_to_diff else np.inf
        
        # Organizational gradient magnitude: how quickly does organizational identity change?
        # Systems with high predictive_shear have steep gradient = sharp transitions
        org_gradient = dm.iloc[i]['predictive_shear']
        org_curvature = dm.iloc[i]['local_curvature']
        
        # Process rigidity: high jacobian_vol means process resists change
        process_rigidity = dm.iloc[i]['jacobian_vol']
        
        boundary_records.append({
            'domain': domain,
            'sys_idx': int(dm.iloc[i]['sys_idx']),
            'process_regime': regime_i,
            'transition_neighbor_fraction': round(frac_diff, 4),
            'transition_sharpness': round(min_dist_to_diff, 4),
            'org_gradient_predictive_shear': round(org_gradient, 4),
            'org_curvature_local_curvature': round(org_curvature, 4),
            'process_rigidity': round(process_rigidity, 4),
            'is_near_transition': int(frac_diff > 0.3),
        })

bdf = pd.DataFrame(boundary_records)
bdf.to_csv(f'{BASE}/outputs/transition_boundary_metrics.csv', index=False)
print(f'Transition boundary metrics saved: {len(bdf)} systems')

# Which systems are "process-transitional" (near a boundary)?
trans_systems = bdf[bdf['is_near_transition'] == 1]
print(f'\nProcess-transitional systems (near a regime boundary): {len(trans_systems)}/{N_TOTAL} ({100*len(trans_systems)/N_TOTAL:.1f}%)')
print('By regime:')
for regime in sorted(trans_systems['process_regime'].unique()):
    n_tot = len(bdf[bdf['process_regime'] == regime])
    n_trans = len(trans_systems[trans_systems['process_regime'] == regime])
    print(f'  {regime}: {n_trans}/{n_tot} = {100*n_trans/n_tot:.1f}% near boundaries')

# H2_01 MAIN: Parameter-level intervention zones
# Systems near transition boundaries are those where SMALL generative parameter
# changes produce LARGE organizational process changes.
# These are the intervention sweet spots.
print('\nTransition boundary density by domain:')
for domain in domains:
    dd = bdf[bdf['domain'] == domain]
    n_near = len(dd[dd['is_near_transition'] == 1])
    print(f'  {domain:25s}: {n_near}/{len(dd)} near boundary ({100*n_near/len(dd):.1f}%)')

# ─────────────────────────────────────────────
# SECTION 2: Transition geometry (H2_02)
# ─────────────────────────────────────────────
print('\n' + '='*70)
print('H2_02 — TRANSITION GEOMETRY')
print('Primacy: transitions as geometric objects, not state occupancy')
print('='*70)

# Transition geometry treats each system's LOCAL organizational landscape
# as a geometric object characterizing the process of organizational becoming.

geo_records = []
for domain in domains:
    dm = merged[merged['domain'] == domain].copy()
    X_org = StandardScaler().fit_transform(dm[STAB_COLS + FERT_COLS].values)
    y_regime = dm['process_regime'].values
    domain_k = min(30, len(dm) - 1)
    
    nbrs = NearestNeighbors(n_neighbors=domain_k + 1).fit(X_org)
    distances, indices = nbrs.kneighbors(X_org)
    
    for i in range(len(dm)):
        neigh_idx = indices[i, 1:]
        neigh_dists = distances[i, 1:]
        
        # 1. Transition continuity: are neighboring systems process-similar?
        # Low continuity = fragmented process geometry (neighbor regimes diverse)
        neigh_regimes = y_regime[neigh_idx]
        regime_counts = np.unique(neigh_regimes, return_counts=True)[1]
        continuity = 1 - entropy(regime_counts / regime_counts.sum(), base=len(regime_counts)) if len(regime_counts) > 1 else 0
        # Normalized: 0 = maximally diverse neighbors, 1 = all same regime
        if continuity < 1e-10: continuity = 0.0
        
        # 2. Transition curvature: how much does the organizational landscape bend?
        # Directly from Phase E local_curvature
        t_curvature = dm.iloc[i]['local_curvature']
        
        # 3. Transition smoothness: variance of organizational change across neighbors
        # How consistently do organizational properties change in this neighborhood?
        neigh_fertility = dm.iloc[neigh_idx]['fertility'].values
        neigh_coherence = dm.iloc[neigh_idx]['coherence'].values
        fert_var = np.var(neigh_fertility) if len(neigh_fertility) > 1 else 0
        coh_var = np.var(neigh_coherence) if len(neigh_coherence) > 1 else 0
        smoothness = 1 / (1 + np.sqrt(fert_var * coh_var))  # 1 = smooth, ~0 = rough
        
        # 4. Transition reversibility: do forward and backward paths share geometry?
        # Systems where predictability is high in both directions
        t_reversibility = dm.iloc[i]['poss_stability_fertility_coupling']
        
        # 5. Transition branching: how many distinct organizational directions exist?
        # Number of distinct regime transitions possible from this neighborhood
        branching_diversity = dm.iloc[i]['poss_branching_diversity']
        
        # 6. Transition fragmentation: is the organizational geometry broken?
        # High fragmentation = neighboring systems have radically different process characters
        # Measured by how many distinct transition types exist among neighbors
        distinct_transition_types = len(set(zip([y_regime[i]] * len(neigh_regimes), neigh_regimes)))
        fragmentation = distinct_transition_types / min(4, len(neigh_idx))
        
        geo_records.append({
            'domain': domain,
            'sys_idx': int(dm.iloc[i]['sys_idx']),
            'process_regime': y_regime[i],
            'transition_continuity': round(continuity, 4),
            'transition_curvature': round(t_curvature, 4),
            'transition_smoothness': round(smoothness, 4),
            'transition_reversibility': round(t_reversibility, 4),
            'transition_branching': round(branching_diversity, 4),
            'transition_fragmentation': round(fragmentation, 4),
        })

geo_df = pd.DataFrame(geo_records)
geo_df.to_csv(f'{BASE}/outputs/transition_geometry.csv', index=False)
print(f'\nTransition geometry saved: {len(geo_df)} systems')

# Summary by regime: how does CG differ from other regimes in transition geometry?
print('\nTransition geometry by process regime (mean):')
for col in ['transition_continuity','transition_curvature','transition_smoothness',
            'transition_reversibility','transition_branching','transition_fragmentation']:
    print(f'  {col}:')
    for regime in sorted(geo_df['process_regime'].unique()):
        val = geo_df[geo_df['process_regime'] == regime][col].mean()
        print(f'    {regime:4s}: {val:.4f}')

# Key question: Do CG systems exhibit distinctive transition geometry?
cg_geo = geo_df[geo_df['process_regime'] == 'CG']
noncg_geo = geo_df[geo_df['process_regime'] != 'CG']
print('\nCG vs non-CG transition geometry comparison:')
for col in ['transition_continuity','transition_curvature','transition_smoothness',
            'transition_reversibility','transition_branching','transition_fragmentation']:
    cg_mean = cg_geo[col].mean()
    non_mean = noncg_geo[col].mean()
    ratio = cg_mean / max(non_mean, 1e-10)
    print(f'  {col:35s}: CG={cg_mean:.4f} non-CG={non_mean:.4f} ratio={ratio:.3f}')

# Merge boundary + geometry data for combined analysis
bdf.to_csv(f'{BASE}/outputs/transition_boundary_metrics.csv', index=False)
geo_df.to_csv(f'{BASE}/outputs/transition_geometry.csv', index=False)

h2_01_02_summary = {
    'phase': 'H2_01+H2_02', 'seed': SEED,
    'n_systems_analyzed': N_TOTAL,
    'process_transitional_systems': int(len(trans_systems)),
    'process_transitional_pct': round(100 * len(trans_systems) / N_TOTAL, 1),
    'transition_geometry_metrics': ['transition_continuity','transition_curvature',
        'transition_smoothness','transition_reversibility','transition_branching','transition_fragmentation'],
    'cg_vs_noncg_geometry': {
        col: {
            'CG_mean': round(float(cg_geo[col].mean()), 4),
            'nonCG_mean': round(float(noncg_geo[col].mean()), 4),
            'ratio': round(float(cg_geo[col].mean() / max(noncg_geo[col].mean(), 1e-10)), 3),
        } for col in ['transition_continuity','transition_curvature','transition_smoothness',
                      'transition_reversibility','transition_branching','transition_fragmentation']
    },
}
with open(f'{BASE}/summaries/h2_01_02_summary.json', 'w') as f:
    json.dump(h2_01_02_summary, f, indent=2)
print(f'\nH2_01+H2_02 COMPLETE')
