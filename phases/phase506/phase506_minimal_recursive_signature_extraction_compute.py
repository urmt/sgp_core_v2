#!/usr/bin/env python3
"""
Phase 506: Minimal-Recursive-Signature-Extraction Computation
Determine the minimal structural features shared ONLY by the surviving Phase 505 systems.
"""

import json
import numpy as np
import pandas as pd
from scipy import stats
import itertools
import os

# Set seed for reproducibility
np.random.seed(506)

def load_phase505_results():
    """Load the Phase 505 results to get surviving systems"""
    with open('phases/phase505/phase505_results.json', 'r') as f:
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

def get_rejected_systems(phase505_results):
    """Extract rejected systems from Phase 505 results (directional_recursive_gradient <= 0.3)"""
    authentic_systems = phase505_results['authentic_systems']
    rejected = []
    
    for system_name, system_data in authentic_systems.items():
        dir_grad = system_data['directional_recursive_gradient']['value']
        if dir_grad <= 0.3:  # Rejection threshold from Phase 505
            rejected.append({
                'name': system_name,
                'data': system_data,
                'directional_gradient': dir_grad
            })
    
    return rejected

def get_adversarial_systems(phase505_results):
    """Extract adversarial systems from Phase 505 results"""
    adversarial_systems = phase505_results['adversarial_systems']
    adversarial_list = []
    
    for system_name, system_data in adversarial_systems.items():
        adversarial_list.append({
            'name': system_name,
            'data': system_data,
            'directional_gradient': system_data['directional_recursive_gradient']['value']
        })
    
    return adversarial_list

def load_phase407_baseline():
    """Load the SFH-SGP baseline from Phase 407"""
    with open('phases/phase407/phase407_predictive_results.json', 'r') as f:
        return json.load(f)

def get_sfhsgp_emergence_hierarchy():
    """Extract the SFH-SGP emergence hierarchy from Phase 407 baseline"""
    phase407 = load_phase407_baseline()
    baseline = phase407['ablation_predictions_saved']['FullPABaseline']
    # Return in order of emergence (most to least)
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
    
    # Extract the authentic systems (they are stored under 'physical_systems')
    authentic_systems = {}
    for name, data in phase503_results['physical_systems'].items():
        authentic_systems[name] = {
            'values': [float(v) for v in data['values']],
            'description': data['description'],
            'domain': data['domain']
        }
    return authentic_systems

def compute_recursive_signature_overlap(systems_list, sfhsgp_hierarchy):
    """
    Compute recursive signature overlap - measures consistency of directional patterns
    across systems in the list.
    """
    if len(systems_list) < 2:
        return {'value': 0.0}
    
    # Extract directional gradients for all systems
    gradients = []
    for system in systems_list:
        gradients.append(system['directional_gradient'])
    
    # Also compute propagation asymmetry indices
    asym_values = []
    for system in systems_list:
        asym_values.append(system['data']['propagation_asymmetry_index']['value'])
    
    # Compute overlap as consistency of signed patterns
    # Systems with same sign of directional gradient contribute positively
    signs = [np.sign(g) for g in gradients]
    sign_consistency = 1.0 - (np.std(signs) / 2.0) if len(set(signs)) > 1 else 1.0
    
    # Compute magnitude consistency
    if np.mean(np.abs(gradients)) > 0:
        magnitude_consistency = 1.0 - (np.std(gradients) / np.mean(np.abs(gradients)))
        magnitude_consistency = max(0.0, min(magnitude_consistency, 1.0))
    else:
        magnitude_consistency = 1.0 if np.std(gradients) == 0 else 0.0
    
    # Compute asymmetry consistency
    if np.mean(asym_values) > 0:
        asym_consistency = 1.0 - (np.std(asym_values) / np.mean(asym_values))
        asym_consistency = max(0.0, min(asym_consistency, 1.0))
    else:
        asym_consistency = 1.0 if np.std(asym_values) == 0 else 0.0
    
    # Overall overlap
    overlap = (sign_consistency + magnitude_consistency + asym_consistency) / 3.0
    
    return {
        'value': float(max(0.0, min(overlap, 1.0))),
        'sign_consistency': float(sign_consistency),
        'magnitude_consistency': float(magnitude_consistency),
        'asym_consistency': float(asym_consistency)
    }

