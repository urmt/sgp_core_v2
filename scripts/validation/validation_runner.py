"""
Validation Runner - Phase A Quick Validation & Phase B Full Runs

NO consciousness, SFH, ontology, or metaphysical terminology.
"""

import numpy as np
import json
import hashlib
import time
import os
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, script_dir)
sys.path.insert(0, os.path.join(script_dir, 'core'))
sys.path.insert(0, os.path.join(script_dir, 'nulls'))


class ValidationRunner:
    """
    Two-phase validation framework.
    
    Phase A: Quick validation (N≤100, k≤50, runtime≤60s)
    Phase B: Full execution (N≤10000, k≤500, trials≥10)
    """
    
    def __init__(self, base_dir: str = '/home/student/sgp_core_v2', seed: int = 42):
        self.base_dir = base_dir
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        self.experiments_dir = os.path.join(base_dir, 'experiments')
        self.outputs_dir = os.path.join(base_dir, 'outputs')
        
        os.makedirs(self.experiments_dir, exist_ok=True)
        os.makedirs(self.outputs_dir, exist_ok=True)
    
    def run_phase_a(self, system_type: str, params: Dict,
                   k_range: Tuple[int, int] = (1, 30),
                   max_runtime: float = 60.0) -> Dict:
        """
        Phase A: Quick validation run.
        
        Returns pass/fail with detailed diagnostics.
        """
        from synthetic_systems import generate_system
        from dk_computation import run_dk_analysis
        
        print(f"\n{'='*60}")
        print(f"PHASE A VALIDATION: {system_type}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        n_original = params.get('n', 50)
        params_a = params.copy()
        params_a['n'] = min(n_original, 100)
        
        print(f"Parameters (Phase A): {params_a}")
        
        try:
            data, meta = generate_system(system_type, **params_a, seed=self.seed)
            print(f"Data generated: shape={data.shape}")
            
            results = run_dk_analysis(data, k_range=k_range, seed=self.seed)
            
            elapsed = time.time() - start_time
            print(f"Runtime: {elapsed:.2f}s")
            
            if elapsed > max_runtime:
                return {
                    'phase': 'a',
                    'status': 'FAIL',
                    'reason': f'Runtime exceeded {max_runtime}s',
                    'elapsed': elapsed
                }
            
            pass_checks = self._run_validation_checks(results, system_type)
            
            output = {
                'phase': 'a',
                'status': 'PASS' if pass_checks['all_pass'] else 'FAIL',
                'checks': pass_checks,
                'results': results,
                'runtime': elapsed,
                'timestamp': datetime.now().isoformat(),
                'params': params_a
            }
            
            self._save_output(output, f'phase_a_{system_type}')
            
            return output
            
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                'phase': 'a',
                'status': 'FAIL',
                'reason': str(e),
                'runtime': elapsed
            }
    
    def run_phase_b(self, system_type: str, params: Dict,
                   k_range: Tuple[int, int] = (1, 100),
                   n_trials: int = 10) -> Dict:
        """
        Phase B: Full execution with multiple trials.
        """
        from synthetic_systems import generate_system
        from dk_computation import run_dk_analysis
        
        print(f"\n{'='*60}")
        print(f"PHASE B FULL RUN: {system_type}")
        print(f"{'='*60}")
        
        trial_results = []
        
        for trial in range(n_trials):
            trial_seed = self.seed + trial
            print(f"\nTrial {trial + 1}/{n_trials} (seed={trial_seed})")
            
            try:
                data, meta = generate_system(system_type, **params, seed=trial_seed)
                results = run_dk_analysis(data, k_range=k_range, seed=trial_seed)
                
                trial_results.append({
                    'trial': trial,
                    'seed': trial_seed,
                    'results': results,
                    'success': True
                })
                
            except Exception as e:
                trial_results.append({
                    'trial': trial,
                    'seed': trial_seed,
                    'error': str(e),
                    'success': False
                })
        
        aggregated = self._aggregate_trials(trial_results)
        
        output = {
            'phase': 'b',
            'status': 'COMPLETE',
            'n_trials': n_trials,
            'successful_trials': sum(1 for r in trial_results if r['success']),
            'aggregated': aggregated,
            'timestamp': datetime.now().isoformat()
        }
        
        self._save_output(output, f'phase_b_{system_type}')
        
        return output
    
    def run_null_comparison(self, data: np.ndarray, null_types: List[str],
                          k_range: Tuple[int, int] = (1, 30)) -> Dict:
        """
        Run null model comparison.
        """
        from dk_computation import run_dk_analysis
        from nulls.null_models import apply_null_model
        
        print(f"\n{'='*60}")
        print(f"NULL MODEL COMPARISON")
        print(f"{'='*60}")
        
        signal_results = run_dk_analysis(data, k_range=k_range, seed=self.seed)
        
        null_results = {}
        
        for null_type in null_types:
            print(f"Testing null: {null_type}")
            
            try:
                null_data, null_meta = apply_null_model(data, null_type, seed=self.seed)
                null_results[null_type] = run_dk_analysis(null_data, k_range=k_range, seed=self.seed)
            except Exception as e:
                null_results[null_type] = {'error': str(e)}
        
        effect_sizes = self._compute_effect_sizes(signal_results, null_results)
        
        output = {
            'signal': signal_results,
            'nulls': null_results,
            'effect_sizes': effect_sizes,
            'timestamp': datetime.now().isoformat()
        }
        
        return output
    
    def _run_validation_checks(self, results: Dict, system_type: str) -> Dict:
        """Run validation checks on results."""
        checks = {}
        
        dk_values = np.array(results['dk_values'])
        
        checks['dk_range_valid'] = bool(
            not np.isnan(dk_values).any() and 
            0 < dk_values.mean() < results['computation_metadata']['n_points']
        )
        
        fit_params = results['fit_params']
        checks['fit_converged'] = bool(results['fit_metadata'].get('converged', False))
        
        if checks['fit_converged']:
            checks['k0_in_range'] = bool(
                0 < fit_params['k0'] < results['computation_metadata']['k_range'][1]
            )
            checks['r_squared_reasonable'] = bool(
                0 <= fit_params['r_squared'] <= 1
            )
        else:
            checks['k0_in_range'] = False
            checks['r_squared_reasonable'] = False
        
        if system_type == 'random_gaussian':
            checks['null_expectation'] = not checks['r_squared_reasonable'] or fit_params['r_squared'] < 0.5
        elif system_type in ['hierarchical', 'sparse']:
            checks['null_expectation'] = checks['r_squared_reasonable'] and fit_params['r_squared'] > 0.5
        
        checks['all_pass'] = all([
            checks['dk_range_valid'],
            checks['fit_converged'],
            checks['r_squared_reasonable']
        ])
        
        return checks
    
    def _aggregate_trials(self, trial_results: List[Dict]) -> Dict:
        """Aggregate results across trials."""
        successful = [r for r in trial_results if r['success']]
        
        if not successful:
            return {'status': 'all_failed'}
        
        k0_values = []
        r2_values = []
        dk_means = []
        
        for r in successful:
            res = r['results']
            k0_values.append(res['fit_params'].get('k0', np.nan))
            r2_values.append(res['fit_params'].get('r_squared', np.nan))
            dk_means.append(np.mean(res['dk_values']))
        
        return {
            'k0_mean': float(np.nanmean(k0_values)),
            'k0_std': float(np.nanstd(k0_values)),
            'r2_mean': float(np.nanmean(r2_values)),
            'r2_std': float(np.nanstd(r2_values)),
            'dk_mean': float(np.nanmean(dk_means)),
            'dk_std': float(np.nanstd(dk_means))
        }
    
    def _compute_effect_sizes(self, signal: Dict, nulls: Dict) -> Dict:
        """Compute effect sizes (signal - null)."""
        effect_sizes = {}
        
        signal_r2 = signal['fit_params'].get('r_squared', 0)
        
        for null_type, null_result in nulls.items():
            if 'error' in null_result:
                effect_sizes[null_type] = {'error': null_result['error']}
                continue
            
            null_r2 = null_result['fit_params'].get('r_squared', 0)
            effect_sizes[null_type] = {
                'r2_delta': float(signal_r2 - null_r2),
                'direction': 'signal_higher' if signal_r2 > null_r2 else 'null_higher'
            }
        
        return effect_sizes
    
    def _save_output(self, output: Dict, name: str):
        """Save output to JSON with metadata."""
        output_path = os.path.join(self.outputs_dir, 'metadata', f'{name}.json')
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"Saved: {output_path}")


if __name__ == '__main__':
    print("Validation Runner")
    print("=" * 50)
    
    runner = ValidationRunner(base_dir='/home/student/sgp_core_v2', seed=42)
    
    print("\n--- Phase A Quick Validation ---")
    result = runner.run_phase_a(
        system_type='random_gaussian',
        params={'n': 50, 'dimensions': 20, 'variance': 1.0},
        k_range=(1, 20)
    )
    
    print(f"\nResult: {result['status']}")
    if 'checks' in result:
        print(f"Checks: {result['checks']}")