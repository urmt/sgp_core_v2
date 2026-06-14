"""
Phase H3+H4+H5 — Transition Maps + Attractors + Minimal Conditions.
Constructs transition probability maps, tests attractor structure.
"""
import numpy as np, pandas as pd, os, json, time, warnings
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

SEED = 3000; np.random.seed(SEED)
BASE = '/home/student/sgp_core_v2/phases/phaseH'
os.makedirs(f'{BASE}/transition_maps', exist_ok=True)
os.makedirs(f'{BASE}/processed', exist_ok=True)

int_df = pd.read_csv(f'{BASE}/interventions/intervention_results.csv')
domains = sorted(int_df['domain'].unique())
regime_order = ['constrained_generative','rigid_coherence','chaotic_fertility','collapse']

t0 = time.time()
print('='*70)
print('PHASE H3+H4+H5 — TRANSITION MAPS + ATTRACTORS + MINIMAL CONDITIONS')
print('='*70)

# === H3: TRANSITION PROBABILITY MAPS ===
print('\n--- H3: Causal Transition Maps ---')
trans_map_records = []

for domain in domains:
    dd = int_df[int_df['domain'] == domain]
    for desc in dd['desc_name'].unique():
        di = dd[dd['desc_name'] == desc]
        for r_from in regime_order:
            rf = di[di['regime_from'] == r_from]
            if len(rf) == 0: continue
            for r_to in regime_order:
                p = len(rf[rf['regime_to'] == r_to]) / len(rf)
                trans_map_records.append({
                    'domain': domain, 'intervention': f'perturb_{desc}',
                    'regime_from': r_from, 'regime_to': r_to,
                    'probability': round(p, 4), 'n_trials': len(rf),
                })

trans_map_df = pd.DataFrame(trans_map_records)
trans_map_df.to_csv(f'{BASE}/transition_maps/regime_transition_maps.csv', index=False)
print(f'Transition maps saved: {len(trans_map_df)} entries')

# === H4: ATTRACTOR ANALYSIS ===
print('\n--- H4: Organizational Attractors ---')
# An attractor regime: high self-transition probability, low escape probability
att_records = []
for domain in domains:
    dd = int_df[int_df['domain'] == domain]
    for r in regime_order:
        rf = dd[dd['regime_from'] == r]
        if len(rf) == 0: continue
        self_prob = len(rf[rf['regime_to'] == r]) / len(rf)
        # Escape probability = 1 - self_prob
        escape_prob = 1 - self_prob
        # Entropy of transition distribution
        probs = np.array([len(rf[rf['regime_to'] == rt]) / len(rf) for rt in regime_order])
        probs = probs[probs > 0]
        trans_entropy = -np.sum(probs * np.log2(probs)) / np.log2(4) if len(probs) > 0 else 0
        
        att_records.append({
            'domain': domain, 'regime': r,
            'self_transition_prob': round(self_prob, 4),
            'escape_probability': round(escape_prob, 4),
            'transition_entropy': round(trans_entropy, 4),
            'n_interventions': len(rf),
        })

att_df = pd.DataFrame(att_records)
att_df.to_csv(f'{BASE}/processed/attractor_analysis.csv', index=False)
print(f'Attractor analysis saved: {len(att_df)} entries')

# Which regimes act as attractors?
print('\nRegime attractor strength (self-transition prob):')
for r in regime_order:
    atts = att_df[att_df['regime'] == r]
    print(f'  {r:30s}: self={atts["self_transition_prob"].mean():.3f}  escape={atts["escape_probability"].mean():.3f}')

print('\nPer-domain attractors:')
for _, r in att_df.iterrows():
    print(f'  {r["domain"]:25s} {r["regime"]:30s}: self={r["self_transition_prob"]:.3f}  escape={r["escape_probability"]:.3f}  H={r["transition_entropy"]:.3f}')

# === H5: MINIMAL CONDITIONS ===
print('\n--- H5: Minimal Conditions for CG from Non-CG ---')
# What intervention most reliably produces CG?
cg_from_noncg = int_df[
    (int_df['regime_from'] != 'constrained_generative') &
    (int_df['regime_to'] == 'constrained_generative')
]
if len(cg_from_noncg) > 0:
    print(f'\nSystems that transition TO constrained generativity: {len(cg_from_noncg)}')
    print('By intervention:')
    for desc, count in cg_from_noncg['desc_name'].value_counts().items():
        total = len(int_df[int_df['desc_name'] == desc])
        print(f'  Perturb {desc:5s}: {count}/{total} = {100*count/total:.1f}%')

    print('\nBy source regime:')
    for r in regime_order:
        if r == 'constrained_generative': continue
        count = len(cg_from_noncg[cg_from_noncg['regime_from'] == r])
        total = len(int_df[int_df['regime_from'] == r])
        print(f'  From {r:25s}: {count}/{total} = {100*count/total:.1f}%')

# Minimal conditions: which descriptor change most predicts C→CG?
print('\nMinimal conditions for entering constrained generativity:')
for domain in domains:
    dd = int_df[(int_df['domain'] == domain) & 
                (int_df['regime_from'] != 'constrained_generative')]
    if len(dd) == 0: continue
    cg_from = dd[dd['regime_to'] == 'constrained_generative']
    total_from = len(dd)
    cg_rate = len(cg_from) / total_from if total_from > 0 else 0
    best_desc = cg_from.groupby('desc_name').size().idxmax() if len(cg_from) > 0 else 'N/A'
    print(f'  {domain:25s}: CG entry rate={cg_rate:.3f}  best trigger={best_desc}')

# Minimal conditions CSV
min_df = int_df[(int_df['regime_to'] == 'constrained_generative') & 
                (int_df['regime_from'] != 'constrained_generative')]
min_df.to_csv(f'{BASE}/processed/minimal_conditions.csv', index=False)
print(f'\nMinimal conditions saved: {len(min_df)} entries')

h3h4h5_summary = {
    'phase': 'H3+H4+H5', 'seed': SEED,
    'n_transition_map_entries': len(trans_map_df),
    'n_attractor_entries': len(att_df),
    'n_minimal_conditions': len(min_df),
    'strongest_self_attractor': str(att_df.loc[att_df['self_transition_prob'].idxmax(), 'regime']),
    'weakest_self_attractor': str(att_df.loc[att_df['self_transition_prob'].idxmin(), 'regime']),
    'cg_entry_rate_from_noncg': len(cg_from_noncg) / max(1, len(int_df[int_df['regime_from'] != 'constrained_generative'])),
    'runtime_seconds': round(time.time() - t0),
}
with open(f'{BASE}/summaries/h3h4h5_summary.json', 'w') as f:
    json.dump(h3h4h5_summary, f, indent=2)
print(f'\nH3+H4+H5 COMPLETE ({time.time()-t0:.1f}s)')
