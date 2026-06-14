#!/usr/bin/env python3
"""
Phase 507: Recursive-Coherence-Asymmetry-Test Computation
Determine whether the extracted minimal recursive signature
depends primarily on coherence preservation, directional asymmetry,
or recursive redistribution balance.
"""

import json
import numpy as np
import pandas as pd
from scipy import stats
import itertools
import os

# Set seed for reproducibility
np.random.seed(507)

def load_phase505_results():
    """Load the Phase 505 results to get surviving systems"""
    with open('phases/phase505/phase505_results.json', 'r') as f:
        return json.load(f)

def load_phase506_results():
    """Load the Phase 506 results"""
    with open('phases/phase506/phase506_results.json', 'r') as f:
        return json.load(f)

def get_surviving_systems(phase505_results):
    """Extract surviving systems from Phase 505 results (directional_recursive_gradient > 0.3)"""
    authentic_systems = phase505_results['authentic_systems']
    surviving = []

    for system_name, system_data in authentic_systems.items():
        dir_grad = system_data['directional_recursive_gradient']['value']
        if dir_grad > 0.3:  # Survival threshold from Phase 505
            surviving.append({
                'name': system_name,
                'data': system_data,
                'directional_gradient': dir_grad
            })

    return surviving

def load_phase407_baseline():
    """Load the SFH-SGP baseline from Phase 407"""
    with open('phases/phase407/phase407_predictive_results.json', 'r') as f:
        return json.load(f)

def get_sfhsgp_emergence_hierarchy():
    """Extract the SFH-SGP emergence hierarchy from Phase 407 baseline"""
    phase407 = load_phase407_baseline()
    baseline = phase407['ablation_predictions_saved']['FullPABaseline']
    return [
        baseline['P-A-N'],    # 0.9285 - most emergent
        baseline['P-A'],      # 0.9283
        baseline['Projection'], # 0.9279
        baseline['P-N'],      # 0.9244
        baseline['Antisymmetry'], # 0.9225
        baseline['Neutral'],  # 0.9031
        baseline['A-N']       # 0.8864 - least emergent
    ]

def load_phase503_authentic_systems():
    """Load the authentic physical systems from Phase 503 results"""
    with open('phases/phase503/phase503_results.json', 'r') as f:
        phase503_results = json.load(f)

    authentic_systems = {}
    for name, data in phase503_results['physical_systems'].items():
        authentic_systems[name] = {
            'values': [float(v) for v in data['values']],
            'description': data['description'],
            'domain': data['domain']
        }
    return authentic_systems

def coherence_scrambling(values, strength=0.5):
    """
    Apply coherence scrambling - randomize phase relationships
    while preserving magnitude ordering
    """
    n = len(values)
    if n < 3:
        return values[:]

    # Create random phase shifts
    phases = np.random.uniform(0, 2*np.pi, n)
    # Apply phase shifts that maintain general order but disrupt coherence
    # Add small random variations that accumulate
    random_walk = np.cumsum(np.random.normal(0, strength * np.std(values), n))

    # Combine with original values
    scrambled = values + random_walk
    # Keep within bounds
    scrambled = np.clip(scrambled, 0, 1)

    return scrambled.tolist()