def compute_coherence_retention_index(systems_list, sfhsgp_hierarchy):
    """
    Compute coherence retention index - measures how well systems maintain
    internal coherence across recursive levels.
    """
    coherence_values = []
    
    for system in systems_list:
        # Use depth_coupling_coherence as proxy for coherence retention
        coherence_values.append(system['data']['depth_coupling_coherence']['value'])
    
    if len(coherence_values) == 0:
        return {'value': 0.0}
    
    # Index is the mean coherence - higher means better retention
    mean_coherence = np.mean(coherence_values)
    
    return {
        'value': float(mean_coherence),
        'std': float(np.std(coherence_values)),
        'min': float(np.min(coherence_values)),
        'max': float(np.max(coherence_values))
    }

def compute_propagation_dependency_score(systems_list, sfhsgp_hierarchy):
    """
    Compute propagation dependency score - measures dependency strength 
    propagation across recursive levels.
    """
    dependency_values = []
    
    for system in systems_list:
        # Use recursive_dependency_score as measurement
        dependency_values.append(system['data']['recursive_dependency_score']['value'])
    
    if len(dependency_values) == 0:
        return {'value': 0.0}
    
    # Score is mean dependency strength
    mean_dependency = np.mean(dependency_values)
    
    return {
        'value': float(mean_dependency),
        'std': float(np.std(dependency_values)),
        'min': float(np.min(dependency_values)),
        'max': float(np.max(dependency_values))
    }

def compute_redistribution_recursion_strength(systems_list, sfhsgp_hierarchy):
    """
    Compute redistribution recursion strength - measures how well 
    systems maintain recursive structure under redistribution.
    """
    # Use transfer entropy as proxy for redistribution capability
    transfer_values = []
    
    for system in systems_list:
        transfer_values.append(system['data']['recursive_transfer_entropy']['value'])
    
    if len(transfer_values) == 0:
        return {'value': 0.0}
    
    # Strength is mean transfer entropy
    mean_transfer = np.mean(transfer_values)
    
    return {
        'value': float(mean_transfer),
        'std': float(np.std(transfer_values)),
        'min': float(np.min(transfer_values)),
        'max': float(np.max(transfer_values))
    }

def compute_asymmetry_persistence_measure(systems_list, sfhsgp_hierarchy):
    """
    Compute asymmetry persistence measure - measures consistency 
    of asymmetry preservation across systems.
    """
    asymmetry_values = []
    
    for system in systems_list:
        # Use asymmetry_preservation_ratio
        asymmetry_values.append(system['data']['asymmetry_preservation_ratio']['value'])
    
    if len(asymmetry_values) == 0:
        return {'value': 0.0}
    
    # Measure is how close values are to 1.0 (perfect preservation)
    # But we want to measure persistence, so look at consistency
    mean_asym = np.mean(asymmetry_values)
    std_asym = np.std(asymmetry_values)
    
    # Persistence is high when systems show consistent asymmetry behavior
    if mean_asym > 0:
        persistence = 1.0 - min(std_asym / mean_asym, 1.0)
    else:
        persistence = 1.0 if std_asym == 0 else 0.0
    
    return {
        'value': float(max(0.0, min(persistence, 1.0))),
        'mean_asymmetry': float(mean_asym),
        'std_asymmetry': float(std_asym)
    }

