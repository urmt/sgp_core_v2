"""
RD-10B.0E: Stress-Test Audit

QUESTION:
> Under what conditions is a criterion informative, uninformative,
> misleading, or trivial?

DESIGN:
For every criterion:
1. Construct worlds designed to break it.
2. Construct worlds where it becomes trivial.
3. Construct worlds where it disagrees maximally with the others.
4. Measure the region in world-space where it is informative.

KEY INSIGHT:
The mismatch between expectation and behavior is the discovery.
Sometimes that mismatch is failure, invariance, degeneracy, or triviality.
The common element is not failure — it is surprise.

STANDING RULE:
> Whenever a pattern appears, ask whether it belongs to
> the world, the representation, the detector, the question,
> or the observer, or the evaluation protocol.
"""

import numpy as np
import json
from collections import defaultdict
import sys

sys.path.insert(0, '/home/student/sgp_core_v2/audits')
from rd10b0_representation_audit import run_world

# ============================================================
# WORLD GENERATORS (designed to stress-test criteria)
# ============================================================

def generate_chaotic_world(seed=42):
    """World designed to break predictive identity."""
    rng = np.random.default_rng(seed)
    
    N, D = 10, 3
    states = rng.standard_normal((N, D))
    
    # High coupling, high nonlinearity → chaos
    weight_matrix = rng.uniform(-2.0, 2.0, (N, N))
    np.fill_diagonal(weight_matrix, 0)
    
    return {
        'N': N, 'D': D,
        'states': states,
        'weight_matrix': weight_matrix,
        'boundary': rng.random(N) < 0.3,
        'decay': 0.01,
        'coupling': 2.0,
        'noise': 0.1,
        'forcing_strength': 1.0,
        'nonlinearity': 3.0,
    }

def generate_uniform_world(seed=42):
    """World designed to break intervention identity."""
    rng = np.random.default_rng(seed)
    
    N, D = 10, 3
    states = rng.standard_normal((N, D))
    
    # Uniform coupling → agents respond identically
    weight_matrix = np.ones((N, N)) * 0.5
    np.fill_diagonal(weight_matrix, 0)
    
    return {
        'N': N, 'D': D,
        'states': states,
        'weight_matrix': weight_matrix,
        'boundary': np.zeros(N, dtype=bool),  # no boundary
        'decay': 0.1,
        'coupling': 0.5,
        'noise': 0.01,
        'forcing_strength': 0.0,
        'nonlinearity': 0.0,
    }

def generate_deterministic_world(seed=42):
    """World designed to break counterfactual identity."""
    rng = np.random.default_rng(seed)
    
    N, D = 10, 3
    states = rng.standard_normal((N, D))
    
    # Low noise, low nonlinearity → deterministic
    weight_matrix = rng.uniform(-0.1, 0.1, (N, N))
    np.fill_diagonal(weight_matrix, 0)
    
    return {
        'N': N, 'D': D,
        'states': states,
        'weight_matrix': weight_matrix,
        'boundary': rng.random(N) < 0.3,
        'decay': 0.1,
        'coupling': 0.1,
        'noise': 0.001,
        'forcing_strength': 0.0,
        'nonlinearity': 0.1,
    }

def generate_trivial_world(seed=42):
    """World designed to break information identity."""
    rng = np.random.default_rng(seed)
    
    N, D = 10, 3
    # All agents same state → trivial
    states = np.ones((N, D)) * 0.5
    
    weight_matrix = rng.uniform(-0.1, 0.1, (N, N))
    np.fill_diagonal(weight_matrix, 0)
    
    return {
        'N': N, 'D': D,
        'states': states,
        'weight_matrix': weight_matrix,
        'boundary': np.zeros(N, dtype=bool),
        'decay': 0.0,
        'coupling': 0.0,
        'noise': 0.0,
        'forcing_strength': 0.0,
        'nonlinearity': 0.0,
    }

def generate_random_world(seed=42):
    """World designed to break causal identity."""
    rng = np.random.default_rng(seed)
    
    N, D = 10, 3
    states = rng.standard_normal((N, D))
    
    # Random, uncorrelated dynamics
    weight_matrix = rng.uniform(-0.01, 0.01, (N, N))
    np.fill_diagonal(weight_matrix, 0)
    
    return {
        'N': N, 'D': D,
        'states': states,
        'weight_matrix': weight_matrix,
        'boundary': rng.random(N) < 0.3,
        'decay': 0.5,
        'coupling': 0.01,
        'noise': 0.2,
        'forcing_strength': 0.0,
        'nonlinearity': 0.0,
    }

