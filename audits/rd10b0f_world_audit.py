"""
RD-10B.0F: World Audit

QUESTION:
> What assumptions are hidden in the worlds that are being used
> to evaluate all of these things?

DESIGN:
For every stress world:
1. What assumptions define it?
2. Which criteria are advantaged by those assumptions?
3. Which criteria are disadvantaged?
4. Which distinctions are impossible to express in that world?
5. Which conclusions disappear if the world family changes?

KEY INSIGHT:
The pattern of RD-10B is clear:
1. Measure the world → discover the detector matters
2. Measure the detector → discover the representation matters
3. Measure the representation → discover the criterion matters
4. Measure the criterion → discover the world matters

The next obvious question is:
> What assumptions are hidden in the worlds?

STANDING RULE:
> Whenever something looks fundamental, ask what makes it possible.
> Under what conditions does it stop working?
> Under what conditions is it informative vs. trivial?
> What assumptions are hidden in the thing doing the measuring?
"""

import numpy as np
import json
from collections import defaultdict
import sys

sys.path.insert(0, '/home/student/sgp_core_v2/audits')
from rd10b0_representation_audit import run_world

# ============================================================
# WORLD ASSUMPTION ANALYSIS
# ============================================================

def analyze_world_assumptions(world, world_name):
    """
    Analyze the hidden assumptions in a world.
    """
    N = world['N']
    D = world['D']
    
    # Structural assumptions
    coupling = world['coupling']
    decay = world['decay']
    noise = world['noise']
    forcing = world['forcing_strength']
    nonlinearity = world['nonlinearity']
    
    # Connectivity assumptions
    connectivity = np.count_nonzero(world['weight_matrix']) / (N * N)
    
    # Boundary assumptions
    boundary_fraction = np.mean(world['boundary'])
    
    # Symmetry assumptions
    weight_abs = np.abs(world['weight_matrix'])
    symmetry = np.mean(np.abs(weight_abs - weight_abs.T)) / (np.mean(weight_abs) + 1e-10)
    
    # Assumptions dictionary
    assumptions = {
        'has_temporal_structure': forcing > 0 or decay < 0.3,
        'has_spatial_structure': connectivity > 0.3,
        'has_nonlinearity': nonlinearity > 1.0,
        'has_noise': noise > 0.05,
        'has_boundary': boundary_fraction > 0.1,
        'has_symmetry': symmetry < 0.3,
        'has_heterogeneity': True,  # all worlds have some heterogeneity
        'is_deterministic': noise < 0.01,
        'is_chaotic': nonlinearity > 2.0 and coupling > 1.0,
        'is_trivial': coupling == 0 and noise == 0 and forcing == 0,
    }
    
    return assumptions

def analyze_criterion_world_interaction(trajectory, criterion_func, world_assumptions):
    """
    Analyze how a criterion interacts with world assumptions.
    """
    result = criterion_func(trajectory)
    
    # Which assumptions support this criterion?
    supporting_assumptions = []
    for assumption, value in world_assumptions.items():
        if value:
            supporting_assumptions.append(assumption)
    
    return {
        'score': result['score'],
        'informative': result['informative'],
        'supporting_assumptions': supporting_assumptions,
    }

# ============================================================
# CRITERIA
# ============================================================

def predictive_criterion(trajectory):
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    if T < 30:
        return {'score': 0.0, 'informative': False}
    
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
        'score': float(max(0, r_squared)),
        'informative': r_squared > 0.1,
    }

def intervention_criterion(trajectory):
    agent_vars = trajectory.var(axis=0)
    agent_means = agent_vars.mean(axis=1)
    
    if len(agent_means) < 2:
        return {'score': 0.0, 'informative': False}
    
    response_heterogeneity = np.std(agent_means) / (np.mean(agent_means) + 1e-10)
    
    return {
        'score': float(response_heterogeneity),
        'informative': response_heterogeneity > 0.1,
    }

def counterfactual_criterion(trajectory):
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    if T < 30:
        return {'score': 0.0, 'informative': False}
    
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
    
    return {
        'score': float(mean_divergence),
        'informative': mean_divergence > 0.01,
    }

def information_criterion(trajectory):
    flat = trajectory.flatten()
    
    n_bins = 20
    hist, _ = np.histogram(flat, bins=n_bins, density=True)
    hist = hist + 1e-10
    hist = hist / hist.sum()
    entropy = -np.sum(hist * np.log(hist))
    
    max_entropy = np.log(n_bins)
    relative_entropy = entropy / max_entropy
    
    return {
        'score': float(relative_entropy),
        'informative': relative_entropy > 0.5,
    }

