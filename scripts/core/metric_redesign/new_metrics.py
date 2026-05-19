"""
New Candidate Metrics for Metric Redesign

NO consciousness, SFH, ontology, or metaphysical terminology.

Metrics:
A. Local Curvature Entropy
B. Scale Transition Instability
C. Multi-scale Spectral Drift
D. Topological Persistence Proxy
E. Temporal Stability Index
"""

import numpy as np
from scipy.stats import entropy
from scipy.spatial import KDTree
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')


class LocalCurvatureEntropy:
    """
    A. LOCAL CURVATURE ENTROPY
    
    Measure variability of second derivative across scales.
    Goal: detect structured transitions vs smooth random scaling.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
    
    def compute(self, k_values: np.ndarray, dk_values: np.ndarray) -> dict:
        """Compute curvature entropy metrics."""
        # First derivative
        d1 = np.diff(dk_values) / (np.diff(k_values) + 1e-10)
        
        # Second derivative
        d2 = np.diff(d1) / (np.diff(k_values[:-1]) + 1e-10)
        
        # Curvature variance
        curv_var = np.var(d2)
        
        # Entropy of curvature distribution
        hist, _ = np.histogram(d2, bins=10, density=True)
        hist = hist / (hist.sum() + 1e-10)
        curv_entropy = entropy(hist + 1e-10)
        
        # Transition sharpness (max absolute curvature)
        max_curv = np.max(np.abs(d2))
        
        # Number of sign changes in d2 (inflection count)
        sign_changes = np.sum(np.diff(np.sign(d2)) != 0)
        
        return {
            'curvature_variance': float(curv_var),
            'curvature_entropy': float(curv_entropy),
            'max_curvature': float(max_curv),
            'inflection_count': int(sign_changes),
            'd1_mean': float(np.mean(np.abs(d1))),
            'd1_std': float(np.std(d1))
        }


class ScaleTransitionInstability:
    """
    B. SCALE TRANSITION INSTABILITY
    
    How unstable local dimensionality becomes across scales.
    Hypothesis: organized systems show nonuniform transitions.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
    
    def compute(self, k_values: np.ndarray, dk_values: np.ndarray) -> dict:
        """Compute scale transition instability."""
        # Compute local D(k) changes
        d1 = np.diff(dk_values)
        
        # Instability = std of first differences
        instability = np.std(d1)
        
        # Non-uniformity = variance of differences
        nonuniformity = np.var(d1)
        
        # Skewness of transitions (organized = asymmetric)
        from scipy.stats import skew
        trans_skew = skew(d1)
        
        # Kurtosis (heavy tails = complex transitions)
        from scipy.stats import kurtosis
        trans_kurt = kurtosis(d1)
        
        # Local variance sliding window
        window = 3
        local_vars = []
        for i in range(len(d1) - window):
            local_vars.append(np.var(d1[i:i+window]))
        
        local_var_mean = np.mean(local_vars) if local_vars else 0
        local_var_ratio = instability / (local_var_mean + 1e-10) if local_var_mean > 0 else 0
        
        return {
            'instability': float(instability),
            'nonuniformity': float(nonuniformity),
            'transition_skew': float(trans_skew),
            'transition_kurtosis': float(trans_kurt),
            'local_variance_ratio': float(local_var_ratio)
        }


class MultiScaleSpectralDrift:
    """
    C. MULTI-SCALE SPECTRAL DRIFT
    
    Eigenvalue spectrum drift across k.
    Goal: detect coordinated geometric compression.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
    
    def compute(self, data: np.ndarray, k_values: list) -> dict:
        """Compute spectral drift metrics."""
        n = data.shape[0]
        
        spectral_velocities = []
        spectral_accelerations = []
        
        tree = KDTree(data)
        
        for k in k_values:
            if k >= n - 1:
                continue
            
            distances, indices = tree.query(data, k=min(k + 2, n - 1))
            distances = distances[:, 1:]
            
            # Spectral properties of distance matrix
            dist_cov = np.cov(distances.T)
            eigenvalues = np.linalg.eigvalsh(dist_cov)
            eigenvalues = np.sort(np.maximum(eigenvalues, 0))
            
            if len(spectral_velocities) > 0:
                drift = eigenvalues - prev_eigenvalues
                spectral_velocities.append(np.mean(np.abs(drift)))
                
                if len(spectral_velocities) > 1:
                    acc = spectral_velocities[-1] - spectral_velocities[-2]
                    spectral_accelerations.append(acc)
            
            prev_eigenvalues = eigenvalues
        
        if spectral_velocities:
            return {
                'spectral_velocity_mean': float(np.mean(spectral_velocities)),
                'spectral_velocity_std': float(np.std(spectral_velocities)),
                'spectral_acceleration_mean': float(np.mean(spectral_accelerations)) if spectral_accelerations else 0.0,
                'spectral_acceleration_std': float(np.std(spectral_accelerations)) if spectral_accelerations else 0.0,
                'spectral_drift_total': float(np.sum(spectral_velocities))
            }
        else:
            return {'error': 'insufficient_k_values'}


class TopologicalPersistenceProxy:
    """
    D. TOPOLOGICAL PERSISTENCE PROXY
    
    Approximate neighbor graph persistence without full TDA.
    Goal: measure cluster survival across scales.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
    
    def compute(self, data: np.ndarray, k_values: list) -> dict:
        """Compute topological persistence proxy."""
        tree = KDTree(data)
        
        persistence_scores = []
        cluster_sizes = []
        
        for k in k_values:
            if k >= data.shape[0] - 1:
                continue
            
            distances, indices = tree.query(data, k=k + 1)
            distances = distances[:, 1:]
            
            # Build connectivity at this scale
            threshold = np.percentile(distances.flatten(), 50)
            adj = distances < threshold
            
            # Count connected components (simple proxy)
            n_components = self._count_components(adj)
            
            # Cluster size distribution
            cluster_sizes.append(n_components)
            
            # Persistence = inverse of component count change
            if len(cluster_sizes) > 1:
                persistence = 1.0 / (abs(cluster_sizes[-1] - cluster_sizes[-2]) + 1)
                persistence_scores.append(persistence)
        
        if persistence_scores:
            return {
                'persistence_mean': float(np.mean(persistence_scores)),
                'persistence_std': float(np.std(persistence_scores)),
                'cluster_variation': float(np.var(cluster_sizes)) if len(cluster_sizes) > 1 else 0.0,
                'final_cluster_count': int(cluster_sizes[-1]) if cluster_sizes else 0
            }
        else:
            return {'error': 'insufficient_data'}
    
    def _count_components(self, adj: np.ndarray) -> int:
        """Simple connected components count."""
        n = adj.shape[0]
        if n < 2:
            return n
        
        visited = set()
        components = 0
        
        for i in range(n):
            if i not in visited:
                components += 1
                stack = [i]
                while stack:
                    node = stack.pop()
                    if node not in visited:
                        visited.add(node)
                        for j in range(n):
                            if j < adj.shape[1] and adj[node, j] and j not in visited:
                                stack.append(j)
        
        return components


