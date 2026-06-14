"""
Phase G6 — Cross-Family Analysis.
Tests whether different families occupy different coherence–fertility regions.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from scipy.stats import ttest_ind
warnings.filterwarnings('ignore')

BASE = '/home/student/sgp_core_v2/phases/phaseG'
phase = pd.read_csv(f'{BASE}/processed/coherence_fertility_phase_space.csv')
domains = sorted(phase['domain'].unique())

t0 = time.time()
print('='*70)
print('PHASE G6 — CROSS-FAMILY ANALYSIS')
print('='*70)

records = []
for domain in domains:
    dm = phase[phase['domain'] == domain]
    rest = phase[phase['domain'] != domain]
    c_mean = dm['coherence'].mean()
    f_mean = dm['fertility'].mean()
    c_rest = rest['coherence'].mean()
    f_rest = rest['fertility'].mean()
    
    # Region composition
    rc = dm['region'].value_counts()
    cg_pct = 100 * rc.get('constrained_generative', 0) / len(dm)
    rigid_pct = 100 * rc.get('rigid_coherence', 0) / len(dm)
    chaotic_pct = 100 * rc.get('chaotic_fertility', 0) / len(dm)
    collapse_pct = 100 * rc.get('collapse', 0) / len(dm)
    
    records.append({
        'domain': domain, 'n_systems': len(dm),
        'coherence_mean': round(c_mean, 4),
        'fertility_mean': round(f_mean, 4),
        'coherence_vs_rest': round(c_mean - c_rest, 4),
        'fertility_vs_rest': round(f_mean - f_rest, 4),
        'constrained_generative_pct': round(cg_pct, 1),
        'rigid_coherence_pct': round(rigid_pct, 1),
        'chaotic_fertility_pct': round(chaotic_pct, 1),
        'collapse_pct': round(collapse_pct, 1),
    })

fam_df = pd.DataFrame(records)
fam_df.to_csv(f'{BASE}/processed/cross_family_positions.csv', index=False)
print(f'Saved: {len(fam_df)} rows')

# Classification
print('\nFamily coherence–fertility profiles:')
for _, r in fam_df.iterrows():
    print(f'  {r["domain"]:25s}: C={r["coherence_mean"]:.3f} F={r["fertility_mean"]:.3f}  '
          f'CG={r["constrained_generative_pct"]:5.1f}%  Rigid={r["rigid_coherence_pct"]:5.1f}%  '
          f'Chaos={r["chaotic_fertility_pct"]:5.1f}%  Collapse={r["collapse_pct"]:5.1f}%')

# Identify primary organizational regime per family
print('\nPrimary regime per family:')
for _, r in fam_df.iterrows():
    regimes = {k: r[k] for k in ['constrained_generative_pct','rigid_coherence_pct',
                                  'chaotic_fertility_pct','collapse_pct']}
    primary = max(regimes, key=regimes.get)
    primary_val = regimes[primary]
    print(f'  {r["domain"]:25s}: {primary:30s} ({primary_val:.0f}%)')

# Which families sustain constrained generativity?
print('\nConstrained generativity families:')
cg_fams = fam_df[fam_df['constrained_generative_pct'] > 10].sort_values('constrained_generative_pct', ascending=False)
for _, r in cg_fams.iterrows():
    print(f'  {r["domain"]:25s}: {r["constrained_generative_pct"]:.1f}%')

print('\nRigid families:')
rig_fams = fam_df[fam_df['rigid_coherence_pct'] > 50]
for _, r in rig_fams.iterrows():
    print(f'  {r["domain"]:25s}: {r["rigid_coherence_pct"]:.1f}%')

print('\nChaotic families:')
cha_fams = fam_df[fam_df['chaotic_fertility_pct'] > 50]
for _, r in cha_fams.iterrows():
    print(f'  {r["domain"]:25s}: {r["chaotic_fertility_pct"]:.1f}%')

print('\nCollapse families:')
col_fams = fam_df[fam_df['collapse_pct'] > 50]
for _, r in col_fams.iterrows():
    print(f'  {r["domain"]:25s}: {r["collapse_pct"]:.1f}%')

g6_summary = {
    'phase': 'G6', 'seed': 3000,
    'constrained_generative_families': [str(d) for d in cg_fams['domain'].values],
    'rigid_families': [str(d) for d in rig_fams['domain'].values] if len(rig_fams) > 0 else [],
    'chaotic_families': [str(d) for d in cha_fams['domain'].values] if len(cha_fams) > 0 else [],
    'collapse_families': [str(d) for d in col_fams['domain'].values] if len(col_fams) > 0 else [],
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/g6_summary.json', 'w') as f:
    json.dump(g6_summary, f, indent=2)

print(f'\nG6 COMPLETE ({time.time()-t0:.1f}s)')
