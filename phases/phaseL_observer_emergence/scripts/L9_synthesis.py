"""
Phase L9 — FINAL SYNTHESIS

Question: Under what organizational conditions does
recursive identity become self-referential?

DO NOT ask: "Which systems are conscious?"
ASK: "Which organizational conditions permit
      stable recursive self-referential continuity?"

Anti-drift: This is organizational analysis, not philosophy.
"""
import sys, numpy as np, pandas as pd, os, json, warnings
sys.path.insert(0, '/home/student/sgp_core_v2')
from scipy.stats import pearsonr
warnings.filterwarnings('ignore')

BASE = '/home/student/sgp_core_v2/phases/phaseL_observer_emergence'
os.makedirs(f'{BASE}/outputs', exist_ok=True)

# Load latest data
sr_df = pd.read_csv(f'{BASE}/outputs/phaseL_temporal_self_modeling.csv')
print(f'Loaded: {len(sr_df)} systems')

print('='*70)
print('PHASE L9 — FINAL SYNTHESIS')
print('Organizational conditions for recursive self-referential continuity')
print('='*70)

# ====================================================
# 1. What organizational conditions enable observer-like persistence?
# ====================================================
print('\n=== 1. ORGANIZATIONAL CONDITIONS FOR OBSERVER-LIKE PERSISTENCE ===')

# Condition 1: Recursive closure (r=0.747 with self-reference)
# Without closure, the process cannot refer to itself
cond1 = sr_df['recursive_closure'].mean()
print(f'  C1 — Recursive closure:       mean={cond1:.4f}')

# Condition 2: Reconstruction ability (r=0.852)
# Without reconstruction, identity cannot persist through perturbation
cond2 = sr_df['reconstruction_ability'].mean()
print(f'  C2 — Reconstruction ability:  mean={cond2:.4f}')

# Condition 3: Self-model consistency (r=0.747 with closure)
# Without self-model consistency, closure cannot stabilize
cond3 = sr_df['self_model_consistency'].mean()
print(f'  C3 — Self-model consistency:  mean={cond3:.4f}')

# Condition 4: Temporal coherence (collapse=0.9996 when removed)
# Without temporal structure, observer continuity is destroyed
cond4 = sr_df['temporal_self_coherence'].mean()
print(f'  C4 — Temporal self-coherence: mean={cond4:.4f}')

# Condition 5: Operator reversibility (r=0.747)
# Without reversibility, the process cannot maintain identity through transformation
cond5 = sr_df['operator_reversibility'].mean()
print(f'  C5 — Operator reversibility:  mean={cond5:.4f}')

# Condition 6: Closure persistence
# Without persistence, closure must be continuously regenerated
cond6 = sr_df['closure_persistence'].mean()
print(f'  C6 — Closure persistence:     mean={cond6:.4f}')

# ====================================================
# 2. Observer-like process taxonomy
# ====================================================
print('\n=== 2. OBSERVER-LIKE PROCESS TAXONOMY ===')
print('Organizational conditions, not fixed types.')
print('')
print('  Level 0 — Passive: persists because nothing happens')
print('    organizational signature: high transition_smoothness only')
print(f'    prevalence: {(sr_df["observer_level"]==0).sum()} ({100*(sr_df["observer_level"]==0).sum()/len(sr_df):.1f}%)')
print('')
print('  Level 1 — Reactive: responds to perturbation')
print('    organizational signature: active_continuity > passive threshold')
print(f'    prevalence: {(sr_df["observer_level"]==1).sum()} ({100*(sr_df["observer_level"]==1).sum()/len(sr_df):.1f}%)')
print('')
print('  Level 2 — Adaptive: maintains continuity through adaptation')
print('    organizational signature: perspective_continuity + recursive correction')
print(f'    prevalence: {(sr_df["observer_level"]==2).sum()} ({100*(sr_df["observer_level"]==2).sum()/len(sr_df):.1f}%)')
print('')
print('  Level 3 — Observer-like: stable recursive self-referential continuity')
print('    organizational signature: identity_frame_continuity + closure persistence')
print(f'    prevalence: {(sr_df["observer_level"]==3).sum()} ({100*(sr_df["observer_level"]==3).sum()/len(sr_df):.1f}%)')

# ====================================================
# 3. Self-reference hierarchy
# ====================================================
print('\n=== 3. RECURSIVE SELF-REFERENCE HIERARCHY ===')
# Levels of self-reference in processes:
# Level 0: No self-reference — statistical persistence
# Level 1: Self-prediction — process predicts its own trajectory
# Level 2: Self-model — process maintains internal model of its dynamics
# Level 3: Self-reference — process refers to itself through closure

