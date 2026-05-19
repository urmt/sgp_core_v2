"""
SGP-CORE V2 Synthetic System Generators

Generators for testing organizational geometry:
- Pure Random Gaussian
- Hierarchical Cluster Manifold
- Sparse Interaction Graph

All use fixed seed (numpy.default_rng(seed=42)).
NO consciousness, SFH, ontology, or metaphysical terminology.
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional
import json
import hashlib


class SyntheticSystemBase:
    """Base class for synthetic system generators."""
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.seed = seed
        self.params = {}
        self._hash = None
    
    def generate(self) -> np.ndarray:
        """Generate the synthetic data."""
        raise NotImplementedError
    
    def get_hash(self) -> str:
        """SHA256 hash of generated data."""
        if self._hash is None:
            data = self.generate()
            self._hash = hashlib.sha256(data.tobytes()).hexdigest()[:16]
        return self._hash
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return metadata for provenance."""
        return {
            'seed': self.seed,
            'params': self.params,
            'class': self.__class__.__name__,
            'data_hash': self.get_hash()
        }


class PureRandomGaussian(SyntheticSystemBase):
    """
    Pure random Gaussian distribution.
    Null baseline - no organizational structure.
    """
    
    def __init__(self, n: int = 100, dimensions: int = 50, 
                 variance: float = 1.0, seed: int = 42):
        super().__init__(seed)
        self.params = {
            'n': n,
            'dimensions': dimensions,
            'variance': variance
        }
        self.n = n
        self.dimensions = dimensions
        self.variance = variance
    
    def generate(self) -> np.ndarray:
        """Generate N x D Gaussian random data."""
        return self.rng.normal(
            loc=0.0,
            scale=np.sqrt(self.variance),
            size=(self.n, self.dimensions)
        )


class HierarchicalClusterManifold(SyntheticSystemBase):
    """
    Hierarchical cluster manifold with nested structure.
    Multi-scale organizational structure.
    """
    
    def __init__(self, n: int = 100, depth: int = 3, 
                 branching: int = 3, cluster_std: float = 0.5,
                 separation: float = 2.0, seed: int = 42):
        super().__init__(seed)
        self.params = {
            'n': n,
            'depth': depth,
            'branching': branching,
            'cluster_std': cluster_std,
            'separation': separation
        }
        self.n = n
        self.depth = depth
        self.branching = branching
        self.cluster_std = cluster_std
        self.separation = separation
    
    def generate(self) -> np.ndarray:
        """Generate hierarchical cluster data."""
        total_clusters = sum(self.branching ** d for d in range(self.depth + 1))
        points_per_cluster = self.n // total_clusters
        
        centers = self._generate_centers()
        
        data = []
        cluster_idx = 0
        for depth in range(self.depth + 1):
            n_clusters_at_depth = self.branching ** depth
            for c in range(n_clusters_at_depth):
                center = centers[cluster_idx]
                n_points = points_per_cluster if cluster_idx < total_clusters - 1 else self.n - len(data)
                
                if n_points > 0:
                    cluster_data = self.rng.normal(
                        loc=center,
                        scale=self.cluster_std,
                        size=(n_points, centers.shape[1])
                    )
                    data.append(cluster_data)
                cluster_idx += 1
        
        return np.vstack(data)
    
    def _generate_centers(self) -> np.ndarray:
        """Generate cluster centers recursively."""
        centers = []
        
        def recurse(center, depth):
            if depth > self.depth:
                return
            
            for b in range(self.branching):
                offset = self.rng.normal(0, self.separation, size=center.shape)
                new_center = center + offset * (self.depth - depth + 1) / self.depth
                centers.append(new_center.copy())
                recurse(new_center, depth + 1)
        
        initial_center = np.zeros(10)
        centers.append(initial_center.copy())
        recurse(initial_center, 0)
        
        return np.array(centers)


class SparseInteractionGraph(SyntheticSystemBase):
    """
    Sparse interaction graph with tunable connectivity.
    Tests organization vs sparsity.
    """
    
    def __init__(self, n: int = 100, sparsity: float = 0.1,
                 connected: bool = True, seed: int = 42):
        super().__init__(seed)
        self.params = {
            'n': n,
            'sparsity': sparsity,
            'connected': connected
        }
        self.n = n
        self.sparsity = sparsity
        self.connected = connected
    
    def generate(self) -> np.ndarray:
        """Generate sparse adjacency matrix and compute embedding."""
        p = self.sparsity
        
        adj = self.rng.binomial(1, p, size=(self.n, self.n))
        adj = (adj + adj.T) > 0
        np.fill_diagonal(adj, False)
        
        if self.connected:
            adj = self._ensure_connected(adj)
        
        lap = self._compute_laplacian(adj)
        eigvals, eigvecs = np.linalg.eigh(lap)
        
        embedding = eigvecs[:, 1:11]
        return embedding
    
    def _ensure_connected(self, adj: np.ndarray) -> np.ndarray:
        """Ensure graph is connected."""
        from scipy.sparse.csgraph import connected_components
        n_components, labels = connected_components(adj, directed=False)
        
        if n_components > 1:
            for i in range(1, n_components):
                idx_i = np.where(labels == 0)[0]
                idx_j = np.where(labels == i)[0]
                if len(idx_i) > 0 and len(idx_j) > 0:
                    adj[idx_i[0], idx_j[0]] = True
                    adj[idx_j[0], idx_i[0]] = True
        
        return adj
    
    def _compute_laplacian(self, adj: np.ndarray) -> np.ndarray:
        """Compute normalized graph Laplacian."""
        degrees = adj.sum(axis=1)
        degree_matrix = np.diag(degrees)
        laplacian = degree_matrix - adj
        
        degree_inv_sqrt = np.diag(1.0 / np.sqrt(degrees + 1e-10))
        normalized_lap = degree_inv_sqrt @ laplacian @ degree_inv_sqrt
        
        return normalized_lap