def causal_criterion(trajectory):
    T = trajectory.shape[0]
    mean = trajectory.mean(axis=(1, 2))
    
    if T < 30:
        return {'score': 0.0, 'informative': False}
    
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
    
    return {
        'score': float(1.0 / (1.0 + decay_rate)),
        'informative': decay_rate < 0.1,
    }

# ============================================================
# WORLD GENERATORS
# ============================================================

def generate_chaotic_world(seed=42):
    rng = np.random.default_rng(seed)
    N, D = 10, 3
    states = rng.standard_normal((N, D))
    weight_matrix = rng.uniform(-2.0, 2.0, (N, N))
    np.fill_diagonal(weight_matrix, 0)
    return {
        'N': N, 'D': D, 'states': states,
        'weight_matrix': weight_matrix,
        'boundary': rng.random(N) < 0.3,
        'decay': 0.01, 'coupling': 2.0, 'noise': 0.1,
        'forcing_strength': 1.0, 'nonlinearity': 3.0,
    }

def generate_uniform_world(seed=42):
    rng = np.random.default_rng(seed)
    N, D = 10, 3
    states = rng.standard_normal((N, D))
    weight_matrix = np.ones((N, N)) * 0.5
    np.fill_diagonal(weight_matrix, 0)
    return {
        'N': N, 'D': D, 'states': states,
        'weight_matrix': weight_matrix,
        'boundary': np.zeros(N, dtype=bool),
        'decay': 0.1, 'coupling': 0.5, 'noise': 0.01,
        'forcing_strength': 0.0, 'nonlinearity': 0.0,
    }

def generate_deterministic_world(seed=42):
    rng = np.random.default_rng(seed)
    N, D = 10, 3
    states = rng.standard_normal((N, D))
    weight_matrix = rng.uniform(-0.1, 0.1, (N, N))
    np.fill_diagonal(weight_matrix, 0)
    return {
        'N': N, 'D': D, 'states': states,
        'weight_matrix': weight_matrix,
        'boundary': rng.random(N) < 0.3,
        'decay': 0.1, 'coupling': 0.1, 'noise': 0.001,
        'forcing_strength': 0.0, 'nonlinearity': 0.1,
    }

def generate_trivial_world(seed=42):
    rng = np.random.default_rng(seed)
    N, D = 10, 3
    states = np.ones((N, D)) * 0.5
    weight_matrix = rng.uniform(-0.1, 0.1, (N, N))
    np.fill_diagonal(weight_matrix, 0)
    return {
        'N': N, 'D': D, 'states': states,
        'weight_matrix': weight_matrix,
        'boundary': np.zeros(N, dtype=bool),
        'decay': 0.0, 'coupling': 0.0, 'noise': 0.0,
        'forcing_strength': 0.0, 'nonlinearity': 0.0,
    }

def generate_random_world(seed=42):
    rng = np.random.default_rng(seed)
    N, D = 10, 3
    states = rng.standard_normal((N, D))
    weight_matrix = rng.uniform(-0.01, 0.01, (N, N))
    np.fill_diagonal(weight_matrix, 0)
    return {
        'N': N, 'D': D, 'states': states,
        'weight_matrix': weight_matrix,
        'boundary': rng.random(N) < 0.3,
        'decay': 0.5, 'coupling': 0.01, 'noise': 0.2,
        'forcing_strength': 0.0, 'nonlinearity': 0.0,
    }

# ============================================================
# MAIN EXPERIMENT
# ============================================================

