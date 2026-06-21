#!/usr/bin/env python3
"""
P10 — Signature Robustness Audit

Tests whether stable signatures remain stable under aggressive protocol perturbation.

Protocol perturbations:
1. Transform variation (rank, raw, zscore, minmax)
2. Temporal subsampling (every 1, 2, 5, 10 timesteps)
3. Window size variation (10, 20, 50, 100 timesteps)
4. Noise injection (Gaussian σ = 0.01, 0.05, 0.1)
"""

import numpy as np
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Output directory
OUT_DIR = Path(__file__).parent
OUT_DIR.mkdir(exist_ok=True)


# ============================================================================
# SIGNATURE DESCRIPTORS (same as P9)
# ============================================================================

def assign_descriptor(c_time_series: list) -> str:
    """Assign provisional descriptor to C time series."""
    if len(c_time_series) < 3:
        return "insufficient_data"
    
    c = np.array(c_time_series)
    
    # Normalize to [0, 1]
    c_min, c_max = c.min(), c.max()
    if c_max - c_min < 1e-10:
        return "constant"
    
    c_norm = (c - c_min) / (c_max - c_min)
    
    # Compute derivatives
    dc = np.diff(c_norm)
    
    # Compute monotonicity
    increasing = np.sum(dc > 0)
    decreasing = np.sum(dc < 0)
    total = len(dc)
    
    # Compute peak timing
    peak_idx = np.argmax(c_norm)
    peak_timing = peak_idx / len(c_norm)
    
    # Compute autocorrelation
    if len(c) > 5:
        autocorr = np.corrcoef(c[:-1], c[1:])[0, 1]
    else:
        autocorr = 0.0
    
    # Compute volatility
    volatility = np.std(c) / (np.mean(c) + 1e-10)
    
    # Assign descriptor based on rules
    if increasing / total > 0.8:
        return "monotonic_increase"
    elif decreasing / total > 0.8:
        return "monotonic_decrease"
    elif peak_timing > 0.3 and peak_timing < 0.7:
        return "peaked"
    elif c_norm[0] > 0.7 and c_norm[1] < 0.3 and c_norm[-1] > 0.5:
        return "high_to_low_to_gradual"
    elif autocorr > 0.7 and volatility < 0.3:
        return "plateaued"
    elif volatility > 0.5:
        return "variable"
    else:
        return "unclassified"


# ============================================================================
# SIGNATURE METRICS (same as P9)
# ============================================================================

def compute_signature_metrics(c_time_series: list) -> dict:
    """Compute quantitative signature metrics."""
    if len(c_time_series) < 3:
        return {
            'temporal_spread': 0.0,
            'peak_timing': 0.0,
            'recovery_slope': 0.0,
            'persistence': 0.0,
            'volatility': 0.0,
            'mean_c': 0.0,
            'std_c': 0.0
        }
    
    c = np.array(c_time_series)
    
    # Temporal spread
    temporal_spread = np.max(c) - np.min(c)
    
    # Peak timing
    peak_idx = np.argmax(c)
    peak_timing = peak_idx / len(c)
    
    # Recovery slope (from min to final)
    min_idx = np.argmin(c)
    if min_idx < len(c) - 1:
        recovery_slope = (c[-1] - c[min_idx]) / (len(c) - min_idx)
    else:
        recovery_slope = 0.0
    
    # Persistence (autocorrelation at lag 1)
    if len(c) > 5:
        persistence = np.corrcoef(c[:-1], c[1:])[0, 1]
    else:
        persistence = 0.0
    
    # Volatility
    volatility = np.std(c) / (np.mean(c) + 1e-10)
    
    # Basic statistics
    mean_c = np.mean(c)
    std_c = np.std(c)
    
    return {
        'temporal_spread': float(temporal_spread),
        'peak_timing': float(peak_timing),
        'recovery_slope': float(recovery_slope),
        'persistence': float(persistence),
        'volatility': float(volatility),
        'mean_c': float(mean_c),
        'std_c': float(std_c)
    }


# ============================================================================
# PROTOCOL PERTURBATIONS
# ============================================================================

