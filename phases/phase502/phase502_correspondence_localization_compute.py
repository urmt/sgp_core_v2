#!/usr/bin/env python3
"""
Phase 502: Correspondence-Localization Computation
Determines WHICH specific organizational structures produce correspondence 
between SFH-SGP and independent mathematical systems.
"""

import json
import numpy as np
import itertools
from scipy import stats
import pandas as pd
import os

# Set seed for reproducibility
np.random.seed(502)

def load_phase501_results():
    """Load the Phase 501 results for the mathematical systems"""
    with open('phases/phase501/phase501_results.json', 'r') as f:
        return json.load(f)

def load_phase407_baseline():
    """Load the SFH-SGP baseline from Phase 407"""
    with open('phases/phase407/phase407_predictive_results.json', 'r') as f:
        return json.load(f)

def extract_sfhsgp_components():
    """Extract the specific SFH-SGP organizational components for analysis"""
    phase407 = load_phase407_baseline()
    
    # Component 1: Emergence hierarchy (from ablation predictions)
    baseline = phase407['ablation_predictions_saved']['FullPABaseline']
    emergence_hierarchy = [
        baseline['P-A-N'],    # 0.9285 - most emergent
        baseline['P-A'],      # 0.9283
        baseline['Projection'], # 0.9279
        baseline['P-N'],      # 0.9244
        baseline['Antisymmetry'], # 0.9225
        baseline['Neutral'],  # 0.9031
        baseline['A-N']       # 0.8864 - least emergent
    ]
    
    # Component 2: Operator weights (P, A, N)
    operator_weights = phase407['predictor']['operator_weights']
    operator_values = [operator_weights['P'], operator_weights['A'], operator_weights['N']]
    
    # Component 3: Sector bases (topological features)
    sector_bases = phase407['predictor']['sector_bases']
    sector_values = [
        sector_bases['P-A-N'],
        sector_bases['P-A'],
        sector_bases['Projection'],
        sector_bases['P-N'],
        sector_bases['Antisymmetry'],
        sector_bases['Neutral'],
        sector_bases['A-N']
    ]
    
    # Component 4: Recursive depth implications (from novel predictions)
    # Using P-A-N values at different depths as proxy for depth localization
    novel_pred = phase407['novel_predictions_saved']['P_Enhanced_NoAN']
    depth_values = [
        novel_pred['P-A-N_d1'],          # Surface level
        novel_pred['P-A-N_d1000'],       # Intermediate
        novel_pred['P-A-N_d67108864']    # Deep recursive
    ]
    # Extend to 7 points by interpolation
    depth_hierarchy = np.linspace(depth_values[0], depth_values[2], 7).tolist()
    
    # Component 5: Attractor signatures (derived from dynamics)
    # Using the range and variation in emergence values as proxy
    attritor_range = max(emergence_hierarchy) - min(emergence_hierarchy)
    attritor_values = [emergence_hierarchy[i] + np.random.normal(0, attritor_range*0.01) 
                       for i in range(7)]  # Small perturbations for diversity
    
    # Component 6: Information channels (using operator interactions)
    # P-A, P-N, A-N combinations as information pathways
    info_channels = [
        baseline['P-A'],    # P-A channel
        baseline['P-N'],    # P-N channel
        baseline['A-N'],    # A-N channel
        baseline['P-A-N'],  # Full channel
        baseline['Projection'], # Projection channel
        (baseline['P-A'] + baseline['P-N'])/2, # Mixed PN
        (baseline['P-A'] + baseline['A-N'])/2  # Mixed AN
    ]
    
    # Component 7: Algebraic constraints (fundamental relations)
    # Using ratios and differences as invariant constraints
    alg_constraints = [
        baseline['P-A-N']/(baseline['P-A'] + 0.001),  # P dominance ratio
        baseline['P-A']/(baseline['A-N'] + 0.001),    # P-A vs A-N
        baseline['Antisymmetry']/baseline['Neutral'], # Anti-sym vs neutral
        baseline['Projection'] - baseline['A-N'],     # Projection gap
        baseline['P-N'] - baseline['A-N'],            # PN-AN difference
        (baseline['P-A'] + baseline['P-N'])/2,      # Average PN
        baseline['P-A-N'] - baseline['Projection']  # Full-projection diff
    ]
    
    return {
        'emergence_hierarchy': emergence_hierarchy,
        'operator_weights': operator_values,
        'sector_bases': sector_values,
        'depth_hierarchy': depth_hierarchy,
        'attractor_signatures': attritor_values,
        'information_channels': info_channels,
        'algebraic_constraints': alg_constraints
    }