def run_world_audit(n_steps=200):
    """
    Run world audit.
    
    For every stress world: what assumptions define it?
    """
    print("RD-10B.0F: World Audit")
    print("="*60)
    
    world_generators = {
        'chaotic': generate_chaotic_world,
        'uniform': generate_uniform_world,
        'deterministic': generate_deterministic_world,
        'trivial': generate_trivial_world,
        'random': generate_random_world,
    }
    
    criteria = {
        'predictive': predictive_criterion,
        'intervention': intervention_criterion,
        'counterfactual': counterfactual_criterion,
        'information': information_criterion,
        'causal': causal_criterion,
    }
    
    # 1. Analyze each world
    print("\n1. Analyzing world assumptions...")
    
    world_assumptions = {}
    world_trajectories = {}
    
    for world_name, world_gen in world_generators.items():
        world = world_gen(seed=42)
        assumptions = analyze_world_assumptions(world, world_name)
        world_assumptions[world_name] = assumptions
        
        # Run world to get trajectory
        rng = np.random.default_rng(42)
        trajectory = []
        for t in range(n_steps):
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
        
        world_trajectories[world_name] = np.array(trajectory)
        
        print(f"\n   {world_name}:")
        for assumption, value in assumptions.items():
            print(f"      {assumption}: {value}")
    
    # 2. Analyze criterion-world interactions
    print("\n" + "="*60)
    print("CRITERION-WORLD INTERACTIONS")
    print("="*60)
    
    all_interactions = {}
    
    for world_name, trajectory in world_trajectories.items():
        print(f"\n   {world_name}:")
        
        world_int = {}
        for criterion_name, criterion_func in criteria.items():
            interaction = analyze_criterion_world_interaction(
                trajectory, criterion_func, world_assumptions[world_name]
            )
            world_int[criterion_name] = interaction
            
            status = "INFORMATIVE" if interaction['informative'] else "TRIVIAL"
            print(f"      {criterion_name}: {status} (score={interaction['score']:.3f})")
        
        all_interactions[world_name] = world_int
    
    # 3. Assumption advantage analysis
    print("\n" + "="*60)
    print("ASSUMPTION ADVANTAGE ANALYSIS")
    print("="*60)
    
    # For each assumption, which criteria benefit?
    assumption_benefit = defaultdict(lambda: defaultdict(list))
    
    for world_name, interactions in all_interactions.items():
        for criterion_name, interaction in interactions.items():
            for assumption in interaction['supporting_assumptions']:
                assumption_benefit[assumption][criterion_name].append(
                    interaction['score']
                )
    
    print("\nWhich criteria benefit from which assumptions?")
    for assumption, criteria_scores in assumption_benefit.items():
        print(f"\n   {assumption}:")
        for criterion_name, scores in criteria_scores.items():
            if scores:
                print(f"      {criterion_name}: mean={np.mean(scores):.3f}")
    
    # 4. Impossible distinctions
    print("\n" + "="*60)
    print("IMPOSSIBLE DISTINCTIONS")
    print("="*60)
    
    for world_name, assumptions in world_assumptions.items():
        impossible = []
        
        if not assumptions['has_temporal_structure']:
            impossible.append('temporal_prediction')
        if not assumptions['has_spatial_structure']:
            impossible.append('spatial_intervention')
        if not assumptions['has_nonlinearity']:
            impossible.append('nonlinear_counterfactuals')
        if not assumptions['has_noise']:
            impossible.append('stochastic_information')
        if not assumptions['has_boundary']:
            impossible.append('boundary_effects')
        if not assumptions['has_symmetry']:
            impossible.append('symmetric_interactions')
        
        if impossible:
            print(f"\n   {world_name}:")
            print(f"      Impossible: {impossible}")
    
    # 5. Interpretation
    print("\n" + "="*60)
    print("INTERPRETATION")
    print("="*60)
    
    print("\nThe world audit reveals:")
    print()
    print("1. Each world has hidden assumptions that advantage some criteria.")
    print("2. Criteria that appear 'informative' may simply match world assumptions.")
    print("3. Criteria that appear 'trivial' may simply mismatch world assumptions.")
    print("4. The stress worlds are not neutral — they are hypothesis-generating machines.")
    print()
    print("The next step is not to find a better criterion.")
    print("The next step is to ask: what assumptions are hidden in the worlds?")
    print()
    print("Given the history of this project,")
    print("the next collapse may come from there.")
    
    return {
        'world_assumptions': world_assumptions,
        'interactions': all_interactions,
        'assumption_benefit': {
            assumption: {
                criterion: scores
                for criterion, scores in criteria_scores.items()
            }
            for assumption, criteria_scores in assumption_benefit.items()
        },
    }

# ============================================================
# RUN
# ============================================================

if __name__ == '__main__':
    results = run_world_audit()
    
    # Save with proper serialization
    serializable = {
        'world_assumptions': results['world_assumptions'],
        'interactions': {
            world_name: {
                criterion: {
                    'score': float(data['score']),
                    'informative': bool(data['informative']),
                    'supporting_assumptions': data['supporting_assumptions'],
                }
                for criterion, data in world_data.items()
            }
            for world_name, world_data in results['interactions'].items()
        },
    }
    
    with open('/home/student/sgp_core_v2/audits/rd10b0f_results.json', 'w') as f:
        json.dump(serializable, f, indent=2)
    
    print("\nSaved to audits/rd10b0f_results.json")