class DynamicalAttractor(SyntheticSystemBase):
    """
    Dynamical systems with attractors.
    Tests temporal organization persistence.
    """
    
    def __init__(self, n_timesteps: int = 100, system_type: str = 'fixed_point',
                 noise: float = 0.01, seed: int = 42):
        super().__init__(seed)
        self.params = {
            'n_timesteps': n_timesteps,
            'system_type': system_type,
            'noise': noise
        }
        self.n_timesteps = n_timesteps
        self.system_type = system_type
        self.noise = noise
    
    def generate(self) -> np.ndarray:
        """Generate dynamical system trajectory."""
        if self.system_type == 'fixed_point':
            return self._fixed_point()
        elif self.system_type == 'limit_cycle':
            return self._limit_cycle()
        elif self.system_type == 'chaos':
            return self._chaos()
        else:
            raise ValueError(f"Unknown system type: {self.system_type}")
    
    def _fixed_point(self) -> np.ndarray:
        """Fixed point attractor."""
        x = np.zeros(self.n_timesteps)
        x0 = self.rng.normal(0, 1)
        for t in range(1, self.n_timesteps):
            x[t] = 0.95 * x[t-1] + self.rng.normal(0, self.noise)
        return x.reshape(-1, 1)
    
    def _limit_cycle(self) -> np.ndarray:
        """Limit cycle (oscillator)."""
        theta = np.zeros(self.n_timesteps)
        for t in range(1, self.n_timesteps):
            theta[t] = theta[t-1] + 0.1 + self.rng.normal(0, self.noise)
        
        x = np.cos(theta)
        y = np.sin(theta)
        return np.column_stack([x, y])
    
    def _chaos(self) -> np.ndarray:
        """Lorenz-like chaotic system."""
        dt = 0.01
        x, y, z = 0.1, 0.0, 0.0
        sigma, rho, beta = 10.0, 28.0, 8/3
        
        trajectory = []
        for t in range(self.n_timesteps):
            dx = sigma * (y - x)
            dy = x * (rho - z) - y
            dz = x * y - beta * z
            
            x += dx * dt + self.rng.normal(0, self.noise)
            y += dy * dt + self.rng.normal(0, self.noise)
            z += dz * dt + self.rng.normal(0, self.noise)
            
            trajectory.append([x, y, z])
        
        return np.array(trajectory)


class CoupledOscillators(SyntheticSystemBase):
    """
    Coupled oscillator network (Kuramoto).
    Tests synchronization geometry.
    """
    
    def __init__(self, n: int = 50, coupling: float = 0.0,
                 n_timesteps: int = 100, seed: int = 42):
        super().__init__(seed)
        self.params = {
            'n': n,
            'coupling': coupling,
            'n_timesteps': n_timesteps
        }
        self.n = n
        self.coupling = coupling
        self.n_timesteps = n_timesteps
    
    def generate(self) -> np.ndarray:
        """Generate coupled oscillator phases."""
        phases = self.rng.uniform(0, 2*np.pi, self.n)
        natural_freqs = self.rng.normal(0, 0.1, self.n)
        
        trajectory = []
        for t in range(self.n_timesteps):
            phases = self._step(phases, natural_freqs)
            trajectory.append(phases.copy())
        
        return np.array(trajectory)
    
    def _step(self, phases: np.ndarray, omegas: np.ndarray) -> np.ndarray:
        """Kuramoto update step."""
        dtheta = omegas.copy()
        
        if self.coupling > 0:
            for i in range(self.n):
                for j in range(self.n):
                    if i != j:
                        dtheta[i] += (self.coupling / self.n) * np.sin(phases[j] - phases[i])
        
        return phases + dtheta * 0.1