def asymmetric_inversion(values, target_asymmetry=1.0):
    """
    Apply asymmetric inversion - invert the pattern asymmetrically
    """
    n = len(values)
    if n < 2:
        return values[:]

    # Compute original asymmetry
    mean_val = np.mean(values)
    third_moment = np.mean((np.array(values) - mean_val)**3)
    var = np.var(values)
    if var > 0:
        original_asym = third_moment / (var**1.5)
    else:
        original_asym = 0.0

    # Apply asymmetric inversion
    inverted = [2*mean_val - v for v in values]
    inverted = np.clip(inverted, 0, 1)

    # Scale to achieve target asymmetry
    inverted_np = np.array(inverted)
    mean_inv = np.mean(inverted_np)
    third_moment_inv = np.mean((inverted_np - mean_inv)**3)
    var_inv = np.var(inverted_np)
    if var_inv > 0:
        asym_inv = third_moment_inv / (var_inv**1.5)
    else:
        asym_inv = 0.0

    # If no asymmetry, apply one-sided inversion
    if abs(asym_inv) < 0.01:
        # Make more asymmetric by taking extreme values
        extremes = [min(values), max(values), min(values)] * (n//3 + 1)
        extremes = extremes[:n]
        inverted = extremes

    return inverted

def recursive_transport_interruption(values, interruption_point=0.5):
    """
    Apply recursive transport interruption - break transport between levels
    """
    n = len(values)
    if n < 4:
        return values[:]

    # Identify break point based on interruption_point (0-1)
    break_idx = int(n * interruption_point)

    # Create two separate regions
    first_half = values[:break_idx]
    second_half = values[break_idx:]

    # Randomize within each region
    np.random.shuffle(first_half)
    np.random.shuffle(second_half)

    # Reconstruct with break
    interrupted = first_half + second_half

    return interrupted

def phase_decorrelation(values, decorrelation_strength=0.5):
    """
    Apply phase decorrelation - destroy phase relationships between levels
    """
    n = len(values)
    if n < 3:
        return values[:]

    # Add random noise that increases with depth (decorrelates phases)
    noise = np.random.normal(0, decorrelation_strength * np.std(values), n)
    decorrelated = np.array(values) + noise
    decorrelated = np.clip(decorrelated, 0, 1)

    return decorrelated.tolist()

def redistribution_saturation(values, saturation_level=0.8):
    """
    Apply redistribution saturation - push redistribution to extreme
    """
    n = len(values)
    if n < 2:
        return values[:]

    # Extreme redistribution: flatten then redistribute
    mean_val = np.mean(values)
    # Make more uniform
    saturated = [mean_val + np.random.normal(0, 0.01, 1)[0] for _ in range(n)]
    saturated = np.clip(saturated, 0, 1)

    return saturated.tolist()

def propagation_fragmentation(values, num_fragments=3):
    """
    Apply propagation fragmentation - break propagation into fragments
    """
    n = len(values)
    if n < num_fragments * 2:
        num_fragments = max(1, n // 2)

    fragments = []
    fragment_size = n // num_fragments

    for i in range(num_fragments):
        start = i * fragment_size
        end = min(start + fragment_size, n)
        if start < n:
            fragment = values[start:end]
            # Randomize within fragment
            np.random.shuffle(fragment)
            fragments.extend(fragment)

    # Pad if needed
    while len(fragments) < n:
        fragments.append(values[len(fragments) % n])

    return fragments[:n]

def delayed_recursive_coupling(values, delay=1):
    """
    Apply delayed recursive coupling - introduce delay in recursive coupling
    """
    n = len(values)
    if n < 3:
        return values[:]

    # Introduce delay by shifting values
    delayed = values.copy()
    if delay > 0 and delay < n:
        # Shift values by delay positions
        shifted = delayed[-delay:] + delayed[:-delay]
        # Add noise to simulate delayed coupling
        noise = np.random.normal(0, 0.05, n)
        delayed = [min(max(s + n, 0), 1) for s, n in zip(shifted, noise)]

    return delayed

def compute_coherence_survival_ratio(original_values, perturbed_values, sfhsgp_hierarchy):
    """
    Compute coherence survival ratio - how well coherence is preserved under perturbation
    """
    min_len = min(len(original_values), len(perturbed_values), len(sfhsgp_hierarchy))
    orig_trunc = np.array(original_values[:min_len])
    pert_trunc = np.array(perturbed_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])

    if len(orig_trunc) < 2:
        return 0.0

    # Compute coherence (depth_coupling_coherence) for both
    def depth_coupling_coherence(seq, ref_seq):
        if len(seq) < 4:
            return 0.0
        third = len(seq) // 3
        if third < 1:
            third = 1
        # Split into thirds
        shallow_seq = seq[:third]
        middle_seq = seq[third:2*third] if 2*third <= len(seq) else seq[third:]
        deep_seq = seq[2*third:3*third] if 3*third <= len(seq) else seq[2*third:]

        shallow_ref = ref_seq[:third]
        middle_ref = ref_seq[third:2*third] if 2*third <= len(ref_seq) else ref_seq[third:]
        deep_ref = ref_seq[2*third:3*third] if 3*third <= len(ref_seq) else ref_seq[2*third:]

        def layer_coherence(layer):
            if len(layer) < 2:
                return 0.0
            mean_abs = np.mean(np.abs(layer))
            if mean_abs > 0:
                return 1.0 - (np.std(layer) / (mean_abs + 1e-10))
            else:
                return 1.0 if np.std(layer) == 0 else 0.0

        coh_shallow = layer_coherence(shallow_seq) * layer_coherence(shallow_ref)
        coh_middle = layer_coherence(middle_seq) * layer_coherence(middle_ref)
        coh_deep = layer_coherence(deep_seq) * layer_coherence(deep_ref)

        # Cross-layer coupling
        avg_seq = np.mean([np.mean(shallow_seq), np.mean(middle_seq), np.mean(deep_seq)])
        avg_ref = np.mean([np.mean(shallow_ref), np.mean(middle_ref), np.mean(deep_ref)])

        if abs(avg_seq) > 1e-10 or abs(avg_ref) > 1e-10:
            return (coh_shallow + coh_middle + coh_deep) / 3.0
        else:
            return (coh_shallow + coh_middle + coh_deep) / 3.0

    # Original coherence
    orig_coherence = depth_coupling_coherence(orig_trunc, sfhsgp_trunc)

    # Perturbed coherence
    pert_coherence = depth_coupling_coherence(pert_trunc, sfhsgp_trunc)

    # Survival ratio: how much coherence is preserved
    if orig_coherence > 0:
        survival_ratio = pert_coherence / orig_coherence
    else:
        survival_ratio = 0.0 if pert_coherence == 0 else 1.0

    return max(0.0, min(survival_ratio, 2.0))  # Cap at 2.0

def compute_asymmetry_dependence_index(original_values, perturbed_values, sfhsgp_hierarchy):
    """
    Compute asymmetry dependence index - how much the system depends on asymmetry
    """
    min_len = min(len(original_values), len(perturbed_values), len(sfhsgp_hierarchy))
    orig_trunc = np.array(original_values[:min_len])
    pert_trunc = np.array(perturbed_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])

    if len(orig_trunc) < 3:
        return 0.0

    def asymmetry_score(seq):
        mean_val = np.mean(seq)
        third_moment = np.mean((seq - mean_val)**3)
        var = np.var(seq)
        if var > 0:
            return abs(third_moment / (var**1.5))
        else:
            return 0.0

    orig_asym = asymmetry_score(orig_trunc)
    pert_asym = asymmetry_score(pert_trunc)
    sfhsgp_asym = asymmetry_score(sfhsgp_trunc)

    # Dependence index: change in asymmetry under perturbation
    if orig_asym > 0:
        asymmetry_change = abs(orig_asym - pert_asym) / orig_asym
    else:
        asymmetry_change = abs(pert_asym) if orig_asym == 0 else 0.0

    # If asymmetry was key, perturbation should change it significantly
    # High change = high dependence on asymmetry
    dependence = asymmetry_change

    return min(dependence, 1.0)

