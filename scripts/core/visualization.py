"""
Visualization Package for SGP-CORE V2

NO consciousness, SFH, ontology, or metaphysical terminology.

Generates:
1. D(k) comparison across systems
2. Null destruction comparison
3. Sigmoid fit examples
4. Residual analysis
5. Parameter stability plots
6. Bootstrap CI plots
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from typing import Dict, List, Optional


class SGPVisualizer:
    """Visualization package for organizational geometry."""
    
    def __init__(self, output_dir: str = '/home/student/sgp_core_v2/outputs/figures'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        plt.style.use('seaborn-v0_8-whitegrid')
    
    def plot_dk_comparison(self, system_results: Dict, filename: str = 'dk_comparison.png'):
        """Plot D(k) curves for multiple systems."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for idx, (system_name, results) in enumerate(system_results.items()):
            dk_values = results['participation_ratio']['dk_values']
            k_values = results['participation_ratio']['k_values']
            
            ax.plot(k_values, dk_values, 'o-', 
                   label=system_name, color=colors[idx % len(colors)],
                   markersize=3, linewidth=1.5)
        
        ax.set_xlabel('k (nearest neighbors)', fontsize=12)
        ax.set_ylabel('D(k) (participation ratio)', fontsize=12)
        ax.set_title('D(k) Comparison Across Systems', fontsize=14)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=150)
        plt.close()
        
        print(f"Saved: {path}")
        return path
    
    def plot_null_comparison(self, signal_results: Dict, null_results: Dict,
                            filename: str = 'null_comparison.png'):
        """Plot signal vs null destruction."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        k_vals = signal_results['participation_ratio']['k_values']
        signal_dk = signal_results['participation_ratio']['dk_values']
        
        axes[0].plot(k_vals, signal_dk, 'o-', label='Signal', 
                    color='#2ca02c', markersize=3)
        
        for null_name, null_res in null_results.items():
            null_dk = null_res['participation_ratio']['dk_values']
            axes[0].plot(k_vals, null_dk, '--', label=null_name, 
                        alpha=0.6, markersize=2)
        
        axes[0].set_xlabel('k')
        axes[0].set_ylabel('D(k)')
        axes[0].set_title('Signal vs Null D(k)')
        axes[0].legend(fontsize=8)
        
        signal_r2 = signal_results['participation_ratio']['sigmoid']['r_squared']
        null_r2s = {name: res['participation_ratio']['sigmoid']['r_squared'] 
                   for name, res in null_results.items()}
        
        names = ['Signal'] + list(null_r2s.keys())
        values = [signal_r2] + list(null_r2s.values())
        colors = ['#2ca02c'] + ['#d62728'] * len(null_r2s)
        
        axes[1].bar(names, values, color=colors)
        axes[1].set_ylabel('Sigmoid R²')
        axes[1].set_title('Model Fit Comparison')
        
        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=150)
        plt.close()
        
        print(f"Saved: {path}")
        return path
    
    def plot_sigmoid_fit(self, k_values: List, dk_values: List, 
                        fit_params: Dict, filename: str = 'sigmoid_fit.png'):
        """Plot sigmoid fit with residuals."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        k_arr = np.array(k_values)
        
        def sigmoid(k, A, k0, beta):
            return A / (1 + np.exp(-beta * (k - k0)))
        
        fitted = sigmoid(k_arr, fit_params['A'], fit_params['k0'], fit_params['beta'])
        
        axes[0].scatter(k_arr, dk_values, s=20, alpha=0.6, label='Data')
        axes[0].plot(k_arr, fitted, 'r-', linewidth=2, 
                    label=f"Fit (k0={fit_params['k0']:.1f}, R²={fit_params['r_squared']:.3f})")
        
        axes[0].axvline(x=fit_params['k0'], color='gray', linestyle='--', 
                       alpha=0.5, label=f'k0 = {fit_params["k0"]:.1f}')
        
        axes[0].set_xlabel('k')
        axes[0].set_ylabel('D(k)')
        axes[0].set_title('Sigmoid Fit')
        axes[0].legend()
        
        residuals = np.array(dk_values) - fitted
        axes[1].scatter(k_arr, residuals, s=20, alpha=0.6)
        axes[1].axhline(y=0, color='r', linestyle='--')
        axes[1].set_xlabel('k')
        axes[1].set_ylabel('Residual')
        axes[1].set_title('Residual Analysis')
        
        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=150)
        plt.close()
        
        print(f"Saved: {path}")
        return path
    
    def plot_bootstrap_ci(self, k_values: List, bootstrap_results: Dict,
                          filename: str = 'bootstrap_ci.png'):
        """Plot bootstrap confidence intervals."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        k_arr = np.array(k_values)
        mean = np.array(bootstrap_results['dk_mean'])
        lower = np.array(bootstrap_results['ci_lower'])
        upper = np.array(bootstrap_results['ci_upper'])
        
        ax.fill_between(k_arr, lower, upper, alpha=0.3, color='blue', label='95% CI')
        ax.plot(k_arr, mean, 'o-', color='blue', markersize=3, label='Mean')
        
        ax.set_xlabel('k')
        ax.set_ylabel('D(k)')
        ax.set_title('Bootstrap Confidence Intervals')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=150)
        plt.close()
        
        print(f"Saved: {path}")
        return path
    
    def plot_parameter_stability(self, trial_results: List, 
                                 filename: str = 'param_stability.png'):
        """Plot parameter stability across trials."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        k0_values = [r['fit_params']['k0'] for r in trial_results if 'k0' in r.get('fit_params', {})]
        r2_values = [r['fit_params']['r_squared'] for r in trial_results]
        
        axes[0, 0].plot(k0_values, 'o-')
        axes[0, 0].set_ylabel('k0')
        axes[0, 0].set_title('k0 Stability')
        
        axes[0, 1].plot(r2_values, 'o-')
        axes[0, 1].set_ylabel('R²')
        axes[0, 1].set_title('R² Stability')
        
        axes[1, 0].hist(k0_values, bins=10, alpha=0.7)
        axes[1, 0].set_xlabel('k0')
        axes[1, 0].set_title('k0 Distribution')
        
        axes[1, 1].hist(r2_values, bins=10, alpha=0.7)
        axes[1, 1].set_xlabel('R²')
        axes[1, 1].set_title('R² Distribution')
        
        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=150)
        plt.close()
        
        print(f"Saved: {path}")
        return path
    
    def plot_all_estimators(self, results: Dict, filename: str = 'all_estimators.png'):
        """Plot all estimator outputs."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        pr = results['participation_ratio']
        axes[0, 0].plot(pr['k_values'], pr['dk_values'], 'o-')
        axes[0, 0].set_title('Participation Ratio')
        
        lb = results.get('levina_bickel', {})
        if lb.get('dk_values'):
            axes[0, 1].plot(lb['k_values'], lb['dk_values'], 'o-')
            axes[0, 1].set_title('Levina-Bickel MLE')
        
        pca = results.get('local_pca_rank', {})
        if pca.get('dk_values'):
            axes[1, 0].plot(pca['k_values'], pca['dk_values'], 'o-')
            axes[1, 0].set_title('Local PCA Rank')
        
        if pr.get('bootstrap'):
            bs = pr['bootstrap']
            axes[1, 1].fill_between(pr['k_values'], bs['ci_lower'], bs['ci_upper'], 
                                    alpha=0.3)
            axes[1, 1].plot(pr['k_values'], pr['dk_values'], 'o-')
            axes[1, 1].set_title('Bootstrap CI')
        
        plt.tight_layout()
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=150)
        plt.close()
        
        print(f"Saved: {path}")
        return path


if __name__ == '__main__':
    print("SGP-CORE V2 Visualization Package")
    print("=" * 50)
    
    vis = SGPVisualizer()
    
    print("Testing visualization...")
    
    from scripts.core.synthetic_systems import generate_system
    from scripts.core.universal_dk_pipeline import UniversalDkPipeline
    
    data, _ = generate_system('random_gaussian', n=100, dimensions=20, seed=42)
    pipeline = UniversalDkPipeline(seed=42)
    results = pipeline.run_full_analysis(data, k_values=list(range(1, 21)))
    
    vis.plot_all_estimators(results, 'test_estimators.png')
    vis.plot_sigmoid_fit(
        results['participation_ratio']['k_values'],
        results['participation_ratio']['dk_values'],
        results['participation_ratio']['sigmoid'],
        'test_sigmoid.png'
    )
    
    print("Visualization working.")