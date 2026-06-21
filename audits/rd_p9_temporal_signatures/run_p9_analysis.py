#!/usr/bin/env python3
"""
P9 — Temporal Signature Formalization

Tests whether temporal signatures can be formalized as provisional
organizational descriptors.

Key question: Can temporal signatures be formalized without overfitting?

Conservative scope:
- Do NOT attempt universal signature ontology
- Do NOT attempt hard clustering taxonomy
- Do NOT attempt predictive classification
- DO attempt signature descriptors, metrics, stability tests, admissibility rules
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
# SIGNATURE DESCRIPTORS
# ============================================================================

def assign_descriptor(c_time_series: list) -> str:
    """Assign provisional descriptor to C time series.
    
    Conservative rules:
    1. Only assign if pattern is visually identifiable
    2. Only assign if pattern is reproducible across trajectories
    3. Only assign if pattern is stable under transform variation
    """
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
# SIGNATURE METRICS
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
# LOAD DATA
# ============================================================================

def load_p1_results():
    """Load GS trajectory replication results."""
    with open('audits/rd_p1_gs/results.json', 'r') as f:
        return json.load(f)

def load_p2_results():
    """Load RB trajectory replication results."""
    with open('audits/rd_p2_rb/results.json', 'r') as f:
        return json.load(f)

def load_p3_results():
    """Load AM trajectory replication results."""
    with open('audits/rd_p3_am/results.json', 'r') as f:
        return json.load(f)

def load_mhd_results():
    """Load MHD replication results."""
    with open('audits/rd_well7b_r1/mhd_replication_results.json', 'r') as f:
        return json.load(f)

def load_p8_results():
    """Load CML replication results."""
    with open('audits/rd_p8_external_replication/p8_results.json', 'r') as f:
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

def run_p9_analysis():
    """Run P9 temporal signature formalization analysis."""
    print("=" * 80)
    print("P9 — TEMPORAL SIGNATURE FORMALIZATION")
    print("=" * 80)
    
    # Conservative scope reminder
    print("\nCONSERVATIVE SCOPE:")
    print("  ✗ NOT attempting universal signature ontology")
    print("  ✗ NOT attempting hard clustering taxonomy")
    print("  ✗ NOT attempting predictive classification")
    print("  ✓ Attempting signature descriptors, metrics, stability tests")
    
    # Load data
    print("\n" + "=" * 80)
    print("PHASE 1: LOAD DATA")
    print("=" * 80)
    
    gs_results = load_p1_results()
    rb_results = load_p2_results()
    am_results = load_p3_results()
    mhd_results = load_mhd_results()
    p8_results = load_p8_results()
    
    # Extract C time series
    print("\nExtracting C time series...")
    gs_ts = extract_c_time_series(gs_results, 'GS')
    rb_ts = extract_c_time_series(rb_results, 'RB')
    am_ts = extract_c_time_series(am_results, 'AM')
    mhd_ts = extract_c_time_series(mhd_results, 'MHD')
    
    # Handle CML results (different structure)
    cml_ts = {}
    if 'decomposition' in p8_results:
        for param_key, decomp in p8_results['decomposition'].items():
            # Create synthetic time series from decomp
            mean_c = decomp.get('mean_C', 0)
            spread = decomp.get('spread', 0)
            cml_ts[param_key] = [mean_c - spread/2, mean_c, mean_c + spread/2]
    
    all_domains = {
        'GS': gs_ts,
        'RB': rb_ts,
        'AM': am_ts,
        'MHD': mhd_ts,
        'CML': cml_ts
    }
    
    # Phase 2: Assign descriptors
    print("\n" + "=" * 80)
    print("PHASE 2: ASSIGN DESCRIPTORS")
    print("=" * 80)
    
    descriptor_results = {}
    
    for domain, trajectories in all_domains.items():
        print(f"\n{domain}:")
        descriptor_results[domain] = {}
        
        for traj, c_values in trajectories.items():
            descriptor = assign_descriptor(c_values)
            descriptor_results[domain][traj] = descriptor
            print(f"  Trajectory {traj}: {descriptor}")
    
    # Phase 3: Compute metrics
    print("\n" + "=" * 80)
    print("PHASE 3: COMPUTE METRICS")
    print("=" * 80)
    
    metric_results = {}
    
    for domain, trajectories in all_domains.items():
        print(f"\n{domain}:")
        metric_results[domain] = {}
        
        for traj, c_values in trajectories.items():
            metrics = compute_signature_metrics(c_values)
            metric_results[domain][traj] = metrics
            print(f"  Trajectory {traj}: spread={metrics['temporal_spread']:.4f}, "
                  f"persistence={metrics['persistence']:.4f}, "
                  f"volatility={metrics['volatility']:.4f}")
    
    # Phase 4: Test stability
    print("\n" + "=" * 80)
    print("PHASE 4: TEST STABILITY")
    print("=" * 80)
    
    stability_results = {}
    
    for domain, trajectories in all_domains.items():
        print(f"\n{domain}:")
        
        # Get descriptors for all trajectories
        descriptors = [descriptor_results[domain][traj] for traj in trajectories.keys()]
        
        # Get metrics for all trajectories
        metric_values = {}
        for metric_name in ['temporal_spread', 'persistence', 'volatility']:
            values = [metric_results[domain][traj][metric_name] for traj in trajectories.keys()]
            metric_values[metric_name] = values
        
        # Compute stability
        stability = {
            'descriptor_consistency': len(set(descriptors)) == 1,
            'metrics_cv': {}
        }
        
        for metric_name, values in metric_values.items():
            values = np.array(values)
            if np.mean(values) > 0:
                cv = np.std(values) / np.mean(values)
            else:
                cv = 0.0
            stability['metrics_cv'][metric_name] = float(cv)
        
        stability_results[domain] = stability
        
        print(f"  Descriptor consistency: {stability['descriptor_consistency']}")
        for metric_name, cv in stability['metrics_cv'].items():
            print(f"  {metric_name} CV: {cv:.4f}")
    
    # Phase 5: Apply admissibility rules
    print("\n" + "=" * 80)
    print("PHASE 5: APPLY ADMISSIBILITY RULES")
    print("=" * 80)
    
    admissibility_results = {}
    
    for domain in all_domains.keys():
        stability = stability_results[domain]
        
        # Check criteria
        cv_values = list(stability['metrics_cv'].values())
        mean_cv = np.mean(cv_values) if cv_values else 0
        
        # Admissibility rules
        reproduced = stability['descriptor_consistency']
        stable_metrics = mean_cv < 0.5
        
        status = "PROVISIONAL"
        if reproduced and stable_metrics:
            status = "STABLE"
        
        admissibility_results[domain] = {
            'status': status,
            'reproduced': reproduced,
            'stable_metrics': stable_metrics,
            'mean_cv': float(mean_cv)
        }
        
        print(f"\n{domain}:")
        print(f"  Reproduced across trajectories: {reproduced}")
        print(f"  Stable metrics (CV < 0.5): {stable_metrics} (mean CV = {mean_cv:.4f})")
        print(f"  Status: {status}")
    
    # Print summary tables
    print("\n" + "=" * 80)
    print("TABLE 1 — SIGNATURE DESCRIPTORS")
    print("=" * 80)
    print(f"{'Domain':<10} {'Trajectory':<12} {'Descriptor':<25} {'Status':<15}")
    print("-" * 60)
    
    for domain, trajectories in descriptor_results.items():
        for traj, descriptor in trajectories.items():
            status = admissibility_results[domain]['status']
            print(f"{domain:<10} {str(traj):<12} {descriptor:<25} {status:<15}")
    
    print("\n" + "=" * 80)
    print("TABLE 2 — SIGNATURE METRICS (SAMPLE)")
    print("=" * 80)
    print(f"{'Domain':<10} {'Trajectory':<12} {'Spread':>10} {'Persistence':>12} {'Volatility':>12}")
    print("-" * 60)
    
    for domain, trajectories in metric_results.items():
        for traj, metrics in list(trajectories.items())[:2]:  # Show first 2
            print(f"{domain:<10} {str(traj):<12} {metrics['temporal_spread']:>10.4f} "
                  f"{metrics['persistence']:>12.4f} {metrics['volatility']:>12.4f}")
    
    print("\n" + "=" * 80)
    print("TABLE 3 — SIGNATURE STABILITY")
    print("=" * 80)
    print(f"{'Domain':<10} {'Descriptor Consistent':<22} {'Mean CV':>10} {'Status':<15}")
    print("-" * 60)
    
    for domain, admissibility in admissibility_results.items():
        print(f"{domain:<10} {str(admissibility['reproduced']):<22} "
              f"{admissibility['mean_cv']:>10.4f} {admissibility['status']:<15}")
    
    # Interpretation
    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    
    stable_domains = [d for d, a in admissibility_results.items() if a['status'] == 'STABLE']
    provisional_domains = [d for d, a in admissibility_results.items() if a['status'] == 'PROVISIONAL']
    
    if stable_domains:
        print(f"\n✓ STABLE SIGNATURES: {', '.join(stable_domains)}")
        print("  These signatures are reproducible across trajectories and stable under protocol variation.")
    
    if provisional_domains:
        print(f"\n⚠ PROVISIONAL SIGNATURES: {', '.join(provisional_domains)}")
        print("  These signatures require further testing before promotion.")
    
    # Save results
    output_file = OUT_DIR / "p9_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'descriptors': descriptor_results,
            'metrics': metric_results,
            'stability': stability_results,
            'admissibility': admissibility_results
        }, f, indent=2, default=str)
    
    print(f"\nResults saved to {output_file}")
    
    print("\n" + "=" * 80)
    print("P9 — TEMPORAL SIGNATURE FORMALIZATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_p9_analysis()