def compute_localized_correspondence(sfhsgp_component, system_emergence_values):
    """
    Compute correspondence between a specific SFH-SGP component and a mathematical system's emergence values
    Uses Spearman correlation for ordinal relationship
    """
    # Ensure same length by truncating or extending
    min_len = min(len(sfhsgp_component), len(system_emergence_values))
    sfhsgp_trunc = sfhsgp_component[:min_len]
    system_trunc = system_emergence_values[:min_len]
    
    if len(sfhsgp_trunc) < 2:
        return {'rho': 0.0, 'p': 1.0, 'tau': 0.0}
    
    # Compute Spearman correlation
    rho, p_val = stats.spearmanr(sfhsgp_trunc, system_trunc)
    
    # Compute Kendall tau
    tau, _ = stats.kendalltau(sfhsgp_trunc, system_trunc)
    
    return {
        'rho': float(rho) if not np.isnan(rho) else 0.0,
        'p': float(p_val) if not np.isnan(p_val) else 1.0,
        'tau': float(tau) if not np.isnan(tau) else 0.0
    }

def analyze_system_localization(system_name, system_data, sfhsgp_components):
    """
    Analyze localization of correspondence for a specific mathematical system
    """
    emergence_values = system_data['emergence_values']
    
    localization_results = {}
    
    # Test each SFH-SGP component
    for component_name, component_values in sfhsgp_components.items():
        corr_result = compute_localized_correspondence(component_values, emergence_values)
        localization_results[component_name] = corr_result
    
    return localization_results

def compute_localization_metrics(all_systems_localization):
    """
    Compute the critical metrics for Phase 502 from the localization analysis
    """
    # Initialize metrics
    metrics = {
        'localized_correspondence_density': {},
        'invariant_overlap_score': {},
        'operator_alignment_index': {},
        'recursive_depth_similarity': {},
        'mismatch_entropy': {},
        'structural_transfer_ratio': {}
    }
    
    # Get component names
    component_names = list(next(iter(all_systems_localization.values())).keys())
    
    # 1. Localized correspondence density (mean rho across systems for each component)
    for component in component_names:
        rhos = []
        for system_name, localization in all_systems_localization.items():
            rhos.append(localization[component]['rho'])
        metrics['localized_correspondence_density'][component] = {
            'mean': float(np.mean(rhos)),
            'std': float(np.std(rhos)),
            'median': float(np.median(rhos))
        }
    
    # 2. Invariant overlap score (proportion of systems with significant correspondence per component)
    for component in component_names:
        significant_count = 0
        total_systems = len(all_systems_localization)
        for system_name, localization in all_systems_localization.items():
            if localization[component]['p'] < 0.05:  # Significant at p < 0.05
                significant_count += 1
        metrics['invariant_overlap_score'][component] = {
            'proportion': float(significant_count / total_systems),
            'count': significant_count,
            'total': total_systems
        }
    
    # 3. Operator alignment index (specific to operator_weights component)
    if 'operator_weights' in component_names:
        op_rhos = [all_systems_localization[sys]['operator_weights']['rho'] 
                   for sys in all_systems_localization.keys()]
        metrics['operator_alignment_index'] = {
            'mean_rho': float(np.mean(op_rhos)),
            'std_rho': float(np.std(op_rhos)),
            'consistency': 1.0 - float(np.std(op_rhos)) if np.std(op_rhos) < 1.0 else 0.0
        }
    
    # 4. Recursive depth similarity (specific to depth_hierarchy component)
    if 'depth_hierarchy' in component_names:
        depth_rhos = [all_systems_localization[sys]['depth_hierarchy']['rho'] 
                      for sys in all_systems_localization.keys()]
        metrics['recursive_depth_similarity'] = {
            'mean_rho': float(np.mean(depth_rhos)),
            'std_rho': float(np.std(depth_rhos)),
            'depth_profile_correlation': float(np.corrcoef(
                [all_systems_localization[sys]['depth_hierarchy']['rho'] 
                 for sys in all_systems_localization.keys()],
                list(range(len(depth_rhos)))
            )[0,1]) if len(depth_rhos) > 1 else 0.0
        }
    
    # 5. Mismatch entropy (uncertainty in non-corresponding regions)
    for component in component_names:
        rhos = [abs(all_systems_localization[sys][component]['rho']) 
                for sys in all_systems_localization.keys()]
        # Convert to probabilities and compute entropy
        probs = np.array(rhos) / (np.sum(rhos) + 1e-10)  # Avoid division by zero
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        metrics['mismatch_entropy'][component] = {
            'entropy': float(entropy),
            'normalized_entropy': float(entropy / np.log(len(rhos))) if len(rhos) > 1 else 0.0
        }
    
    # 6. Structural transfer ratio (fraction of SFH-SGP structure that transfers to each system)
    for system_name in all_systems_localization.keys():
        significant_components = 0
        total_components = len(component_names)
        for component in component_names:
            if all_systems_localization[system_name][component]['p'] < 0.05:
                significant_components += 1
        metrics['structural_transfer_ratio'][system_name] = {
            'proportion': float(significant_components / total_components),
            'count': significant_components,
            'total': total_components
        }
    
    return metrics