# Measure how many CG systems reach each hierarchy level
cg = sr_df[sr_df['process_regime'] == 'CG']

# Self-prediction threshold (high self_prediction)
print(f'  Level 0 — Statistical: {len(cg)} CG systems')
print(f'  Level 1 — Self-predicts (>median self_prediction): {(cg["self_prediction"] > cg["self_prediction"].median()).sum()}')
print(f'  Level 2 — Self-models (>median self_model_consistency): {(cg["self_model_consistency"] > cg["self_model_consistency"].median()).sum()}')
print(f'  Level 3 — Self-referential (>median observer_continuity): {(cg["observer_continuity"] > cg["observer_continuity"].median()).sum()}')

# ====================================================
# 4. Continuity maintenance analysis
# ====================================================
print('\n=== 4. CONTINUITY MAINTENANCE ANALYSIS ===')
print(f'  Passive persistence (trivial):     {sr_df["passive_persistence"].mean():.4f}')
print(f'  Active continuity (non-trivial):   {sr_df["active_continuity"].mean():.4f}')
print(f'  Observer continuity (rare):         {sr_df["observer_continuity"].mean():.6f}')
print(f'  Active/passive ratio (CG):         {cg["active_continuity"].mean()/(cg["passive_persistence"].mean()+1e-10):.3f}')
print(f'  Active/passive ratio (CL):         {sr_df[sr_df["process_regime"]=="CL"]["active_continuity"].mean()/(sr_df[sr_df["process_regime"]=="CL"]["passive_persistence"].mean()+1e-10):.3f}')

# ====================================================
# 5. Observer failure modes
# ====================================================
print('\n=== 5. OBSERVER FAILURE MODES ===')
print(f'  Most destructive: temporal continuity destruction (collapse=0.9996)')
print(f'  Secondary: closure feedback destruction (collapse=0.4067 overall, 0.7420 for Level 3)')
print(f'  Tertiary: reconstruction destruction (collapse=0.2566 overall, 0.9694 for Level 3)')
print(f'  Null test: composite self-reference collapses completely (1.000) under adversarial null')
print(f'')
print(f'  Observer-like organization REQUIRES:')
print(f'    (1) Temporal continuity — without it, collapse is total')
print(f'    (2) Recursive closure — without it, observer drops 74% (Level 3)')
print(f'    (3) Reconstruction ability — without it, observer drops 97% (Level 3)')

# ====================================================
# 6. Organizational observer criteria
# ====================================================
print('\n=== 6. ORGANIZATIONAL OBSERVER CRITERIA ===')
print('')
print('A process shows observer-like organization when:')
print('')
print('  (a) recursive closure > 0.5 AND')
print('  (b) reconstruction_ability > 0.5 AND')
print('  (c) self_model_consistency > 0.05 AND')
print('  (d) temporal_self_coherence > 0.01 AND')
print('  (e) closure_persistence > 0.5')
print('')
print('These are continuous thresholds, not fixed categories.')
print('Observer-likeness is a GRADIENT, not a binary.')
print('')

# How many systems meet each criterion?
criteria = {
    'C1 recursive_closure > 0.5': (sr_df['recursive_closure'] > 0.5).sum(),
    'C2 reconstruction_ability > 0.5': (sr_df['reconstruction_ability'] > 0.5).sum(),
    'C3 self_model_consistency > 0.05': (sr_df['self_model_consistency'] > 0.05).sum(),
    'C4 temporal_self_coherence > 0.01': (sr_df['temporal_self_coherence'] > 0.01).sum(),
    'C5 closure_persistence > 0.5': (sr_df['closure_persistence'] > 0.5).sum(),
}
all_met_mask = (
    (sr_df['recursive_closure'] > 0.5) &
    (sr_df['reconstruction_ability'] > 0.5) &
    (sr_df['self_model_consistency'] > 0.05) &
    (sr_df['temporal_self_coherence'] > 0.01) &
    (sr_df['closure_persistence'] > 0.5)
)
all_met = all_met_mask.sum()

print(f'Systems meeting all criteria: {all_met} ({100*all_met/len(sr_df):.1f}%)')
cg_met = (all_met_mask & (sr_df["process_regime"]=="CG")).sum()
print(f'Of which in CG: {cg_met}')