def generate_system(system_type: str, **kwargs) -> Tuple[np.ndarray, Dict]:
    """
    Factory function for generating synthetic systems.
    
    Args:
        system_type: One of 'random_gaussian', 'hierarchical', 'sparse', 
                     'attractor', 'oscillator'
        **kwargs: Parameters for the specific system
    
    Returns:
        (data, metadata)
    """
    generators = {
        'random_gaussian': PureRandomGaussian,
        'hierarchical': HierarchicalClusterManifold,
        'sparse': SparseInteractionGraph,
        'attractor': DynamicalAttractor,
        'oscillator': CoupledOscillators
    }
    
    if system_type not in generators:
        raise ValueError(f"Unknown system: {system_type}")
    
    gen = generators[system_type](**kwargs)
    data = gen.generate()
    metadata = gen.get_metadata()
    metadata['system_type'] = system_type
    
    return data, metadata


class ProgressiveCompression(SyntheticSystemBase):
    """
    Progressive compression system (simulates layered processing).
    Tests D(k) across compression layers.
    """
    
    def __init__(self, n: int = 100, initial_dim: int = 100, 
                 layers: int = 5, compression_schedule: float = 0.5,
                 noise: float = 0.01, seed: int = 42):
        super().__init__(seed)
        self.params = {
            'n': n,
            'initial_dim': initial_dim,
            'layers': layers,
            'compression_schedule': compression_schedule,
            'noise': noise
        }
        self.n = n
        self.initial_dim = initial_dim
        self.layers = layers
        self.compression_schedule = compression_schedule
        self.noise = noise
    
    def generate(self) -> np.ndarray:
        """Generate multi-layer compressed representations."""
        base_data = self.rng.normal(0, 1, size=(self.n, self.initial_dim))
        
        layer_data = [base_data]
        current_dim = self.initial_dim
        
        for layer in range(self.layers):
            next_dim = max(2, int(current_dim * self.compression_schedule))
            
            projection = self.rng.randn(current_dim, next_dim)
            projected = layer_data[-1] @ projection
            
            normalized = projected / (np.linalg.norm(projected, axis=1, keepdims=True) + 1e-10)
            
            noised = normalized + self.rng.normal(0, self.noise, size=normalized.shape)
            
            layer_data.append(noised)
            current_dim = next_dim
        
        return layer_data[-1]


class NetworkPropagation(SyntheticSystemBase):
    """
    Network propagation system (signal spreading on graph).
    Tests organization in propagating systems.
    """
    
    def __init__(self, n: int = 100, sparsity: float = 0.1, 
                 propagation_steps: int = 10, seed: int = 42):
        super().__init__(seed)
        self.params = {
            'n': n,
            'sparsity': sparsity,
            'propagation_steps': propagation_steps
        }
        self.n = n
        self.sparsity = sparsity
        self.propagation_steps = propagation_steps
    
    def generate(self) -> np.ndarray:
        """Generate network propagation states."""
        p = self.sparsity
        adj = self.rng.binomial(1, p, size=(self.n, self.n))
        adj = (adj + adj.T) > 0
        np.fill_diagonal(adj, False)
        
        degrees = adj.sum(axis=1) + 1e-10
        transition = adj / degrees[:, np.newaxis]
        
        initial_signal = self.rng.uniform(0, 1, size=self.n)
        state = initial_signal.copy()
        
        for step in range(self.propagation_steps):
            state = transition @ state
            state = state + self.rng.normal(0, 0.01, size=state.shape)
        
        embeddings = []
        for i in range(self.n):
            state_i = initial_signal.copy()
            path = []
            for _ in range(5):
                state_i = transition @ state_i
                path.append(state_i.copy())
            embeddings.append(np.concatenate(path) if path else state)
        
        max_len = max(len(e) for e in embeddings)
        padded = np.array([np.pad(e, (0, max_len - len(e))) for e in embeddings])
        
        return padded[:, :min(max_len, 50)]


def generate_system(system_type: str, **kwargs) -> Tuple[np.ndarray, Dict]:
    """
    Factory function for generating synthetic systems.
    
    Args:
        system_type: One of the available system types
        **kwargs: Parameters for the specific system
    
    Returns:
        (data, metadata)
    """
    generators = {
        'random_gaussian': PureRandomGaussian,
        'hierarchical': HierarchicalClusterManifold,
        'sparse': SparseInteractionGraph,
        'attractor': DynamicalAttractor,
        'oscillator': CoupledOscillators,
        'compression': ProgressiveCompression,
        'propagation': NetworkPropagation
    }
    
    if system_type not in generators:
        raise ValueError(f"Unknown system: {system_type}")
    
    gen = generators[system_type](**kwargs)
    data = gen.generate()
    metadata = gen.get_metadata()
    metadata['system_type'] = system_type
    
    return data, metadata


if __name__ == '__main__':
    print("SGP-CORE V2 Synthetic System Generators")
    print("=" * 50)
    print("\nTesting generators...")
    
    for system_type in ['random_gaussian', 'hierarchical', 'sparse', 'attractor', 'oscillator']:
        data, meta = generate_system(system_type, seed=42, n=50)
        print(f"{system_type}: shape={data.shape}, hash={meta['data_hash']}")
    
    print("\nAll generators working.")