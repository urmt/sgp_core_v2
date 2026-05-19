"""
SGP-CORE V2 Cross-Domain Generalization Protocol

Test whether surviving metrics generalize across domains.
"""

import numpy as np
import json
import sys
from typing import Dict, List

sys.path.insert(0, 'scripts/temporal_memory')
sys.path.insert(0, 'scripts/replay_resistance')

from temporal_dynamics import generate_temporal_system
from memory_metrics import (
    InteractionMemoryScore,
    StructuralPersistence,
    TemporalConsensusScore
)
from final_replay_detection import data_drift


DOMAINS = [
    "financial",
    "biological", 
    "language",
    "network",
    "weather"
]


def product_metric(memory: float, persistence: float, consensus: float) -> float:
    """Product-based metric from V2_013."""
    return (memory * persistence * consensus) ** (1/3)


def evaluate_domain(domain: str, n: int, seed: int) -> Dict:
    """
    Evaluate metrics for a domain using temporal systems as proxies.
    """
    # Map domains to temporal systems that simulate their properties
    domain_mapping = {
        "financial": ("stable_hierarchy", {'n': n, 'dimensions': 5, 'n_timesteps': 25}),
        "biological": ("perturb_recover", {'n': n, 'dimensions': 4, 'n_timesteps': 20}),
        "language": ("stable_hierarchy", {'n': n, 'dimensions': 8, 'n_timesteps': 30}),
        "network": ("perturb_recover", {'n': n, 'dimensions': 5, 'n_timesteps': 25}),
        "weather": ("stable_hierarchy", {'n': n, 'dimensions': 3, 'n_timesteps': 40})
    }
    
    system_type, params = domain_mapping[domain]
    
    traj, _ = generate_temporal_system(system_type, seed=seed, **params)
    
    memory = InteractionMemoryScore(seed).compute(traj)['memory_score_mean']
    persistence = StructuralPersistence(seed).compute(traj)['persistence_mean']
    consensus = TemporalConsensusScore(seed).compute(traj)['consensus_mean']
    drift = data_drift(traj)
    
    product = product_metric(memory, persistence, consensus)
    
    # Ratio vs random baseline
    random_traj, _ = generate_temporal_system("random_temporal", seed=seed, **params)
    random_memory = InteractionMemoryScore(seed).compute(random_traj)['memory_score_mean']
    random_persist = StructuralPersistence(seed).compute(random_traj)['persistence_mean']
    random_consensus = TemporalConsensusScore(seed).compute(random_traj)['consensus_mean']
    random_product = product_metric(random_memory, random_persist, random_consensus)
    
    ratio = product / (random_product + 1e-9)
    
    return {
        'domain': domain,
        'memory': memory,
        'persistence': persistence,
        'consensus': consensus,
        'drift': drift,
        'product_score': product,
        'random_baseline': random_product,
        'ratio_vs_random': ratio
    }


def cross_domain_score(metric_results: Dict) -> Dict:
    """Compute cross-domain stability score."""
    ratios = [r['ratio_vs_random'] for r in metric_results.values()]
    
    mean_ratio = np.mean(ratios)
    variance = np.var(ratios)
    stability = 1 / (1 + variance)
    
    return {
        "mean_ratio": mean_ratio,
        "variance": variance,
        "cross_domain_stability": stability
    }


def evaluate_generalization(domain_results: Dict) -> Dict:
    """Evaluate if metrics generalize across domains."""
    stable_count = sum(1 for r in domain_results.values() if r['ratio_vs_random'] > 1.5)
    
    return {
        "stable_domains": stable_count,
        "total_domains": len(domain_results),
        "generalizes": stable_count >= 4
    }


def run_cross_domain_test():
    """Run cross-domain generalization test."""
    np.random.seed(42)
    
    print("=" * 60)
    print("V2_017 CROSS-DOMAIN GENERALIZATION")
    print("=" * 60)
    
    domain_results = {}
    
    print("\n=== EVALUATING DOMAINS ===")
    
    for domain in DOMAINS:
        result = evaluate_domain(domain, n=30, seed=42)
        domain_results[domain] = result
        
        status = "STABLE" if result['ratio_vs_random'] > 1.5 else "WEAK"
        print(f"{domain}: ratio={result['ratio_vs_random']:.2f}x [{status}]")
    
    # Cross-domain analysis
    print("\n=== CROSS-DOMAIN ANALYSIS ===")
    
    cross = cross_domain_score(domain_results)
    print(f"Mean ratio: {cross['mean_ratio']:.2f}x")
    print(f"Variance: {cross['variance']:.4f}")
    print(f"Stability: {cross['cross_domain_stability']:.4f}")
    
    # Generalization verdict
    gen = evaluate_generalization(domain_results)
    print(f"\nStable domains: {gen['stable_domains']}/{gen['total_domains']}")
    print(f"Generalizes: {'YES' if gen['generalizes'] else 'NO'}")
    
    # Save results
    output = '/home/student/sgp_core_v2/outputs/cross_domain_generalization/cross_domain_results.json'
    with open(output, 'w') as f:
        json.dump({
            'domain_results': domain_results,
            'cross_domain_analysis': cross,
            'generalization': gen
        }, f, indent=2, default=str)
    
    print(f"\nSaved: {output}")
    
    return domain_results


if __name__ == '__main__':
    run_cross_domain_test()