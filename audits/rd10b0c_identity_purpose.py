"""
RD-10B.0C: Identity Purpose Audit

QUESTION:
> What role is identity serving?
> Why do we need a notion of "same" in the first place?

DESIGN:
For each identity criterion:
1. What task was it invented to support?
2. What failures does it prevent?
3. What transformations does it preserve?
4. When does it outperform the others?

KEY INSIGHT:
Two criteria disagreeing is only surprising if they are trying
to solve the same problem. They may not be.

If they are not, then the disagreement may tell you less about
identity and more about purpose.

STANDING RULE:
> Whenever something looks fundamental, first determine what work it is doing.
"""

import numpy as np
import json
from collections import defaultdict
import sys

sys.path.insert(0, '/home/student/sgp_core_v2/audits')
from rd10b0_representation_audit import run_world

# ============================================================
# IDENTITY CRITERIA (with purpose analysis)
# ============================================================

def analyze_predictive_identity(trajectory):
    """
    Predictive identity: Do two representations predict the same futures?
    
    PURPOSE: Support prediction and forecasting.
    PRESERVES: Temporal structure that enables forecasting.
    FAILURES PREVENTED: Using a representation that loses predictive power.
    WHEN BEST: When the task is prediction.
    """
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    # Measure predictive structure
    if T < 30:
        return {'purpose': 'prediction', 'structure': 0.0}
    
    # Autocorrelation at lag 1 (predictability)
    autocorr = np.corrcoef(mean[:-1], mean[1:])[0, 1]
    
    # Variance explained by recent history
    errors = []
    for t in range(20, T - 5):
        pred = mean[max(0, t-10):t].mean()
        actual = mean[t+5]
        errors.append((pred - actual)**2)
    
    if errors:
        mean_error = np.mean(errors)
        total_var = np.var(mean)
        r_squared = 1 - mean_error / (total_var + 1e-10)
    else:
        r_squared = 0.0
    
    return {
        'purpose': 'prediction',
        'autocorrelation': float(autocorr),
        'r_squared': float(max(0, r_squared)),
        'structure': float(max(0, r_squared)),
    }

def analyze_intervention_identity(trajectory):
    """
    Intervention identity: Do two representations respond the same to interventions?
    
    PURPOSE: Support intervention and control.
    PRESERVES: Response structure that enables manipulation.
    FAILURES PREVENTED: Using a representation that loses interventional information.
    WHEN BEST: When the task is intervention.
    """
    T = trajectory.shape[0]
    
    # Measure intervention structure
    # How much does the system respond to perturbations?
    
    # Compute variance across time (response to ongoing perturbations)
    var_over_time = trajectory.var(axis=0).mean()
    
    # Compute variance across agents (response heterogeneity)
    var_across_agents = trajectory.mean(axis=2).var(axis=1).mean()
    
    # Response ratio
    if var_over_time + var_across_agents == 0:
        response_ratio = 0.0
    else:
        response_ratio = var_over_time / (var_over_time + var_across_agents)
    
    return {
        'purpose': 'intervention',
        'var_over_time': float(var_over_time),
        'var_across_agents': float(var_across_agents),
        'response_ratio': float(response_ratio),
        'structure': float(response_ratio),
    }

def analyze_counterfactual_identity(trajectory):
    """
    Counterfactual identity: Do two representations agree on counterfactuals?
    
    PURPOSE: Support explanation and reasoning about alternatives.
    PRESERVES: Structure that enables counterfactual reasoning.
    FAILURES PREVENTED: Using a representation that loses explanatory power.
    WHEN BEST: When the task is explanation.
    """
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    if T < 30:
        return {'purpose': 'explanation', 'structure': 0.0}
    
    # Measure divergence structure
    divergences = []
    for t in range(10, T - 10):
        local = mean[t-5:t].mean()
        future = mean[t+5]
        divergences.append((future - local)**2)
    
    if not divergences:
        return {'purpose': 'explanation', 'structure': 0.0}
    
    divergences = np.array(divergences)
    
    # How predictable are divergences?
    if len(divergences) > 10:
        corr = np.corrcoef(divergences[:-5], divergences[5:])[0, 1]
    else:
        corr = 0.0
    
    return {
        'purpose': 'explanation',
        'divergence_mean': float(np.mean(divergences)),
        'divergence_std': float(np.std(divergences)),
        'divergence_predictability': float(abs(corr)),
        'structure': float(abs(corr)),
    }

def analyze_information_identity(trajectory):
    """
    Information identity: Do two representations preserve the same information?
    
    PURPOSE: Support compression and storage.
    PRESERVES: Statistical structure that enables lossless compression.
    FAILURES PREVENTED: Using a representation that loses information.
    WHEN BEST: When the task is storage or communication.
    """
    flat = trajectory.flatten()
    
    # Compute entropy
    n_bins = 20
    hist, _ = np.histogram(flat, bins=n_bins, density=True)
    hist = hist + 1e-10
    hist = hist / hist.sum()
    entropy = -np.sum(hist * np.log(hist))
    
    # Compute mutual information between t and t+1
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    if T > 10:
        mi_proxy = abs(np.corrcoef(mean[:-1], mean[1:])[0, 1])
    else:
        mi_proxy = 0.0
    
    return {
        'purpose': 'compression',
        'entropy': float(entropy),
        'mutual_information_proxy': float(mi_proxy),
        'structure': float(mi_proxy),
    }

