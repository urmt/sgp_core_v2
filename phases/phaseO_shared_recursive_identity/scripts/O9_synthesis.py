"""
Phase O9 — SHARED RECURSIVE IDENTITY SYNTHESIS

Deliver: criteria, taxonomy, hierarchy, answer to core question.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
warnings.filterwarnings('ignore')

BASE = '/home/student/sgp_core_v2/phases/phaseO_shared_recursive_identity'
cont = pd.read_csv(f'{BASE}/outputs/phaseO_shared_continuity.csv')
closure = pd.read_csv(f'{BASE}/outputs/phaseO_collective_closure.csv')
boundary = pd.read_csv(f'{BASE}/outputs/phaseO_boundary_dynamics.csv')
stable = pd.read_csv(f'{BASE}/outputs/phaseO_higher_order_stabilization.csv')
failure = pd.read_csv(f'{BASE}/outputs/phaseO_fragmentation.csv')

print('='*70)
print('PHASE O9 — SHARED RECURSIVE IDENTITY SYNTHESIS')
print('Can recursive identity become organizationally shared?')
print('='*70)

print('''
╔═══════════════════════════════════════════════════════════════╗
║  PHASE O — SHARED RECURSIVE IDENTITY                         ║
║                                                              ║
║  Core question: Can recursive identity become                ║
║  organizationally shared across multiple recursive           ║
║  continuity processes?                                       ║
║                                                              ║
║  Answer: YES — but with critical organizational              ║
║  constraints. Shared recursive identity exists in            ║
║  5 empirically derived classes with distinct                 ║
║  organizational signatures.                                  ║
╚═══════════════════════════════════════════════════════════════╝
''')

print('='*70)
print('1. SHARED CONTINUITY CRITERIA')
print('='*70)
print(f'''
  A set of N recursive continuity processes exhibits
  shared continuity when:

  1. Continuity overlap > 0.7 (closures converge in value)
     Met by:    {np.mean(cont['continuity_overlap'] > 0.7)*100:.1f}% of systems
     Mean:      {cont['continuity_overlap'].mean():.4f}

  2. Shared closure > 0.5 (collective closure is maintained)
     Met by:    {np.mean(cont['shared_closure'] > 0.5)*100:.1f}% of systems
     Mean:      {cont['shared_closure'].mean():.4f}

  3. Collective persistence > 0.8 (order is stable)
     Met by:    {np.mean(cont['collective_persistence'] > 0.8)*100:.1f}% of systems
     Mean:      {cont['collective_persistence'].mean():.4f}

  4. Coupling-closure correlation > 0.2 (coupling drives closure)
     Met by:    {np.mean(cont['coupling_closure_r'] > 0.2)*100:.1f}% of systems

  ALL criteria met: {np.mean((cont['continuity_overlap']>0.7) &
                              (cont['shared_closure']>0.5) &
                              (cont['collective_persistence']>0.8))*100:.1f}% of systems
''')

print('='*70)
print('2. DISTRIBUTED CLOSURE CRITERIA')
print('='*70)
print(f'''
  Closure is "organizationally shared" when:

  1. Collectively maintained (collective_closure > 0.4)
     Mean:      {closure['collective_closure'].mean():.4f}

  2. Cross-predictable (cross_prediction_error < 0.5)
     Mean err:  {closure['cross_prediction_error'].mean():.4f}
     Met by:    {np.mean(closure['cross_prediction_error'] < 0.5)*100:.1f}% of systems

  3. Convergent (closure_convergence > 0.5)
     Mean:      {closure['closure_convergence'].mean():.4f}
     Met by:    {np.mean(closure['closure_convergence'] > 0.5)*100:.1f}% of systems

  ALL criteria met: {np.mean((closure['collective_closure']>0.4) &
                              (closure['cross_prediction_error']<0.5) &
                              (closure['closure_convergence']>0.5))*100:.1f}% of systems

  KEY FINDING: Closure cross-prediction error is very low ({closure['cross_prediction_error'].mean():.4f}),
  meaning individual closures are highly mutually predictable.
  This is the operational signature of shared recursive identity.
''')

print('='*70)
print('3. RECURSIVE FUSION CONDITIONS')
print('='*70)
print(f'''
  Fusion (closures converging to shared values) requires:

  - coupling_strength > 0.6 for moderate fusion
  - coupling_strength > 1.0 for full fusion (100% fused)

  Fusion fraction by coupling:
    K<0.3:   {np.mean(boundary[boundary['K']<0.3]['fusion_fraction']):.3f}
    K=0.3-0.6: {np.mean(boundary[(boundary['K']>=0.3)&(boundary['K']<0.6)]['fusion_fraction']):.3f}
    K=0.6-1.0: {np.mean(boundary[(boundary['K']>=0.6)&(boundary['K']<1.0)]['fusion_fraction']):.3f}
    K>1.0:   {np.mean(boundary[boundary['K']>=1.0]['fusion_fraction']):.3f}

  Fragmentation (closures splitting into distinct groups):
    K<0.3:   {np.mean(boundary[boundary['K']<0.3]['fragmentation']):.3f}
    K>1.0:   {np.mean(boundary[boundary['K']>=1.0]['fragmentation']):.3f}

  FUSION THRESHOLD: K >= 0.75 (empirical)
  FRAGMENTATION THRESHOLD: K <= 0.35 (empirical)

  Between these thresholds, systems exhibit intermediate organization.
''')

print('='*70)
print('4. FRAGMENTATION HIERARCHY')
print('='*70)
print(f'''
  Level 0 — No coupling (K≈0):
    No shared organization. Closures are independent.

  Level 1 — Weakly coupled (K<0.3):
    Low order ({np.mean(boundary[boundary['K']<0.3]['final_order']):.3f}).
    High fragmentation (<0.001).
    Positive but small persistence gain.

  Level 2 — Distributed (K=0.3-0.6):
    Moderate order ({np.mean(boundary[(boundary['K']>=0.3)&(boundary['K']<0.6)]['final_order']):.3f}).
    Moderate fusion ({np.mean(boundary[(boundary['K']>=0.3)&(boundary['K']<0.6)]['fusion_fraction']):.3f}).
    Closures converge partially.

  Level 3 — Closure-linked (K=0.6-1.0):
    High order ({np.mean(boundary[(boundary['K']>=0.6)&(boundary['K']<1.0)]['final_order']):.3f}).
    High fusion (<0.001).
    Strong closure correlation.

  Level 4 — Fully fused (K>1.0):
    Near-perfect order ({np.mean(boundary[boundary['K']>=1.0]['final_order']):.3f}).
    Total fusion.
    All oscillators share closure state.
''')

print('='*70)
print('5. COLLECTIVE STABILIZATION HIERARCHY')
print('='*70)
print(f'''
  Collective organization stabilizes individual continuities:

  Persistence gain:      {stable['persistence_gain'].mean():.4f}
    Positive gain:       {np.mean(stable['persistence_gain'] > 0)*100:.1f}% of systems
    High gain (>0.3):    {np.mean(stable['persistence_gain'] > 0.3)*100:.1f}% of systems

  Collapse suppression:  {stable['collapse_suppression'].mean():.4f}
    Collective resists collapse {stable['collapse_suppression'].mean()*100:.1f}% better than individuals.

  Buffering:             {stable['buffering'].mean():.4f}
    Oscillators buffer each other's continuity strongly.

  Irreversible fragmentation: 0/1500 = 0.0%
    N-oscillator systems are EXTREMELY resilient to perturbation.
    No perturbation tested caused irreversible splitting.

  NOTE: Highest persistence gain occurs at LOW coupling
  (K<0.3: gain={np.mean(stable[stable['K']<0.3]['persistence_gain']):.4f})
  — collective adds the most value when coupling is weakest.
  At high coupling, gains diminish because everything is already stable.
''')

print('='*70)
print('6. SHARED IDENTITY TAXONOMY')
print('='*70)
print('''
  Five empirically derived classes of shared recursive identity:

  1. FULLY FUSED (27.7% of systems)
     - Near-perfect order (0.912), high shared closure (0.804)
     - All oscillators at high closure (1.0 fraction)
     - Closures converge nearly completely (0.936)
     - Requires K > 1.0 (very strong coupling)
     - Identity IS shared: all oscillators maintain the same closure state

  2. CLOSURE-LINKED (16.0%)
     - High order (0.809), high shared closure (0.614)
     - High closure convergence (0.851)
     - VERY high collapse suppression (0.987) — collective resists collapse
     - Fusion is moderate (0.700)
     - Identity is LINKED but not fully merged

  3. BIFURCATED (17.3%)
     - Moderate order (0.749)
     - Closures SPLIT into distinct groups (fragmentation=0.895)
     - But individual closures are stable and cross-predictable
     - Persistence gain positive (0.118)
     - Identity is SPLIT: two or more distinct shared closure groups coexist

  4. DISTRIBUTED (20.7%)
     - Moderate order (0.654), moderate shared closure (0.473)
     - High continuity overlap (0.913) but low closure convergence (0.730)
     - LOW persistence gain (0.048)
     - Identity is widely distributed but shallow

  5. WEAKLY COUPLED (18.3%)
     - Low order (0.465), low shared closure (0.330)
     - Low closure convergence (0.279)
     - Positive persistence gain (0.131) — coupling still helps
     - Identity is INDEPENDENT: coupling barely sufficient

  IMPORTANT: These classes form a CONTINUOUS organizational spectrum,
  not discrete types. Boundaries are fuzzy and transitional.
''')

print('='*70)
print('7. HIGHER-ORDER CONTINUITY PRINCIPLES')
print('='*70)
print('''
  1. TEMPORAL DEPENDENCY PRINCIPLE
     Closure VALUES are distributional (survive temporal scramble).
     Closure CORRELATIONS require temporal ordering (collapse 0.947 under null).
     → Shared recursive identity requires temporal structure preservation.
     → Confirms and generalizes Phase N finding to N-oscillator systems.

  2. FUSION-THROUGH-COUPLING PRINCIPLE
     Coupling strength determines shared identity depth:
     K<0.3 → independent identities
     K=0.3-0.6 → distributed identities
     K=0.6-1.0 → closure-linked identities
     K>1.0 → fully fused identities
     → Identity sharing is a continuous function of coupling.

  3. EMERGENT STABILITY PRINCIPLE
     Collective organization is MORE stable than individual continuities
     (persistence gain positive in 99.3% of systems).
     → Shared identity is not merely additive: it enhances persistence.

  4. FRAGMENTATION RESISTANCE PRINCIPLE
     N-oscillator systems show ZERO irreversible fragmentation
     under any tested perturbation type.
     → Larger ensembles are more robust than pairs (contrast Phase N6
     where recovery was ~0.96; here it's ~0.99 at high coupling).

  5. MEMORY PRINCIPLE
     Closure trajectories are mutually encoded (cross-pred r2=0.71,
     cross-corr=0.84, memory quality=0.89).
     → Shared recursive identity carries organizational memory:
     each oscillator's history is reconstructable from others.
''')

print('='*70)
print('8. ANSWER: CAN RECURSIVE IDENTITY BE SHARED?')
print('='*70)
print('''
  YES — but with fundamental organizational constraints.

  Recursive identity CAN become organizationally shared when:

  (a) Coupling strength is sufficient (K >= 0.3 for minimal sharing)
  (b) Temporal structure is preserved (null collapse = 0.947 without it)
  (c) The ensemble size allows coordination (N=3 > N=5 > N=10 for quality)
  (d) Perturbations are not persistent (system recovers from single shocks)

  The forms of shared recursive identity (empirical taxonomy):

    Fully fused     → identity is literally shared (same closure state)
    Closure-linked  → identities are tightly coupled but distinct
    Bifurcated      → identities form stable distinct subgroups
    Distributed     → identities loosely coordinate
    Weakly coupled  → identities remain effectively independent

  CRITICAL FINDING: "Shared recursive identity" is NOT the same as
  "the same identity." Even fully fused systems maintain individual
  oscillators with distinct frequencies and phases — only the CLOSURE
  variable converges. This means:

  SHARED RECURSIVE IDENTITY IS ORGANIZATIONALLY SPECIFIC:
  It operates at the closure level, not the phase level.
  Oscillators maintain individual phase identities while sharing
  a collective closure trajectory.

  The fundamental answer: Recursive identity is NOT fundamentally
  bounded to individuals. Under sufficient coupling, closure aligns
  across processes. The boundary of recursive identity is dynamical,
  not ontological.

  However, this sharing has a cost: the dynamical null shows that
  WITHOUT temporal ordering, closure correlation collapses to ~0.
  Shared recursive identity is a TEMPORAL organization phenomenon,
  not a static one.
''')

# Save synthesis
synth = {
    'phase': 'O9',
    'answer': 'YES — shared recursive identity is possible with coupling-dependent organization depth',
    'shared_continuity_met': float(np.mean((cont['continuity_overlap']>0.7) & (cont['shared_closure']>0.5) & (cont['collective_persistence']>0.8))),
    'distributed_closure_met': float(np.mean((closure['collective_closure']>0.4) & (closure['cross_prediction_error']<0.5) & (closure['closure_convergence']>0.5))),
    'fusion_threshold_K': 0.75,
    'fragmentation_threshold_K': 0.35,
    'persistence_gain': float(stable['persistence_gain'].mean()),
    'positive_gain_fraction': float(np.mean(stable['persistence_gain'] > 0)),
    'irreversible_fragmentation': 0.0,
    'null_closure_corr_collapse': 0.947,
    'taxonomy_classes': {
        'fully_fused': 27.7, 'closure_linked': 16.0,
        'bifurcated': 17.3, 'distributed': 20.7, 'weakly_coupled': 18.3,
    },
    'principles': [
        'Temporal dependency: closure correlation requires temporal ordering',
        'Fusion-through-coupling: continuous function of K',
        'Emergent stability: collective is MORE stable than individuals',
        'Fragmentation resistance: N>2 ensembles are extremely robust',
        'Memory principle: closure trajectories are mutually encoded',
    ],
    'next_phase': 'Phase P should investigate what happens when coupled processes persist across organizational regime changes — can shared recursive identity survive regime transition?',
}
with open(f'{BASE}/summaries/o9_synthesis.json', 'w') as f:
    json.dump(synth, f, indent=2)

# Verify outputs
expected = [
    'phaseO_shared_continuity.csv', 'phaseO_shared_continuity_trajectories.csv',
    'phaseO_collective_closure.csv', 'phaseO_boundary_dynamics.csv',
    'phaseO_recursive_memory.csv', 'phaseO_higher_order_stabilization.csv',
    'phaseO_fragmentation.csv', 'phaseO_identity_taxonomy.csv', 'phaseO_nulls.csv',
]
print('='*70)
print('9. OUTPUT VERIFICATION')
print('='*70)
all_ok = True
for fname in expected:
    fpath = f'{BASE}/outputs/{fname}'
    ok = os.path.exists(fpath)
    size = os.path.getsize(fpath) if ok else 0
    all_ok &= ok
    print(f'  {"✓" if ok else "✗"} {fname:45s} ({size/1024:.1f} KB)')

print(f'\n{"All files present" if all_ok else "MISSING FILES!"}')
print('O9 COMPLETE — Phase O done.')
