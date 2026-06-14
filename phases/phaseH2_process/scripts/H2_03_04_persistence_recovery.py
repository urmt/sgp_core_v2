"""
H2_03 + H2_04 — Transition Persistence + Transition Recovery.

Persistence = duration of coherent generativity UNDER perturbation.
Recovery = can the process reconstruct itself AFTER collapse?

These test whether CG is sustained organizational process continuity,
not just a lucky parameter configuration.

NEVER call this "dwell time" — it is TRANSITION PERSISTENCE.
NEVER call this "return probability" — it is TRANSITION RECOVERABILITY.
"""
import numpy as np, pandas as pd, os, json, warnings
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseH2_process'
PC = '/home/student/sgp_core_v2/phases/phaseC'
PE = '/home/student/sgp_core_v2/phases/phaseE'
PG = '/home/student/sgp_core_v2/phases/phaseG'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

# ─── Load ───
df = pd.read_csv(f'{PC}/phaseC_metrics.csv')
df['sys_idx'] = df.groupby('domain').cumcount()
phaseG = pd.read_csv(f'{PG}/processed/coherence_fertility_phase_space.csv')
merged = df.merge(phaseG, on=['sys_idx','domain'])
merged['process_regime'] = merged['region'].map({'constrained_generative':'CG','rigid_coherence':'RG',
                                                   'chaotic_fertility':'CH','collapse':'CL'})
domains = sorted(merged['domain'].unique())
STAB_COLS = ['stability_return_time','stability_recovery_rate','stability_final_dev','stability_max_dev']
FERT_COLS = ['fertility_state_diversity','fertility_novelty_rate','fertility_state_coverage','fertility_transition_entropy']

print('='*70)
print('H2_03 — TRANSITION PERSISTENCE')
print('Question: How long does CG persist under organizational perturbation?')
print('='*70)

PERSIST_WALKS = 20    # random walk trials per system
PERSIST_MAX_STEPS = 100  # max steps before truncation

persist_records = []

for domain in domains:
    dm = merged[merged['domain'] == domain].copy().reset_index(drop=True)
    if len(dm) < 10: continue
    X_org = StandardScaler().fit_transform(dm[STAB_COLS + FERT_COLS].values)
    y_regime = dm['process_regime'].values
    cg_indices = np.where(y_regime == 'CG')[0]
    domain_k = min(20, len(dm) - 1)
    
    nbrs = NearestNeighbors(n_neighbors=domain_k + 1).fit(X_org)
    _, indices = nbrs.kneighbors(X_org)
    
    for i in cg_indices:
        # Simulate PERSIST_WALKS random walks from this CG system
        persistence_steps = []
        for walk in range(PERSIST_WALKS):
            current = i
            steps = 0
            for _ in range(PERSIST_MAX_STEPS):
                if y_regime[current] != 'CG':
                    break  # transition exited CG
                steps += 1
                # Move to a random neighbor (excluding self)
                neighbors = indices[current, 1:]
                probs = np.ones(len(neighbors))
                probs = probs / probs.sum()
                current = int(np.random.choice(neighbors, p=probs))
            persistence_steps.append(steps)
        
        # Persistence half-life: median steps before CG exit
        half_life = np.median(persistence_steps)
        max_survive = np.max(persistence_steps)
        
        # Perturbation tolerance: how much organizational distance can this CG
        # system sustain before leaving CG? Measured as mean distance to nearest
        # non-CG neighbor in organizational space.
        neigh_distances = []
        for j in indices[i, 1:]:
            if y_regime[j] != 'CG':
                dist = np.linalg.norm(X_org[i] - X_org[j])
                neigh_distances.append(dist)
        tolerance = np.min(neigh_distances) if neigh_distances else np.inf
        
        persist_records.append({
            'domain': domain,
            'sys_idx': int(dm.iloc[i]['sys_idx']),
            'persistence_half_life': int(half_life),
            'persistence_max_survival': int(max_survive),
            'persistence_variance': int(np.var(persistence_steps)),
            'perturbation_tolerance': round(tolerance, 4),
        })
    
    
persist_df = pd.DataFrame(persist_records)
persist_df.to_csv(f'{BASE}/outputs/persistence_metrics.csv', index=False)
print(f'\nPersistence metrics saved: {len(persist_df)} CG systems')

# Summary
print('\nCG persistence by domain (mean values):')
for domain in domains:
    dd = persist_df[persist_df['domain'] == domain]
    if len(dd) == 0:
        print(f'  {domain:25s}: no CG systems')
        continue
    print(f'  {domain:25s}: half_life={dd["persistence_half_life"].mean():.1f} '
          f'max_survival={dd["persistence_max_survival"].mean():.1f} '
          f'tolerance={dd["perturbation_tolerance"].mean():.3f}')

print(f'\nOverall CG persistence: half_life={persist_df["persistence_half_life"].mean():.2f} '
      f'max_survival={persist_df["persistence_max_survival"].mean():.2f}')

# ─────────────────────────────────────────────
# H2_04 — TRANSITION RECOVERY
# ─────────────────────────────────────────────
print('\n' + '='*70)
print('H2_04 — TRANSITION RECOVERY')
print('Question: Can CG processes reconstruct themselves after organizational collapse?')
print('='*70)

RECOVERY_WALKS = 10

recovery_records = []