def compute_recursive_balance_strength(original_values, perturbed_values, sfhsgp_hierarchy):
    """
    Compute recursive balance strength - measures balance in recursive redistribution
    """
    min_len = min(len(original_values), len(perturbed_values), len(sfhsgp_hierarchy))
    orig_trunc = np.array(original_values[:min_len])
    pert_trunc = np.array(perturbed_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])

    if len(orig_trunc) < 3:
        return 0.0

    # Balance: how evenly values are distributed
    def balance_score(seq):
        if len(seq) < 2:
            return 0.0
        mean_abs = np.mean(np.abs(seq))
        if mean_abs > 0:
            return 1.0 - (np.std(seq) / (mean_abs + 1e-10))
        else:
            return 1.0 if np.std(seq) == 0 else 0.0

    orig_balance = balance_score(orig_trunc)
    pert_balance = balance_score(pert_trunc)
    sfhsgp_balance = balance_score(sfhsgp_trunc)

    # Recursive balance strength: maintenance of balance under perturbation
    if orig_balance > 0:
        strength = pert_balance / orig_balance
    else:
        strength = 0.0

    return max(0.0, min(strength, 2.0))

def compute_propagation_fragmentation_score(original_values, perturbed_values, sfhsgp_hierarchy):
    """
    Compute propagation fragmentation score - measures how propagation is fragmented
    """
    min_len = min(len(original_values), len(perturbed_values), len(sfhsgp_hierarchy))
    orig_trunc = np.array(original_values[:min_len])
    pert_trunc = np.array(perturbed_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])

    if len(orig_trunc) < 3:
        return 0.0

    # Fragmentation: measure breaks in monotonic propagation
    def fragmentation_measure(seq):
        # Count direction changes
        diffs = np.diff(seq)
        if len(diffs) == 0:
            return 0.0
        sign_changes = np.sum(np.sign(diffs[:-1]) != np.sign(diffs[1:]))
        # Normalize by length
        return sign_changes / len(diffs)

    orig_frag = fragmentation_measure(orig_trunc)
    pert_frag = fragmentation_measure(pert_trunc)
    sfhsgp_frag = fragmentation_measure(sfhsgp_trunc)

    # Score: increase in fragmentation
    if orig_frag > 0:
        fragmentation_increase = pert_frag / orig_frag
    else:
        fragmentation_increase = pert_frag if orig_frag == 0 else 0.0

    return min(fragmentation_increase, 2.0)

