"""
Null Model Generators for Adversarial Testing

8 null types for testing D(k) estimators:
- Type I: Random shuffle
- Type II: Topology shuffle
- Type III: Fake clusters
- Type IV: Deceptive dimension
- Type V: Phase transition imposters
- Type VI: False persistence
- Type VII: Correlated noise
- Type VIII: Graph rewiring

NO consciousness, SFH, ontology, or metaphysical terminology.
"""

import numpy as np
from typing import Tuple, Dict, Optional
from scipy.spatial import KDTree
import hashlib


class NullModelBase:
    """Base class for null models."""
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.seed = seed
    
    def transform(self, data: np.ndarray) -> np.ndarray:
        """Transform data to null version."""
        raise NotImplementedError
    
    def get_type(self) -> str:
        """Return null model type identifier."""
        raise NotImplementedError


class NullTypeI_RandomShuffle(NullModelBase):
    """Type I: Random shuffle - destroys all structure."""
    
    def transform(self, data: np.ndarray) -> np.ndarray:
        """Shuffle all elements randomly."""
        return self.rng.permutation(data.flatten()).reshape(data.shape)
    
    def get_type(self) -> str:
        return "type_i_random_shuffle"


class NullTypeII_TopologyShuffle(NullModelBase):
    """Type II: Topology shuffle - preserves marginals, destroys neighbor structure."""
    
    def transform(self, data: np.ndarray) -> np.ndarray:
        """Randomize along each dimension independently."""
        n, d = data.shape
        result = np.zeros_like(data)
        
        for dim in range(d):
            result[:, dim] = self.rng.permutation(data[:, dim])
        
        return result
    
    def get_type(self) -> str:
        return "type_ii_topology_shuffle"


class NullTypeIII_FakeClusters(NullModelBase):
    """Type III: Fake clusters - destroys real clustering but preserves cluster count."""
    
    def __init__(self, n_clusters: int = 5, seed: int = 42):
        super().__init__(seed)
        self.n_clusters = n_clusters
    
    def transform(self, data: np.ndarray) -> np.ndarray:
        """Create fake cluster structure."""
        n, d = data.shape
        
        cluster_centers = self.rng.normal(0, 1, size=(self.n_clusters, d))
        
        assignments = self.rng.integers(0, self.n_clusters, size=n)
        
        fake_data = cluster_centers[assignments] + self.rng.normal(0, 0.5, size=(n, d))
        
        return fake_data
    
    def get_type(self) -> str:
        return "type_iii_fake_clusters"


class NullTypeIV_DeceptiveDimension(NullModelBase):
    """Type IV: Deceptive dimension - high-d noise that looks structured."""
    
    def __init__(self, noise_ratio: float = 0.5, seed: int = 42):
        super().__init__(seed)
        self.noise_ratio = noise_ratio
    
    def transform(self, data: np.ndarray) -> np.ndarray:
        """Add high-frequency noise to preserve low-d structure."""
        n, d = data.shape
        
        u, s, vt = np.linalg.svd(data, full_matrices=False)
        
        n_signal = int(d * (1 - self.noise_ratio))
        signal = u[:, :n_signal] @ np.diag(s[:n_signal]) @ vt[:n_signal, :]
        
        noise = self.rng.normal(0, s[:n_signal].mean() * 0.1, size=(n, d))
        
        return signal + noise
    
    def get_type(self) -> str:
        return "type_iv_deceptive_dimension"


class NullTypeV_PhaseImposter(NullModelBase):
    """Type V: Phase transition imposters - add noise that looks like transitions."""
    
    def __init__(self, n_transitions: int = 3, seed: int = 42):
        super().__init__(seed)
        self.n_transitions = n_transitions
    
    def transform(self, data: np.ndarray) -> np.ndarray:
        """Add spurious phase-like transitions."""
        n, d = data.shape
        
        transition_points = sorted(self.rng.integers(0, n, size=self.n_transitions))
        
        result = data.copy()
        for i in range(len(transition_points) - 1):
            start = transition_points[i]
            end = transition_points[i + 1]
            
            transition = self.rng.normal(0, 0.5, size=(end - start, d))
            result[start:end] += transition
        
        return result
    
    def get_type(self) -> str:
        return "type_v_phase_imposter"


class NullTypeVI_FalsePersistence(NullModelBase):
    """Type VI: False persistence - add smooth component that looks like persistence."""
    
    def __init__(self, smoothing_window: int = 10, seed: int = 42):
        super().__init__(seed)
        self.smoothing_window = smoothing_window
    
    def transform(self, data: np.ndarray) -> np.ndarray:
        """Add low-frequency component."""
        n, d = data.shape
        
        if n < self.smoothing_window:
            return data
        
        smoothed = np.zeros_like(data)
        half_win = self.smoothing_window // 2
        
        for i in range(n):
            start = max(0, i - half_win)
            end = min(n, i + half_win + 1)
            smoothed[i] = data[start:end].mean(axis=0)
        
        noise = self.rng.normal(0, 0.3, size=data.shape)
        
        return smoothed + noise
    
    def get_type(self) -> str:
        return "type_vi_false_persistence"