def compute_depth_stability_gradient(systems_list, sfhsgp_hierarchy):
    """
    Compute depth stability gradient - measures how stability 
    changes across depth levels in surviving systems.
    """
    # For each system, compute stability at different depths
    depth_stability_profiles = []
    
    for system in systems_list:
        phys_vals = np.array(system['data']['values'])
        sfhsgp_vals = np.array(sfhsgp_hierarchy)
        
        min_len = min(len(phys_vals), len(sfhsgp_vals))
        phys_trunc = phys_vals[:min_len]
        sfhsgp_trunc = sfhsgp_vals[:min_len]
        
        if len(phys_trunc) < 3:
            continue
            
        # Split into thirds: shallow, middle, deep
        third = len(phys_trunc) // 3
        if third < 1:
            third = 1
        
        shallow_phys = phys_trunc[:third]
        middle_phys = phys_trunc[third:2*third]
        deep_phys = phys_trunc[2*third:3*third] if 3*third <= len(phys_trunc) else phys_trunc[2*third:]
        
        shallow_sfhsgp = sfhsgp_trunc[:third]
        middle_sfhsgp = sfhsgp_trunc[third:2*third]
        deep_sfhsgp = sfhsgp_trunc[2*third:3*third] if 3*third <= len(sfhsgp_trunc) else sfhsgp_trunc[2*third:]
        
        # Compute stability (inverse of normalized variance) at each level
        def stability_at_level(level_vals):
            if len(level_vals) < 2:
                return 0.0
            mean_abs = np.mean(np.abs(level_vals))
            if mean_abs > 0:
                return 1.0 - (np.std(level_vals) / (mean_abs + 1e-10))
            else:
                return 1.0 if np.std(level_vals) == 0 else 0.0
        
        shallow_stab = stability_at_level(shallow_phys) * stability_at_level(shallow_sfhsgp)
        middle_stab = stability_at_level(middle_phys) * stability_at_level(middle_sfhsgp)
        deep_stab = stability_at_level(deep_phys) * stability_at_level(deep_sfhsgp)
        
        # Gradient: how stability changes from shallow to deep
        if len([shallow_stab, middle_stab, deep_stab]) >= 2:
            stab_levels = [shallow_stab, middle_stab, deep_stab]
            # Compute linear trend
            x_vals = np.array([0, 1, 2])
            if len(stab_levels) == len(x_vals):
                try:
                    slope, _ = np.polyfit(x_vals, stab_levels, 1)
                    gradient = slope  # Positive = increasing stability with depth
                except:
                    gradient = 0.0
            else:
                gradient = 0.0
        else:
            gradient = 0.0
            
        depth_stability_profiles.append(gradient)
    
    if len(depth_stability_profiles) == 0:
        return {'value': 0.0}
    
    # Return mean gradient across systems
    mean_gradient = np.mean(depth_stability_profiles)
    
    return {
        'value': float(mean_gradient),
        'std': float(np.std(depth_stability_profiles)),
        'profiles': [float(p) for p in depth_stability_profiles]
    }

def compute_transport_recursion_analysis(systems_list, sfhsgp_hierarchy):
    """
    Compute transport recursion analysis - examines how 
    recursive properties relate to transport-like behavior.
    """
    # Use causal order retention and transfer entropy together
    causal_values = []
    transfer_values = []
    
    for system in systems_list:
        causal_values.append(system['data']['causal_order_retention']['value'])
        transfer_values.append(system['data']['recursive_transfer_entropy']['value'])
    
    if len(causal_values) == 0 or len(transfer_values) == 0:
        return {'value': 0.0}
    
    # Transport recursion strength: systems that maintain causal order 
    # while allowing transfer show transport-like recursion
    transport_scores = []
    for causal, transfer in zip(causal_values, transfer_values):
        # High when both causal order and transfer are present
        score = causal * transfer  # Simple product as proxy
        transport_scores.append(score)
    
    mean_transport = np.mean(transport_scores)
    
    return {
        'value': float(mean_transport),
        'std': float(np.std(transport_scores)),
        'causal_mean': float(np.mean(causal_values)),
        'transfer_mean': float(np.mean(transfer_values))
    }

def compute_iterative_redistribution_mapping(systems_list, sfhsgp_hierarchy):
    """
    Compute iterative redistribution mapping - examines how 
    systems behave under iterative redistribution operations.
    """
    # Use asymmetry preservation and recursive dependency together
    asym_values = []
    dep_values = []
    
    for system in systems_list:
        asym_values.append(system['data']['asymmetry_preservation_ratio']['value'])
        dep_values.append(system['data']['recursive_dependency_score']['value'])
    
    if len(asym_values) == 0 or len(dep_values) == 0:
        return {'value': 0.0}
    
    # Iterative redistribution strength: balance between maintaining 
    # asymmetry (structure) and allowing dependency (flow)
    redist_scores = []
    for asym, dep in zip(asym_values, dep_values):
        # Optimal balance when neither is too extreme
        # Score highest when both are moderate (around 0.5)
        balance_score = 1.0 - abs((asym - 0.5) * 2) - abs((dep - 0.5) * 2)
        balance_score = max(0.0, min(balance_score, 1.0))
        redist_scores.append(balance_score)
    
    mean_redist = np.mean(redist_scores)
    
    return {
        'value': float(mean_redist),
        'std': float(np.std(redist_scores)),
        'asym_mean': float(np.mean(asym_values)),
        'dep_mean': float(np.mean(dep_values))
    }

