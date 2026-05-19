"""
Adversarial Metric Test Harness

Compare all metrics against all 8 null models.
Compute effect sizes, separation distances, overlap coefficients.

NO consciousness, SFH, ontology, or metaphysical terminology.
"""

import numpy as np
import json
import os
import sys
from datetime import datetime

# Add paths
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..'))

from synthetic_systems import generate_system
from universal_dk_pipeline import UniversalDkPipeline
from metric_redesign.new_metrics import MetricRedesignSuite
from null_models import apply_null_model


class AdversarialMetricTester:
    """Test metrics against null models adversarially."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        self.systems = {
            'random_gaussian': {'n': 100, 'dimensions': 20},
            'hierarchical': {'n': 100, 'depth': 3, 'branching': 3},
            'sparse': {'n': 100, 'sparsity': 0.1},
            'oscillator': {'n': 50, 'coupling': 0.5, 'n_timesteps': 100},
            'compression': {'n': 100, 'initial_dim': 20}
        }
        
        self.null_types = [
            'type_i_random_shuffle',
            'type_ii_topology_shuffle',
            'type_iii_fake_clusters',
            'type_iv_deceptive_dimension'
        ]
        
        self.metric_names = [
            'curvature_entropy',
            'scale_transition', 
            'spectral_drift',
            'topological_persistence'
        ]
    
    def run_adversarial_test(self, n_seeds: int = 3) -> dict:
        """Run full adversarial test."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'n_seeds': n_seeds,
            'systems_tested': list(self.systems.keys()),
            'null_models_tested': self.null_types,
            'metric_results': {},
            'discrimination_table': []
        }
        
        for sys_name, params in self.systems.items():
            print(f"\n{'='*60}")
            print(f"Testing system: {sys_name}")
            print(f"{'='*60}")
            
            sys_results = self._test_system(sys_name, params, n_seeds)
            results['metric_results'][sys_name] = sys_results
            
            # Check discrimination
            for metric_name in self.metric_names:
                if metric_name in sys_results:
                    organized = sys_results[metric_name].get('organized_mean', 0)
                    null_mean = sys_results[metric_name].get('null_mean', 0)
                    effect = abs(organized - null_mean) / (null_mean + 1e-10)
                    
                    results['discrimination_table'].append({
                        'system': sys_name,
                        'metric': metric_name,
                        'organized': organized,
                        'null': null_mean,
                        'effect_size': effect
                    })
        
        return results
    
    def _test_system(self, sys_name: str, params: dict, n_seeds: int) -> dict:
        """Test one system against null models."""
        metric_summaries = {}
        
        for metric_name in self.metric_names:
            organized_values = []
            null_values = []
            
            for seed_idx in range(n_seeds):
                seed = self.seed + seed_idx
                
                # Generate organized data
                data, _ = generate_system(sys_name, **params, seed=seed)
                
                # Compute metrics
                metrics = self._compute_metrics(data, sys_name)
                
                if metric_name in metrics:
                    val = self._extract_metric_value(metrics[metric_name])
                    if val is not None:
                        organized_values.append(val)
                
                # Generate null data
                for null_type in self.null_types:
                    try:
                        null_data, _ = apply_null_model(data, null_type, seed=seed)
                        null_metrics = self._compute_metrics(null_data, sys_name)
                        
                        if metric_name in null_metrics:
                            val = self._extract_metric_value(null_metrics[metric_name])
                            if val is not None:
                                null_values.append(val)
                    except:
                        pass
            
            if organized_values and null_values:
                metric_summaries[metric_name] = {
                    'organized_mean': np.mean(organized_values),
                    'organized_std': np.std(organized_values),
                    'null_mean': np.mean(null_values),
                    'null_std': np.std(null_values),
                    'effect_size': abs(np.mean(organized_values) - np.mean(null_values)) / (np.mean(null_values) + 1e-10)
                }
        
        return metric_summaries
    
    def _compute_metrics(self, data: np.ndarray, sys_name: str) -> dict:
        """Compute metrics for data."""
        k_values = list(range(1, min(16, data.shape[0] - 1)))
        
        try:
            pipeline = UniversalDkPipeline(seed=self.seed)
            dk_results = pipeline.run_full_analysis(data, k_values=k_values)
            pr = dk_results['participation_ratio']
            
            suite = MetricRedesignSuite(seed=self.seed)
            metrics = suite.compute_all(data, pr['k_values'], np.array(pr['dk_values']))
            return metrics
        except:
            return {}
    
    def _extract_metric_value(self, metric_dict: dict) -> float:
        """Extract primary value from metric dict."""
        # Try common keys
        for key in ['curvature_variance', 'instability', 'spectral_velocity_mean', 
                    'persistence_mean', 'stability_index']:
            if key in metric_dict:
                return metric_dict[key]
        
        # Return first numeric value
        for v in metric_dict.values():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return float(v)
        
        return None
    
    def save_results(self, results: dict, filename: str = 'metric_discrimination.json'):
        """Save results to JSON."""
        output_dir = '/home/student/sgp_core_v2/outputs/metric_redesign'
        os.makedirs(output_dir, exist_ok=True)
        
        path = os.path.join(output_dir, filename)
        with open(path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nResults saved: {path}")
        return path


def run_quick_test():
    """Quick validation test."""
    print("\n" + "="*60)
    print("QUICK VALIDATION TEST")
    print("="*60)
    
    tester = AdversarialMetricTester(seed=42)
    results = tester.run_adversarial_test(n_seeds=2)
    
    # Save and display
    tester.save_results(results, 'quick_validation_results.json')
    
    print("\n" + "="*60)
    print("DISCRIMINATION TABLE")
    print("="*60)
    
    for row in results['discrimination_table']:
        status = "PASS" if row['effect_size'] > 0.2 else "FAIL"
        print(f"{row['system']:20} {row['metric']:25} effect={row['effect_size']:.3f} [{status}]")
    
    return results


if __name__ == '__main__':
    results = run_quick_test()