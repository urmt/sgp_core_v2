"""
D(k) Participation Ratio Computation

Computes participation ratio D(k) for k-nearest neighbor distances.
NO consciousness, SFH, ontology, or metaphysical terminology.
"""

import numpy as np
from typing import Tuple, Dict, Optional, List
from scipy.spatial import KDTree
from scipy.optimize import curve_fit
import hashlib
import json
import time


class DkComputer:
    """
    Compute D(k) using participation ratio method.
    
    For each point i, compute:
    - Distance to k nearest neighbors
    - Probability p_ij = d_ij / sum_k(d_ik)
    - Participation ratio D_i = 1 / sum_j(p_ij^2)
    - Average D(k) over all points
    """
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.seed = seed
    
    def compute(self, data: np.ndarray, k_values: Optional[List[int]] = None,
               n_jobs: int = 1) -> Tuple[np.ndarray, Dict]:
        """
        Compute D(k) for range of k values.
        
        Args:
            data: N x D data matrix
            k_values: List of k values to test (default: 1 to min(100, N-1))
            n_jobs: Number of parallel jobs
        
        Returns:
            (k_values, dk_values, metadata)
        """
        n = data.shape[0]
        
        if k_values is None:
            k_max = min(100, n - 1)
            k_values = list(range(1, k_max + 1))
        
        k_values = np.array(k_values)
        k_values = k_values[k_values < n]
        
        dk_values = []
        
        tree = KDTree(data)
        
        for k in k_values:
            distances, indices = tree.query(data, k=k + 1)
            
            dist_sum = distances.sum(axis=1, keepdims=True)
            probs = distances / (dist_sum + 1e-10)
            
            probs_squared = probs ** 2
            D_i = 1.0 / (probs_squared.sum(axis=1) + 1e-10)
            
            dk = D_i.mean()
            dk_values.append(dk)
        
        dk_values = np.array(dk_values)
        
        metadata = {
            'n_points': n,
            'dimensionality': data.shape[1],
            'k_range': [int(k_values.min()), int(k_values.max())],
            'dk_mean': float(dk_values.mean()),
            'dk_std': float(dk_values.std()),
            'seed': self.seed
        }
        
        return k_values, dk_values, metadata
    
    def fit_sigmoid(self, k_values: np.ndarray, dk_values: np.ndarray
                    ) -> Tuple[Dict, Dict]:
        """
        Fit sigmoid model: D(k) = A / (1 + exp(-beta*(k - k0)))
        
        Returns:
            (fit_params, fit_metadata)
        """
        def sigmoid(k, A, k0, beta):
            return A / (1 + np.exp(-beta * (k - k0)))
        
        try:
            popt, pcov = curve_fit(
                sigmoid, k_values, dk_values,
                p0=[dk_values.max(), k_values.mean(), 0.1],
                bounds=([0, 0, 0.01], [dk_values.max() * 2, k_values.max(), 10]),
                maxfev=5000
            )
            
            A, k0, beta = popt
            pred = sigmoid(k_values, *popt)
            
            ss_res = ((dk_values - pred) ** 2).sum()
            ss_tot = ((dk_values - dk_values.mean()) ** 2).sum()
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            fit_params = {
                'A': float(A),
                'k0': float(k0),
                'beta': float(beta),
                'r_squared': float(r_squared)
            }
            
            fit_metadata = {
                'model': 'sigmoid',
                'converged': True,
                'n_points': len(k_values)
            }
            
            return fit_params, fit_metadata
            
        except Exception as e:
            return {
                'A': np.nan,
                'k0': np.nan,
                'beta': np.nan,
                'r_squared': np.nan
            }, {
                'model': 'sigmoid',
                'converged': False,
                'error': str(e)
            }
    
    def compute_full(self, data: np.ndarray, k_values: Optional[List[int]] = None
                     ) -> Dict:
        """
        Compute D(k) and fit model in one call.
        
        Returns complete results dictionary.
        """
        k_vals, dk_vals, meta = self.compute(data, k_values)
        
        fit_params, fit_meta = self.fit_sigmoid(k_vals, dk_vals)
        
        results = {
            'k_values': k_vals.tolist(),
            'dk_values': dk_vals.tolist(),
            'computation_metadata': meta,
            'fit_params': fit_params,
            'fit_metadata': fit_meta,
            'data_hash': hashlib.sha256(data.tobytes()).hexdigest()[:16]
        }
        
        return results


def run_dk_analysis(data: np.ndarray, k_range: Tuple[int, int] = (1, 50),
                    seed: int = 42) -> Dict:
    """
    Run full D(k) analysis pipeline.
    """
    computer = DkComputer(seed=seed)
    
    k_values = list(range(k_range[0], k_range[1] + 1))
    results = computer.compute_full(data, k_values)
    
    return results


if __name__ == '__main__':
    print("D(k) Participation Ratio Computation")
    print("=" * 50)
    
    from synthetic_systems import generate_system
    
    data, _ = generate_system('random_gaussian', n=100, dimensions=20, seed=42)
    results = run_dk_analysis(data, k_range=(1, 30), seed=42)
    
    print(f"Data shape: {data.shape}")
    print(f"D(k) range: {min(results['dk_values']):.3f} - {max(results['dk_values']):.3f}")
    print(f"Fit k0: {results['fit_params']['k0']}")
    print(f"Fit R²: {results['fit_params']['r_squared']:.3f}")
    print("\nComputation complete.")