def perform_null_testing(sfhsgp_components, n_permutations=1000):
    """
    Perform null hypothesis testing by permuting the emergence values
    """
    null_distributions = {}
    
    # Get one system's emergence values to permute (using first system as template)
    phase501_results = load_phase501_results()
    first_system = list(phase501_results['systems'].values())[0]
    template_values = first_system['emergence_values']
    
    for component_name, component_values in sfhsgp_components.items():
        null_rhos = []
        min_len = min(len(component_values), len(template_values))
        comp_trunc = component_values[:min_len]
        template_trunc = template_values[:min_len]
        
        if len(comp_trunc) < 2:
            null_distributions[component_name] = {'rho': []}
            continue
            
        for _ in range(n_permutations):
            # Permute the template values
            permuted = np.random.permutation(template_trunc)
            # Compute correlation with SFH-SGP component
            rho, _ = stats.spearmanr(comp_trunc, permuted)
            if not np.isnan(rho):
                null_rhos.append(float(rho))
        
        null_distributions[component_name] = {
            'rho': null_rhos,
            'mean': float(np.mean(null_rhos)) if null_rhos else 0.0,
            'std': float(np.std(null_rhos)) if null_rhos else 0.0
        }
    
    return null_distributions

def compute_z_scores(localization_results, null_distributions):
    """
    Compute z-scores for localization results against null distributions
    """
    z_scores = {}
    
    for system_name, localization in localization_results.items():
        z_scores[system_name] = {}
        for component_name, component_result in localization.items():
            if component_name in null_distributions:
                null_mean = null_distributions[component_name]['mean']
                null_std = null_distributions[component_name]['std']
                if null_std > 0:
                    z_score = (component_result['rho'] - null_mean) / null_std
                else:
                    z_score = 0.0
                z_scores[system_name][component_name] = {
                    'z_score': float(z_score),
                    'null_mean': null_mean,
                    'null_std': null_std
                }
    
    return z_scores

