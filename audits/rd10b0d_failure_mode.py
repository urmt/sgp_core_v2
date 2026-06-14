"""
RD-10B.0D: Failure-Mode Audit

QUESTION:
> Under what conditions does each criterion stop working?

DESIGN:
For each identity criterion:
1. When does it succeed?
2. When does it fail?
3. What distinctions become invisible under it?
4. What transformations leave it invariant?
5. What transformations break it?

KEY INSIGHT:
Throughout this program, the most reliable discoveries have not come
from asking "What is this?" They have come from asking:
"Under what conditions does this stop working?"

STANDING RULE:
> Whenever something looks fundamental, ask what makes it possible.
> Under what conditions does it stop working?
"""

import numpy as np
import json
from collections import defaultdict
import sys

sys.path.insert(0, '/home/student/sgp_core_v2/audits')
from rd10b0_representation_audit import run_world

# ============================================================
# FAILURE-MODE ANALYSIS
# ============================================================

def analyze_predictive_failure(trajectory):
    """
    When does predictive identity fail?
    
    Success: system has strong temporal autocorrelation.
    Failure: system is chaotic or has no temporal structure.
    """
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    if T < 30:
        return {'criterion': 'predictive', 'success': False, 'reason': 'insufficient_data'}
    
    # Autocorrelation at multiple lags
    lags = [1, 2, 5, 10, 20]
    autocorrs = []
    
    for lag in lags:
        if T > lag + 10:
            corr = np.corrcoef(mean[:-lag], mean[lag:])[0, 1]
            autocorrs.append(corr)
    
    if not autocorrs:
        return {'criterion': 'predictive', 'success': False, 'reason': 'no_autocorrelation'}
    
    # Success if autocorrelation is strong
    mean_autocorr = np.mean(np.abs(autocorrs))
    success = mean_autocorr > 0.3
    
    # What becomes invisible?
    invisible = []
    if mean_autocorr < 0.3:
        invisible.append('temporal_structure')
    if np.std(np.abs(autocorrs)) < 0.1:
        invisible.append('multi_scale_dynamics')
    
    return {
        'criterion': 'predictive',
        'success': success,
        'mean_autocorr': float(mean_autocorr),
        'invisible': invisible,
        'invariant': 'temporal_reversal',  # reversing time breaks prediction
        'breaks': 'chaos',
    }

def analyze_intervention_failure(trajectory):
    """
    When does intervention identity fail?
    
    Success: system responds differently to different interventions.
    Failure: system is invariant to interventions.
    """
    T = trajectory.shape[0]
    
    # Measure response heterogeneity
    # How much do different agents respond differently?
    
    agent_vars = trajectory.var(axis=0)  # variance per agent per dim
    agent_means = agent_vars.mean(axis=1)  # mean variance per agent
    
    if len(agent_means) < 2:
        return {'criterion': 'intervention', 'success': False, 'reason': 'insufficient_agents'}
    
    # Success if agents respond differently
    response_heterogeneity = np.std(agent_means) / (np.mean(agent_means) + 1e-10)
    success = response_heterogeneity > 0.1
    
    # What becomes invisible?
    invisible = []
    if response_heterogeneity < 0.1:
        invisible.append('agent_differences')
    
    return {
        'criterion': 'intervention',
        'success': success,
        'response_heterogeneity': float(response_heterogeneity),
        'invisible': invisible,
        'invariant': 'agent_permutation',  # permuting agents breaks intervention identity
        'breaks': 'uniform_response',
    }

def analyze_counterfactual_failure(trajectory):
    """
    When does counterfactual identity fail?
    
    Success: system has multiple possible futures from similar states.
    Failure: system is deterministic from similar states.
    """
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    if T < 30:
        return {'criterion': 'counterfactual', 'success': False, 'reason': 'insufficient_data'}
    
    # Measure divergence from similar states
    divergences = []
    for t in range(10, T - 10):
        # Find similar earlier states
        current = mean[t]
        earlier = mean[max(0, t-20):t]
        
        if len(earlier) > 0:
            distances = np.abs(earlier - current)
            similar_idx = np.where(distances < np.std(distances) + 1e-10)[0]
            
            if len(similar_idx) > 0:
                # Future from similar states
                futures = [mean[t+5] for t in similar_idx if t+5 < T]
                if futures:
                    divergence = np.std(futures)
                    divergences.append(divergence)
    
    if not divergences:
        return {'criterion': 'counterfactual', 'success': False, 'reason': 'no_divergence'}
    
    # Success if there is divergence (multiple futures)
    mean_divergence = np.mean(divergences)
    success = mean_divergence > 0.01
    
    # What becomes invisible?
    invisible = []
    if mean_divergence < 0.01:
        invisible.append('alternative_futures')
    
    return {
        'criterion': 'counterfactual',
        'success': success,
        'mean_divergence': float(mean_divergence),
        'invisible': invisible,
        'invariant': 'deterministic_systems',  # deterministic systems have no counterfactuals
        'breaks': 'stochasticity',
    }

def analyze_information_failure(trajectory):
    """
    When does information identity fail?
    
    Success: system has complex statistical structure.
    Failure: system is trivial (constant or simple).
    """
    flat = trajectory.flatten()
    
    # Measure entropy
    n_bins = 20
    hist, _ = np.histogram(flat, bins=n_bins, density=True)
    hist = hist + 1e-10
    hist = hist / hist.sum()
    entropy = -np.sum(hist * np.log(hist))
    
    # Maximum possible entropy
    max_entropy = np.log(n_bins)
    
    # Success if entropy is high (complex structure)
    relative_entropy = entropy / max_entropy
    success = relative_entropy > 0.5
    
    # What becomes invisible?
    invisible = []
    if relative_entropy < 0.5:
        invisible.append('complex_structure')
    
    return {
        'criterion': 'information',
        'success': success,
        'entropy': float(entropy),
        'relative_entropy': float(relative_entropy),
        'invisible': invisible,
        'invariant': 'deterministic_transformations',  # deterministic transforms preserve entropy
        'breaks': 'information_loss',
    }

