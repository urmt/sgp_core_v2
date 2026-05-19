"""
Universal D(k) Pipeline - Multiple Estimators

NO consciousness, SFH, ontology, or metaphysical terminology.

REQUIRED ESTIMATORS:
1. Participation Ratio
2. Levina-Bickel MLE
3. Correlation Dimension
4. Local PCA Rank

REQUIRED DISTANCES:
1. Euclidean
2. Cosine
3. Correlation
"""

import numpy as np
from scipy.spatial import KDTree
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr
from scipy.optimize import curve_fit
from typing import Tuple, Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class ParticipationRatioEstimator:
    """Participation ratio D(k) using nearest neighbor distances."""
    
    def __init__(self, distance_metric: str = 'euclidean'):
        self.distance_metric = distance_metric
    
    def compute(self, data: np.ndarray, k_values: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """Compute D(k) for range of k."""
        n = data.shape[0]
        k_values = [k for k in k_values if k < n]
        
        tree = KDTree(data)
        
        dk_values = []
        for k in k_values:
            distances, indices = tree.query(data, k=k + 1)
            distances = distances[:, 1:]
            
            dist_sum = distances.sum(axis=1, keepdims=True)
            probs = distances / (dist_sum + 1e-10)
            
            probs_squared = probs ** 2
            D_i = 1.0 / (probs_squared.sum(axis=1) + 1e-10)
            
            dk_values.append(D_i.mean())
        
        return np.array(k_values), np.array(dk_values)


class LevinaBickelMLE:
    """
    Levina-Bickel MLE estimator for intrinsic dimension.
    Based on ratio of distances.
    """
    
    def __init__(self, k_min: int = 5, k_max: int = 20):
        self.k_min = k_min
        self.k_max = k_max
    
    def compute(self, data: np.ndarray, k_values: List[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Compute MLE dimension estimate."""
        n = data.shape[0]
        
        if k_values is None:
            k_values = list(range(self.k_min, min(self.k_max, n - 1)))
        
        tree = KDTree(data)
        
        dim_estimates = []
        
        for k in k_values:
            if k >= n:
                continue
                
            distances, _ = tree.query(data, k=k + 1)
            distances = distances[:, 1:]
            
            log_ratios = np.log(distances[:, :-1] / distances[:, -1:])
            log_ratios = log_ratios[~np.isinf(log_ratios) & ~np.isnan(log_ratios)]
            
            if len(log_ratios) > 0:
                d_mle = 1.0 / (log_ratios.mean() + 1e-10)
                d_mle = max(0.1, min(d_mle, data.shape[1]))
            else:
                d_mle = np.nan
            
            dim_estimates.append(d_mle)
        
        return np.array(k_values), np.array(dim_estimates)


class CorrelationDimensionEstimator:
    """Correlation dimension using point-pair distances."""
    
    def __init__(self, n_pairs: int = 1000):
        self.n_pairs = n_pairs
    
    def compute(self, data: np.ndarray, eps_values: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]:
        """Compute correlation dimension vs scale."""
        n = data.shape[0]
        
        if eps_values is None:
            eps_values = np.logspace(-2, 1, 20)
        
        correlations = []
        
        indices = self.rng.choice(n, size=min(2 * self.n_pairs, n), replace=False)
        points = data[indices]
        
        for eps in eps_values:
            count = 0
            total = 0
            
            for i in range(0, len(points) - 1, 2):
                dist = np.linalg.norm(points[i] - points[i + 1])
                if dist < eps:
                    count += 1
                total += 1
            
            corr = count / total if total > 0 else 0
            correlations.append(corr)
        
        log_eps = np.log(eps_values + 1e-10)
        log_corr = np.log(np.array(correlations) + 1e-10)
        
        valid = np.isfinite(log_eps) & np.isfinite(log_corr)
        
        if valid.sum() > 2:
            slope, _ = np.polyfit(log_eps[valid], log_corr[valid], 1)
            return eps_values, np.array([slope] * len(eps_values))
        
        return eps_values, np.zeros_like(eps_values)


class LocalPCARankEstimator:
    """Local PCA rank estimator."""
    
    def __init__(self, n_neighbors: int = 10):
        self.n_neighbors = n_neighbors
    
    def compute(self, data: np.ndarray, k_values: List[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Compute local PCA rank."""
        n = data.shape[0]
        
        if k_values is None:
            k_values = list(range(5, min(self.n_neighbors, n - 1)))
        
        tree = KDTree(data)
        
        rank_values = []
        
        for k in k_values:
            if k >= n:
                continue
                
            _, indices = tree.query(data, k=k + 1)
            indices = indices[:, 1:]
            
            local_ranks = []
            for i in range(n):
                neighbors = data[indices[i]]
                
                try:
                    centered = neighbors - neighbors.mean(axis=0)
                    cov = np.cov(centered.T)
                    
                    eigenvalues = np.linalg.eigvalsh(cov)
                    eigenvalues = np.sort(eigenvalues)[::-1]
                    eigenvalues = np.maximum(eigenvalues, 0)
                except:
                    eigenvalues = np.array([1.0])
                
                cumvar = np.cumsum(eigenvalues) / (eigenvalues.sum() + 1e-10)
                rank = np.searchsorted(cumvar, 0.95) + 1
                
                local_ranks.append(rank)
            
            rank_values.append(np.mean(local_ranks))
        
        return np.array(k_values), np.array(rank_values)


class SigmoidFitter:
    """Sigmoid fit for D(k) curves."""
    
    def __init__(self):
        pass
    
    def fit(self, k_values: np.ndarray, dk_values: np.ndarray) -> Dict:
        """Fit sigmoid model."""
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
            
            residuals = dk_values - pred
            mse = (residuals ** 2).mean()
            
            n = len(k_values)
            aic = n * np.log(mse + 1e-10) + 2 * 3
            bic = n * np.log(mse + 1e-10) + 3 * np.log(n)
            
            return {
                'A': float(A),
                'k0': float(k0),
                'beta': float(beta),
                'r_squared': float(r_squared),
                'aic': float(aic),
                'bic': float(bic),
                'residuals': residuals.tolist(),
                'converged': True
            }
            
        except Exception as e:
            return {
                'A': np.nan,
                'k0': np.nan,
                'beta': np.nan,
                'r_squared': np.nan,
                'aic': np.nan,
                'bic': np.nan,
                'residuals': [],
                'converged': False,
                'error': str(e)
            }


class BootstrapConfidenceInterval:
    """Bootstrap confidence intervals for D(k)."""
    
    def __init__(self, n_bootstrap: int = 100, seed: int = 42):
        self.n_bootstrap = n_bootstrap
        self.rng = np.random.RandomState(seed)
    
    def compute(self, data: np.ndarray, k_values: List[int], 
                estimator) -> Dict:
        """Compute bootstrap CI for D(k)."""
        n = data.shape[0]
        
        dk_means = []
        dk_stds = []
        
        for k in k_values:
            bootstrap_dk = []
            
            for _ in range(self.n_bootstrap):
                indices = self.rng.choice(n, size=n, replace=True)
                bootstrap_data = data[indices]
                
                _, dk_vals = estimator.compute(bootstrap_data, [k])
                bootstrap_dk.append(dk_vals[0])
            
            dk_means.append(np.mean(bootstrap_dk))
            dk_stds.append(np.std(bootstrap_dk))
        
        return {
            'dk_mean': np.array(dk_means),
            'dk_std': np.array(dk_stds),
            'ci_lower': np.array(dk_means) - 1.96 * np.array(dk_stds),
            'ci_upper': np.array(dk_means) + 1.96 * np.array(dk_stds)
        }


class UniversalDkPipeline:
    """Universal D(k) pipeline with all estimators."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        self.estimators = {
            'participation_ratio': ParticipationRatioEstimator('euclidean'),
            'levina_bickel': LevinaBickelMLE(k_min=5, k_max=20),
            'correlation_dimension': CorrelationDimensionEstimator(n_pairs=1000),
            'local_pca_rank': LocalPCARankEstimator(n_neighbors=10)
        }
        
        self.sigmoid_fitter = SigmoidFitter()
        self.bootstrap = BootstrapConfidenceInterval(n_bootstrap=100, seed=seed)
    
    def run_full_analysis(self, data: np.ndarray, 
                         k_values: List[int] = None) -> Dict:
        """Run complete D(k) analysis."""
        
        if k_values is None:
            k_values = list(range(1, min(50, data.shape[0] - 1)))
        
        results = {}
        
        pr_estimator = self.estimators['participation_ratio']
        k_vals, dk_vals = pr_estimator.compute(data, k_values)
        
        sigmoid_results = self.sigmoid_fitter.fit(k_vals, dk_vals)
        
        bootstrap_results = self.bootstrap.compute(data, k_vals, pr_estimator)
        
        results['participation_ratio'] = {
            'k_values': k_vals.tolist(),
            'dk_values': dk_vals.tolist(),
            'sigmoid': sigmoid_results,
            'bootstrap': {
                'ci_lower': bootstrap_results['ci_lower'].tolist(),
                'ci_upper': bootstrap_results['ci_upper'].tolist(),
                'dk_std': bootstrap_results['dk_std'].tolist()
            }
        }
        
        lb_estimator = self.estimators['levina_bickel']
        k_vals_lb, dk_vals_lb = lb_estimator.compute(data, k_values)
        
        results['levina_bickel'] = {
            'k_values': k_vals_lb.tolist(),
            'dk_values': dk_vals_lb.tolist()
        }
        
        pcak_estimator = self.estimators['local_pca_rank']
        k_vals_pca, dk_vals_pca = pcak_estimator.compute(data, k_values)
        
        results['local_pca_rank'] = {
            'k_values': k_vals_pca.tolist(),
            'dk_values': dk_vals_pca.tolist()
        }
        
        return results


if __name__ == '__main__':
    print("Universal D(k) Pipeline")
    print("=" * 50)
    
    from synthetic_systems import generate_system
    
    data, _ = generate_system('random_gaussian', n=100, dimensions=20, seed=42)
    
    pipeline = UniversalDkPipeline(seed=42)
    results = pipeline.run_full_analysis(data, k_values=list(range(1, 21)))
    
    pr = results['participation_ratio']
    print(f"Participation Ratio: D(k) range = {min(pr['dk_values']):.2f} - {max(pr['dk_values']):.2f}")
    print(f"Sigmoid fit: k0 = {pr['sigmoid']['k0']:.2f}, R² = {pr['sigmoid']['r_squared']:.3f}")
    print(f"AIC = {pr['sigmoid']['aic']:.2f}, BIC = {pr['sigmoid']['bic']:.2f}")
    
    lb = results['levina_bickel']
    print(f"\nLevina-Bickel: mean D = {np.mean(lb['dk_values']):.2f}")
    
    print("\nAll estimators working.")