def main():
    print("Starting Phase 502: Correspondence-Localization Analysis...")
    
    # Load data
    print("Loading Phase 501 results...")
    phase501_results = load_phase501_results()
    
    print("Loading Phase 407 baseline...")
    phase407_baseline = load_phase407_baseline()
    
    # Extract SFH-SGP components
    print("Extracting SFH-SGP organizational components...")
    sfhsgp_components = extract_sfhsgp_components()
    
    # Show what we extracted
    print("\nSFH-SGP Components Extracted:")
    for name, values in sfhsgp_components.items():
        print(f"  {name}: {len(values)} values")
        print(f"    Range: [{min(values):.4f}, {max(values):.4f}]")
    
    # Analyze each mathematical system
    print("\nAnalyzing localization for each mathematical system...")
    all_systems_localization = {}
    
    for system_name, system_data in phase501_results['systems'].items():
        print(f"  Analyzing {system_name}...")
        localization = analyze_system_localization(system_name, system_data, sfhsgp_components)
        all_systems_localization[system_name] = localization
    
    # Perform null testing
    print("\nPerforming null hypothesis testing (1000 permutations)...")
    null_distributions = perform_null_testing(sfhsgp_components, n_permutations=1000)
    
    # Compute z-scores
    print("Computing z-scores against null distributions...")
    z_scores = compute_z_scores(all_systems_localization, null_distributions)
    
    # Compute localization metrics
    print("Computing localization metrics...")
    localization_metrics = compute_localization_metrics(all_systems_localization)
    
    # Determine significance for each component
    component_significance = {}
    for component in sfhsgp_components.keys():
        # Count how many systems show significant correspondence (p < 0.05) for this component
        sig_count = 0
        total_systems = len(all_systems_localization)
        for system_name, localization in all_systems_localization.items():
            if localization[component]['p'] < 0.05:
                sig_count += 1
        
        component_significance[component] = {
            'significant_systems': sig_count,
            'total_systems': total_systems,
            'proportion': sig_count / total_systems if total_systems > 0 else 0.0,
            'is_significant': sig_count >= 2  # At least 2/8 systems for component significance
        }
    
    # Overall success criteria: at least 4/6 metrics show significant localization
    # We'll use the invariant overlap score as our primary metric
    significant_components = sum(1 for comp in component_significance.values() 
                                if comp['is_significant'])
    total_components = len(component_significance)
    
    success = significant_components >= 4  # At least 4/7 components show localization
    
    # Prepare results
    results = {
        'phase': 502,
        'seed': 502,
        'tier': 3,
        'n_mathematical_systems': len(phase501_results['systems']),
        'n_sfhsgp_components': len(sfhsgp_components),
        'n_null_permutations': 1000,
        'sfhsgp_components': {name: [float(v) for v in vals] 
                               for name, vals in sfhsgp_components.items()},
        'systems_localization': all_systems_localization,
        'null_distributions': null_distributions,
        'z_scores': z_scores,
        'localization_metrics': localization_metrics,
        'component_significance': component_significance,
        'summary': {
            'significant_components': significant_components,
            'total_components': total_components,
            'localization_success': success,
            'verdict': 'CORRESPONDENCE-LOCALIZATION-BOUNDED' if success else 'NO-LOCALIZATION-DETECTED'
        }
    }
    
    # Save results
    os.makedirs('phases/phase502', exist_ok=True)
    with open('phases/phase502/phase502_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Also save a CSV summary for easy viewing
    summary_rows = []
    for system_name, localization in all_systems_localization.items():
        for component_name, component_result in localization.items():
            summary_rows.append({
                'system': system_name,
                'component': component_name,
                'spearman_rho': component_result['rho'],
                'spearman_p': component_result['p'],
                'kendall_tau': component_result['tau'],
                'significant': component_result['p'] < 0.05
            })
    
    df = pd.DataFrame(summary_rows)
    df.to_csv('phases/phase502/phase502_localization_summary.csv', index=False)
    
    # Print summary
    print("\n" + "="*60)
    print("PHASE 502 RESULTS SUMMARY")
    print("="*60)
    print(f"SFH-SGP Components Analyzed: {total_components}")
    print(f"Components with Significant Localization: {significant_components}")
    print(f"Localization Success: {success}")
    print(f"Verdict: {results['summary']['verdict']}")
    
    print("\nComponent Significance Breakdown:")
    for component_name, sig_info in component_significance.items():
        status = "SIGNIFICANT" if sig_info['is_significant'] else "NOT SIGNIFICANT"
        print(f"  {component_name}: {sig_info['significant_systems']}/{sig_info['total_systems']} systems "
              f"({sig_info['proportion']*100:.1f}%) - {status}")
    
    print("\nLocalization Metrics Summary:")
    for metric_name, metric_values in localization_metrics.items():
        if isinstance(metric_values, dict) and 'mean' in str(metric_values):
            print(f"  {metric_name}: {metric_values}")
        elif isinstance(metric_values, dict):
            # For nested dicts, show a summary
            print(f"  {metric_name}: {len(metric_values)} components/systems analyzed")
    
    print(f"\nResults saved to:")
    print(f"  phases/phase502/phase502_results.json")
    print(f"  phases/phase502/phase502_localization_summary.csv")
    
    return results

if __name__ == "__main__":
    main()