def compute_recursive_transport_persistence(original_values, perturbed_values, sfhsgp_hierarchy):
    """
    Compute recursive transport persistence - how well transport information persists
    """
    min_len = min(len(original_values), len(perturbed_values), len(sfhsgp_hierarchy))
    orig_trunc = np.array(original_values[:min_len])
    pert_trunc = np.array(perturbed_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])

    if len(orig_trunc) < 3:
        return 0.0

    # Transport persistence: correlation between sequential differences
    def transport_persistence(seq):
        if len(seq) < 3:
            return 0.0
        diffs = np.diff(seq)
        if len(diffs) < 2:
            return 0.0
        # Autocorrelation of differences
        return np.corrcoef(diffs[:-1], diffs[1:])[0, 1] if len(diffs) >= 2 else 0.0

    orig_transport = transport_persistence(orig_trunc)
    pert_transport = transport_persistence(pert_trunc)
    sfhsgp_transport = transport_persistence(sfhsgp_trunc)

    # Persistence under perturbation
    if abs(orig_transport) > 0:
        persistence = pert_transport / orig_transport
    else:
        persistence = 0.0 if abs(pert_transport) < 1e-10 else 1.0

    return max(0.0, min(abs(persistence), 2.0))

def compute_signature_retention_decay(original_values, perturbed_values, sfhsgp_hierarchy):
    """
    Compute signature retention decay - how much the recursive signature degrades
    """
    min_len = min(len(original_values), len(perturbed_values), len(sfhsgp_hierarchy))
    orig_trunc = np.array(original_values[:min_len])
    pert_trunc = np.array(perturbed_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])

    if len(orig_trunc) < 2:
        return 0.0

    # Compute directional gradient for both
    def directional_gradient(seq, ref_seq):
        if len(seq) < 3 or len(ref_seq) < 3:
            return 0.0
        phys_grad = np.diff(seq)
        sfhsgp_grad = np.diff(ref_seq)
        same_sign = np.mean(np.sign(phys_grad) == np.sign(sfhsgp_grad))
        if np.std(phys_grad) > 0 and np.std(sfhsgp_grad) > 0:
            grad_cor = np.corrcoef(phys_grad, sfhsgp_grad)[0,1]
            if np.isnan(grad_cor):
                grad_cor = 0.0
            return same_sign * (1 + grad_cor) / 2
        else:
            return same_sign

    orig_grad = directional_gradient(orig_trunc, sfhsgp_trunc)
    pert_grad = directional_gradient(pert_trunc, sfhsgp_trunc)

    # Decay: how much directional gradient is lost
    if orig_grad > 0:
        decay = 1.0 - (pert_grad / orig_grad)
    else:
        decay = 0.0 if pert_grad == 0 else 1.0

    return max(0.0, min(decay, 1.0))

