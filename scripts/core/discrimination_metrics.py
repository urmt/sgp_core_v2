"""
Adversarial Discrimination Metrics

Metrics that might distinguish organized from random systems:
1. Curvature instability
2. Inflection sharpness  
3. Residual entropy
4. Bootstrap variance
5. Multi-scale derivative consistency

NO consciousness, SFH, ontology, or metaphysical terminology.
"""

import numpy as np
from scipy.stats import entropy
from scipy.special import rel_entr
from typing import Dict, List


class DiscriminationMetrics:
    """Enhanced metrics for adversarial discrimination."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
    
    def compute_curvature_instability(self, k_values: np.ndarray, dk_values: np.ndarray) -> Dict:
        """Measure curvature variation in D(k) curve."""
        # First derivative
        d1 = np.diff(dk_values) / np.diff(k_values)
        # Second derivative
        d2 = np.diff(d1)
        
        curvature_metrics = {
            'd1_mean': float(np.mean(np.abs(d1))),
            'd1_std': float(np.std(d1)),
            'd2_mean': float(np.mean(np.abs(d2))),
            'd2_std': float(np.std(d2)),
            'curvature_variance': float(np.var(d2)),
            'max_curvature': float(np.max(np.abs(d2)))
        }
        
        return curvature_metrics
    
    def compute_inflection_sharpness(self, k_values: np.ndarray, dk_values: np.ndarray) -> Dict:
        """Measure inflection point sharpness (should be higher for non-linear)."""
        # Normalize
        k_norm = (k_values - k_values.min()) / (k_values.max() - k_values.min() + 1e-10)
        dk_norm = (dk_values - dk_values.min()) / (dk_values.max() - dk_values.min() + 1e-10)
        
        # Compute curvature
        d1 = np.gradient(dk_norm, k_norm)
        d2 = np.gradient(d1, k_norm)
        
        # Find inflection (where d2 = 0)
        sign_changes = np.where(np.diff(np.sign(d2)))[0]
        
        return {
            'inflection_count': len(sign_changes),
            'inflection_indices': sign_changes.tolist(),
            'max_d2': float(np.max(np.abs(d2))),
            'mean_d2': float(np.mean(np.abs(d2))),
            'sharpness': float(np.max(np.abs(d2)) / (np.mean(np.abs(d2)) + 1e-10))
        }
    
    def compute_residual_entropy(self, k_values: np.ndarray, dk_values: np.ndarray, 
                                  fit_params: Dict) -> Dict:
        """Measure residual structure (non-random should have lower entropy)."""
        def sigmoid(k, A, k0, beta):
            return A / (1 + np.exp(-beta * (k - k0)))
        
        predicted = sigmoid(k_values, fit_params['A'], fit_params['k0'], fit_params['beta'])
        residuals = dk_values - predicted
        
        # Normalize residuals
        res_norm = (residuals - residuals.mean()) / (residuals.std() + 1e-10)
        
        # Binned entropy
        n_bins = 10
        hist, _ = np.histogram(res_norm, bins=n_bins, density=True)
        hist = hist / (hist.sum() + 1e-10)
        
        return {
            'residual_mean': float(np.mean(np.abs(residuals))),
            'residual_std': float(np.std(residuals)),
            'residual_skew': float(((residuals - residuals.mean())**3).mean() / (residuals.std()**3 + 1e-10)),
            'residual_entropy': float(entropy(hist + 1e-10)),
            'max_residual': float(np.max(np.abs(residuals)))
        }
    
    def compute_bootstrap_variance(self, data: np.ndarray, k_values: List[int], 
                                    n_bootstrap: int = 50) -> Dict:
        """Measure bootstrap variance of k0 estimation."""
        from universal_dk_pipeline import UniversalDkPipeline
        
        k0_estimates = []
        r2_estimates = []
        
        n = data.shape[0]
        
        for _ in range(n_bootstrap):
            indices = self.rng.choice(n, size=n, replace=True)
            bootstrap_data = data[indices]
            
            pipeline = UniversalDkPipeline(seed=self.rng.randint(0, 10000))
            try:
                results = pipeline.run_full_analysis(bootstrap_data, k_values=k_values)
                sig = results['participation_ratio']['sigmoid']
                if sig['converged'] and not np.isnan(sig['k0']):
                    k0_estimates.append(sig['k0'])
                    r2_estimates.append(sig['r_squared'])
            except:
                pass
        
        if len(k0_estimates) > 1:
            return {
                'k0_mean': float(np.mean(k0_estimates)),
                'k0_std': float(np.std(k0_estimates)),
                'k0_cv': float(np.std(k0_estimates) / (np.mean(k0_estimates) + 1e-10)),
                'r2_mean': float(np.mean(r2_estimates)),
                'r2_std': float(np.std(r2_estimates)),
                'collapse_rate': float((n_bootstrap - len(k0_estimates)) / n_bootstrap)
            }
        else:
            return {'error': 'insufficient_estimates'}
    
    def compute_derivative_consistency(self, k_values: np.ndarray, dk_values: np.ndarray,
                                       window_sizes: List[int] = [3, 5, 7]) -> Dict:
        """Measure consistency of derivatives across scales."""
        d1_all = []
        
        for ws in window_sizes:
            if ws < len(k_values):
                d1 = np.diff(dk_values)
                # Simple moving average
                d1_smooth = np.convolve(d1, np.ones(ws)/ws, mode='valid')
                d1_all.append(d1_smooth)
        
        if len(d1_all) >= 2:
            # Correlation between scales
            correlations = []
            for i in range(len(d1_all) - 1):
                min_len = min(len(d1_all[i]), len(d1_all[i+1]))
                corr = np.corrcoef(d1_all[i][:min_len], d1_all[i+1][:min_len])[0, 1]
                correlations.append(corr)
            
            return {
                'cross_scale_correlation': float(np.mean(correlations)),
                'scale_correlations': correlations,
                'consistency_score': float(np.min(correlations))
            }
        else:
            return {'error': 'insufficient_scales'}
    
    def compute_all(self, k_values: List, dk_values: np.ndarray, 
                   fit_params: Dict, data: np.ndarray) -> Dict:
        """Compute all discrimination metrics."""
        k_arr = np.array(k_values)
        
        metrics = {}
        
        metrics['curvature'] = self.compute_curvature_instability(k_arr, dk_values)
        metrics['inflection'] = self.compute_inflection_sharpness(k_arr, dk_values)
        metrics['residual'] = self.compute_residual_entropy(k_arr, dk_values, fit_params)
        metrics['derivative'] = self.compute_derivative_consistency(k_arr, dk_values)
        
        bootstrap = self.compute_bootstrap_variance(data, k_values, n_bootstrap=30)
        if 'error' not in bootstrap:
            metrics['bootstrap'] = bootstrap
        
        return metrics


if __name__ == '__main__':
    print("Discrimination Metrics")
    print("="*50)
    
    from synthetic_systems import generate_system
    from universal_dk_pipeline import UniversalDkPipeline
    
    # Test on random vs hierarchical
    for sys_type in ['random_gaussian', 'hierarchical']:
        data, _ = generate_system(sys_type, n=100, seed=42)
        
        pipeline = UniversalDkPipeline(seed=42)
        results = pipeline.run_full_analysis(data, k_values=list(range(1, 21)))
        
        pr = results['participation_ratio']
        dm = DiscriminationMetrics(seed=42)
        metrics = dm.compute_all(
            pr['k_values'], 
            np.array(pr['dk_values']),
            pr['sigmoid'],
            data
        )
        
        print(f"\\n{sys_type}:")
        print(f"  curvature variance: {metrics['curvature']['curvature_variance']:.6f}")
        print(f"  residual entropy: {metrics['residual']['residual_entropy']:.4f}")
        print(f"  cross-scale corr: {metrics['derivative'].get('cross_scale_correlation', 'N/A')}")
    
    print("\\nMetrics working.")