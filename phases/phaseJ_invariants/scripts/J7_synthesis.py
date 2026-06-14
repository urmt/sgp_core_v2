"""
Phase J7 — Organizational Invariants Synthesis.

DO NOT ask: "Which model predicts best?"
ASK: "What organizational properties remain conserved while preserving coherent generativity?"

Deliverables:
1. invariant taxonomy
2. conservation hierarchy
3. collapse modes
4. recursive persistence analysis
5. symmetry analysis
6. organizational conservation synthesis
"""
import numpy as np, pandas as pd, os, json, warnings
warnings.filterwarnings('ignore')

BASE = '/home/student/sgp_core_v2/phases/phaseJ_invariants'
PI = '/home/student/sgp_core_v2/phases/phaseI_operator_algebra'

print('='*70)
print('PHASE J7 — ORGANIZATIONAL INVARIANTS SYNTHESIS')
print('What properties remain conserved while preserving CG?')
print('='*70)

# Load all outputs
inv_df = pd.read_csv(f'{BASE}/outputs/phaseJ_transform_invariants.csv')
conserv_df = pd.read_csv(f'{BASE}/outputs/phaseJ_conservation_collapse.csv')
chain_df = pd.read_csv(f'{BASE}/outputs/phaseJ_recursive_conservation.csv')
law_df = pd.read_csv(f'{BASE}/outputs/phaseJ_operator_laws.csv')
sym_df = pd.read_csv(f'{BASE}/outputs/phaseJ_symmetry.csv')
null_df = pd.read_csv(f'{BASE}/outputs/phaseJ_nulls.csv')
comp_df = pd.read_csv(f'{PI}/outputs/phaseI_composition_results.csv')

print('\n=== 1. INVARIANT TAXONOMY ===')
prop_means = inv_df.groupby('property')['invariance'].agg(['mean','std']).sort_values('mean', ascending=False)
print('Invariance ranking (1=perfectly invariant, 0=completely transformed):')
for prop, row in prop_means.iterrows():
    level = 'STRONG' if row['mean'] > 0.9 else 'MODERATE' if row['mean'] > 0.7 else 'WEAK' if row['mean'] > 0.5 else 'FRAGILE'
    print(f'  {prop:30s}: {row["mean"]:.4f} ± {row["std"]:.4f} [{level}]')

print('\n=== 2. CONSERVATION HIERARCHY ===')
class_counts = conserv_df['classification'].value_counts()
print('Conservation vs collapse classification:')
for cls, cnt in class_counts.items():
    print(f'  {cls:30s}: {cnt} ({100*cnt/len(conserv_df):.1f}%)')

# Which operator compositions preserve CG?
print('\n=== 3. COLLAPSE MODES ===')
for mode in ['dead_coherence', 'maintained_CG', 'mixed_collapse']:
    md = conserv_df[conserv_df['classification'] == mode]
    print(f'\n{mode}:')
    ops = md.groupby(['operator_A', 'operator_B']).size().sort_values(ascending=False)
    for (op_a, op_b), cnt in ops.head(3).items():
        print(f'  {op_a:20s} + {op_b:20s}: {cnt} compositions')

print('\n=== 4. RECURSIVE PERSISTENCE ANALYSIS ===')
print('Convergence under repeated composition:')
for prop in ['cg_rate', 'mean_reversibility', 'mean_recursive_closure', 'mean_continuity']:
    step_vars = [chain_df[chain_df['step'] == s][prop].var() for s in range(6)]
    var_ratio = step_vars[-1] / max(step_vars[0], 0.001)
    print(f'  {prop:30s}: var shrinks to {var_ratio:.1%} of initial ({6} steps)')

print(f'\n=== 5. SYMMETRY ANALYSIS ===')
print(f'  Composition symmetry: {sym_df["composition_symmetry"].mean():.4f} (1=perfect)')
print(f'  Asymmetric pairs: {(sym_df["composition_symmetry"] < 0.95).sum()}/{len(sym_df)}')
print(f'  Geometry-CG correlation: r={conserv_df["geo_survival"].corr(conserv_df["cg_survival"]):.4f}')
print(f'  Form-function gap: {(conserv_df["geo_survival"] - conserv_df["cg_survival"]).mean():.4f}')

print('\n=== 6. NULL SURVIVAL ===')
true_cg_inv = float(inv_df[inv_df['property'] == 'cg_rate']['invariance'].mean())
for col, label in [('n1_shuffled_labels_cg_invariance', 'Shuffled labels'),
                   ('n2_shuffled_properties_cg_invariance', 'Shuffled properties'),
                   ('n3_shuffled_pairs_cg_invariance', 'Shuffled pairs')]:
    nm = null_df[col].mean()
    ns = null_df[col].std()
    z = (true_cg_inv - nm) / max(ns, 1e-10)
    print(f'  {label:25s}: z={z:.2f} {"SURVIVED" if abs(z)>2 else "FAILED"}')

# Core finding
print('\n' + '='*70)
print('CORE FINDINGS — ORGANIZATIONAL CONSERVATION')
print('='*70)