def compute_coherence_reconstruction_index(original_values, perturbed_values, sfhsgp_hierarchy):
    """
    Compute coherence reconstruction index - can coherence be partially reconstructed
    """
    min_len = min(len(original_values), len(perturbed_values), len(sfhsgp_hierarchy))
    orig_trunc = np.array(original_values[:min_len])
    pert_trunc = np.array(perturbed_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])

    if len(orig_trunc) < 2:
        return 0.0

    # Reconstruction: correlation between original and perturbed coherence
    def coherence_at_level(seq, ref_seq):
        if len(seq) < 4:
            return 0.0
        third = len(seq) // 3
        if third < 1:
            third = 1
        shallow_seq = seq[:third]
        middle_seq = seq[third:2*third] if 2*third <= len(seq) else seq[third:]
        deep_seq = seq[2*third:3*third] if 3*third <= len(seq) else seq[2*third:]

        shallow_ref = ref_seq[:third]
        middle_ref = ref_seq[third:2*third] if 2*third <= len(ref_seq) else ref_seq[third:]
        deep_ref = ref_seq[2*third:3*third] if 3*third <= len(ref_seq) else ref_seq[2*third:]

        def mean_coherence(layer1, layer2):
            if len(layer1) < 2 or len(layer2) < 2:
                return 0.0
            return np.corrcoef(layer1, layer2)[0,1] if len(layer1) == len(layer2) else 0.0

        coh_shallow = mean_coherence(shallow_seq, shallow_ref)
        coh_middle = mean_coherence(middle_seq, middle_ref)
        coh_deep = mean_coherence(deep_seq, deep_ref)

        return (coh_shallow + coh_middle + coh_deep) / 3.0

    orig_coherence = coherence_at_level(orig_trunc, sfhsgp_trunc)
    pert_coherence = coherence_at_level(pert_trunc, sfhsgp_trunc)

    # Reconstruction index: how much original coherence is preserved
    if abs(orig_coherence) > 0:
        reconstruction = pert_coherence / orig_coherence
    else:
        reconstruction = 0.0 if abs(pert_coherence) < 1e-10 else 1.0

    return max(0.0, min(abs(reconstruction), 2.0))

# Define adversarial conditions
adversarial_conditions = {
    'coherence_scrambling': {'function': coherence_scrambling, 'strength': 0.5},
    'asymmetric_inversion': {'function': asymmetric_inversion, 'target_asymmetry': 1.0},
    'recursive_transport_interruption': {'function': recursive_transport_interruption, 'interruption_point': 0.5},
    'phase_decorrelation': {'function': phase_decorrelation, 'decorrelation_strength': 0.5},
    'redistribution_saturation': {'function': redistribution_saturation, 'saturation_level': 0.8},
    'propagation_fragmentation': {'function': propagation_fragmentation, 'num_fragments': 3},
    'delayed_recursive_coupling': {'function': delayed_recursive_coupling, 'delay': 1}
}

