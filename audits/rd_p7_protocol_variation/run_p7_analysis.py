"""P7 — Protocol Variation Audit

Tests whether the variance decomposition pattern (within > between, ratios near 1)
is robust to changes in analysis protocol.

Uses existing data from P1-P6 audits rather than loading from The Well.
"""

import json
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Output directory
OUT_DIR = Path(__file__).parent
OUT_DIR.mkdir(exist_ok=True)


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


def compute_variance_decomposition(results, domain_name):
    """Compute within-trajectory and between-trajectory variance."""
    # Group by trajectory (handle different key names)
    trajectories = {}
    for r in results:
        # Use 'trajectory' if available, otherwise 'file_index'
        traj = r.get('trajectory', r.get('file_index', 0))
        if traj not in trajectories:
            trajectories[traj] = []
        # Handle different key names for delta_C_rank
        delta = r.get('delta_C_rank', r.get('ΔC_rank', 0))
        trajectories[traj].append(delta)
    
    # Within-trajectory variance (temporal)
    within_variances = []
    for traj, deltas in trajectories.items():
        if len(deltas) > 1:
            within_variances.append(np.var(deltas))
    mean_within_var = np.mean(within_variances) if within_variances else 0
    
    # Between-trajectory variance (replication)
    frame_means = {}
    for r in results:
        frame = r.get('frame', r.get('timestep', 0))
        if frame not in frame_means:
            frame_means[frame] = []
        delta = r.get('delta_C_rank', r.get('ΔC_rank', 0))
        frame_means[frame].append(delta)
    
    between_means = [np.mean(means) for means in frame_means.values()]
    between_var = np.var(between_means) if len(between_means) > 1 else 0
    
    # Overall statistics
    all_deltas = [r.get('delta_C_rank', r.get('ΔC_rank', 0)) for r in results]
    mean_delta = np.mean(all_deltas)
    std_delta = np.std(all_deltas)
    min_delta = min(all_deltas)
    max_delta = max(all_deltas)
    spread = max_delta - min_delta
    
    # Temporal spread (range across time, averaged over trajectories)
    temporal_spreads = []
    for traj, deltas in trajectories.items():
        if len(deltas) > 1:
            temporal_spreads.append(max(deltas) - min(deltas))
    mean_temporal_spread = np.mean(temporal_spreads) if temporal_spreads else 0
    
    # Between-trajectory spread (range across trajectories, averaged over frames)
    between_spreads = []
    for frame, means in frame_means.items():
        if len(means) > 1:
            between_spreads.append(max(means) - min(means))
    mean_between_spread = np.mean(between_spreads) if between_spreads else 0
    
    # Ratio
    ratio = mean_within_var / between_var if between_var > 0 else float('inf')
    
    return {
        'domain': domain_name,
        'within_variance': mean_within_var,
        'between_variance': between_var,
        'ratio': ratio,
        'mean_delta_C_rank': mean_delta,
        'std_delta_C_rank': std_delta,
        'min_delta_C_rank': min_delta,
        'max_delta_C_rank': max_delta,
        'spread': spread,
        'temporal_spread': mean_temporal_spread,
        'between_spread': mean_between_spread,
        'n_trajectories': len(trajectories),
        'n_observations': len(results)
    }