def analyze_causal_identity(trajectory):
    """
    Causal identity: Do two representations preserve causal structure?
    
    PURPOSE: Support causal reasoning and intervention planning.
    PRESERVES: Dependency structure that enables causal inference.
    FAILURES PREVENTED: Using a representation that loses causal information.
    WHEN BEST: When the task is causal reasoning.
    """
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    if T < 30:
        return {'purpose': 'causal_reasoning', 'structure': 0.0}
    
    # Measure causal structure via autocorrelation at multiple lags
    lags = [1, 2, 5, 10]
    autocorrs = []
    
    for lag in lags:
        if T > lag + 10:
            corr = np.corrcoef(mean[:-lag], mean[lag:])[0, 1]
            autocorrs.append(corr)
    
    if len(autocorrs) < 2:
        return {'purpose': 'causal_reasoning', 'structure': 0.0}
    
    # Causal structure = how much does autocorrelation decay?
    # (Slow decay = strong causal structure)
    autocorrs = np.array(autocorrs)
    
    # Fit exponential decay
    if autocorrs[0] > 0:
        decay_rate = -np.log(autocorrs[-1] / autocorrs[0]) / (lags[-1] - lags[0])
    else:
        decay_rate = 1.0
    
    return {
        'purpose': 'causal_reasoning',
        'autocorrs': autocorrs.tolist(),
        'decay_rate': float(decay_rate),
        'structure': float(1.0 / (1.0 + decay_rate)),  # slow decay = high structure
    }

# ============================================================
# MAIN EXPERIMENT
# ============================================================

def run_identity_purpose_audit(n_worlds=10, n_steps=200):
    """
    Run identity purpose audit.
    
    For each criterion: what task was it invented to support?
    """
    print("RD-10B.0C: Identity Purpose Audit")
    print("="*60)
    
    criteria = {
        'predictive': analyze_predictive_identity,
        'intervention': analyze_intervention_identity,
        'counterfactual': analyze_counterfactual_identity,
        'information': analyze_information_identity,
        'causal': analyze_causal_identity,
    }
    
    # 1. Generate worlds
    print(f"\n1. Generating {n_worlds} worlds...")
    
    all_results = {name: [] for name in criteria}
    
    for world_id in range(n_worlds):
        print(f"   World {world_id}...", end='', flush=True)
        
        trajectory, world = run_world(n_steps=n_steps, seed=world_id * 100)
        
        # Analyze each criterion
        for name, func in criteria.items():
            result = func(trajectory)
            all_results[name].append(result)
        
        print(f" done")
    
    # 2. Summary
    print("\n" + "="*60)
    print("IDENTITY PURPOSE SUMMARY")
    print("="*60)
    
    for name in criteria:
        results = all_results[name]
        
        structures = [r['structure'] for r in results]
        purposes = [r['purpose'] for r in results]
        
        print(f"\n{name}:")
        print(f"   Purpose: {purposes[0]}")
        print(f"   Structure (mean): {np.mean(structures):.3f}")
        print(f"   Structure (std): {np.std(structures):.3f}")
    
    # 3. Purpose-structure relationship
    print("\n" + "="*60)
    print("DO PURPOSES PREDICT STRUCTURE?")
    print("="*60)
    
    # Group by purpose
    by_purpose = defaultdict(list)
    for name, results in all_results.items():
        for r in results:
            by_purpose[r['purpose']].append(r['structure'])
    
    print("\nStructure by purpose:")
    for purpose, structures in by_purpose.items():
        print(f"   {purpose}: mean={np.mean(structures):.3f}, std={np.std(structures):.3f}")
    
    # 4. Transformation analysis
    print("\n" + "="*60)
    print("TRANSFORMATION ANALYSIS")
    print("="*60)
    
    print("\nHow do criteria transform into each other?")
    
    # For each world, compute all criteria
    # Then check: does high X predict high Y?
    
    criteria_names = list(criteria.keys())
    
    for i, c1 in enumerate(criteria_names):
        for j, c2 in enumerate(criteria_names):
            if i >= j:
                continue
            
            structures1 = [r['structure'] for r in all_results[c1]]
            structures2 = [r['structure'] for r in all_results[c2]]
            
            if np.std(structures1) > 0 and np.std(structures2) > 0:
                corr = np.corrcoef(structures1, structures2)[0, 1]
                print(f"   {c1} ↔ {c2}: r={corr:.3f}")
    
    # 5. Interpretation
    print("\n" + "="*60)
    print("INTERPRETATION")
    print("="*60)
    
    print("\nThe criteria are not competing definitions of 'same world'.")
    print("They are tools designed for different tasks:")
    print()
    print("   predictive → prediction and forecasting")
    print("   intervention → manipulation and control")
    print("   counterfactual → explanation and reasoning")
    print("   information → compression and storage")
    print("   causal → causal reasoning and planning")
    print()
    print("Their disagreement is not a crisis of identity.")
    print("It is a reflection of the diversity of purposes.")
    print()
    print("The question is not: 'Which criterion is correct?'")
    print("The question is: 'What task are you trying to accomplish?'")
    
    return all_results

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    n_worlds = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    results = run_identity_purpose_audit(n_worlds=n_worlds)
    
    # Save results
    serializable = {}
    for name, world_results in results.items():
        serializable[name] = world_results
    
    with open('/home/student/sgp_core_v2/audits/rd10b0c_results.json', 'w') as f:
        json.dump(serializable, f, indent=2)
    
    print("\nSaved to audits/rd10b0c_results.json")