# ============================================================
# CRITERIA (same as before)
# ============================================================

def predictive_criterion(trajectory):
    """Predictive identity criterion."""
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    if T < 30:
        return {'score': 0.0, 'informative': False}
    
    # Autocorrelation at lag 1
    autocorr = np.corrcoef(mean[:-1], mean[1:])[0, 1]
    
    # Prediction error
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
    
    # Informative if r_squared > 0.1
    informative = r_squared > 0.1
    
    return {
        'score': float(max(0, r_squared)),
        'informative': informative,
        'autocorrelation': float(autocorr),
    }

def intervention_criterion(trajectory):
    """Intervention identity criterion."""
    T = trajectory.shape[0]
    
    # Response heterogeneity
    agent_vars = trajectory.var(axis=0)
    agent_means = agent_vars.mean(axis=1)
    
    if len(agent_means) < 2:
        return {'score': 0.0, 'informative': False}
    
    response_heterogeneity = np.std(agent_means) / (np.mean(agent_means) + 1e-10)
    
    # Informative if heterogeneity > 0.1
    informative = response_heterogeneity > 0.1
    
    return {
        'score': float(response_heterogeneity),
        'informative': informative,
    }

def counterfactual_criterion(trajectory):
    """Counterfactual identity criterion."""
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    if T < 30:
        return {'score': 0.0, 'informative': False}
    
    # Divergence from similar states
    divergences = []
    for t in range(10, T - 10):
        current = mean[t]
        earlier = mean[max(0, t-20):t]
        
        if len(earlier) > 0:
            distances = np.abs(earlier - current)
            similar_idx = np.where(distances < np.std(distances) + 1e-10)[0]
            
            if len(similar_idx) > 0:
                futures = [mean[t+5] for t in similar_idx if t+5 < T]
                if futures:
                    divergence = np.std(futures)
                    divergences.append(divergence)
    
    if not divergences:
        return {'score': 0.0, 'informative': False}
    
    mean_divergence = np.mean(divergences)
    
    # Informative if divergence > 0.01
    informative = mean_divergence > 0.01
    
    return {
        'score': float(mean_divergence),
        'informative': informative,
    }

def information_criterion(trajectory):
    """Information identity criterion."""
    flat = trajectory.flatten()
    
    n_bins = 20
    hist, _ = np.histogram(flat, bins=n_bins, density=True)
    hist = hist + 1e-10
    hist = hist / hist.sum()
    entropy = -np.sum(hist * np.log(hist))
    
    max_entropy = np.log(n_bins)
    relative_entropy = entropy / max_entropy
    
    # Informative if relative entropy > 0.5
    informative = relative_entropy > 0.5
    
    return {
        'score': float(relative_entropy),
        'informative': informative,
        'entropy': float(entropy),
    }

def causal_criterion(trajectory):
    """Causal identity criterion."""
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    if T < 30:
        return {'score': 0.0, 'informative': False}
    
    # Autocorrelation decay
    lags = [1, 2, 5, 10]
    autocorrs = []
    
    for lag in lags:
        if T > lag + 10:
            corr = np.corrcoef(mean[:-lag], mean[lag:])[0, 1]
            autocorrs.append(corr)
    
    if len(autocorrs) < 2:
        return {'score': 0.0, 'informative': False}
    
    autocorrs = np.array(autocorrs)
    decay_rate = -np.log(autocorrs[-1] / (autocorrs[0] + 1e-10) + 1e-10) / (lags[-1] - lags[0])
    
    # Informative if decay_rate < 0.1
    informative = decay_rate < 0.1
    
    return {
        'score': float(1.0 / (1.0 + decay_rate)),
        'informative': informative,
        'decay_rate': float(decay_rate),
    }

# ============================================================
# MAIN EXPERIMENT
# ============================================================