class TemporalStabilityIndex:
    """
    E. TEMPORAL STABILITY INDEX
    
    For dynamical systems: measure persistence through time.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
    
    def compute(self, trajectory: np.ndarray, window_size: int = 10) -> dict:
        """
        Compute temporal stability metrics.
        trajectory: T x D time series
        """
        n_steps = trajectory.shape[0]
        
        if n_steps < window_size * 2:
            return {'error': 'insufficient_timesteps'}
        
        # Rolling D(k) computation
        dk_rolling = []
        
        for i in range(0, n_steps - window_size, window_size // 2):
            window_data = trajectory[i:i+window_size]
            
            if window_data.shape[0] < 5:
                continue
            
            try:
                tree = KDTree(window_data)
                k = min(3, window_data.shape[0] - 1)
                distances, _ = tree.query(window_data, k=k+1)
                distances = distances[:, 1:]
                
                dist_sum = distances.sum(axis=1, keepdims=True)
                probs = distances / (dist_sum + 1e-10)
                probs_sq = probs ** 2
                D_i = 1.0 / (probs_sq.sum(axis=1) + 1e-10)
                dk_rolling.append(D_i.mean())
            except:
                continue
        
        if len(dk_rolling) < 3:
            return {'error': 'insufficient_windows'}
        
        dk_rolling = np.array(dk_rolling)
        
        # Stability metrics
        stability = 1.0 / (np.std(dk_rolling) + 1e-10)
        
        # Drift (total change over time)
        drift = np.sum(np.abs(np.diff(dk_rolling)))
        
        # Recurrence (how often returns to similar state)
        mean_val = np.mean(dk_rolling)
        recurrences = np.sum(np.abs(dk_rolling - mean_val) < np.std(dk_rolling))
        
        return {
            'stability_index': float(stability),
            'total_drift': float(drift),
            'recurrence_ratio': float(recurrences / len(dk_rolling)),
            'dk_mean': float(np.mean(dk_rolling)),
            'dk_std': float(np.std(dk_rolling))
        }


class MetricRedesignSuite:
    """All new metrics in one suite."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        self.metrics = {
            'curvature_entropy': LocalCurvatureEntropy(seed),
            'scale_transition': ScaleTransitionInstability(seed),
            'spectral_drift': MultiScaleSpectralDrift(seed),
            'topological_persistence': TopologicalPersistenceProxy(seed),
            'temporal_stability': TemporalStabilityIndex(seed)
        }
    
    def compute_all(self, data: np.ndarray, k_values: list, 
                   dk_values: np.ndarray = None) -> dict:
        """Compute all metrics."""
        results = {}
        
        # Curvature entropy (needs k, dk)
        if dk_values is not None:
            results['curvature_entropy'] = self.metrics['curvature_entropy'].compute(
                np.array(k_values), np.array(dk_values)
            )
        
        # Scale transition (needs k, dk)
        if dk_values is not None:
            results['scale_transition'] = self.metrics['scale_transition'].compute(
                np.array(k_values), np.array(dk_values)
            )
        
        # Spectral drift (needs data)
        results['spectral_drift'] = self.metrics['spectral_drift'].compute(data, k_values)
        
        # Topological persistence (needs data)
        results['topological_persistence'] = self.metrics['topological_persistence'].compute(data, k_values)
        
        return results


if __name__ == '__main__':
    print("New Metrics Suite")
    print("=" * 50)
    
    import sys
    sys.path.insert(0, '../')
    from synthetic_systems import generate_system
    from universal_dk_pipeline import UniversalDkPipeline
    
    # Test on random vs hierarchical
    for sys_type in ['random_gaussian', 'hierarchical']:
        data, _ = generate_system(sys_type, n=100, dimensions=20, seed=42)
        
        pipeline = UniversalDkPipeline(seed=42)
        dk_results = pipeline.run_full_analysis(data, k_values=list(range(1, 16)))
        
        pr = dk_results['participation_ratio']
        
        suite = MetricRedesignSuite(seed=42)
        metrics = suite.compute_all(data, pr['k_values'], np.array(pr['dk_values']))
        
        print(f"\n{sys_type}:")
        print(f"  curvature_var: {metrics.get('curvature_entropy', {}).get('curvature_variance', 'N/A')}")
        print(f"  instability: {metrics.get('scale_transition', {}).get('instability', 'N/A')}")
    
    print("\nMetrics working.")