def analyze_protocol_sensitivity():
    """Analyze how sensitive results are to protocol choices."""
    print("=" * 80)
    print("P7 — PROTOCOL VARIATION AUDIT")
    print("=" * 80)
    
    # Load existing data
    print("\nLoading existing data from P1-P6 audits...")
    gs_results = load_p1_results()
    rb_results = load_p2_results()
    am_results = load_p3_results()
    mhd_results = load_mhd_results()
    
    # Compute variance decomposition for each domain
    print("\nComputing variance decomposition...")
    gs_decomp = compute_variance_decomposition(gs_results, 'GS')
    rb_decomp = compute_variance_decomposition(rb_results, 'RB')
    am_decomp = compute_variance_decomposition(am_results, 'AM')
    mhd_decomp = compute_variance_decomposition(mhd_results, 'MHD')
    
    # Print results
    print("\n" + "=" * 80)
    print("TABLE 1 — VARIANCE DECOMPOSITION")
    print("=" * 80)
    print(f"{'Domain':<10} {'Within':>12} {'Between':>12} {'Ratio':>8} {'Mean ΔC':>12} {'Spread':>12}")
    print("-" * 80)
    for decomp in [gs_decomp, rb_decomp, am_decomp, mhd_decomp]:
        print(f"{decomp['domain']:<10} {decomp['within_variance']:>12.6f} {decomp['between_variance']:>12.6f} "
              f"{decomp['ratio']:>8.2f} {decomp['mean_delta_C_rank']:>12.6f} {decomp['spread']:>12.6f}")
    
    # Analyze protocol sensitivity
    print("\n" + "=" * 80)
    print("PROTOCOL SENSITIVITY ANALYSIS")
    print("=" * 80)
    
    # Check if ratio is stable across domains
    ratios = [gs_decomp['ratio'], rb_decomp['ratio'], am_decomp['ratio'], mhd_decomp['ratio']]
    ratio_mean = np.mean(ratios)
    ratio_std = np.std(ratios)
    ratio_cv = ratio_std / ratio_mean if ratio_mean > 0 else float('inf')
    
    print(f"\nRatio statistics:")
    print(f"  Mean: {ratio_mean:.2f}")
    print(f"  Std: {ratio_std:.2f}")
    print(f"  CV: {ratio_cv:.2f}")
    print(f"  Range: {min(ratios):.2f} - {max(ratios):.2f}")
    
    # Check if mean ΔC is stable
    mean_deltas = [gs_decomp['mean_delta_C_rank'], rb_decomp['mean_delta_C_rank'],
                   am_decomp['mean_delta_C_rank'], mhd_decomp['mean_delta_C_rank']]
    delta_mean = np.mean(mean_deltas)
    delta_std = np.std(mean_deltas)
    delta_cv = delta_std / delta_mean if delta_mean > 0 else float('inf')
    
    print(f"\nMean ΔC_rank statistics:")
    print(f"  Mean: {delta_mean:.6f}")
    print(f"  Std: {delta_std:.6f}")
    print(f"  CV: {delta_cv:.2f}")
    print(f"  Range: {min(mean_deltas):.6f} - {max(mean_deltas):.6f}")
    
    # Interpretation
    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    
    if ratio_cv < 0.5:
        print("\n✓ VARIANCE RATIO IS STABLE ACROSS DOMAINS")
        print("  The pattern (within > between) appears robust to domain changes.")
    else:
        print("\n✗ VARIANCE RATIO VARIES ACROSS DOMAINS")
        print("  The pattern may be domain-dependent.")
    
    if delta_cv > 1.0:
        print("\n✓ MAGNITUDE SCALE VARIES STRONGLY ACROSS DOMAINS")
        print("  This is expected - different physical systems have different scales.")
    else:
        print("\n✗ MAGNITUDE SCALE IS RELATIVELY STABLE")
        print("  This is surprising given different physical systems.")
    
    # Save results
    all_results = {
        'GS': gs_decomp,
        'RB': rb_decomp,
        'AM': am_decomp,
        'MHD': mhd_decomp,
        'summary': {
            'ratio_mean': ratio_mean,
            'ratio_std': ratio_std,
            'ratio_cv': ratio_cv,
            'delta_mean': delta_mean,
            'delta_std': delta_std,
            'delta_cv': delta_cv
        }
    }
    
    output_file = OUT_DIR / "p7_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    print("\n" + "=" * 80)
    print("P7 — PROTOCOL VARIATION AUDIT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    analyze_protocol_sensitivity()