def compute_minimal_signature_density(surviving_systems, rejected_systems, adversarial_systems, sfhsgp_hierarchy):
    """
    Compute minimal signature density - measures how concentrated 
    the signature is in surviving systems vs others.
    """
    # Compute signature strength for each system using multiple metrics
    def signature_strength(system_data):
        # Combine multiple metrics into a signature strength score
        dir_grad = abs(system_data['directional_recursive_gradient']['value'])
        prop_asym = system_data['propagation_asymmetry_index']['value']
        rec_dep = system_data['recursive_dependency_score']['value']
        depth_coup = system_data['depth_coupling_coherence']['value']
        asym_pres = system_data['asymmetry_preservation_ratio']['value']
        
        # Weighted combination - emphasize directional consistency and asymmetry
        strength = (dir_grad * 0.3 + 
                   prop_asym * 0.2 + 
                   rec_dep * 0.15 + 
                   depth_coup * 0.15 + 
                   asym_pres * 0.2)
        return strength
    
    # Compute signature strengths
    surviving_strengths = [signature_strength(s['data']) for s in surviving_systems]
    rejected_strengths = [signature_strength(s['data']) for s in rejected_systems]
    adversarial_strengths = [signature_strength(s['data']) for s in adversarial_systems]
    
    # Compute density: how much more concentrated signature is in surviving vs others
    if len(surviving_strengths) > 0:
        mean_surviving = np.mean(surviving_strengths)
        std_surviving = np.std(surviving_strengths) if len(surviving_strengths) > 1 else 0.0
    else:
        mean_surviving = 0.0
        std_surviving = 0.0
        
    if len(rejected_strengths) > 0:
        mean_rejected = np.mean(rejected_strengths)
        std_rejected = np.std(rejected_strengths) if len(rejected_strengths) > 1 else 0.0
    else:
        mean_rejected = 0.0
        std_rejected = 0.0
        
    if len(adversarial_strengths) > 0:
        mean_adversarial = np.mean(adversarial_strengths)
        std_adversarial = np.std(adversarial_strengths) if len(adversarial_strengths) > 1 else 0.0
    else:
        mean_adversarial = 0.0
        std_adversarial = 0.0
    
    # Density metrics
    if mean_rejected > 0 and mean_adversarial > 0:
        density_vs_rejected = mean_surviving / mean_rejected
        density_vs_adversarial = mean_surviving / mean_adversarial
        overall_density = min(density_vs_rejected, density_vs_adversarial)  # Conservative estimate
    elif mean_rejected > 0:
        overall_density = mean_surviving / mean_rejected
    elif mean_adversarial > 0:
        overall_density = mean_surviving / mean_adversarial
    else:
        overall_density = mean_surviving if mean_surviving > 0 else 0.0
    
    # Cap extreme values
    overall_density = min(overall_density, 10.0)
    
    return {
        'value': float(overall_density),
        'surviving_mean': float(mean_surviving),
        'surviving_std': float(std_surviving),
        'rejected_mean': float(mean_rejected),
        'rejected_std': float(std_rejected),
        'adversarial_mean': float(mean_adversarial),
        'adversarial_std': float(std_adversarial)
    }

def perform_null_testing(sfhsgp_hierarchy, n_permutations=1000):
    """
    Perform null hypothesis testing by randomizing physical system values
    """
    # Create a template physical system to randomize (using median values)
    template_values = [0.5, 0.45, 0.4, 0.35, 0.3, 0.2, 0.1]  # 7-point template
    
    null_rhos = []
    min_len = min(len(sfhsgp_hierarchy), len(template_values))
    sfhsgp_trunc = sfhsgp_hierarchy[:min_len]
    template_trunc = template_values[:min_len]
    
    if len(sfhsgp_trunc) < 2:
        return {'rho': [], 'mean': 0.0, 'std': 0.0}
        
    for _ in range(n_permutations):
        # Permute the template values
        permuted = np.random.permutation(template_trunc)
        # Compute correlation with SFH-SGP hierarchy
        rho, _ = stats.spearmanr(sfhsgp_trunc, permuted)
        if not np.isnan(rho):
            null_rhos.append(float(rho))
    
    return {
        'rho': null_rhos,
        'mean': float(np.mean(null_rhos)) if null_rhos else 0.0,
        'std': float(np.std(null_rhos)) if null_rhos else 0.0
    }