def apply_transform(c_values: list, transform: str) -> list:
    """Apply transform to C values."""
    c = np.array(c_values)
    
    if transform == "rank":
        from scipy.stats import rankdata
        return rankdata(c, method="ordinal").tolist()
    elif transform == "raw":
        return c.tolist()
    elif transform == "zscore":
        mean = np.mean(c)
        std = np.std(c)
        if std < 1e-10:
            return c.tolist()
        return ((c - mean) / std).tolist()
    elif transform == "minmax":
        c_min, c_max = c.min(), c.max()
        if c_max - c_min < 1e-10:
            return c.tolist()
        return ((c - c_min) / (c_max - c_min)).tolist()
    else:
        return c.tolist()


def apply_subsampling(c_values: list, factor: int) -> list:
    """Apply temporal subsampling."""
    return c_values[::factor]


def apply_windowing(c_values: list, window_size: int) -> list:
    """Apply windowed averaging."""
    if len(c_values) < window_size:
        return c_values
    
    c = np.array(c_values)
    kernel = np.ones(window_size) / window_size
    smoothed = np.convolve(c, kernel, mode='valid')
    return smoothed.tolist()


def apply_noise(c_values: list, sigma: float) -> list:
    """Apply Gaussian noise injection."""
    c = np.array(c_values)
    rng = np.random.default_rng(42)
    noise = rng.normal(0, sigma, len(c))
    return (c + noise).tolist()


# ============================================================================
# LOAD DATA
# ============================================================================

def load_p9_results():
    """Load P9 baseline signatures."""
    with open('audits/rd_p9_temporal_signatures/p9_results.json', 'r') as f:
        return json.load(f)


