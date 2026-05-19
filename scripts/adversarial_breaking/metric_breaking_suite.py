"""
Metric Breaking Suite

NO consciousness, SFH, ontology, or metaphysical terminology.

Test V2_004 metrics against adversarial systems to try to BREAK them.
"""

import numpy as np
import json
import os
from typing import Dict, List, Tuple
import sys

# Add paths
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..', 'core'))
sys.path.insert(0, script_dir)

from synthetic_systems import generate_system
from universal_dk_pipeline import UniversalDkPipeline
from metric_redesign.new_metrics import MetricRedesignSuite
from null_models import apply_null_model
from adversarial_systems import generate_adversarial


class MetricBreakingSuite:
    """Test metrics against adversarial systems."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        # Legitimate systems (from V2_004)
        self.legitimate_systems = {
            'random_gaussian': {'n': 100, 'dimensions': 10},
            'hierarchical': {'n': 100, 'depth': 3},
            'sparse': {'n': 100, 'sparsity': 0.1},
            'oscillator': {'n': 50, 'coupling': 0.5, 'n_timesteps': 100}
        }
        
        # Adversarial systems (new)
        self.adversarial_systems = {
            'fake_hierarchy': {'n': 100, 'dimensions': 10, 'depth': 3, 'noise': 0.5},
            'deceptive_curvature': {'n': 100, 'dimensions': 10, 'curvature_injection': 0.8},
            'false_persistence': {'n': 100, 'dimensions': 10, 'duplication_rate': 0.2},
            'hybrid_null_monster': {'n': 100, 'dimensions': 10, 'deception_strength': 0.5}
        }
        
        self.metric_names = ['curvature_entropy', 'scale_transition', 'topological_persistence']
        self.suite = MetricRedesignSuite(seed=seed)
    
    def run_stress_test(self, n_seeds: int = 5) -> Dict:
        """Run full stress test."""
        results = {
            'legitimate': {},
            'adversarial': {},
            'false_positive_analysis': {},
            'false_negative_analysis': {}
        }
        
        # Test legitimate systems
        print("\n=== Testing Legitimate Systems ===")
        for sys_name, params in self.legitimate_systems.items():
            metrics = self._test_system(sys_name, params, n_seeds)
            results['legitimate'][sys_name] = metrics
            print(f"{sys_name}: curv={metrics.get('curvature', (0,0))[0]:.6f}")
        
        # Test adversarial systems
        print("\n=== Testing Adversarial Systems ===")
        for sys_name, params in self.adversarial_systems.items():
            metrics = self._test_system_adversarial(sys_name, params, n_seeds)
            results['adversarial'][sys_name] = metrics
            print(f"{sys_name}: curv={metrics.get('curvature', (0,0))[0]:.6f}")
        
        # Compute false positive/negative rates
        results['false_positive_analysis'] = self._compute_false_positive_rates(results)
        results['false_negative_analysis'] = self._compute_false_negative_rates(results)
        
        return results
    
    def _test_system(self, sys_name: str, params: Dict, n_seeds: int) -> Dict:
        """Test a legitimate system."""
        metric_values = {m: [] for m in self.metric_names}
        
        for seed_offset in range(n_seeds):
            seed = self.seed + seed_offset
            
            data, _ = generate_system(sys_name, **params, seed=seed)
            metrics = self._compute_metrics(data, sys_name)
            
            for m_name in self.metric_names:
                val = self._extract_metric_value(metrics, m_name)
                if val is not None:
                    metric_values[m_name].append(val)
        
        return {m: (np.mean(v), np.std(v)) for m, v in metric_values.items() if v}
    
    def _test_system_adversarial(self, sys_name: str, params: Dict, n_seeds: int) -> Dict:
        """Test an adversarial system."""
        metric_values = {m: [] for m in self.metric_names}
        
        for seed_offset in range(n_seeds):
            seed = self.seed + seed_offset
            
            data, meta = generate_adversarial(sys_name, **params, seed=seed)
            metrics = self._compute_metrics(data, sys_name)
            
            for m_name in self.metric_names:
                val = self._extract_metric_value(metrics, m_name)
                if val is not None:
                    metric_values[m_name].append(val)
        
        return {m: (np.mean(v), np.std(v)) for m, v in metric_values.items() if v}
    
    def _compute_metrics(self, data: np.ndarray, sys_name: str) -> Dict:
        """Compute metrics for data."""
        k_vals = list(range(1, min(11, data.shape[0] - 1)))
        
        pipeline = UniversalDkPipeline(seed=self.seed)
        dk_results = pipeline.run_full_analysis(data, k_values=k_vals)
        pr = dk_results['participation_ratio']
        
        metrics = self.suite.compute_all(data, pr['k_values'], np.array(pr['dk_values']))
        return metrics
    
    def _extract_metric_value(self, metrics: Dict, metric_name: str) -> float:
        """Extract value from metric dict."""
        mapping = {
            'curvature_entropy': 'curvature_variance',
            'scale_transition': 'instability',
            'topological_persistence': 'persistence_mean'
        }
        
        if metric_name in metrics and 'error' not in metrics[metric_name]:
            return metrics[metric_name].get(mapping.get(metric_name, ''), None)
        return None
    
    def _compute_false_positive_rates(self, results: Dict) -> Dict:
        """Compute false positive rates - adversarial mistaken for legitimate."""
        fpr = {}
        
        for metric in self.metric_names:
            # Get legitimate mean
            leg_vals = []
            for sys_name in results['legitimate']:
                if metric in results['legitimate'][sys_name]:
                    leg_vals.append(results['legitimate'][sys_name][metric][0])
            legit_mean = np.mean(leg_vals) if leg_vals else 0
            
            # Get adversarial means
            adv_vals = []
            for sys_name in results['adversarial']:
                if metric in results['adversarial'][sys_name]:
                    adv_vals.append(results['adversarial'][sys_name][metric][0])
            adv_mean = np.mean(adv_vals) if adv_vals else 0
            
            # Calculate overlap
            if adv_mean > 0 and legit_mean > 0:
                # If adversarial is within 2x of legitimate, consider it "fooling"
                ratio = adv_mean / legit_mean
                fpr[metric] = {
                    'legit_mean': legit_mean,
                    'adv_mean': adv_mean,
                    'ratio': ratio,
                    'fooled': ratio > 0.5  # Within 2x = fooled
                }
        
        return fpr
    
    def _compute_false_negative_rates(self, results: Dict) -> Dict:
        """Compute false negative rates - legitimate mistaken for random."""
        fnr = {}
        
        for metric in self.metric_names:
            random_mean = 0
            organized_mean = 0
            
            if 'random_gaussian' in results['legitimate']:
                if metric in results['legitimate']['random_gaussian']:
                    random_mean = results['legitimate']['random_gaussian'][metric][0]
            
            # Average of organized systems
            organized_vals = []
            for sys_name in ['hierarchical', 'sparse']:
                if sys_name in results['legitimate'] and metric in results['legitimate'][sys_name]:
                    organized_vals.append(results['legitimate'][sys_name][metric][0])
            
            if organized_vals:
                organized_mean = np.mean(organized_vals)
            
            # If ratio is low, we failed to detect organization
            if random_mean > 0 and organized_mean > 0:
                ratio = organized_mean / random_mean
                fnr[metric] = {
                    'random_mean': random_mean,
                    'organized_mean': organized_mean,
                    'discrimination_ratio': ratio,
                    'detection_failed': ratio < 1.5  # Need at least 1.5x
                }
        
        return fnr
    
    def save_results(self, results: Dict, filename: str = 'metric_breakdown.json'):
        """Save results."""
        output_dir = '/home/student/sgp_core_v2/outputs/adversarial_breaking'
        os.makedirs(output_dir, exist_ok=True)
        
        path = os.path.join(output_dir, filename)
        with open(path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"Results saved: {path}")
        return path


def run_stress_test():
    """Run the stress test."""
    print("=" * 60)
    print("METRIC STRESS TEST - ADVERSARIAL BREAKING")
    print("=" * 60)
    
    tester = MetricBreakingSuite(seed=42)
    results = tester.run_stress_test(n_seeds=5)
    
    # Save
    tester.save_results(results, 'stress_test_results.json')
    
    # Print summary
    print("\n" + "=" * 60)
    print("FALSE POSITIVE ANALYSIS (Adversarial Fooling)")
    print("=" * 60)
    
    for metric, analysis in results['false_positive_analysis'].items():
        status = "FOOLED" if analysis['fooled'] else "RESISTED"
        print(f"{metric}: ratio={analysis['ratio']:.2f} [{status}]")
    
    print("\n" + "=" * 60)
    print("DISCRIMINATION (Legitimate vs Random)")
    print("=" * 60)
    
    for metric, analysis in results['false_negative_analysis'].items():
        status = "DETECTED" if not analysis['detection_failed'] else "FAILED"
        print(f"{metric}: ratio={analysis['discrimination_ratio']:.2f}x [{status}]")
    
    return results


if __name__ == '__main__':
    run_stress_test()