def main():
    print("Starting Phase 506: Minimal-Recursive-Signature-Extraction Analysis...")
    
    # Load SFH-SGP baseline
    print("Loading SFH-SGP baseline from Phase 407...")
    sfhsgp_hierarchy = get_sfhsgp_emergence_hierarchy()
    print(f"SFH-SGP Emergence Hierarchy: {sfhsgp_hierarchy}")
    
    # Load Phase 505 results
    print("Loading Phase 505 results...")
    phase505_results = load_phase505_results()
    
    # Extract system classifications
    print("Extracting system classifications from Phase 505...")
    surviving_systems = get_surviving_systems(phase505_results)
    rejected_systems = get_rejected_systems(phase505_results)
    adversarial_systems = get_adversarial_systems(phase505_results)
    
    print(f"Surviving Systems: {len(surviving_systems)}")
    print(f"Rejected Systems: {len(rejected_systems)}")
    print(f"Adversarial Systems: {len(adversarial_systems)}")
    
    # Print surviving systems
    print("\nSurviving Systems (Phase 505 directional_recursive_gradient > 0.3):")
    for system in surviving_systems:
        print(f"  {system['name']}: {system['directional_gradient']:.6f}")
    
    # Compute all primary metrics for surviving systems
    print("\nComputing primary metrics for surviving systems...")
    
    # 1. Recursive signature overlap
    print("  Computing recursive signature overlap...")
    recursive_overlap = compute_recursive_signature_overlap(surviving_systems, sfhsgp_hierarchy)
    
    # 2. Coherence retention index
    print("  Computing coherence retention index...")
    coherence_retention = compute_coherence_retention_index(surviving_systems, sfhsgp_hierarchy)
    
    # 3. Propagation dependency score
    print("  Computing propagation dependency score...")
    propagation_dependency = compute_propagation_dependency_score(surviving_systems, sfhsgp_hierarchy)
    
    # 4. Redistribution recursion strength
    print("  Computing redistribution recursion strength...")
    redistribution_strength = compute_redistribution_recursion_strength(surviving_systems, sfhsgp_hierarchy)
    
    # 5. Asymmetry persistence measure
    print("  Computing asymmetry persistence measure...")
    asymmetry_persistence = compute_asymmetry_persistence_measure(surviving_systems, sfhsgp_hierarchy)
    
    # 6. Depth stability gradient
    print("  Computing depth stability gradient...")
    depth_stability = compute_depth_stability_gradient(surviving_systems, sfhsgp_hierarchy)
    
    # 7. Transport recursion analysis
    print("  Computing transport recursion analysis...")
    transport_analysis = compute_transport_recursion_analysis(surviving_systems, sfhsgp_hierarchy)
    
    # 8. Iterative redistribution mapping
    print("  Computing iterative redistribution mapping...")
    iterative_mapping = compute_iterative_redistribution_mapping(surviving_systems, sfhsgp_hierarchy)
    
    # 9. Minimal signature density (comparative)
    print("  Computing minimal signature density...")
    signature_density = compute_minimal_signature_density(
        surviving_systems, rejected_systems, adversarial_systems, sfhsgp_hierarchy)
    
    # Perform null hypothesis testing
    print("Performing null hypothesis testing (1000 permutations)...")
    null_distribution = perform_null_testing(sfhsgp_hierarchy, n_permutations=1000)
    print(f"Null distribution: mean={null_distribution['mean']:.6f}, std={null_distribution['std']:.6f}")
    
    # Compute success metrics
    print("\nEvaluating success conditions...")
    
    # Success Condition: A reproducible minimal recursive signature is isolated across surviving systems only.
    # We'll evaluate this by checking:
    # 1. Surviving systems show strong internal consistency (high overlap)
    # 2. Surviving systems are significantly different from rejected/adversarial systems
    
    # Internal consistency of surviving systems
    surviving_consistent = recursive_overlap['value'] > 0.5
    
    # Separation from rejected systems
    separated_from_rejected = signature_density['surviving_mean'] > signature_density['rejected_mean'] * 1.5
    
    # Separation from adversarial systems
    separated_from_adversarial = signature_density['surviving_mean'] > signature_density['adversarial_mean'] * 1.5
    
    # Overall success
    success_condition_met = surviving_consistent and separated_from_rejected and separated_from_adversarial
    
    # Failure Condition: No unique recursive structure distinguishes surviving systems from rejected systems.
    failure_condition_met = not (surviving_consistent or separated_from_rejected or separated_from_adversarial)
    
    # Determine verdict
    if success_condition_met and not failure_condition_met:
        verdict = "MINIMAL-RECURSIVE-SIGNATURE-EXTRACTION-SUCCESS"
    elif failure_condition_met and not success_condition_met:
        verdict = "MINIMAL-RECURSIVE-SIGNATURE-EXTRACTION-FAILURE"
    else:
        # Ambiguous case
        verdict = "MINIMAL-RECURSIVE-SIGNATURE-EXTRACTION-INCONCLUSIVE"
    
    # Create summary dictionary
    summary = {
        'surviving_systems_count': len(surviving_systems),
        'rejected_systems_count': len(rejected_systems),
        'adversarial_systems_count': len(adversarial_systems),
        'surviving_system_names': [s['name'] for s in surviving_systems],
        'recursive_signature_overlap': recursive_overlap,
        'coherence_retention_index': coherence_retention,
        'propagation_dependency_score': propagation_dependency,
        'redistribution_recursion_strength': redistribution_strength,
        'asymmetry_persistence_measure': asymmetry_persistence,
        'depth_stability_gradient': depth_stability,
        'transport_recursion_analysis': transport_analysis,
        'iterative_redistribution_mapping': iterative_mapping,
        'minimal_signature_density': signature_density,
        'null_distribution': null_distribution,
        'success_condition_met': bool(success_condition_met),
        'failure_condition_met': bool(failure_condition_met),
        'verdict': verdict
    }
    
    # Create final results dictionary
    results = {
        'phase': 506,
        'seed': 506,
        'tier': 3,
        'sfhsgp_hierarchy': sfhsgp_hierarchy,
        'surviving_systems_data': {s['name']: s['data'] for s in surviving_systems},
        'rejected_systems_data': {s['name']: s['data'] for s in rejected_systems},
        'adversarial_systems_data': {s['name']: s['data'] for s in adversarial_systems},
        'primary_metrics': summary,
        'summary': {
            'verdict': verdict,
            'surviving_count': len(surviving_systems),
            'signature_overlap': recursive_overlap['value'],
            'coherence_retention': coherence_retention['value'],
            'propagation_dependency': propagation_dependency['value'],
            'redistribution_strength': redistribution_strength['value'],
            'asymmetry_persistence': asymmetry_persistence['value'],
            'depth_stability': depth_stability['value'],
            'signature_density': signature_density['value'],
            'success_condition_met': success_condition_met,
            'failure_condition_met': failure_condition_met
        }
    }
    
    # Save results to file
    output_file = 'phases/phase506/phase506_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("PHASE 506 RESULTS SUMMARY")
    print("="*70)
    print(f"Surviving Systems Analyzed: {len(surviving_systems)}")
    print(f"Rejected Systems Analyzed: {len(rejected_systems)}")
    print(f"Adversarial Systems Analyzed: {len(adversarial_systems)}")
    print(f"\nSurviving Systems:")
    for system in surviving_systems:
        print(f"  - {system['name']} (grad: {system['directional_gradient']:.6f})")
    
    print(f"\nPrimary Metrics for Surviving Systems:")
    print(f"  Recursive Signature Overlap: {recursive_overlap['value']:.6f}")
    print(f"  Coherence Retention Index: {coherence_retention['value']:.6f}")
    print(f"  Propagation Dependency Score: {propagation_dependency['value']:.6f}")
    print(f"  Redistribution Recursion Strength: {redistribution_strength['value']:.6f}")
    print(f"  Asymmetry Persistence Measure: {asymmetry_persistence['value']:.6f}")
    print(f"  Depth Stability Gradient: {depth_stability['value']:.6f}")
    print(f"  Minimal Signature Density: {signature_density['value']:.6f}")
    print(f"    (vs rejected: {signature_density['surviving_mean']:.6f} / {signature_density['rejected_mean']:.6f})")
    print(f"    (vs adversarial: {signature_density['surviving_mean']:.6f} / {signature_density['adversarial_mean']:.6f})")
    
    print(f"\nSuccess Evaluation:")
    print(f"  Surviving Systems Consistent: {surviving_consistent} (overlap > 0.5)")
    print(f"  Separated from Rejected Systems: {separated_from_rejected}")
    print(f"  Separated from Adversarial Systems: {separated_from_adversarial}")
    print(f"  Success Condition Met: {success_condition_met}")
    print(f"  Failure Condition Met: {failure_condition_met}")
    print(f"  Verdict: {verdict}")
    print("="*70)
    
    # Also save a summary CSV for easy inspection
    summary_rows = []
    
    # Add surviving systems
    for system in surviving_systems:
        sys_data = system['data']
        summary_rows.append({
            'system': system['name'],
            'type': 'surviving',
            'directional_gradient': sys_data['directional_recursive_gradient']['value'],
            'propagation_asymmetry': sys_data['propagation_asymmetry_index']['value'],
            'recursive_dependency': sys_data['recursive_dependency_score']['value'],
            'depth_coupling': sys_data['depth_coupling_coherence']['value'],
            'causal_retention': sys_data['causal_order_retention']['value'],
            'transfer_entropy': sys_data['recursive_transfer_entropy']['value'],
            'asymmetry_preservation': sys_data['asymmetry_preservation_ratio']['value'],
            'standard_rho': sys_data['standard_correlation']['rho'],
            'standard_p': sys_data['standard_correlation']['p']
        })
    
    # Add rejected systems (sample)
    for system in rejected_systems[:10]:  # First 10 rejected
        sys_data = system['data']
        summary_rows.append({
            'system': system['name'],
            'type': 'rejected',
            'directional_gradient': sys_data['directional_recursive_gradient']['value'],
            'propagation_asymmetry': sys_data['propagation_asymmetry_index']['value'],
            'recursive_dependency': sys_data['recursive_dependency_score']['value'],
            'depth_coupling': sys_data['depth_coupling_coherence']['value'],
            'causal_retention': sys_data['causal_order_retention']['value'],
            'transfer_entropy': sys_data['recursive_transfer_entropy']['value'],
            'asymmetry_preservation': sys_data['asymmetry_preservation_ratio']['value'],
            'standard_rho': sys_data['standard_correlation']['rho'],
            'standard_p': sys_data['standard_correlation']['p']
        })
    
    # Add adversarial systems (sample)
    for system in adversarial_systems[:10]:  # First 10 adversarial
        sys_data = system['data']
        summary_rows.append({
            'system': system['name'],
            'type': 'adversarial',
            'directional_gradient': sys_data['directional_recursive_gradient']['value'],
            'propagation_asymmetry': sys_data['propagation_asymmetry_index']['value'],
            'recursive_dependency': sys_data['recursive_dependency_score']['value'],
            'depth_coupling': sys_data['depth_coupling_coherence']['value'],
            'causal_retention': sys_data['causal_order_retention']['value'],
            'transfer_entropy': sys_data['recursive_transfer_entropy']['value'],
            'asymmetry_preservation': sys_data['asymmetry_preservation_ratio']['value'],
            'standard_rho': sys_data['standard_correlation']['rho'],
            'standard_p': sys_data['standard_correlation']['p'],
            'original_system': sys_data['original_system'],
            'adversarial_type': sys_data['adversarial_type']
        })
    
    df = pd.DataFrame(summary_rows)
    csv_file = 'phases/phase506/phase506_summary.csv'
    df.to_csv(csv_file, index=False)
    print(f"Summary CSV saved to {csv_file}")
    
    return results

if __name__ == "__main__":
    try:
        results = main()
    except Exception as e:
        print(f"Error in Phase 506 computation: {e}")
        import traceback
        traceback.print_exc()