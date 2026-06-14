#!/usr/bin/env python3
"""
Phase 504: Adversarial-Physical-Discrimination Computation
Determines whether SFH-SGP correspondence reflects genuine structural specificity
or overgeneralized correspondence capture by testing against adversarial pseudo-physical systems.
"""

import json
import numpy as np
import itertools
from scipy import stats
import pandas as pd
import os

# Set seed for reproducibility
np.random.seed(504)

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

def generate_adversarial_systems(authentic_systems):
    """
    Generate adversarial pseudo-physical systems for each authentic system.
    Each adversarial system will have similar superficial properties but lack genuine recursive stability structure.
    """
    adversarial_systems = {}
    
    for system_name, system_data in authentic_systems.items():
        original_values = system_data['values']
        description = system_data['description']
        domain = system_data['domain']
        
        # We'll create 3 types of adversarial systems for each authentic system:
        # 1. Shuffled values (breaks any ordinal relationship but preserves distribution)
        # 2. Gaussian noise added to original values (preserves trend but adds randomness)
        # 3. Random values in same range (completely random)
        
        # For simplicity, we'll generate one adversarial system per authentic system using a combination
        # that is designed to lack recursive stability structure while appearing physical.
        
        # Method: Reverse the order of values (anti-correlated) plus add some noise
        # This should destroy any meaningful correspondence with SFH-SGP hierarchy
        reversed_values = list(reversed(original_values))
        # Add small noise to avoid perfect anti-correlation (which might still be significant)
        noise = np.random.normal(0, 0.05, len(reversed_values))
        adversarial_values = [max(0, min(1, v + n)) for v, n in zip(reversed_values, noise)]
        
        # Ensure values are in [0,1] range
        adversarial_values = [max(0, min(1, v)) for v in adversarial_values]
        
        adversarial_systems[f"{system_name}_Adversarial"] = {
            'values': adversarial_values,
            'description': f"Adversarial version of {description}",
            'domain': domain,
            'is_adversarial': True,
            'original_system': system_name
        }
    
    return adversarial_systems