def run_stress_test(n_steps=200):
    """
    Run stress-test audit.
    
    For each criterion: construct worlds designed to break it,
    and measure when it is informative vs. trivial.
    """
    print("RD-10B.0E: Stress-Test Audit")
    print("="*60)
    
    # World generators
    world_generators = {
        'chaotic': generate_chaotic_world,
        'uniform': generate_uniform_world,
        'deterministic': generate_deterministic_world,
        'trivial': generate_trivial_world,
        'random': generate_random_world,
        'normal': lambda seed: run_world(n_steps=n_steps, seed=seed)[1],
    }
    
    # Criteria
    criteria = {
        'predictive': predictive_criterion,
        'intervention': intervention_criterion,
        'counterfactual': counterfactual_criterion,
        'information': information_criterion,
        'causal': causal_criterion,
    }
    
    # 1. Generate stress worlds
    print("\n1. Generating stress worlds...")
    
    all_results = {}
    
    for world_name, world_gen in world_generators.items():
        print(f"\n   {world_name}:")
        
        world = world_gen(seed=42)
        
        # Run world
        rng = np.random.default_rng(42)
        trajectory = []
        for t in range(n_steps):
            # Simple dynamics
            N, D = world['states'].shape
            new_states = np.zeros_like(world['states'])
            
            for i in range(N):
                influence = np.zeros(D)
                for j in range(N):
                    if j != i:
                        diff = world['states'][j] - world['states'][i]
                        weight = world['weight_matrix'][j, i]
                        influence += weight * diff
                
                if world['nonlinearity'] > 0:
                    influence = np.tanh(world['nonlinearity'] * influence)
                
                decay_force = -world['decay'] * world['states'][i]
                forcing = world['forcing_strength'] * np.sin(2 * np.pi * t / 50 + i)
                
                new_states[i] = world['states'][i] + decay_force + influence + forcing
                
                if world['boundary'][i]:
                    new_states[i] *= 0.95
            
            new_states += world['noise'] * rng.standard_normal((N, D))
            world['states'] = new_states
            trajectory.append(world['states'].copy())
        
        trajectory = np.array(trajectory)
        
        # Apply each criterion
        world_results = {}
        for criterion_name, criterion_func in criteria.items():
            result = criterion_func(trajectory)
            world_results[criterion_name] = result
            
            status = "INFORMATIVE" if result['informative'] else "TRIVIAL"
            print(f"      {criterion_name}: {status} (score={result['score']:.3f})")
        
        all_results[world_name] = world_results
    
    # 2. Analysis
    print("\n" + "="*60)
    print("STRESS-TEST ANALYSIS")
    print("="*60)
    
    # For each criterion, count informative vs trivial across worlds
    print("\nCriterion informativeness across stress worlds:")
    
    for criterion_name in criteria:
        informative_count = 0
        total_count = 0
        
        for world_name, world_results in all_results.items():
            total_count += 1
            if world_results[criterion_name]['informative']:
                informative_count += 1
        
        informativeness = informative_count / total_count
        print(f"   {criterion_name}: {informative_count}/{total_count} informative ({informativeness:.0%})")
    
    # 3. Disagreement analysis
    print("\n" + "="*60)
    print("DISAGREEMENT ANALYSIS")
    print("="*60)
    
    print("\nWorlds where criteria disagree:")
    
    for world_name, world_results in all_results.items():
        informative_criteria = [name for name, r in world_results.items() if r['informative']]
        trivial_criteria = [name for name, r in world_results.items() if not r['informative']]
        
        if informative_criteria and trivial_criteria:
            print(f"\n   {world_name}:")
            print(f"      Informative: {informative_criteria}")
            print(f"      Trivial: {trivial_criteria}")
    
    # 4. Interpretation
    print("\n" + "="*60)
    print("INTERPRETATION")
    print("="*60)
    
    print("\nThe stress test reveals:")
    print()
    for criterion_name in criteria:
        informative_count = sum(1 for wr in all_results.values() if wr[criterion_name]['informative'])
        total = len(all_results)
        print(f"   {criterion_name}: informative in {informative_count}/{total} worlds")
    print()
    print("A criterion that is always informative may be measuring something generic.")
    print("A criterion that is never informative may be broken.")
    print("A criterion that is sometimes informative has a defined domain of applicability.")
    print()
    print("The question is not: 'Which criterion is correct?'")
    print("The question is: 'Under what conditions is each criterion informative?'")
    
    return all_results

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    results = run_stress_test()
    
    # Save results (with proper serialization)
    serializable = {}
    for world_name, world_results in results.items():
        serializable[world_name] = {}
        for criterion_name, criterion_result in world_results.items():
            serializable[world_name][criterion_name] = {
                'score': float(criterion_result['score']),
                'informative': bool(criterion_result['informative']),
            }
    
    with open('/home/student/sgp_core_v2/audits/rd10b0e_results.json', 'w') as f:
        json.dump(serializable, f, indent=2)
    
    print("\nSaved to audits/rd10b0e_results.json")