for domain in domains:
    dm = merged[merged['domain'] == domain].copy().reset_index(drop=True)
    if len(dm) < 10: continue
    X_org = StandardScaler().fit_transform(dm[STAB_COLS + FERT_COLS].values)
    y_regime = dm['process_regime'].values
    cg_indices = np.where(y_regime == 'CG')[0]
    domain_k = min(20, len(dm) - 1)
    
    nbrs = NearestNeighbors(n_neighbors=domain_k + 1).fit(X_org)
    distances, indices = nbrs.kneighbors(X_org)
    
    for i in cg_indices:
        # Find non-CG neighbors (collapse targets)
        noncg_neighbors = [j for j in indices[i, 1:] if y_regime[j] != 'CG']
        if len(noncg_neighbors) == 0:
            # No non-CG neighbor reachable in one step — CG is locally isolated
            recovery_records.append({
                'domain': domain,
                'sys_idx': int(dm.iloc[i]['sys_idx']),
                'collapse_available': 0,
                'recovery_possible': -1,
                'recovery_steps_mean': -1,
                'recovery_probability': -1,
                'recovery_entropy': -1,
                'collapse_regime_shifts': -1,
            })
            continue
        
        # For each non-CG neighbor, attempt recovery
        recovery_attempts = []
        recovery_pathways = []
        
        for collapse_target in noncg_neighbors[:5]:  # limit for speed
            coll_regime = y_regime[collapse_target]
            
            for walk in range(RECOVERY_WALKS):
                current = collapse_target
                steps_to_recovery = 0
                recovered = False
                pathway = [i, collapse_target]  # CG → non-CG
                
                for step in range(PERSIST_MAX_STEPS):
                    if y_regime[current] == 'CG':
                        recovered = True
                        break
                    neighbors = indices[current, 1:]
                    # Remove already visited to avoid loops
                    probs = np.ones(len(neighbors))
                    probs = probs / probs.sum()
                    current = int(np.random.choice(neighbors, p=probs))
                    pathway.append(current)
                    steps_to_recovery += 1
                
                recovery_attempts.append({
                    'recovered': recovered,
                    'steps': steps_to_recovery if recovered else PERSIST_MAX_STEPS,
                    'collapse_regime': coll_regime,
                })
                
                if recovered:
                    recovery_pathways.append(pathway)
        
        if len(recovery_attempts) == 0:
            continue
        
        rec_prob = np.mean([a['recovered'] for a in recovery_attempts])
        rec_steps = np.mean([a['steps'] for a in recovery_attempts if a['recovered']]) if rec_prob > 0 else -1
        coll_regimes = [a['collapse_regime'] for a in recovery_attempts]
        regime_unique, regime_counts = np.unique(coll_regimes, return_counts=True)
        rec_entropy = -np.sum((regime_counts/regime_counts.sum()) * np.log2(regime_counts/regime_counts.sum())) if len(regime_counts) > 1 else 0
        
        recovery_records.append({
            'domain': domain,
            'sys_idx': int(dm.iloc[i]['sys_idx']),
            'collapse_available': len(noncg_neighbors),
            'recovery_possible': int(rec_prob > 0),
            'recovery_steps_mean': round(rec_steps, 2) if rec_prob > 0 else -1,
            'recovery_probability': round(rec_prob, 4),
            'recovery_entropy': round(rec_entropy, 4),
            'collapse_regime_shifts': len(regime_unique),
        })

recovery_df = pd.DataFrame(recovery_records)
recovery_df.to_csv(f'{BASE}/outputs/recovery_metrics.csv', index=False)
print(f'\nRecovery metrics saved: {len(recovery_df)} CG systems')

# Summary
recoverable = recovery_df[recovery_df['recovery_possible'] == 1]
non_recoverable = recovery_df[recovery_df['recovery_possible'] == 0]
no_collapse = recovery_df[recovery_df['collapse_available'] == 0]
print(f'\nCG recovery analysis:')
print(f'  Recoverable: {len(recoverable)}/{len(recovery_df)} ({100*len(recoverable)/len(recovery_df):.1f}%)')
print(f'  No recovery pathway: {len(non_recoverable)} (no collapse neighbor)')
print(f'  Locally isolated CG (no non-CG neighbors): {len(no_collapse)}')

print('\nRecovery by domain:')
for domain in domains:
    dd = recovery_df[recovery_df['domain'] == domain]
    if len(dd) == 0: continue
    rec = dd[dd['recovery_possible'] == 1]
    print(f'  {domain:25s}: {len(rec)}/{len(dd)} recoverable ({100*len(rec)/len(dd):.1f}%) '
          f'recovery_prob={rec["recovery_probability"].mean():.3f} '
          f'recovery_steps={rec["recovery_steps_mean"].mean():.1f}')

h2_03_04_summary = {
    'phase': 'H2_03+H2_04', 'seed': SEED,
    'n_cg_systems_analyzed': len(persist_df),
    'global_persistence_half_life': float(persist_df['persistence_half_life'].mean()),
    'global_persistence_max': float(persist_df['persistence_max_survival'].mean()),
    'global_perturbation_tolerance': float(persist_df['perturbation_tolerance'].mean()),
    'n_cg_recoverable': int(len(recoverable)),
    'n_cg_non_recoverable': int(len(non_recoverable) + len(no_collapse)),
    'global_recovery_probability': float(recoverable['recovery_probability'].mean()) if len(recoverable) > 0 else 0,
    'global_recovery_steps': float(recoverable['recovery_steps_mean'].mean()) if len(recoverable) > 0 else -1,
}
with open(f'{BASE}/summaries/h2_03_04_summary.json', 'w') as f:
    json.dump(h2_03_04_summary, f, indent=2)
print(f'\nH2_03+H2_04 COMPLETE')