def compute_correspondence(physical_values, sfhsgp_hierarchy):
    """
    Compute correspondence between a physical system's values and SFH-SGP emergence hierarchy
    Uses Spearman correlation for ordinal relationship
    """
    # Ensure same length by truncating or extending to match
    min_len = min(len(physical_values), len(sfhsgp_hierarchy))
    phys_trunc = physical_values[:min_len]
    sfhsgp_trunc = sfhsgp_hierarchy[:min_len]
    
    if len(phys_trunc) < 2:
        return {'rho': 0.0, 'p': 1.0, 'tau': 0.0}
    
    # Compute Spearman correlation
    rho, p_val = stats.spearmanr(phys_trunc, sfhsgp_trunc)
    
    # Compute Kendall tau
    tau, _ = stats.kendalltau(phys_trunc, sfhsgp_trunc)
    
    return {
        'rho': float(rho) if not np.isnan(rho) else 0.0,
        'p': float(p_val) if not np.isnan(p_val) else 1.0,
        'tau': float(tau) if not np.isnan(tau) else 0.0
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

def compute_z_score(observed_rho, null_distribution):
    """Compute z-score of observed correlation against null distribution"""
    null_mean = null_distribution['mean']
    null_std = null_distribution['std']
    if null_std > 0:
        return (observed_rho - null_mean) / null_std
    else:
        return 0.0

def main():
    print("Starting Phase 504: Adversarial-Physical-Discrimination Analysis...")
    
    # Load SFH-SGP baseline
    print("Loading SFH-SGP baseline from Phase 407...")
    sfhsgp_hierarchy = get_sfhsgp_emergence_hierarchy()
    print(f"SFH-SGP Emergence Hierarchy: {[round(x, 4) for x in sfhsgp_hierarchy]}")
    
    # Load authentic physical systems from Phase 503
    print("Loading authentic physical systems from Phase 503...")
    authentic_systems = load_phase503_authentic_systems()
    print(f"Loaded {len(authentic_systems)} authentic physical systems")
    
    # Generate adversarial pseudo-physical systems
    print("Generating adversarial pseudo-physical systems...")
    adversarial_systems = generate_adversarial_systems(authentic_systems)
    print(f"Generated {len(adversarial_systems)} adversarial systems")
    
    # Combine authentic and adversarial systems for processing
    all_systems = {**authentic_systems, **adversarial_systems}
    
    # Perform null testing (once for all systems, using same baseline)
    print("\nPerforming null hypothesis testing (1000 permutations)...")
    null_distribution = perform_null_testing(sfhsgp_hierarchy, n_permutations=1000)
    print(f"Null distribution: mean={null_distribution['mean']:.4f}, std={null_distribution['std']:.4f}")
    
    # Analyze each system (both authentic and adversarial)
    print("\nAnalyzing correspondence for authentic and adversarial systems...")
    all_systems_results = {}
    
    for system_name, system_data in all_systems.items():
        print(f"  Analyzing {system_name}...")
        correspondence = compute_correspondence(
            system_data['values'], 
            sfhsgp_hierarchy
        )
        
        # Compute z-score against null
        z_score = compute_z_score(correspondence['rho'], null_distribution)
        
        all_systems_results[system_name] = {
            'system_data': system_data,
            'correspondence': correspondence,
            'z_score': z_score,
            'null_distribution': null_distribution,
            'is_adversarial': system_data.get('is_adversarial', False),
            'original_system': system_data.get('original_system', None)
        }
    
    # Separate authentic and adversarial results
    authentic_results = {name: results for name, results in all_systems_results.items() 
                         if not results['is_adversarial']}
    adversarial_results = {name: results for name, results in all_systems_results.items() 
                           if results['is_adversarial']}
    
    # Determine significance for each system (p < 0.05)
    authentic_significant = [name for name, results in authentic_results.items() 
                            if results['correspondence']['p'] < 0.05]
    adversarial_significant = [name for name, results in adversarial_results.items() 
                              if results['correspondence']['p'] < 0.05]
    
    # Compute discrimination metrics
    n_authentic = len(authentic_systems)
    n_adversarial = len(adversarial_systems)
    
    # 1. discrimination_ratio: Mean |rho| authentic / Mean |rho| adversarial
    auth_rhos = [abs(results['correspondence']['rho']) for results in authentic_results.values()]
    adv_rhos = [abs(results['correspondence']['rho']) for results in adversarial_results.values()]
    mean_auth_rho = np.mean(auth_rhos) if auth_rhos else 0.0
    mean_adv_rho = np.mean(adv_rhos) if adv_rhos else 0.0
    discrimination_ratio = mean_auth_rho / mean_adv_rho if mean_adv_rho > 0 else float('inf')
    
    # 2. adversarial_false_positive_rate: Fraction of adversarial systems showing significant correspondence
    adversarial_false_positive_rate = len(adversarial_significant) / n_adversarial if n_adversarial > 0 else 0.0
    
    # 3. recursive_specificity_index: (Mean auth rho - Mean adv rho) / (Mean auth rho + Mean adv rho)
    if mean_auth_rho + mean_adv_rho > 0:
        recursive_specificity_index = (mean_auth_rho - mean_adv_rho) / (mean_auth_rho + mean_adv_rho)
    else:
        recursive_specificity_index = 0.0
    
    # 4. null_physical_separation: z-score separation for authentic systems (mean)
    auth_z_scores = [results['z_score'] for results in authentic_results.values()]
    mean_auth_z = np.mean(auth_z_scores) if auth_z_scores else 0.0
    
    # 5. pseudo_system_rejection_rate: 1 - adversarial_false_positive_rate
    pseudo_system_rejection_rate = 1.0 - adversarial_false_positive_rate
    
    # 6. structural_authenticity_score: Correlation between authenticity (1 for authentic, 0 for adversarial) and |rho|
    all_names = list(all_systems_results.keys())
    all_rhos = [abs(all_systems_results[name]['correspondence']['rho']) for name in all_names]
    authenticity_scores = [1.0 if not all_systems_results[name]['is_adversarial'] else 0.0 for name in all_names]
    if len(set(authenticity_scores)) > 1:  # Need both 0s and 1s for correlation
        structural_authenticity_score, _ = stats.spearmanr(authenticity_scores, all_rhos)
        structural_authenticity_score = float(structural_authenticity_score) if not np.isnan(structural_authenticity_score) else 0.0
    else:
        structural_authenticity_score = 0.0
    
    # Overall success criteria: 
    # - Authentic systems should show strong correspondence (majority significant)
    # - Adversarial systems should show weak correspondence (minority significant)
    # - Discrimination ratio should be > 1 (authentic > adversarial)
    auth_success = len(authentic_significant) >= max(1, n_authentic // 2)  # At least half authentic systems significant
    adv_success = len(adversarial_significant) < n_adversarial // 2  # Less than half adversarial systems significant
    disc_success = discrimination_ratio > 1.0  # Authentic correspondence greater than adversarial
    overall_success = bool(auth_success and adv_success and disc_success)  # Convert to Python bool for JSON
    
    # Prepare results - ensure all values are JSON serializable
    results = {
        'phase': 504,
        'seed': 504,
        'tier': 3,
        'n_authentic_systems': int(n_authentic),
        'n_adversarial_systems': int(n_adversarial),
        'n_null_permutations': int(1000),
        'sfhsgp_hierarchy': [float(v) for v in sfhsgp_hierarchy],
        'authentic_systems': {name: {
            'values': [float(v) for v in data['values']],
            'description': str(data['description']),
            'domain': str(data['domain'])
        } for name, data in authentic_systems.items()},
        'adversarial_systems': {name: {
            'values': [float(v) for v in data['values']],
            'description': str(data['description']),
            'domain': str(data['domain']),
            'original_system': str(data['original_system'])
        } for name, data in adversarial_systems.items()},
        'authentic_results': {
            name: {
                'correspondence': {
                    'rho': float(results['correspondence']['rho']),
                    'p': float(results['correspondence']['p']),
                    'tau': float(results['correspondence']['tau'])
                },
                'z_score': float(results['z_score']),
                'system_data': results['system_data']
            } for name, results in authentic_results.items()
        },
        'adversarial_results': {
            name: {
                'correspondence': {
                    'rho': float(results['correspondence']['rho']),
                    'p': float(results['correspondence']['p']),
                    'tau': float(results['correspondence']['tau'])
                },
                'z_score': float(results['z_score']),
                'system_data': results['system_data']
            } for name, results in adversarial_results.items()
        },
        'null_distribution': {
            'rho': [float(v) for v in null_distribution['rho']],
            'mean': float(null_distribution['mean']),
            'std': float(null_distribution['std'])
        },
        'discrimination_metrics': {
            'discrimination_ratio': float(discrimination_ratio),
            'adversarial_false_positive_rate': float(adversarial_false_positive_rate),
            'recursive_specificity_index': float(recursive_specificity_index),
            'null_physical_separation': float(mean_auth_z),
            'pseudo_system_rejection_rate': float(pseudo_system_rejection_rate),
            'structural_authenticity_score': float(structural_authenticity_score)
        },
        'summary': {
            'authentic_significant': int(len(authentic_significant)),
            'authentic_total': int(n_authentic),
            'adversarial_significant': int(len(adversarial_significant)),
            'adversarial_total': int(n_adversarial),
            'discrimination_ratio': float(discrimination_ratio),
            'recursive_specificity_index': float(recursive_specificity_index),
            'authentic_success': bool(auth_success),
            'adversarial_success': bool(adv_success),
            'discrimination_success': bool(disc_success),
            'overall_success': bool(overall_success),
            'verdict': 'ADVERSARIAL-PHYSICAL-DISCRIMINATION-SUCCESS' if overall_success else 'ADVERSARIAL-PHYSICAL-DISCRIMINATION-FAILURE'
        }
    }
    
    # Save results
    os.makedirs('phases/phase504', exist_ok=True)
    with open('phases/phase504/phase504_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Also save a CSV summary for easy viewing
    summary_rows = []
    # Add authentic systems
    for system_name, results in authentic_results.items():
        summary_rows.append({
            'system': system_name,
            'type': 'authentic',
            'domain': str(results['system_data']['domain']),
            'description': str(results['system_data']['description']),
            'spearman_rho': float(results['correspondence']['rho']),
            'spearman_p': float(results['correspondence']['p']),
            'kendall_tau': float(results['correspondence']['tau']),
            'z_score': float(results['z_score']),
            'significant': bool(results['correspondence']['p'] < 0.05)
        })
    # Add adversarial systems
    for system_name, results in adversarial_results.items():
        summary_rows.append({
            'system': system_name,
            'type': 'adversarial',
            'domain': str(results['system_data']['domain']),
            'description': str(results['system_data']['description']),
            'spearman_rho': float(results['correspondence']['rho']),
            'spearman_p': float(results['correspondence']['p']),
            'kendall_tau': float(results['correspondence']['tau']),
            'z_score': float(results['z_score']),
            'significant': bool(results['correspondence']['p'] < 0.05)
        })
    
    df = pd.DataFrame(summary_rows)
    df.to_csv('phases/phase504/phase504_adversarial_summary.csv', index=False)
    
    # Print summary
    print("\n" + "="*70)
    print("PHASE 504 RESULTS SUMMARY")
    print("="*70)
    print(f"SFH-SGP Reference Hierarchy: {[round(x, 4) for x in sfhsgp_hierarchy]}")
    print(f"Authentic Systems Analyzed: {n_authentic}")
    print(f"Adversarial Systems Analyzed: {n_adversarial}")
    print(f"Authentic Systems Significant: {len(authentic_significant)}/{n_authentic} ({len(authentic_significant)/n_authentic*100:.1f}%)")
    print(f"Adversarial Systems Significant: {len(adversarial_significant)}/{n_adversarial} ({len(adversarial_significant)/n_adversarial*100:.1f}%)")
    print(f"Discrimination Ratio (|rho|_auth/|rho|_adv): {discrimination_ratio:.2f}")
    print(f"Recursive Specificity Index: {recursive_specificity_index:.2f}")
    print(f"Null Physical Separation (mean z-score): {mean_auth_z:.2f}")
    print(f"Pseudo System Rejection Rate: {pseudo_system_rejection_rate:.2f}")
    print(f"Structural Authenticity Score: {structural_authenticity_score:.2f}")
    print(f"Authentic Success (≥50% significant): {auth_success}")
    print(f"Adversarial Success (<50% significant): {adv_success}")
    print(f"Discrimination Success (ratio > 1.0): {disc_success}")
    print(f"Overall Success: {overall_success}")
    print(f"Verdict: {results['summary']['verdict']}")
    
    print("\nTop 5 Authentic Systems by Correspondence Strength:")
    sorted_auth = sorted(
        authentic_results.items(),
        key=lambda x: abs(x[1]['correspondence']['rho']),
        reverse=True
    )
    for i, (system_name, results) in enumerate(sorted_auth[:5]):
        corr = results['correspondence']
        print(f"  {i+1}. {system_name}")
        print(f"     ρ = {corr['rho']:.4f}, p = {corr['p']:.4f}, τ = {corr['tau']:.4f}, z = {results['z_score']:.2f}")
    
    print("\nTop 5 Adversarial Systems by Correspondence Strength:")
    sorted_adv = sorted(
        adversarial_results.items(),
        key=lambda x: abs(x[1]['correspondence']['rho']),
        reverse=True
    )
    for i, (system_name, results) in enumerate(sorted_adv[:5]):
        corr = results['correspondence']
        print(f"  {i+1}. {system_name}")
        print(f"     ρ = {corr['rho']:.4f}, p = {corr['p']:.4f}, τ = {corr['tau']:.4f}, z = {results['z_score']:.2f}")
    
    print(f"\nResults saved to:")
    print(f"  phases/phase504/phase504_results.json")
    print(f"  phases/phase504/phase504_adversarial_summary.csv")
    
    return results

if __name__ == "__main__":
    main()