def extract_c_time_series(results: list, domain_name: str) -> dict:
    """Extract C time series from trajectory results."""
    # Group by trajectory
    trajectories = {}
    for r in results:
        traj = r.get('trajectory', r.get('file_index', 0))
        if traj not in trajectories:
            trajectories[traj] = []
        
        # Handle different key names
        c_val = r.get('delta_C_rank', r.get('ΔC_rank', r.get('C', 0)))
        timestep = r.get('frame', r.get('timestep', 0))
        
        trajectories[traj].append({
            'timestep': timestep,
            'C': c_val
        })
    
    # Sort by timestep and extract C values
    time_series = {}
    for traj, data in trajectories.items():
        sorted_data = sorted(data, key=lambda x: x['timestep'])
        c_values = [d['C'] for d in sorted_data]
        time_series[traj] = c_values
    
    return time_series


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def run_p10_analysis():
    """Run P10 signature robustness audit."""
    print("=" * 80)
    print("P10 — SIGNATURE ROBUSTNESS AUDIT")
    print("=" * 80)
    
    # Load data
    print("\n" + "=" * 80)
    print("PHASE 1: LOAD BASELINE SIGNATURES")
    print("=" * 80)
    
    p9_results = load_p9_results()
    baseline_descriptors = p9_results['descriptors']
    
    print("\nBaseline descriptors:")
    for domain, trajectories in baseline_descriptors.items():
        # Get most common descriptor
        descriptors = list(trajectories.values())
        if descriptors:
            from collections import Counter
            most_common = Counter(descriptors).most_common(1)[0][0]
            print(f"  {domain}: {most_common}")
    
    # Load trajectory data
    print("\nLoading trajectory data...")
    gs_results = json.load(open('audits/rd_p1_gs/results.json', 'r'))
    rb_results = json.load(open('audits/rd_p2_rb/results.json', 'r'))
    am_results = json.load(open('audits/rd_p3_am/results.json', 'r'))
    mhd_results = json.load(open('audits/rd_well7b_r1/mhd_replication_results.json', 'r'))
    
    # Extract C time series
    gs_ts = extract_c_time_series(gs_results, 'GS')
    rb_ts = extract_c_time_series(rb_results, 'RB')
    am_ts = extract_c_time_series(am_results, 'AM')
    mhd_ts = extract_c_time_series(mhd_results, 'MHD')
    
    # Use first trajectory from each domain for robustness testing
    test_data = {
        'GS': gs_ts.get(0, []),
        'RB': rb_ts.get(0, []),
        'AM': am_ts.get(0, []),
        'MHD': mhd_ts.get(0, [])
    }
    
    # Phase 2: Protocol perturbation
    print("\n" + "=" * 80)
    print("PHASE 2: PROTOCOL PERTURBATION")
    print("=" * 80)
    
    perturbation_results = {}
    
    for domain, c_values in test_data.items():
        if not c_values:
            continue
        
        print(f"\n{domain}:")
        perturbation_results[domain] = {
            'baseline_descriptor': assign_descriptor(c_values),
            'baseline_metrics': compute_signature_metrics(c_values),
            'perturbations': {}
        }
        
        # Test transform variations
        print("  Testing transform variations...")
        for transform in ['rank', 'raw', 'zscore', 'minmax']:
            c_perturbed = apply_transform(c_values, transform)
            descriptor = assign_descriptor(c_perturbed)
            metrics = compute_signature_metrics(c_perturbed)
            
            perturbation_results[domain]['perturbations'][f'transform_{transform}'] = {
                'descriptor': descriptor,
                'metrics': metrics,
                'descriptor_stable': descriptor == perturbation_results[domain]['baseline_descriptor']
            }
        
        # Test subsampling
        print("  Testing temporal subsampling...")
        for factor in [1, 2, 5, 10]:
            c_perturbed = apply_subsampling(c_values, factor)
            if len(c_perturbed) >= 3:
                descriptor = assign_descriptor(c_perturbed)
                metrics = compute_signature_metrics(c_perturbed)
                
                perturbation_results[domain]['perturbations'][f'subsample_{factor}'] = {
                    'descriptor': descriptor,
                    'metrics': metrics,
                    'descriptor_stable': descriptor == perturbation_results[domain]['baseline_descriptor']
                }
        
        # Test windowing
        print("  Testing window size variation...")
        for window_size in [3, 5, 10]:
            if len(c_values) >= window_size:
                c_perturbed = apply_windowing(c_values, window_size)
                if len(c_perturbed) >= 3:
                    descriptor = assign_descriptor(c_perturbed)
                    metrics = compute_signature_metrics(c_perturbed)
                    
                    perturbation_results[domain]['perturbations'][f'window_{window_size}'] = {
                        'descriptor': descriptor,
                        'metrics': metrics,
                        'descriptor_stable': descriptor == perturbation_results[domain]['baseline_descriptor']
                    }
        
        # Test noise injection
        print("  Testing noise injection...")
        for sigma in [0.01, 0.05, 0.1]:
            c_perturbed = apply_noise(c_values, sigma)
            descriptor = assign_descriptor(c_perturbed)
            metrics = compute_signature_metrics(c_perturbed)
            
            perturbation_results[domain]['perturbations'][f'noise_{sigma}'] = {
                'descriptor': descriptor,
                'metrics': metrics,
                'descriptor_stable': descriptor == perturbation_results[domain]['baseline_descriptor']
            }
    
    # Phase 3: Stability assessment
    print("\n" + "=" * 80)
    print("PHASE 3: STABILITY ASSESSMENT")
    print("=" * 80)
    
    stability_results = {}
    
    for domain, results in perturbation_results.items():
        print(f"\n{domain}:")
        
        perturbations = results['perturbations']
        
        # Descriptor stability
        descriptor_stable_count = sum(1 for p in perturbations.values() if p['descriptor_stable'])
        total_perturbations = len(perturbations)
        descriptor_stability = descriptor_stable_count / total_perturbations if total_perturbations > 0 else 0
        
        # Metric stability
        metric_values = {
            'temporal_spread': [],
            'persistence': [],
            'volatility': []
        }
        
        for p in perturbations.values():
            for metric_name in metric_values:
                metric_values[metric_name].append(p['metrics'][metric_name])
        
        metric_cvs = {}
        for metric_name, values in metric_values.items():
            values = np.array(values)
            if np.mean(values) > 0:
                cv = np.std(values) / np.mean(values)
            else:
                cv = 0.0
            metric_cvs[metric_name] = float(cv)
        
        mean_cv = np.mean(list(metric_cvs.values()))
        
        # Overall robustness
        if descriptor_stability >= 0.8 and mean_cv < 0.2:
            overall_status = "ROBUST"
        elif descriptor_stability >= 0.6 and mean_cv < 0.3:
            overall_status = "MARGINAL"
        else:
            overall_status = "FRAGILE"
        
        stability_results[domain] = {
            'descriptor_stability': descriptor_stability,
            'metric_cvs': metric_cvs,
            'mean_cv': mean_cv,
            'overall_status': overall_status
        }
        
        print(f"  Descriptor stability: {descriptor_stability:.2f}")
        print(f"  Metric CVs: {metric_cvs}")
        print(f"  Mean CV: {mean_cv:.4f}")
        print(f"  Overall status: {overall_status}")
    
    # Print summary tables
    print("\n" + "=" * 80)
    print("TABLE 1 — DESCRIPTOR STABILITY UNDER PERTURBATION")
    print("=" * 80)
    print(f"{'Domain':<10} {'Baseline':<25} {'Stability':>10} {'Status':<15}")
    print("-" * 60)
    
    for domain, results in perturbation_results.items():
        baseline = results['baseline_descriptor']
        stability = stability_results[domain]['descriptor_stability']
        status = stability_results[domain]['overall_status']
        print(f"{domain:<10} {baseline:<25} {stability:>10.2f} {status:<15}")
    
    print("\n" + "=" * 80)
    print("TABLE 2 — METRIC STABILITY ACROSS PERTURBATIONS")
    print("=" * 80)
    print(f"{'Domain':<10} {'Spread CV':>10} {'Persistence CV':>15} {'Volatility CV':>15} {'Mean CV':>10}")
    print("-" * 60)
    
    for domain, results in stability_results.items():
        cvs = results['metric_cvs']
        print(f"{domain:<10} {cvs['temporal_spread']:>10.4f} {cvs['persistence']:>15.4f} "
              f"{cvs['volatility']:>15.4f} {results['mean_cv']:>10.4f}")
    
    print("\n" + "=" * 80)
    print("TABLE 3 — SIGNATURE ROBUSTNESS CLASSIFICATION")
    print("=" * 80)
    print(f"{'Domain':<10} {'Descriptor Stability':<20} {'Metric Stability':<18} {'Overall':<15}")
    print("-" * 60)
    
    for domain, results in stability_results.items():
        desc_stab = "HIGH" if results['descriptor_stability'] >= 0.8 else "MEDIUM" if results['descriptor_stability'] >= 0.6 else "LOW"
        metric_stab = "HIGH" if results['mean_cv'] < 0.2 else "MEDIUM" if results['mean_cv'] < 0.3 else "LOW"
        print(f"{domain:<10} {desc_stab:<20} {metric_stab:<18} {results['overall_status']:<15}")
    
    # Interpretation
    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    
    robust_domains = [d for d, r in stability_results.items() if r['overall_status'] == 'ROBUST']
    marginal_domains = [d for d, r in stability_results.items() if r['overall_status'] == 'MARGINAL']
    fragile_domains = [d for d, r in stability_results.items() if r['overall_status'] == 'FRAGILE']
    
    if robust_domains:
        print(f"\n✓ ROBUST SIGNATURES: {', '.join(robust_domains)}")
        print("  These signatures survive aggressive protocol perturbation.")
    
    if marginal_domains:
        print(f"\n⚠ MARGINAL SIGNATURES: {', '.join(marginal_domains)}")
        print("  These signatures are moderately stable but may be fragile under some perturbations.")
    
    if fragile_domains:
        print(f"\n✗ FRAGILE SIGNATURES: {', '.join(fragile_domains)}")
        print("  These signatures do not survive aggressive protocol perturbation.")
    
    # Save results
    output_file = OUT_DIR / "p10_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'perturbations': perturbation_results,
            'stability': stability_results
        }, f, indent=2, default=str)
    
    print(f"\nResults saved to {output_file}")
    
    print("\n" + "=" * 80)
    print("P10 — SIGNATURE ROBUSTNESS AUDIT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_p10_analysis()
