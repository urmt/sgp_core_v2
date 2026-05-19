#!/usr/bin/env python3
"""
SGP-CORE V2 Synthetic Foundation Pipeline

Main entry point for synthetic system validation.

NO consciousness, SFH, ontology, or metaphysical terminology.

Usage:
    python main_pipeline.py --system random_gaussian --phase a
    python main_pipeline.py --system hierarchical --phase b --trials 10
"""

import argparse
import os
import sys
import json
import hashlib
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description='SGP-CORE V2 Synthetic Pipeline')
    parser.add_argument('--system', type=str, required=True,
                       choices=['random_gaussian', 'hierarchical', 'sparse', 'attractor', 'oscillator'],
                       help='Synthetic system type')
    parser.add_argument('--phase', type=str, required=True,
                       choices=['a', 'b', 'null'],
                       help='Phase: a=quick validation, b=full run, null=comparison')
    parser.add_argument('--n', type=int, default=50, help='Number of points')
    parser.add_argument('--dims', type=int, default=20, help='Dimensions')
    parser.add_argument('--k-range', type=int, nargs=2, default=[1, 30], help='k range')
    parser.add_argument('--trials', type=int, default=10, help='Number of trials (phase b)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--null-types', type=str, nargs='+', 
                       default=['type_i_random_shuffle', 'type_ii_topology_shuffle'],
                       help='Null model types')
    
    args = parser.parse_args()
    
    from scripts.core.synthetic_systems import generate_system
    from scripts.core.dk_computation import run_dk_analysis
    from scripts.validation.validation_runner import ValidationRunner
    from scripts.nulls.null_models import apply_null_model
    
    base_dir = '/home/student/sgp_core_v2'
    os.makedirs(base_dir, exist_ok=True)
    
    print("=" * 70)
    print("SGP-CORE V2 SYNTHETIC FOUNDATION PIPELINE")
    print(f"System: {args.system}, Phase: {args.phase}")
    print("=" * 70)
    
    system_params = _get_system_params(args.system, args.n, args.dims)
    
    runner = ValidationRunner(base_dir=base_dir, seed=args.seed)
    
    if args.phase == 'a':
        result = runner.run_phase_a(
            system_type=args.system,
            params=system_params,
            k_range=tuple(args.k_range)
        )
        
        print(f"\n{'='*70}")
        print(f"PHASE A RESULT: {result['status']}")
        print(f"{'='*70}")
        
        if result['status'] == 'PASS':
            print("✓ Quick validation PASSED")
            print("  → Ready for Phase B full runs")
        else:
            print(f"✗ Quick validation FAILED: {result.get('reason', 'Unknown')}")
            print("  → Fix issues before proceeding")
    
    elif args.phase == 'b':
        print(f"\nRunning Phase B with {args.trials} trials...")
        
        result = runner.run_phase_b(
            system_type=args.system,
            params=system_params,
            k_range=tuple(args.k_range),
            n_trials=args.trials
        )
        
        print(f"\n{'='*70}")
        print(f"PHASE B RESULT: {result['status']}")
        print(f"Successful trials: {result['successful_trials']}/{result['n_trials']}")
        print(f"{'='*70}")
        
        if 'aggregated' in result:
            agg = result['aggregated']
            print(f"k0 mean: {agg.get('k0_mean', 'N/A'):.3f} ± {agg.get('k0_std', 0):.3f}")
            print(f"R² mean: {agg.get('r2_mean', 'N/A'):.3f} ± {agg.get('r2_std', 0):.3f}")
    
    elif args.phase == 'null':
        print("\nGenerating original data...")
        data, meta = generate_system(args.system, **system_params, seed=args.seed)
        
        print(f"Running null comparison...")
        result = runner.run_null_comparison(
            data=data,
            null_types=args.null_types,
            k_range=tuple(args.k_range)
        )
        
        print(f"\n{'='*70}")
        print("NULL COMPARISON RESULTS")
        print(f"{'='*70}")
        
        signal_r2 = result['signal']['fit_params']['r_squared']
        print(f"Signal R²: {signal_r2:.3f}")
        
        for null_type, effect in result['effect_sizes'].items():
            if 'error' not in effect:
                print(f"{null_type}: ΔR² = {effect['r2_delta']:.3f} ({effect['direction']})")
        
        effect_size = result['effect_sizes']
        significant_effects = [k for k, v in effect_size.items() 
                              if 'r2_delta' in v and abs(v['r2_delta']) > 0.1]
        
        if significant_effects:
            print(f"\n✓ Significant effects: {significant_effects}")
        else:
            print(f"\n✗ No significant effects detected")


def _get_system_params(system_type: str, n: int, dims: int) -> dict:
    """Get parameters for system type."""
    params_map = {
        'random_gaussian': {'n': n, 'dimensions': dims, 'variance': 1.0},
        'hierarchical': {'n': n, 'depth': 3, 'branching': 3, 'cluster_std': 0.5},
        'sparse': {'n': n, 'sparsity': 0.1, 'connected': True},
        'attractor': {'n_timesteps': n, 'system_type': 'limit_cycle', 'noise': 0.01},
        'oscillator': {'n': n, 'coupling': 0.5, 'n_timesteps': 100}
    }
    return params_map.get(system_type, {})


if __name__ == '__main__':
    main()