def main():
    print("Starting Phase 507: Recursive-Coherence-Asymmetry-Test Analysis...")

    # Load data
    print("Loading Phase 505 results...")
    phase505_results = load_phase505_results()

    print("Loading Phase 407 baseline...")
    sfhsgp_hierarchy = get_sfhsgp_emergence_hierarchy()
    print(f"SFH-SGP Emergence Hierarchy: {sfhsgp_hierarchy}")

    # Get surviving systems
    print("Extracting surviving systems from Phase 505...")
    surviving_systems = get_surviving_systems(phase505_results)
    print(f"Surviving Systems: {len(surviving_systems)}")

    for system in surviving_systems:
        print(f"  - {system['name']} (grad: {system['directional_gradient']:.6f})")

    # Load original values
    print("Loading original physical system values...")
    phase503_authentic = load_phase503_authentic_systems()

    # Results storage (using globally defined adversarial_conditions)
    results = {
        'phase': 507,
        'seed': 507,
        'tier': 3,
        'sfhsgp_hierarchy': sfhsgp_hierarchy,
        'surviving_systems': {s['name']: s for s in surviving_systems},
        'adversarial_conditions': adversarial_conditions,
        'metrics_by_system': {},
        'summary': {}
    }

    print("\nApplying adversarial conditions to surviving systems...")

    for system in surviving_systems:
        sys_name = system['name']
        original_data = phase503_authentic[sys_name]['values']

        print(f"\nAnalyzing {sys_name}...")
        metrics_by_condition = {}

        for condition_name, condition_params in adversarial_conditions.items():
            perturb_func = condition_params['function']
            perturbed_values = perturb_func(original_data.copy(), **{k: v for k, v in condition_params.items() if k != 'function'})

            # Compute all seven metrics
            coherence_survival = compute_coherence_survival_ratio(original_data, perturbed_values, sfhsgp_hierarchy)
            asymmetry_dependence = compute_asymmetry_dependence_index(original_data, perturbed_values, sfhsgp_hierarchy)
            recursive_balance = compute_recursive_balance_strength(original_data, perturbed_values, sfhsgp_hierarchy)
            propagation_fragmentation = compute_propagation_fragmentation_score(original_data, perturbed_values, sfhsgp_hierarchy)
            recursive_transport = compute_recursive_transport_persistence(original_data, perturbed_values, sfhsgp_hierarchy)
            signature_decay = compute_signature_retention_decay(original_data, perturbed_values, sfhsgp_hierarchy)
            coherence_reconstruction = compute_coherence_reconstruction_index(original_data, perturbed_values, sfhsgp_hierarchy)

            metrics_by_condition[condition_name] = {
                'coherence_survival_ratio': coherence_survival,
                'asymmetry_dependence_index': asymmetry_dependence,
                'recursive_balance_strength': recursive_balance,
                'propagation_fragmentation_score': propagation_fragmentation,
                'recursive_transport_persistence': recursive_transport,
                'signature_retention_decay': signature_decay,
                'coherence_reconstruction_index': coherence_reconstruction
            }

        results['metrics_by_system'][sys_name] = metrics_by_condition

    # Compute summary metrics across all surviving systems
    print("\nComputing summary metrics...")
    summary_metrics = {}

    for metric_name in ['coherence_survival_ratio', 'asymmetry_dependence_index',
                       'recursive_balance_strength', 'propagation_fragmentation_score',
                       'recursive_transport_persistence', 'signature_retention_decay',
                       'coherence_reconstruction_index']:

        values = []
        for sys_name, conditions in results['metrics_by_system'].items():
            for condition_name, metrics in conditions.items():
                values.append(metrics[metric_name])

        if len(values) > 0:
            summary_metrics[metric_name] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values))
            }

    results['summary'] = summary_metrics

    # Identify dominant drivers
    print("\nIdentifying dominant drivers...")
    dominant_drivers = []

    # A driver is dominant if its metric shows high consistency across conditions
    for metric_name, stats in summary_metrics.items():
        # High consistency: low std relative to mean, and high mean
        if stats['mean'] > 0.5 and stats['std'] / max(stats['mean'], 1e-10) < 0.5:
            dominant_drivers.append(metric_name)

    results['dominant_drivers'] = dominant_drivers
    results['success_condition'] = len(dominant_drivers) > 0

    # Save results
    output_file = 'phases/phase507/phase507_results.json'
    # Replace function objects with names for JSON serialization
    serializable_adversarial = {k: v['function'].__name__ for k, v in adversarial_conditions.items()}
    results['adversarial_conditions'] = serializable_adversarial

    # Compute cross-system collapse synchrony for coherence destruction
    # Check if coherence_survival_ratio under 'coherence_scrambling' is low for ALL systems
    coherence_ratios = []
    for sys_name, conds in results['metrics_by_system'].items():
        ratio = conds.get('coherence_scrambling', {}).get('coherence_survival_ratio')
        if ratio is not None:
            coherence_ratios.append(ratio)
    # Define collapse if all ratios below 0.2 (arbitrary low threshold)
    cross_system_collapse = all(r < 0.2 for r in coherence_ratios) if coherence_ratios else False
    results['cross_system_collapse_synchrony'] = cross_system_collapse

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)


    print(f"\nResults saved to {output_file}")

    # Print summary
    print("\n" + "="*70)
    print("PHASE 507 RESULTS SUMMARY")
    print("="*70)
    print(f"Surviving Systems Analyzed: {len(surviving_systems)}")
    print(f"Cross-system collapse synchrony (coherence scrambling): {cross_system_collapse}")

    print(f"\nSummary Metrics (across all systems and conditions):")
    for metric_name, stats in summary_metrics.items():
        print(f"  {metric_name}: {stats['mean']:.6f} +/- {stats['std']:.6f} (range: {stats['min']:.6f}-{stats['max']:.6f})")

    print(f"\nDominant Drivers: {dominant_drivers}")
    print(f"Success Condition Met: {len(dominant_drivers) > 0}")
    print(f"Verdict: {'MINIMAL-RECURSIVE-SIGNATURE-SUCCESS' if len(dominant_drivers) > 0 else 'MINIMAL-RECURSIVE-SIGNATURE-FAILURE'}")
    print("="*70)

    return results

if __name__ == "__main__":
    try:
        results = main()
    except Exception as e:
        print(f"Error in Phase 507 computation: {e}")
        import traceback
        traceback.print_exc()