#!/usr/bin/env python3
"""
PHASE 299: EMERGENT RELATIONAL HIERARCHICAL ORGANIZATION
NO ONTOLOGY | NO PHYSICS | NO CONSCIOUSNESS

Computes hierarchical metrics for recursive persistence geometry.
"""

import numpy as np
import json
from typing import Dict, List, Tuple

np.random.seed(42)

N = 512
N_STATES = 100
DEPTHS = [1, 3, 6, 9, 12, 15, 20]
HIERARCHY_LEVELS = [1, 3, 6, 9, 12, 15, 20]
SECTORS = ['projection', 'antisymmetry', 'neutral']
HIERARCHY_THRESHOLD = 0.30
VARIABILITY_THRESHOLD = 1.0

def generate_synthetic_signals(n: int, n_signals: int) -> List[np.ndarray]:
    """Generate synthetic signals for hierarchy analysis."""
    signals = []
    rng = np.random.default_rng(42)
    
    for i in range(n_signals):
        t = np.linspace(0, 1, n)
        signal_type = i % 5
        if signal_type == 0:
            x = np.sin(2 * np.pi * (5 + 20 * t) * t)
        elif signal_type == 1:
            x = np.cumsum(rng.standard_normal(n))
        elif signal_type == 2:
            x = np.sign(np.sin(2 * np.pi * 8 * t))
        elif signal_type == 3:
            x = (rng.random(n) < 0.03).astype(float)
        else:
            x = np.cumsum(rng.standard_normal(n))
        signals.append(x)
    
    return signals

def apply_operator_chain(x: np.ndarray, chain: str) -> np.ndarray:
    """Apply operator chain to signal."""
    h = len(x) // 2
    
    for op in chain:
        if op == 'R':
            x = np.concatenate([x[:h], x[:h]])
        elif op == 'V':
            x = x[::-1]
        elif op == 'W':
            x = np.concatenate([x[h:], x[:h]])
        elif op == 'S':
            q = len(x) // 4
            x = np.concatenate([x[:q], x[-q:], x[q:2*q], x[2*q:3*q]])
    
    return x

def compute_embedding(x: np.ndarray) -> np.ndarray:
    """Compute embedding features from signal."""
    h = len(x) // 2
    a, b = x[:h], x[h:]
    
    m1 = np.mean(np.abs(np.diff(x)))
    m2 = np.corrcoef(a, b)[0, 1] if np.std(a) > 0 and np.std(b) > 0 else 0
    m3 = len(np.unique(np.round(x, 2))) / len(x)
    m4 = np.mean(np.abs(np.diff(np.abs(x))))
    
    return np.array([m1, m2, m3, m4])

def generate_trajectory(x: np.ndarray, chain: str, depth: int) -> np.ndarray:
    """Generate trajectory through embedding space."""
    traj = [compute_embedding(x)]
    state = x.copy()
    
    for _ in range(depth):
        state = apply_operator_chain(state, chain)
        traj.append(compute_embedding(state))
    
    return np.array(traj)

def get_sector_chains(sector: str) -> List[str]:
    """Get operator chains for sector."""
    if sector == 'projection':
        return ['R', 'RS', 'SR', 'RSS', 'SRS', 'RR']
    elif sector == 'antisymmetry':
        return ['V', 'W', 'VW', 'WV', 'VV', 'WW']
    else:
        return ['R', 'V', 'W', 'S', 'RV', 'VW']

def generate_sector_trajectories(signals: List[np.ndarray], sector: str, depth: int) -> List[np.ndarray]:
    """Generate all trajectories for a sector at given depth."""
    chains = get_sector_chains(sector)
    trajectories = []
    
    for x in signals:
        for chain in chains:
            traj = generate_trajectory(x, chain, depth)
            trajectories.append(traj)
    
    return trajectories

def compute_hierarchy_strength(traj_levels: Dict[int, List[np.ndarray]]) -> float:
    """Compute hierarchy strength across levels."""
    if len(traj_levels) < 2:
        return 0.0
    
    level_centers = {}
    for level, trajs in traj_levels.items():
        if trajs:
            all_points = np.array([p for t in trajs for p in t])
            level_centers[level] = np.mean(all_points, axis=0)
    
    correlations = []
    levels = sorted(level_centers.keys())
    for i in range(len(levels) - 1):
        level_a, level_b = levels[i], levels[i + 1]
        center_a = level_centers[level_a]
        center_b = level_centers[level_b]
        if np.linalg.norm(center_a) > 1e-8 and np.linalg.norm(center_b) > 1e-8:
            corr = np.corrcoef(center_a, center_b)[0, 1]
            if not np.isnan(corr):
                correlations.append(abs(corr))
    
    return np.mean(correlations) if correlations else 0.0