def analyze_causal_failure(trajectory):
    """
    When does causal identity fail?
    
    Success: system has strong autocorrelation structure.
    Failure: system is random or has no causal dependencies.
    """
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    if T < 30:
        return {'criterion': 'causal', 'success': False, 'reason': 'insufficient_data'}
    
    # Measure causal structure via autocorrelation decay
    lags = [1, 2, 5, 10]
    autocorrs = []
    
    for lag in lags:
        if T > lag + 10:
            corr = np.corrcoef(mean[:-lag], mean[lag:])[0, 1]
            autocorrs.append(corr)
    
    if len(autocorrs) < 2:
        return {'criterion': 'causal', 'success': False, 'reason': 'insufficient_autocorrelation'}
    
    # Success if autocorrelation decays slowly (strong causal structure)
    autocorrs = np.array(autocorrs)
    decay_rate = -np.log(autocorrs[-1] / (autocorrs[0] + 1e-10) + 1e-10) / (lags[-1] - lags[0])
    
    success = decay_rate < 0.1  # slow decay = strong causal structure
    
    # What becomes invisible?
    invisible = []
    if decay_rate > 0.1:
        invisible.append('long_range_dependencies')
    
    return {
        'criterion': 'causal',
        'success': success,
        'decay_rate': float(decay_rate),
        'invisible': invisible,
        'invariant': 'time_reversal',  # time reversal breaks causal structure
        'breaks': 'randomness',
    }

# ============================================================
# MAIN EXPERIMENT
# ============================================================

def run_failure_mode_audit(n_worlds=10, n_steps=200):
    """
    Run failure-mode audit.
    
    For each criterion: under what conditions does it stop working?
    """
    print("RD-10B.0D: Failure-Mode Audit")
    print("="*60)
    
    criteria = {
        'predictive': analyze_predictive_failure,
        'intervention': analyze_intervention_failure,
        'counterfactual': analyze_counterfactual_failure,
        'information': analyze_information_failure,
        'causal': analyze_causal_failure,
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
        
        # Quick summary
        successes = sum(1 for name in criteria if all_results[name][-1]['success'])
        print(f" ({successes}/{len(criteria)} succeed)")
    
    # 2. Summary
    print("\n" + "="*60)
    print("FAILURE-MODE SUMMARY")
    print("="*60)
    
    for name in criteria:
        results = all_results[name]
        
        successes = sum(1 for r in results if r['success'])
        failures = len(results) - successes
        
        # Collect invisible distinctions
        all_invisible = []
        for r in results:
            all_invisible.extend(r.get('invisible', []))
        
        invisible_counts = defaultdict(int)
        for inv in all_invisible:
            invisible_counts[inv] += 1
        
        print(f"\n{name}:")
        print(f"   Successes: {successes}/{len(results)}")
        print(f"   Failures: {failures}/{len(results)}")
        print(f"   Invisible distinctions: {dict(invisible_counts)}")
    
    # 3. Cross-criterion analysis
    print("\n" + "="*60)
    print("CROSS-CRITERION FAILURE PATTERNS")
    print("="*60)
    
    # Which worlds fail for multiple criteria?
    world_failures = defaultdict(list)
    
    for name, results in all_results.items():
        for world_id, r in enumerate(results):
            if not r['success']:
                world_failures[world_id].append(name)
    
    print("\nWorlds that fail multiple criteria:")
    for world_id, failed_criteria in sorted(world_failures.items()):
        if len(failed_criteria) > 1:
            print(f"   World {world_id}: {failed_criteria}")
    
    # 4. Transformation analysis
    print("\n" + "="*60)
    print("INVARIANT TRANSFORMATIONS")
    print("="*60)
    
    for name in criteria:
        results = all_results[name]
        invariants = [r.get('invariant', 'none') for r in results]
        breaks = [r.get('breaks', 'none') for r in results]
        
        print(f"\n{name}:")
        print(f"   Invariant under: {invariants[0]}")
        print(f"   Broken by: {breaks[0]}")
    
    # 5. Interpretation
    print("\n" + "="*60)
    print("INTERPRETATION")
    print("="*60)
    
    print("\nEach criterion has a domain of success and a domain of failure:")
    print()
    for name in criteria:
        results = all_results[name]
        successes = sum(1 for r in results if r['success'])
        print(f"   {name}: succeeds {successes}/{len(results)} times")
    print()
    print("The failures are informative:")
    print("   - When predictive fails, temporal structure is absent.")
    print("   - When intervention fails, agents respond uniformly.")
    print("   - When counterfactual fails, the system is deterministic.")
    print("   - When information fails, the system is trivial.")
    print("   - When causal fails, dependencies are random.")
    print()
    print("These failure modes are not bugs.")
    print("They are the conditions under which each criterion becomes uninformative.")
    print()
    print("The question is not: 'Which criterion is correct?'")
    print("The question is: 'Under what conditions is each criterion informative?'")
    
    return all_results

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    n_worlds = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    results = run_failure_mode_audit(n_worlds=n_worlds)
    
    # Save results
    serializable = {}
    for name, world_results in results.items():
        serializable[name] = world_results
    
    with open('/home/student/sgp_core_v2/audits/rd10b0d_results.json', 'w') as f:
        json.dump(serializable, f, indent=2)
    
    print("\nSaved to audits/rd10b0d_results.json")