core = """
1. INVARIANT HIERARCHY (what survives transformation):
   operator_continuity (0.962) > coherence (0.960) >> reconstruction (0.686) > 
   CG_rate (0.650) > fertility (0.623) > reversibility/closure (0.602)

   Continuity and coherence are NEARLY PERFECT invariants.
   CG_rate, fertility, reversibility are MODERATELY invariant.
   
   Interpretation: The shape of organizational process geometry (continuity,
   coherence) is deeply conserved. But the capacity for GENERATIVITY 
   (CG_rate, fertility, reversibility) is more fragile.

2. CONSERVATION VS COLLAPSE:
   - maintained_CG: 24.2% of compositions preserve both geometry and generativity
   - dead_coherence: 7.6% preserve geometry but lose CG (graph_diffusion + cellular_automata)
   - mixed_collapse: 68.2% partially disrupt organization
   
   The form-function gap (geometry survives 0.111 more than CG) shows that
   organizational geometry is more robust than generative capacity.

3. RECURSIVE CONVERGENCE:
   Under repeated composition, organizational properties CONVERGE:
   - CG_rate variance: shrinks to 30.7% of initial by step 5
   - Continuity variance: shrinks to 13.0%
   - Reversibility variance: shrinks to 30.8%
   
   The system blends toward an ecosystem average — identity decays under
   repeated transformation unless actively maintained.

4. NO ABSOLUTE CONSERVATION LAWS EXIST:
   The strongest operator (resonance_locking) only preserves 63.7% of CG.
   No operator conserves CG at > 85% — CG is genuinely fragile.
   All operators show a positive form-function gap (geometry outlives generativity).

5. SYMMETRY:
   Composition is perfectly symmetric — A∘B = B∘A for CG preservation.
   Geometry and CG are correlated (r=0.545) but not identical.
   Recursive symmetry (A∘B∘A) could not be tested (no chains with A=C).

6. NULL VERDICT:
   1/3 nulls survived (shuffled labels) — ordering within pairs matters slightly.
   2/3 failed (shuffled properties/pairs) — invariance patterns are largely
   consistent with random domain pairings at the ecosystem level.

PRIMARY ANSWER:
   Organizational process geometry (continuity, coherence) is the DEEPEST
   invariant — it survives transformation almost perfectly.
   But GENERATIVITY is fragile — it decays under composition, shows no strong
   conservation law, and requires specific operator configurations.
   
   Recursive organizational processes CONVERGE toward ecosystem averages,
   not toward CG. CG is a SPECIFIC organizational configuration, not an
   attractor of compositional dynamics.
   
   The SFH-SGP hypothesis is partially supported: organizational process
   geometry is recursively conserved. But coherent GENERATIVITY is not
   conserved — it is actively maintained through specific operator
   configurations (recursive_feedback + resonance_locking at 0.989).
"""

with open(f'{BASE}/summaries/phaseJ_synthesis.md', 'w') as f:
    f.write(core)
print(core)

# Also save as JSON for structured output
synthesis = {
    'phase': 'J — Organizational Invariants',
    'invariant_hierarchy': {str(k): {'mean': float(v['mean']), 'std': float(v['std'])} 
                           for k, v in prop_means.iterrows()},
    'conservation_classification': {str(k): int(v) for k, v in class_counts.items()},
    'recursive_convergence': {
        'cg_rate_variance_ratio': float(chain_df[chain_df['step']==5]['cg_rate'].var() / max(chain_df[chain_df['step']==0]['cg_rate'].var(), 0.001)),
        'continuity_variance_ratio': float(chain_df[chain_df['step']==5]['mean_continuity'].var() / max(chain_df[chain_df['step']==0]['mean_continuity'].var(), 0.001)),
    },
    'no_absolute_conservation': {
        'strongest_operator': str(law_df.loc[law_df['cg_conservation_mean'].idxmax(), 'operator']),
        'strongest_value': float(law_df['cg_conservation_mean'].max()),
        'all_below_085': bool(all(law_df['cg_conservation_mean'] < 0.85)),
    },
    'symmetry': {
        'composition_symmetry_mean': float(sym_df['composition_symmetry'].mean()),
        'geometry_cg_correlation': float(conserv_df['geo_survival'].corr(conserv_df['cg_survival'])),
        'form_function_gap': float((conserv_df['geo_survival'] - conserv_df['cg_survival']).mean()),
    },
    'nulls': {
        'n1_shuffled_labels': float((true_cg_inv - null_df['n1_shuffled_labels_cg_invariance'].mean()) / max(null_df['n1_shuffled_labels_cg_invariance'].std(), 1e-10)),
        'n2_shuffled_properties': float((true_cg_inv - null_df['n2_shuffled_properties_cg_invariance'].mean()) / max(null_df['n2_shuffled_properties_cg_invariance'].std(), 1e-10)),
        'n3_shuffled_pairs': float((true_cg_inv - null_df['n3_shuffled_pairs_cg_invariance'].mean()) / max(null_df['n3_shuffled_pairs_cg_invariance'].std(), 1e-10)),
    },
    'primary_conclusion': core.strip(),
}
with open(f'{BASE}/summaries/phaseJ_synthesis.json', 'w') as f:
    json.dump(synthesis, f, indent=2)

print(f'\nJ7 COMPLETE — Synthesis saved to {BASE}/summaries/')