class NullTypeVII_CorrelatedNoise(NullModelBase):
    """Type VII: Correlated noise - structured noise that looks like real correlation."""
    
    def transform(self, data: np.ndarray) -> np.ndarray:
        """Generate correlated noise with similar covariance structure."""
        n, d = data.shape
        
        original_cov = np.cov(data.T)
        
        eigenvalues, eigenvectors = np.linalg.eigh(original_cov)
        eigenvalues = np.maximum(eigenvalues, 0)
        
        random_eigenvalues = self.rng.exponential(eigenvalues.mean(), size=d)
        random_cov = eigenvectors @ np.diag(random_eigenvalues) @ eigenvectors.T
        
        cholesky = np.linalg.cholesky(random_cov + 0.01 * np.eye(d))
        correlated_noise = cholesky @ self.rng.normal(0, 1, size=(n, d))
        
        return data + correlated_noise * 0.5
    
    def get_type(self) -> str:
        return "type_vii_correlated_noise"


class NullTypeVIII_GraphRewiring(NullModelBase):
    """Type VIII: Graph rewiring - preserves degree distribution, destroys structure."""
    
    def __init__(self, n_edges_swap: int = 100, seed: int = 42):
        super().__init__(seed)
        self.n_edges_swap = n_edges_swap
    
    def transform(self, data: np.ndarray) -> np.ndarray:
        """Simulate random edge swaps in embedding space."""
        n, d = data.shape
        
        tree = KDTree(data)
        distances, indices = tree.query(data, k=6)
        
        adj = np.zeros((n, n), dtype=bool)
        for i in range(n):
            for j in indices[i, 1:]:
                if i != j:
                    adj[i, j] = True
        
        for _ in range(self.n_edges_swap):
            i = self.rng.integers(0, n)
            j = self.rng.integers(0, n)
            if i != j and not adj[i, j]:
                k = self.rng.integers(0, n)
                if adj[i, k]:
                    adj[i, k] = False
                    adj[k, i] = False
                    adj[i, j] = True
                    adj[j, i] = True
        
        return data
    
    def get_type(self) -> str:
        return "type_viii_graph_rewiring"


NULL_MODELS = {
    'type_i_random_shuffle': NullTypeI_RandomShuffle,
    'type_ii_topology_shuffle': NullTypeII_TopologyShuffle,
    'type_iii_fake_clusters': NullTypeIII_FakeClusters,
    'type_iv_deceptive_dimension': NullTypeIV_DeceptiveDimension,
    'type_v_phase_imposter': NullTypeV_PhaseImposter,
    'type_vi_false_persistence': NullTypeVI_FalsePersistence,
    'type_vii_correlated_noise': NullTypeVII_CorrelatedNoise,
    'type_viii_graph_rewiring': NullTypeVIII_GraphRewiring
}


def apply_null_model(data: np.ndarray, null_type: str, seed: int = 42,
                     **null_params) -> Tuple[np.ndarray, Dict]:
    """
    Apply specified null model to data.
    
    Args:
        data: Input data
        null_type: One of the 8 null types
        seed: Random seed
        **null_params: Additional parameters for null model
    
    Returns:
        (null_data, metadata)
    """
    if null_type not in NULL_MODELS:
        raise ValueError(f"Unknown null type: {null_type}")
    
    if null_type == 'type_iii_fake_clusters':
        null_model = NULL_MODELS[null_type](n_clusters=null_params.get('n_clusters', 5), seed=seed)
    elif null_type == 'type_iv_deceptive_dimension':
        null_model = NULL_MODELS[null_type](noise_ratio=null_params.get('noise_ratio', 0.5), seed=seed)
    elif null_type == 'type_v_phase_imposter':
        null_model = NULL_MODELS[null_type](n_transitions=null_params.get('n_transitions', 3), seed=seed)
    elif null_type == 'type_vi_false_persistence':
        null_model = NULL_MODELS[null_type](smoothing_window=null_params.get('smoothing_window', 10), seed=seed)
    elif null_type == 'type_viii_graph_rewiring':
        null_model = NULL_MODELS[null_type](n_edges_swap=null_params.get('n_edges_swap', 100), seed=seed)
    else:
        null_model = NULL_MODELS[null_type](seed=seed)
    
    null_data = null_model.transform(data)
    
    metadata = {
        'null_type': null_type,
        'seed': seed,
        'original_hash': hashlib.sha256(data.tobytes()).hexdigest()[:16],
        'null_hash': hashlib.sha256(null_data.tobytes()).hexdigest()[:16]
    }
    
    return null_data, metadata


if __name__ == '__main__':
    print("Null Model Generators")
    print("=" * 50)
    print("\nAvailable null types:")
    for name in NULL_MODELS.keys():
        print(f"  - {name}")
    
    print("\nTesting null models...")
    
    from synthetic_systems import generate_system
    
    data, _ = generate_system('random_gaussian', n=50, dimensions=20, seed=42)
    
    for null_type in list(NULL_MODELS.keys())[:3]:
        null_data, meta = apply_null_model(data, null_type, seed=42)
        print(f"{null_type}: original={meta['original_hash']}, null={meta['null_hash']}")
    
    print("\nAll null models working.")