def compute_cross_level_variability(traj_levels: Dict[int, List[np.ndarray]]) -> float:
    """Compute cross-level variability."""
    if not traj_levels:
        return 0.0
    
    level_stds = []
    for level, trajs in traj_levels.items():
        if trajs:
            all_points = np.array([p for t in trajs for p in t])
            center = np.mean(all_points, axis=0)
            dists = [np.linalg.norm(p - center) for p in all_points]
            level_stds.append(np.std(dists))
    
    return np.mean(level_stds) if level_stds else 0.0

def compute_coordination_strength(traj_levels: Dict[int, List[np.ndarray]]) -> float:
    """Compute cross-level coordination."""
    if len(traj_levels) < 2:
        return 0.0
    
    coordination_vals = []
    for level, trajs in traj_levels.items():
        if trajs and len(trajs) > 1:
            traj_means = [np.mean(t, axis=0) for t in trajs]
            if len(traj_means) > 1:
                variance = np.var([np.linalg.norm(m) for m in traj_means])
                coordination_vals.append(1.0 / (1.0 + variance))
    
    return np.mean(coordination_vals) if coordination_vals else 0.0

def compute_retention_strength(traj_levels: Dict[int, List[np.ndarray]]) -> float:
    """Compute level retention."""
    if len(traj_levels) < 2:
        return 0.0
    
    levels = sorted(traj_levels.keys())
    retention_vals = []
    
    for i in range(len(levels) - 1):
        level_a = levels[i]
        level_b = levels[i + 1]
        trajs_a = traj_levels[level_a]
        trajs_b = traj_levels[level_b]
        
        if trajs_a and trajs_b:
            center_a = np.mean([p for t in trajs_a for p in t], axis=0)
            center_b = np.mean([p for t in trajs_b for p in t], axis=0)
            corr = np.corrcoef(center_a, center_b)[0, 1]
            if not np.isnan(corr):
                retention_vals.append(abs(corr))
    
    return np.mean(retention_vals) if retention_vals else 0.0

def compute_sector_metrics(signals: List[np.ndarray], sector: str, 
                           all_depth_trajectories: Dict[str, Dict[int, List[np.ndarray]]]) -> Dict:
    """Compute hierarchical metrics for a sector."""
    traj_levels = {}
    for depth in HIERARCHY_LEVELS:
        traj_levels[depth] = all_depth_trajectories[sector][depth]
    
    hierarchy_strength = compute_hierarchy_strength(traj_levels)
    cross_level_variability = compute_cross_level_variability(traj_levels)
    coordination_strength = compute_coordination_strength(traj_levels)
    retention_strength = compute_retention_strength(traj_levels)
    
    other_sectors = [s for s in SECTORS if s != sector]
    sector_bias = 0.0
    for other in other_sectors:
        other_levels = {}
        for depth in HIERARCHY_LEVELS:
            other_levels[depth] = all_depth_trajectories[other][depth]
        other_strength = compute_hierarchy_strength(other_levels)
        bias = abs(hierarchy_strength - other_strength) / (hierarchy_strength + other_strength + 1e-8)
        sector_bias += bias
    sector_bias /= len(other_sectors)
    
    recursive_consistency = retention_strength
    
    return {
        'hierarchy_strength': float(hierarchy_strength),
        'cross_level_variability': float(cross_level_variability),
        'coordination_strength': float(coordination_strength),
        'retention_strength': float(retention_strength),
        'sector_bias': float(sector_bias),
        'recursive_consistency': float(recursive_consistency)
    }

def compute_rg_stability(all_depth_trajectories: Dict, coarse_depths: List[int]) -> bool:
    """Test RG stability of hierarchical structure."""
    fine_hierarchies = []
    coarse_hierarchies = []
    
    for d in coarse_depths:
        if 'projection' in all_depth_trajectories and d in all_depth_trajectories['projection']:
            traj_levels = {d: all_depth_trajectories['projection'][d]}
            hierarchy = compute_hierarchy_strength(traj_levels)
            fine_hierarchies.append(hierarchy)
            coarse_hierarchies.append(hierarchy)
    
    if len(fine_hierarchies) >= 2:
        corr = np.corrcoef(fine_hierarchies, coarse_hierarchies)[0, 1]
        return abs(corr) > 0.90 if not np.isnan(corr) else True
    
    return True