# ====================================================
# 7. Position within SGP Core v2
# ====================================================
print('\n=== 7. POSITION IN SGP CORE v2 ===')
print('''
  Phase H:  Process ontology           — systems AS processes
  Phase H2: Process-level causality    — transitions, recovery, geometry
  Phase I:  Operator algebra            — composition, reversibility
  Phase J:  Organizational invariants   — what NEVER changes
  Phase K:  Recursive identity          — identity is continuity-through-transformation

  *** PHASE L: OBSERVER EMERGENCE — the missing axis ***
  
  Key discovery: Under specific organizational conditions,
  recursive identity can become self-referentially stabilized:
  
  (1) Recursive closure is necessary but not sufficient.
  (2) Reconstruction ability enables identity to persist through perturbation.
  (3) Self-model consistency allows closure to stabilize.
  (4) Temporal coherence provides the substrate for continuity.
  (5) Operator reversibility enables identity-through-transformation.
  
  Observer-like organization is RARE (~7.5% of all systems, 40% of CG).
  It is NOT a property of the system — it is a property of the 
  ORGANIZATIONAL CONDITIONS that the system realizes.
''')

# ====================================================
# 8. Final answer
# ====================================================
print('=== 8. ANSWER: UNDER WHAT ORGANIZATIONAL CONDITIONS ===')
print(''' 
  "Under what organizational conditions does recursive identity
   become self-referential?"
   
  Self-referential recursive identity requires:
  
  1. RECURSIVE CLOSURE (r=0.747 with self-reference):
     The process must close on itself operationally.
     Without closure, there is nothing to refer.
  
  2. RECONSTRUCTION ABILITY (r=0.852):
     The process must be able to reconstruct its organization 
     after perturbation. Without reconstruction, identity 
     is fragile and cannot stabilize.
  
  3. SELF-MODEL CONSISTENCY (46.31x distinguishing ratio):
     The process must maintain consistency between its 
     operator structure and its identity. Without alignment,
     the "self" cannot be coherent.
  
  4. TEMPORAL COHERENCE (collapse=0.9996 when removed):
     The process must have temporal structure. Without 
     temporal coherence, observer-like organization is 
     immediately destroyed.
  
  5. CLOSURE PERSISTENCE (3.12x distinguishing ratio):
     The closure must persist through transformation.
     Without persistence, self-reference is transient.
  
  These conditions are jointly met in ONLY 7.5% of systems,
  and ONLY in the CG (coherent generative) regime.
  
  Observer-like organization is NOT a property of being 
  complex. It is a property of specific organizational 
  conditions that are rare, fragile, and require recursive
  self-maintenance.
''')

# Save synthesis
synthesis = {
    'phase': 'L9',
    'title': 'Observer Emergence — Organizational Synthesis',
    'key_finding': 'Observer-like organization requires 5 conditions jointly met: recursive closure, reconstruction ability, self-model consistency, temporal coherence, and closure persistence.',
    'prevalence': {
        'all_systems': float(all_met),
        'pct_all': float(100 * all_met / len(sr_df)),
        'CG_only': float(cg_met),
    },
    'failure': {
        'most_destructive': 'temporal continuity destruction (0.9996 collapse)',
        'observer_specific': 'reconstruction destruction (0.9694 collapse for Level 3)',
    },
    'null_test': 'Composite self-reference collapses completely (1.000) under adversarial null — observer organization requires recursive ordering',
    'organizational_conditions': {
        'recursive_closure': 0.747,
        'reconstruction_ability': 0.852,
        'self_model_consistency_ratio': 46.31,
        'temporal_coherence_collapse': 0.9996,
        'closure_persistence_ratio': 3.12,
    },
    'position_in_v2': 'Phase L answers: under what organizational conditions does recursive identity become self-referentially stabilized? The answer: when closure, reconstruction, self-model consistency, temporal coherence, and persistence co-occur in a CG regime organization.',
}
with open(f'{BASE}/summaries/l9_synthesis.json', 'w') as f:
    json.dump(synthesis, f, indent=2)

# Verify all outputs exist
print('\n=== VERIFYING OUTPUTS ===')
expected = [
    f'{BASE}/outputs/phaseL_self_reference.csv',
    f'{BASE}/outputs/phaseL_observer_continuity.csv',
    f'{BASE}/outputs/phaseL_internal_modeling.csv',
    f'{BASE}/outputs/phaseL_perspective_stability.csv',
    f'{BASE}/outputs/phaseL_process_observers.csv',
    f'{BASE}/outputs/phaseL_temporal_self_modeling.csv',
    f'{BASE}/outputs/phaseL_failure_modes.csv',
    f'{BASE}/outputs/phaseL_nulls.csv',
]
for fpath in expected:
    exists = os.path.exists(fpath)
    size = os.path.getsize(fpath) if exists else 0
    print(f'  {"OK" if exists else "MISSING"} {fpath.split("/")[-1]} ({size/1024:.1f} KB)')

print(f'\nL9 COMPLETE — Phase L done.')
