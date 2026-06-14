#!/usr/bin/env python3
"""
Phase 505: Directional-Recursive-Discrimination Computation
Repairs the correspondence framework by distinguishing:
true recursive organizational propagation
FROM
mere monotonic structural ordering.
"""

import json
import numpy as np
import itertools
from scipy import stats
import pandas as pd
import os

# Set seed for reproducibility
np.random.seed(505)

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
    Generate adversarial pseudo-physical systems for Phase 505.
    These systems are designed to test the new directional recursive metrics:
    - monotonic fake hierarchies
    - order-preserving shuffles  
    - mirrored recursion
    - static-scale ordering
    - synthetic directional inversion
    - pseudo-depth generators
    - recursive decoupling systems
    """
    adversarial_systems = {}
    
    for system_name, system_data in authentic_systems.items():
        original_values = system_data['values']
        description = system_data['description']
        domain = system_data['domain']
        
        # Generate 7 different types of adversarial systems as specified in framework
        min_len = min(len(original_values), 7)  # Match SFH-SGP hierarchy length
        orig_trunc = original_values[:min_len]
        
        # 1. Monotonic fake hierarchies - perfectly ordered but no recursive meaning
        if len(orig_trunc) >= 2:
            mono_fake = np.linspace(min(orig_trunc), max(orig_trunc), len(orig_trunc))
        else:
            mono_fake = orig_trunc
            
        # 2. Order-preserving shuffles - shuffle but maintain relative ordering through sorting indices
        if len(orig_trunc) >= 3:
            indices = list(range(len(orig_trunc)))
            np.random.shuffle(indices)
            order_preserve = [orig_trunc[i] for i in sorted(indices)]  # This actually sorts, let me fix
            # Correct approach: apply permutation to values
            perm_indices = np.random.permutation(len(orig_trunc))
            order_preserve = [orig_trunc[i] for i in perm_indices]
        else:
            order_preserve = orig_trunc
            
        # 3. Mirrored recursion - reverse the pattern
        mirrored = list(reversed(orig_trunc))
        
        # 4. Static-scale ordering - same value at all scales (no hierarchical progression)
        static_scale = [np.mean(orig_trunc)] * len(orig_trunc)
        
        # 5. Synthetic directional inversion - invert the direction relative to mean
        mean_val = np.mean(orig_trunc)
        synth_invert = [2*mean_val - v for v in orig_trunc]
        # Ensure bounds [0,1]
        synth_invert = [max(0, min(1, v)) for v in synth_invert]
        
        # 6. Pseudo-depth generators - fake depth with repeating pattern
        if len(orig_trunc) >= 3:
            pseudo_depth = [orig_trunc[0], orig_trunc[len(orig_trunc)//2], orig_trunc[-1]] * (len(orig_trunc)//3 + 1)
            pseudo_depth = pseudo_depth[:len(orig_trunc)]
        else:
            pseudo_depth = orig_trunc
            
        # 7. Recursive decoupling systems - break relationships between levels
        if len(orig_trunc) >= 4:
            # Decouple by shuffling adjacent pairs
            decoupled = orig_trunc.copy()
            for i in range(0, len(decoupled)-1, 2):
                if i+1 < len(decoupled):
                    decoupled[i], decoupled[i+1] = decoupled[i+1], decoupled[i]
        else:
            decoupled = orig_trunc
            
        # Store all adversarial variants
        adversarial_types = [
            ('MonotonicFake', mono_fake),
            ('OrderPreserve', order_preserve),
            ('MirroredRecursion', mirrored),
            ('StaticScale', static_scale),
            ('SyntheticInvert', synth_invert),
            ('PseudoDepth', pseudo_depth),
            ('RecursiveDecouple', decoupled)
        ]
        
        for adv_type, adv_values in adversarial_types:
            adversarial_systems[f"{system_name}_{adv_type}_Adversarial"] = {
                'values': [float(v) for v in adv_values],
                'description': f"{adv_type} adversarial version of {description}",
                'domain': domain,
                'is_adversarial': True,
                'original_system': system_name,
                'adversarial_type': adv_type
            }
     
    return adversarial_systems

def compute_spearman_correlation(physical_values, sfhsgp_hierarchy):
    """
    Compute standard Spearman correlation (original metric)
    """
    min_len = min(len(physical_values), len(sfhsgp_hierarchy))
    phys_trunc = physical_values[:min_len]
    sfhsgp_trunc = sfhsgp_hierarchy[:min_len]
    
    if len(phys_trunc) < 2:
        return {'rho': 0.0, 'p': 1.0, 'tau': 0.0}
    
    rho, p_val = stats.spearmanr(phys_trunc, sfhsgp_trunc)
    tau, _ = stats.kendalltau(phys_trunc, sfhsgp_trunc)
    
    return {
        'rho': float(rho) if not np.isnan(rho) else 0.0,
        'p': float(p_val) if not np.isnan(p_val) else 1.0,
        'tau': float(tau) if not np.isnan(tau) else 0.0
    }

def compute_directional_recursive_gradient(physical_values, sfhsgp_hierarchy):
    """
    Compute directional recursive gradient metric.
    Measures not just correlation but direction-specific recursive progression.
    """
    min_len = min(len(physical_values), len(sfhsgp_hierarchy))
    phys_trunc = np.array(physical_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])
    
    if len(phys_trunc) < 3:
        return {'value': 0.0, 'sign': 0}
    
    # Compute gradients (differences between consecutive levels)
    phys_grad = np.diff(phys_trunc)
    sfhsgp_grad = np.diff(sfhsgp_trunc)
    
    # Check if gradients have same sign (same direction of change)
    same_sign = np.sign(phys_grad) == np.sign(sfhsgp_grad)
    
    # Directional recursive gradient: proportion of same-sign gradients weighted by magnitude agreement
    if np.std(phys_grad) > 0 and np.std(sfhsgp_grad) > 0:
        grad_correlation = np.corrcoef(phys_grad, sfhsgp_grad)[0,1]
        if np.isnan(grad_correlation):
            grad_correlation = 0.0
        # Combine sign agreement with gradient correlation
        directional_score = np.mean(same_sign) * (1 + grad_correlation) / 2
    else:
        # Fallback to sign agreement only
        directional_score = np.mean(same_sign)
    
    # Determine overall sign of recursion (positive = same direction as SFH-SGP)
    overall_sign = 1 if np.mean(phys_grad * sfhsgp_grad) > 0 else -1
    
    return {
        'value': float(directional_score),
        'sign': int(overall_sign)
    }

def compute_propagation_asymmetry_index(physical_values, sfhsgp_hierarchy):
    """
    Compute propagation asymmetry index.
    Measures asymmetry in propagation patterns between systems.
    """
    min_len = min(len(physical_values), len(sfhsgp_hierarchy))
    phys_trunc = np.array(physical_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])
    
    if len(phys_trunc) < 3:
        return {'value': 0.0}
    
    # Compute second-order differences (acceleration/deceleration of propagation)
    phys_second = np.diff(np.diff(phys_trunc))
    sfhsgp_second = np.diff(np.diff(sfhsgp_trunc))
    
    if len(phys_second) == 0:
        return {'value': 0.0}
    
    # Asymmetry index: difference in propagation dynamics
    asym_index = np.mean(np.abs(phys_second - sfhsgp_second))
    
    # Normalize by the scale of sfhsgp second differences
    sfhsgp_scale = np.mean(np.abs(sfhsgp_second)) + 1e-10
    normalized_asym = asym_index / sfhsgp_scale
    
    return {
        'value': float(min(normalized_asym, 1.0))  # Cap at 1.0
    }

def compute_recursive_dependency_score(physical_values, sfhsgp_hierarchy):
    """
    Compute recursive dependency score.
    Measures dependency strength across recursive levels using mutual information approximation.
    """
    min_len = min(len(physical_values), len(sfhsgp_hierarchy))
    phys_trunc = np.array(physical_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])
    
    if len(phys_trunc) < 3:
        return {'value': 0.0}
    
    # Discretize values into bins for dependency estimation
    n_bins = min(5, len(phys_trunc))
    try:
        phys_binned = pd.cut(phys_trunc, bins=n_bins, labels=False)
        sfhsgp_binned = pd.cut(sfhsgp_trunc, bins=n_bins, labels=False)
    except:
        # Fallback if binning fails
        return {'value': 0.0}
    
    # Remove any NaN values that might have occurred
    valid_mask = ~(pd.isna(phys_binned) | pd.isna(sfhsgp_binned))
    if np.sum(valid_mask) < 2:
        return {'value': 0.0}
        
    phys_clean = phys_binned[valid_mask]
    sfhsgp_clean = sfhsgp_binned[valid_mask]
    
    # Calculate mutual information approximation
    # MI(X;Y) = H(X) + H(Y) - H(X,Y)
    def entropy(labels):
        if len(labels) == 0:
            return 0.0
        counts = np.bincount(labels)
        probs = counts[counts > 0] / len(labels)
        return -np.sum(probs * np.log(probs + 1e-10))
    
    def joint_entropy(x_labels, y_labels):
        if len(x_labels) == 0:
            return 0.0
        # Create joint pairs
        pairs = list(zip(x_labels, y_labels))
        # Convert to flat indices for bincount
        max_x = np.max(x_labels) if len(x_labels) > 0 else 0
        max_y = np.max(y_labels) if len(y_labels) > 0 else 0
        flat_indices = x_labels * (max_y + 1) + y_labels
        counts = np.bincount(flat_indices)
        probs = counts[counts > 0] / len(flat_indices)
        return -np.sum(probs * np.log(probs + 1e-10))
    
    h_phys = entropy(phys_clean)
    h_sfhsgp = entropy(sfhsgp_clean)
    h_joint = joint_entropy(phys_clean, sfhsgp_clean)
    
    mi = h_phys + h_sfhsgp - h_joint
    # Ensure non-negative
    mi = max(0.0, mi)
    
    # Normalize by joint entropy
    if h_joint > 0:
        normalized_mi = mi / h_joint
    else:
        normalized_mi = 0.0
        
    return {
        'value': float(min(normalized_mi, 1.0))
    }

def compute_depth_coupling_coherence(physical_values, sfhsgp_hierarchy):
    """
    Compute depth coupling coherence.
    Assesses coherence across different depth levels in the hierarchy.
    """
    min_len = min(len(physical_values), len(sfhsgp_hierarchy))
    phys_trunc = np.array(physical_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])
    
    if len(phys_trunc) < 4:
        return {'value': 0.0}
    
    # Split into depth layers: shallow, middle, deep
    n_third = len(phys_trunc) // 3
    if n_third < 1:
        n_third = 1
    
    shallow_phys = phys_trunc[:n_third]
    middle_phys = phys_trunc[n_third:2*n_third] 
    deep_phys = phys_trunc[2*n_third:3*n_third] if 3*n_third <= len(phys_trunc) else phys_trunc[2*n_third:]
    
    shallow_sfhsgp = sfhsgp_trunc[:n_third]
    middle_sfhsgp = sfhsgp_trunc[n_third:2*n_third]
    deep_sfhsgp = sfhsgp_trunc[2*n_third:3*n_third] if 3*n_third <= len(sfhsgp_trunc) else sfhsgp_trunc[2*n_third:]
    
    # Compute coherence within each layer (internal consistency)
    def layer_coherence(layer):
        if len(layer) < 2:
            return 0.0
        # Coherence as 1 - normalized variance
        if np.mean(np.abs(layer)) > 0:
            return 1.0 - (np.std(layer) / (np.mean(np.abs(layer)) + 1e-10))
        else:
            return 1.0 if np.std(layer) == 0 else 0.0
    
    coh_shallow = layer_coherence(shallow_phys) * layer_coherence(shallow_sfhsgp)
    coh_middle = layer_coherence(middle_phys) * layer_coherence(middle_sfhsgp)
    coh_deep = layer_coherence(deep_phys) * layer_coherence(deep_sfhsgp)
    
    # Cross-layer coupling: correlation between layer averages
    layer_avgs_phys = [np.mean(shallow_phys) if len(shallow_phys) > 0 else 0,
                      np.mean(middle_phys) if len(middle_phys) > 0 else 0,
                      np.mean(deep_phys) if len(deep_phys) > 0 else 0]
    layer_avgs_sfhsgp = [np.mean(shallow_sfhsgp) if len(shallow_sfhsgp) > 0 else 0,
                        np.mean(middle_sfhsgp) if len(middle_sfhsgp) > 0 else 0,
                        np.mean(deep_sfhsgp) if len(deep_sfhsgp) > 0 else 0]
    
    if len(layer_avgs_phys) >= 2 and len(layer_avgs_sfhsgp) >= 2:
        # Remove any pairs where one is zero to avoid misleading correlations
        valid_pairs = [(p, s) for p, s in zip(layer_avgs_phys, layer_avgs_sfhsgp) 
                      if abs(p) > 1e-10 or abs(s) > 1e-10]
        if len(valid_pairs) >= 2:
            phys_vals, sfhsgp_vals = zip(*valid_pairs)
            if np.std(phys_vals) > 0 and np.std(sfhsgp_vals) > 0:
                coupling_corr = np.corrcoef(phys_vals, sfhsgp_vals)[0,1]
                if np.isnan(coupling_corr):
                    coupling_corr = 0.0
            else:
                coupling_corr = 0.0
        else:
            coupling_corr = 0.0
    else:
        coupling_corr = 0.0
    
    # Overall depth coupling coherence
    internal_coherence = np.mean([coh_shallow, coh_middle, coh_deep])
    depth_coupling = (internal_coherence + abs(coupling_corr)) / 2
    
    return {
        'value': float(max(0.0, min(depth_coupling, 1.0)))
    }

def compute_causal_order_retention(physical_values, sfhsgp_hierarchy):
    """
    Compute causal order retention.
    Evaluates preservation of causal ordering in the system.
    """
    min_len = min(len(physical_values), len(sfhsgp_hierarchy))
    phys_trunc = np.array(physical_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])
    
    if len(phys_trunc) < 3:
        return {'value': 0.0}
    
    # Causal order: for a recursive system, early changes should propagate to later changes
    # Measure how well the temporal/ordering structure is preserved
    
    # Compute pairwise order relations
    def order_consistency(seq):
        if len(seq) < 2:
            return 0.0
        consistent_pairs = 0
        total_pairs = 0
        for i in range(len(seq)):
            for j in range(i+1, len(seq)):
                total_pairs += 1
                # Check if order is preserved (both increasing or both decreasing)
                if (seq[j] - seq[i]) * (seq[j] - seq[i]) >= 0:  # Always true, let me fix
                    # Actually check directional consistency
                    diff_ij = seq[j] - seq[i]
                    # For causal order, we expect consistent propagation direction
                    consistent_pairs += 1  # Simplified for now
        return consistent_pairs / max(total_pairs, 1)
    
    # Better approach: compare rank order correlations
    phys_ranks = stats.rankdata(phys_trunc)
    sfhsgp_ranks = stats.rankdata(sfhsgp_trunc)
    
    # Causal order retention: how well rank orders match
    if np.std(phys_ranks) > 0 and np.std(sfhsgp_ranks) > 0:
        rank_corr = np.corrcoef(phys_ranks, sfhsgp_ranks)[0,1]
        if np.isnan(rank_corr):
            rank_corr = 0.0
        causal_score = abs(rank_corr)  # Use absolute value for retention magnitude
    else:
        causal_score = 0.0
    
    return {
        'value': float(max(0.0, min(causal_score, 1.0)))
    }

def compute_recursive_transfer_entropy(physical_values, sfhsgp_hierarchy):
    """
    Compute recursive transfer entropy.
    Measures information transfer in recursive systems using a simplified approach.
    """
    min_len = min(len(physical_values), len(sfhsgp_hierarchy))
    phys_trunc = np.array(physical_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])
    
    if len(phys_trunc) < 3:
        return {'value': 0.0}
    
    # Simplified transfer entropy: predict future values from past values
    # TE(X->Y) = I(Y_future; X_past | Y_past)
    
    # For simplicity, we'll use a lag-1 approximation
    if len(phys_trunc) < 3:
        return {'value': 0.0}
    
    # Past and future values
    phys_past = phys_trunc[:-1]  # All but last
    phys_future = phys_trunc[1:]   # All but first
    sfhsgp_past = sfhsgp_trunc[:-1]
    sfhsgp_future = sfhsgp_trunc[1:]
    
    # Compute how much knowing past of one system improves prediction of future of another
    # Transfer entropy from phys to sfhsgp: TE(phys -> sfhsgp)
    # TE = I(sfhsgp_future; phys_past | sfhsgp_past)
    
    # Discretize for simplicity
    n_bins = min(4, len(phys_trunc)//2)
    if n_bins < 2:
        n_bins = 2
    
    try:
        phys_past_disc = pd.cut(phys_past, bins=n_bins, labels=False)
        phys_future_disc = pd.cut(phys_future, bins=n_bins, labels=False)
        sfhsgp_past_disc = pd.cut(sfhsgp_past, bins=n_bins, labels=False)
        sfhsgp_future_disc = pd.cut(sfhsgp_future, bins=n_bins, labels=False)
    except:
        return {'value': 0.0}
    
    # Remove NaN values
    valid_mask = ~(pd.isna(phys_past_disc) | pd.isna(phys_future_disc) | 
                   pd.isna(sfhsgp_past_disc) | pd.isna(sfhsgp_future_disc))
    if np.sum(valid_mask) < 2:
        return {'value': 0.0}
    
    phys_past_clean = phys_past_disc[valid_mask]
    phys_future_clean = phys_future_disc[valid_mask]
    sfhsgp_past_clean = sfhsgp_past_disc[valid_mask]
    sfhsgp_future_clean = sfhsgp_future_disc[valid_mask]
    
    # Simple transfer entropy approximation
    # TE ≈ I(X_future; Y_past) - I(X_future; Y_past | X_past)
    # For simplicity, we'll use: TE ≈ correlation between phys_past and sfhsgp_future
    # conditioned on sfhsgp_past
    
    if len(set(phys_past_clean)) > 1 and len(set(sfhsgp_future_clean)) > 1:
        try:
            # Compute correlation between phys_past and sfhsgp_future
            te_value = np.abs(np.corrcoef(phys_past_clean.astype(float), 
                                        sfhsgp_future_clean.astype(float))[0,1])
            if np.isnan(te_value):
                te_value = 0.0
        except:
            te_value = 0.0
    else:
        te_value = 0.0
    
    return {
        'value': float(min(te_value, 1.0))
    }

def compute_asymmetry_preservation_ratio(physical_values, sfhsgp_hierarchy):
    """
    Compute asymmetry preservation ratio.
    Ratio of asymmetry preservation in authentic vs adversarial systems.
    """
    min_len = min(len(physical_values), len(sfhsgp_hierarchy))
    phys_trunc = np.array(physical_values[:min_len])
    sfhsgp_trunc = np.array(sfhsgp_hierarchy[:min_len])
    
    if len(phys_trunc) < 4:
        return {'value': 0.0}
    
    # Compute asymmetry as third-order moment (skewness-like measure)
    def compute_asymmetry(seq):
        if len(seq) < 3:
            return 0.0
        mean_val = np.mean(seq)
        # Third central moment
        third_moment = np.mean((seq - mean_val)**3)
        # Normalize by variance^1.5
        var = np.var(seq)
        if var > 0:
            asymmetry = third_moment / (var**1.5)
        else:
            asymmetry = 0.0
        return abs(asymmetry)
    
    phys_asym = compute_asymmetry(phys_trunc)
    sfhsgp_asym = compute_asymmetry(sfhsgp_trunc)
    
    # Ratio: how much of the SFH-SGP asymmetry is preserved in the physical system
    if sfhsgp_asym > 0:
        ratio = phys_asym / sfhsgp_asym
    else:
        ratio = 0.0 if phys_asym == 0 else 1.0  # If SFH-SGP has no asymmetry, perfect match if phys also has none
    
    return {
        'value': float(min(ratio, 2.0))  # Allow up to 2x preservation
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
    print("Starting Phase 505: Directional-Recursive-Discrimination Analysis...")
    
    # Load SFH-SGP baseline
    print("Loading SFH-SGP baseline from Phase 407...")
    sfhsgp_hierarchy = get_sfhsgp_emergence_hierarchy()
    print(f"SFH-SGP Emergence Hierarchy: {sfhsgp_hierarchy}")
    
    # Load authentic physical systems
    print("Loading authentic physical systems from Phase 503...")
    authentic_systems = load_phase503_authentic_systems()
    print(f"Loaded {len(authentic_systems)} authentic physical systems")
    
    # Generate adversarial systems
    print("Generating adversarial pseudo-physical systems...")
    adversarial_systems = generate_adversarial_systems(authentic_systems)
    print(f"Generated {len(adversarial_systems)} adversarial systems")
    
    # Perform null hypothesis testing
    print("Performing null hypothesis testing (1000 permutations)...")
    null_distribution = perform_null_testing(sfhsgp_hierarchy, n_permutations=1000)
    print(f"Null distribution: mean={null_distribution['mean']:.6f}, std={null_distribution['std']:.6f}")
    
    # Analyze correspondence for authentic and adversarial systems
    print("\nAnalyzing correspondence for authentic and adversarial systems...")
    
    # Storage for results
    authentic_results = {}
    adversarial_results = {}
    
    # Process authentic systems
    for system_name, system_data in authentic_systems.items():
        print(f"  Analyzing {system_name}...")
        
        # Standard metrics
        std_corr = compute_spearman_correlation(system_data['values'], sfhsgp_hierarchy)
        
        # New directional recursive metrics
        dir_grad = compute_directional_recursive_gradient(system_data['values'], sfhsgp_hierarchy)
        prop_asym = compute_propagation_asymmetry_index(system_data['values'], sfhsgp_hierarchy)
        rec_dep = compute_recursive_dependency_score(system_data['values'], sfhsgp_hierarchy)
        depth_coup = compute_depth_coupling_coherence(system_data['values'], sfhsgp_hierarchy)
        causal_ret = compute_causal_order_retention(system_data['values'], sfhsgp_hierarchy)
        rec_trans = compute_recursive_transfer_entropy(system_data['values'], sfhsgp_hierarchy)
        asym_pres = compute_asymmetry_preservation_ratio(system_data['values'], sfhsgp_hierarchy)
        
        # Compute z-score for standard correlation
        z_score = compute_z_score(std_corr['rho'], null_distribution)
        
        authentic_results[system_name] = {
            'standard_correlation': std_corr,
            'directional_recursive_gradient': dir_grad,
            'propagation_asymmetry_index': prop_asym,
            'recursive_dependency_score': rec_dep,
            'depth_coupling_coherence': depth_coup,
            'causal_order_retention': causal_ret,
            'recursive_transfer_entropy': rec_trans,
            'asymmetry_preservation_ratio': asym_pres,
            'z_score': z_score,
            'values': system_data['values'],
            'description': system_data['description'],
            'domain': system_data['domain']
        }
    
    # Process adversarial systems
    for system_name, system_data in adversarial_systems.items():
        print(f"  Analyzing {system_name}...")
        
        # Standard metrics
        std_corr = compute_spearman_correlation(system_data['values'], sfhsgp_hierarchy)
        
        # New directional recursive metrics
        dir_grad = compute_directional_recursive_gradient(system_data['values'], sfhsgp_hierarchy)
        prop_asym = compute_propagation_asymmetry_index(system_data['values'], sfhsgp_hierarchy)
        rec_dep = compute_recursive_dependency_score(system_data['values'], sfhsgp_hierarchy)
        depth_coup = compute_depth_coupling_coherence(system_data['values'], sfhsgp_hierarchy)
        causal_ret = compute_causal_order_retention(system_data['values'], sfhsgp_hierarchy)
        rec_trans = compute_recursive_transfer_entropy(system_data['values'], sfhsgp_hierarchy)
        asym_pres = compute_asymmetry_preservation_ratio(system_data['values'], sfhsgp_hierarchy)
        
        # Compute z-score for standard correlation
        z_score = compute_z_score(std_corr['rho'], null_distribution)
        
        adversarial_results[system_name] = {
            'standard_correlation': std_corr,
            'directional_recursive_gradient': dir_grad,
            'propagation_asymmetry_index': prop_asym,
            'recursive_dependency_score': rec_dep,
            'depth_coupling_coherence': depth_coup,
            'causal_order_retention': causal_ret,
            'recursive_transfer_entropy': rec_trans,
            'asymmetry_preservation_ratio': asym_pres,
            'z_score': z_score,
            'values': system_data['values'],
            'description': system_data['description'],
            'domain': system_data['domain'],
            'is_adversarial': system_data['is_adversarial'],
            'original_system': system_data['original_system'],
            'adversarial_type': system_data['adversarial_type']
        }
    
    # Compute summary statistics
    print("\nComputing summary statistics...")
    
    # Authentic systems summary
    auth_std_rhos = [result['standard_correlation']['rho'] for result in authentic_results.values()]
    auth_dir_grads = [result['directional_recursive_gradient']['value'] for result in authentic_results.values()]
    auth_z_scores = [result['z_score'] for result in authentic_results.values()]
    
    # Adversarial systems summary
    adv_std_rhos = [result['standard_correlation']['rho'] for result in adversarial_results.values()]
    adv_dir_grads = [result['directional_recursive_gradient']['value'] for result in adversarial_results.values()]
    adv_z_scores = [result['z_score'] for result in adversarial_results.values()]
    
    # Compute means and standard deviations
    auth_std_mean = np.mean(auth_std_rhos) if auth_std_rhos else 0.0
    auth_std_std = np.std(auth_std_rhos) if auth_std_rhos else 0.0
    auth_dir_mean = np.mean(auth_dir_grads) if auth_dir_grads else 0.0
    auth_dir_std = np.std(auth_dir_grads) if auth_dir_grads else 0.0
    auth_z_mean = np.mean(auth_z_scores) if auth_z_scores else 0.0
    auth_z_std = np.std(auth_z_scores) if auth_z_scores else 0.0
    
    adv_std_mean = np.mean(adv_std_rhos) if adv_std_rhos else 0.0
    adv_std_std = np.std(adv_std_rhos) if adv_std_rhos else 0.0
    adv_dir_mean = np.mean(adv_dir_grads) if adv_dir_grads else 0.0
    adv_dir_std = np.std(adv_dir_grads) if adv_dir_grads else 0.0
    adv_z_mean = np.mean(adv_z_scores) if adv_z_scores else 0.0
    adv_z_std = np.std(adv_z_scores) if adv_z_scores else 0.0
    
    # Compute discrimination metrics
    # Discrimination ratio for standard correlation: |auth_mean| / |adv_mean| 
    # (avoiding division by zero)
    denom_std = abs(adv_std_mean) if abs(adv_std_mean) > 1e-10 else 1e-10
    discrimination_ratio_std = abs(auth_std_mean) / denom_std
    
    # Discrimination ratio for directional recursive gradient: auth_mean / adv_mean
    # (higher values indicate better discrimination)
    denom_dir = abs(adv_dir_mean) if abs(adv_dir_mean) > 1e-10 else 1e-10
    discrimination_ratio_dir = auth_dir_mean / denom_dir if denom_dir > 0 else 0.0
    
    # Adversarial false positive rate (standard correlation): fraction with |rho| > 0.3 and p < 0.05
    adv_false_pos_std = 0
    adv_total_std = len(adversarial_results)
    for result in adversarial_results.values():
        if abs(result['standard_correlation']['rho']) > 0.3 and result['standard_correlation']['p'] < 0.05:
            adv_false_pos_std += 1
    adv_false_pos_rate_std = adv_false_pos_std / max(adv_total_std, 1)
    
    # Adversarial false positive rate (directional): fraction with dir_grad > 0.3
    adv_false_pos_dir = 0
    adv_total_dir = len(adversarial_results)
    for result in adversarial_results.values():
        if result['directional_recursive_gradient']['value'] > 0.3:
            adv_false_pos_dir += 1
    adv_false_pos_rate_dir = adv_false_pos_dir / max(adv_total_dir, 1)
    
    # Recursive specificity index: (auth_mean - adv_mean) / (auth_mean + adv_mean)
    # For standard correlation
    denom_rsic_std = abs(auth_std_mean) + abs(adv_std_mean)
    recursive_specificity_index_std = (abs(auth_std_mean) - abs(adv_std_mean)) / max(denom_rsic_std, 1e-10)
    
    # For directional recursive gradient
    denom_rsic_dir = auth_dir_mean + adv_dir_mean
    recursive_specificity_index_dir = (auth_dir_mean - adv_dir_mean) / max(abs(denom_rsic_dir), 1e-10)
    
    # Null physical separation (mean z-score)
    null_physical_separation = auth_z_mean
    
    # Pseudo system rejection rate: fraction of adversarial systems correctly rejected
    # Using directional metric with threshold 0.3
    pseudo_system_rejection = 0
    total_adversarial = len(adversarial_results)
    for result in adversarial_results.values():
        if result['directional_recursive_gradient']['value'] <= 0.3:  # Correctly rejected (low directional score)
            pseudo_system_rejection += 1
    pseudo_system_rejection_rate = pseudo_system_rejection / max(total_adversarial, 1)
    
    # Structural authenticity score: correlation between system authenticity and directional gradient
    authentic_flags = [1.0 if not result.get('is_adversarial', False) else 0.0 
                      for result in list(authentic_results.values()) + list(adversarial_results.values())]
    dir_grad_values = [result['directional_recursive_gradient']['value'] 
                      for result in list(authentic_results.values()) + list(adversarial_results.values())]
    
    if len(authentic_flags) > 1 and len(dir_grad_values) > 1:
        if np.std(authentic_flags) > 0 and np.std(dir_grad_values) > 0:
            structural_authenticity_score = np.corrcoef(authentic_flags, dir_grad_values)[0,1]
            if np.isnan(structural_authenticity_score):
                structural_authenticity_score = 0.0
        else:
            structural_authenticity_score = 0.0
    else:
        structural_authenticity_score = 0.0
    
    # Determine success conditions
    # Authentic success: >=50% of authentic systems show significant directional recursive gradient (>0.3)
    auth_sig_count = sum(1 for result in authentic_results.values() 
                        if result['directional_recursive_gradient']['value'] > 0.3)
    authentic_success = (auth_sig_count / max(len(authentic_results), 1)) >= 0.5
    
    # Adversarial success: <50% of adversarial systems show significant directional recursive gradient (>0.3)
    adv_sig_count = sum(1 for result in adversarial_results.values() 
                       if result['directional_recursive_gradient']['value'] > 0.3)
    adversarial_success = (adv_sig_count / max(len(adversarial_results), 1)) < 0.5
    
    # Discrimination success: directional discrimination ratio > 1.0
    discrimination_success = discrimination_ratio_dir > 1.0
    
    # Overall success: all three conditions met
    overall_success = authentic_success and adversarial_success and discrimination_success
    
    # Determine verdict
    if overall_success:
        verdict = "DIRECTIONAL-RECURSIVE-DISCRIMINATION-SUCCESS"
    else:
        verdict = "DIRECTIONAL-RECURSIVE-DISCRIMINATION-FAILURE"
    
    # Create summary dictionary with JSON-serializable values
    summary = {
        'authentic_significant': auth_sig_count,
        'authentic_total': len(authentic_results),
        'adversarial_significant': adv_sig_count,
        'adversarial_total': len(adversarial_results),
        'authentic_success': bool(authentic_success),  # Ensure it's a proper boolean
        'adversarial_success': bool(adversarial_success),  # Ensure it's a proper boolean
        'discrimination_ratio_standard': float(discrimination_ratio_std),
        'discrimination_ratio_directional': float(discrimination_ratio_dir),
        'recursive_specificity_index_standard': float(recursive_specificity_index_std),
        'recursive_specificity_index_directional': float(recursive_specificity_index_dir),
        'null_physical_separation': float(null_physical_separation),
        'pseudo_system_rejection_rate': float(pseudo_system_rejection_rate),
        'structural_authenticity_score': float(structural_authenticity_score),
        'discrimination_success': bool(discrimination_success),  # Ensure it's a proper boolean
        'overall_success': bool(overall_success),  # Ensure it's a proper boolean
        'verdict': verdict
    }
    
    # Create final results dictionary
    results = {
        'phase': 505,
        'seed': 505,
        'tier': 3,
        'sfhsgp_hierarchy': sfhsgp_hierarchy,
        'authentic_systems': authentic_results,
        'adversarial_systems': adversarial_results,
        'null_distribution': null_distribution,
        'discrimination_metrics': {
            'discrimination_ratio_standard': discrimination_ratio_std,
            'discrimination_ratio_directional': discrimination_ratio_dir,
            'adversarial_false_positive_rate_standard': adv_false_pos_rate_std,
            'adversarial_false_positive_rate_directional': adv_false_pos_rate_dir,
            'recursive_specificity_index_standard': recursive_specificity_index_std,
            'recursive_specificity_index_directional': recursive_specificity_index_dir,
            'null_physical_separation': null_physical_separation,
            'pseudo_system_rejection_rate': pseudo_system_rejection_rate,
            'structural_authenticity_score': structural_authenticity_score
        },
        'summary': summary
    }
    
    # Save results to file
    output_file = 'phases/phase505/phase505_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("PHASE 505 RESULTS SUMMARY")
    print("="*60)
    print(f"SFH-SGP Reference Hierarchy: {sfhsgp_hierarchy}")
    print(f"Authentic Systems Analyzed: {len(authentic_results)}")
    print(f"Adversarial Systems Analyzed: {len(adversarial_results)}")
    print(f"Authentic Systems Significant (dir_grad > 0.3): {auth_sig_count}/{len(authentic_results)} ({auth_sig_count/max(len(authentic_results),1)*100:.1f}%)")
    print(f"Adversarial Systems Significant (dir_grad > 0.3): {adv_sig_count}/{len(adversarial_results)} ({adv_sig_count/max(len(adversarial_results),1)*100:.1f}%)")
    print(f"Discrimination Ratio (Standard): {discrimination_ratio_std:.6f}")
    print(f"Discrimination Ratio (Directional): {discrimination_ratio_dir:.6f}")
    print(f"Recursive Specificity Index (Standard): {recursive_specificity_index_std:.6f}")
    print(f"Recursive Specificity Index (Directional): {recursive_specificity_index_dir:.6f}")
    print(f"Null Physical Separation (mean z-score): {null_physical_separation:.6f}")
    print(f"Pseudo System Rejection Rate: {pseudo_system_rejection_rate:.6f}")
    print(f"Structural Authenticity Score: {structural_authenticity_score:.6f}")
    print(f"Authentic Success (≥50% significant): {authentic_success}")
    print(f"Adversarial Success (<50% significant): {adversarial_success}")
    print(f"Discrimination Success (ratio > 1.0): {discrimination_success}")
    print(f"Overall Success: {overall_success}")
    print(f"Verdict: {verdict}")
    print("="*60)
    
    # Also save a summary CSV for easy inspection
    summary_data = []
    for system_name, result in authentic_results.items():
        summary_data.append({
            'system': system_name,
            'type': 'authentic',
            'domain': result['domain'],
            'standard_rho': result['standard_correlation']['rho'],
            'standard_p': result['standard_correlation']['p'],
            'directional_gradient': result['directional_recursive_gradient']['value'],
            'propagation_asymmetry': result['propagation_asymmetry_index']['value'],
            'recursive_dependency': result['recursive_dependency_score']['value'],
            'depth_coupling': result['depth_coupling_coherence']['value'],
            'causal_retention': result['causal_order_retention']['value'],
            'transfer_entropy': result['recursive_transfer_entropy']['value'],
            'asymmetry_preservation': result['asymmetry_preservation_ratio']['value'],
            'z_score': result['z_score']
        })
    
    for system_name, result in adversarial_results.items():
        summary_data.append({
            'system': system_name,
            'type': 'adversarial',
            'domain': result['domain'],
            'standard_rho': result['standard_correlation']['rho'],
            'standard_p': result['standard_correlation']['p'],
            'directional_gradient': result['directional_recursive_gradient']['value'],
            'propagation_asymmetry': result['propagation_asymmetry_index']['value'],
            'recursive_dependency': result['recursive_dependency_score']['value'],
            'depth_coupling': result['depth_coupling_coherence']['value'],
            'causal_retention': result['causal_order_retention']['value'],
            'transfer_entropy': result['recursive_transfer_entropy']['value'],
            'asymmetry_preservation': result['asymmetry_preservation_ratio']['value'],
            'z_score': result['z_score'],
            'is_adversarial': result['is_adversarial'],
            'original_system': result['original_system'],
            'adversarial_type': result['adversarial_type']
        })
    
    df = pd.DataFrame(summary_data)
    csv_file = 'phases/phase505/phase505_summary.csv'
    df.to_csv(csv_file, index=False)
    print(f"Summary CSV saved to {csv_file}")
    
    return results

if __name__ == "__main__":
    try:
        results = main()
    except Exception as e:
        print(f"Error in Phase 505 computation: {e}")
        import traceback
        traceback.print_exc()