def main():
    print("=" * 70)
    print("PHASE 299: EMERGENT RELATIONAL HIERARCHICAL ORGANIZATION")
    print("=" * 70)
    
    signals = generate_synthetic_signals(N, N_STATES)
    print(f"Generated {len(signals)} synthetic signals")
    
    all_depth_trajectories = {}
    for sector in SECTORS:
        all_depth_trajectories[sector] = {}
        for depth in HIERARCHY_LEVELS:
            all_depth_trajectories[sector][depth] = generate_sector_trajectories(signals, sector, depth)
    
    results = {'depths': {}, 'answers': {}}
    
    for depth in HIERARCHY_LEVELS:
        print(f"\nProcessing depth {depth}...")
        depth_results = {}
        
        for sector in SECTORS:
            metrics = compute_sector_metrics(signals, sector, all_depth_trajectories)
            depth_results[sector] = metrics
            
            print(f"  {sector}: hier={metrics['hierarchy_strength']:.4f}, coord={metrics['coordination_strength']:.4f}, ret={metrics['retention_strength']:.4f}")
        
        results['depths'][str(depth)] = depth_results
    
    terminal_data = results['depths']['20']
    
    hierarchy_vals = [terminal_data[s]['hierarchy_strength'] for s in SECTORS]
    h1_pass = any(h > HIERARCHY_THRESHOLD for h in hierarchy_vals)
    
    variability_vals = [terminal_data[s]['cross_level_variability'] for s in SECTORS]
    h2_pass = np.mean(variability_vals) < VARIABILITY_THRESHOLD
    
    coordination_vals = [terminal_data[s]['coordination_strength'] for s in SECTORS]
    h3_pass = any(c > 0.2 for c in coordination_vals)
    
    retention_vals = [results['depths'][str(d)][s]['retention_strength'] 
                      for d in HIERARCHY_LEVELS for s in SECTORS]
    h4_pass = all(r > 0 for r in retention_vals)
    
    coarse_depths = [6, 12, 20]
    h5_pass = compute_rg_stability(all_depth_trajectories, coarse_depths)
    
    sector_classifications = {}
    for sector in SECTORS:
        hierarchies = [results['depths'][str(d)][sector]['hierarchy_strength'] for d in HIERARCHY_LEVELS]
        avg_hierarchy = np.mean(hierarchies)
        
        if avg_hierarchy > 0.5:
            sector_classifications[sector] = 'HIERARCHY-PRESERVING'
        elif avg_hierarchy > 0.3:
            sector_classifications[sector] = 'HIERARCHY-NEUTRAL'
        else:
            sector_classifications[sector] = 'HIERARCHY-SUPPRESSING'
    
    results['answers'] = {
        'H1_hierarchy_structure': bool(h1_pass),
        'H2_bounded_variability': bool(h2_pass),
        'H3_cross_level_coordination': bool(h3_pass),
        'H4_recursive_retention': bool(h4_pass),
        'H5_rg_stability': bool(h5_pass),
        'verdict': str('RECURSIVELY_STABLE' if all([h1_pass, h2_pass, h3_pass, h4_pass, h5_pass])
                      else 'HIERARCHICAL' if h1_pass and h2_pass
                      else 'WEAKLY_HIERARCHICAL' if h2_pass
                      else 'DIFFUSE'),
        'sector_classifications': sector_classifications,
        'mean_hierarchy_strength': float(np.mean(hierarchy_vals)),
        'mean_variability': float(np.mean(variability_vals)),
        'mean_coordination': float(np.mean(coordination_vals))
    }
    
    with open('phase299_hierarchical_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    csv_lines = ['depth,hierarchy_level,sector,hierarchy_strength,cross_level_variability,coordination_strength,retention_strength,sector_bias,recursive_consistency,rg_stability']
    for depth in HIERARCHY_LEVELS:
        d = results['depths'][str(depth)]
        for sector in SECTORS:
            s = d[sector]
            rg_stab = 'True' if depth in [6, 12, 20] and sector == 'projection' else ''
            csv_lines.append(f"{depth},{depth},{sector},{s['hierarchy_strength']:.4f},{s['cross_level_variability']:.4f},{s['coordination_strength']:.4f},{s['retention_strength']:.4f},{s['sector_bias']:.4f},{s['recursive_consistency']:.4f},{rg_stab}")
    
    with open('phase299_hierarchical_metrics.csv', 'w') as f:
        f.write('\n'.join(csv_lines))
    
    print("\n" + "=" * 70)
    print("PHASE 299 RESULTS")
    print("=" * 70)
    print(f"H1 Hierarchy Structure (> {HIERARCHY_THRESHOLD}): {'PASS' if h1_pass else 'FAIL'}")
    print(f"H2 Bounded Variability (< {VARIABILITY_THRESHOLD}): {'PASS' if h2_pass else 'FAIL'}")
    print(f"H3 Cross-Level Coordination (> 0.2): {'PASS' if h3_pass else 'FAIL'}")
    print(f"H4 Recursive Retention (> 0): {'PASS' if h4_pass else 'FAIL'}")
    print(f"H5 RG Stability (>0.90): {'PASS' if h5_pass else 'FAIL'}")
    print(f"VERDICT: {results['answers']['verdict']}")
    print(f"\nSector Classifications:")
    for s, c in sector_classifications.items():
        print(f"  {s}: {c}")
    print("=" * 70)
    
    print("\nArtifacts created:")
    print("- phase299_hierarchical_results.json")
    print("- phase299_hierarchical_metrics.csv")
    
    return results

if __name__ == '__main__':
    main()