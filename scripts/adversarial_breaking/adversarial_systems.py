"""
Adversarial Systems for Metric Breaking

NO consciousness, SFH, ontology, or metaphysical terminology.

These systems are designed to LOOK organized but actually contain NO true organization.
They are meant to test whether metrics detect REAL structure or just ARTIFACTS.
"""

import numpy as np
from typing import Tuple, Dict
import hashlib


class AdversarialSystemBase:
    """Base class for adversarial systems."""
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.seed = seed
    
    def generate(self) -> np.ndarray:
        """Generate adversarial data."""
        raise NotImplementedError
    
    def get_metadata(self) -> Dict:
        """Return metadata."""
        return {
            'seed': self.seed,
            'system_type': self.__class__.__name__
        }


class FakeHierarchySystem(AdversarialSystemBase):
    """
    A. FAKE HIERARCHY SYSTEM
    
    Random data that LOOKS hierarchical but has NO true hierarchy.
    """
    
    def __init__(self, n: int = 100, dimensions: int = 10, depth: int = 3, 
                 branching: int = 3, noise: float = 0.5, seed: int = 42):
        super().__init__(seed)
        self.params = {'n': n, 'dimensions': dimensions, 'depth': depth, 
                      'branching': branching, 'noise': noise}
        self.n = n
        self.dimensions = dimensions
        self.depth = depth
        self.branching = branching
        self.noise = noise
    
    def generate(self) -> np.ndarray:
        """Generate fake hierarchical structure."""
        # Create random cluster centers
        total_clusters = sum(self.branching ** d for d in range(self.depth + 1))
        points_per_cluster = self.n // total_clusters
        
        centers = self.rng.normal(0, 1, size=(total_clusters, self.dimensions))
        
        # Generate points - looks hierarchical but is random assignment
        data = []
        for i in range(total_clusters):
            n_pts = points_per_cluster if i < total_clusters - 1 else self.n - len(data)
            # Random cluster assignment (NOT hierarchical)
            cluster_data = self.rng.normal(
                loc=centers[i],
                scale=self.noise,
                size=(n_pts, self.dimensions)
            )
            # SHUFFLE - destroy any real structure
            shuffled = cluster_data[self.rng.permutation(len(cluster_data))]
            data.append(shuffled)
        
        result = np.vstack(data)
        # FINAL SHUFFLE - destroy any remaining order
        return result[self.rng.permutation(len(result))]


class DeceptiveCurvatureSystem(AdversarialSystemBase):
    """
    B. DECEPTIVE CURVATURE SYSTEM
    
    Inject artificial curvature transitions without real topology.
    """
    
    def __init__(self, n: int = 100, dimensions: int = 10, 
                 curvature_injection: float = 0.8, seed: int = 42):
        super().__init__(seed)
        self.params = {'n': n, 'dimensions': dimensions, 'curvature_injection': curvature_injection}
        self.n = n
        self.dimensions = dimensions
        self.injection = curvature_injection
    
    def generate(self) -> np.ndarray:
        """Generate data with artificial curvature."""
        # Start with random Gaussian
        data = self.rng.normal(0, 1, size=(self.n, self.dimensions))
        
        # Apply non-linear warping to create artificial "transitions"
        # This makes D(k) look structured but it's just a transform
        k = self.injection
        warped = np.tanh(k * data) * np.sign(data)
        
        # Add more fake curvature with synthetic elbows
        for i in range(0, self.n, self.n // 5):
            idx = min(i + self.n // 10, self.n)
            # Artificially inflate variance in regions
            warped[i:idx] *= 1.5
        
        return warped


class FalsePersistenceSystem(AdversarialSystemBase):
    """
    C. FALSE PERSISTENCE SYSTEM
    
    Create fake neighborhood persistence without real clusters.
    """
    
    def __init__(self, n: int = 100, dimensions: int = 10,
                 duplication_rate: float = 0.2, seed: int = 42):
        super().__init__(seed)
        self.params = {'n': n, 'dimensions': dimensions, 'duplication_rate': duplication_rate}
        self.n = n
        self.dimensions = dimensions
        self.dup_rate = duplication_rate
    
    def generate(self) -> np.ndarray:
        """Generate data with fake persistence."""
        # Generate base random data
        data = self.rng.normal(0, 1, size=(self.n, self.dimensions))
        
        # Duplicate neighborhoods to create fake persistence
        n_dup = int(self.n * self.dup_rate)
        
        # Pick random "anchor" points
        anchors = self.rng.choice(self.n, size=n_dup // 3, replace=False)
        
        # Create copies with tiny noise
        copies = []
        for anchor in anchors:
            for _ in range(3):
                noise = self.rng.normal(0, 0.01, size=(1, self.dimensions))
                copies.append(data[anchor:anchor+1] + noise)
        
        if copies:
            copy_data = np.vstack(copies)
            # Mix copies into original
            result = np.vstack([data, copy_data])
            # Shuffle to destroy any real structure
            return result[self.rng.permutation(len(result))][:self.n]
        
        return data


class RandomTemporalCoherence(AdversarialSystemBase):
    """
    D. RANDOM TEMPORAL COHERENCE
    
    Fake temporal stability using autocorrelated noise.
    """
    
    def __init__(self, n_timesteps: int = 100, dimensions: int = 5,
                 coherence: float = 0.95, seed: int = 42):
        super().__init__(seed)
        self.params = {'n_timesteps': n_timesteps, 'dimensions': dimensions, 'coherence': coherence}
        self.n_t = n_timesteps
        self.dims = dimensions
        self.coherence = coherence
    
    def generate(self) -> np.ndarray:
        """Generate fake temporal coherence."""
        trajectory = np.zeros((self.n_t, self.dims))
        
        for d in range(self.dims):
            # Autocorrelated random walk - looks stable but is random
            state = self.rng.normal(0, 1)
            for t in range(self.n_t):
                # AR(1) process - creates apparent stability
                state = self.coherence * state + self.rng.normal(0, 1 - self.coherence)
                trajectory[t, d] = state
        
        return trajectory


class HybridNullMonster(AdversarialSystemBase):
    """
    E. HYBRID NULL MONSTERS
    
    Combine multiple deception methods to create worst-case adversarial data.
    """
    
    def __init__(self, n: int = 100, dimensions: int = 10, 
                 deception_strength: float = 0.5, seed: int = 42):
        super().__init__(seed)
        self.params = {'n': n, 'dimensions': dimensions, 'deception_strength': deception_strength}
        self.n = n
        self.dims = dimensions
        self.strength = deception_strength
    
    def generate(self) -> np.ndarray:
        """Generate hybrid adversarial system."""
        # Method 1: Fake hierarchy
        fake_hier = FakeHierarchySystem(self.n, self.dims, depth=2, 
                                        noise=0.3 * self.strength, seed=self.seed)
        data = fake_hier.generate()
        
        # Method 2: Deceptive curvature
        decurv = DeceptiveCurvatureSystem(self.n, self.dims, 
                                         curvature_injection=0.5 * self.strength, 
                                         seed=self.seed + 1)
        data = 0.5 * data + 0.5 * decurv.generate()[:self.n]
        
        # Method 3: False persistence (subset)
        false_persist = FalsePersistenceSystem(self.n, self.dims, 
                                                duplication_rate=0.1 * self.strength,
                                                seed=self.seed + 2)
        data_persist = false_persist.generate()
        
        # Combine
        result = np.vstack([data, data_persist])
        
        # Shuffle final
        return result[self.rng.permutation(len(result))][:self.n]


def generate_adversarial(system_type: str, **kwargs) -> Tuple[np.ndarray, Dict]:
    """Factory function for adversarial systems."""
    systems = {
        'fake_hierarchy': FakeHierarchySystem,
        'deceptive_curvature': FalsePersistenceSystem,
        'false_persistence': DeceptiveCurvatureSystem,
        'random_temporal': RandomTemporalCoherence,
        'hybrid_null_monster': HybridNullMonster
    }
    
    if system_type not in systems:
        raise ValueError(f"Unknown adversarial system: {system_type}")
    
    gen = systems[system_type](**kwargs)
    data = gen.generate()
    metadata = gen.get_metadata()
    metadata['system_type'] = f'adversarial_{system_type}'
    
    return data, metadata


if __name__ == '__main__':
    print("Adversarial Systems")
    print("=" * 50)
    
    for sys_type in ['fake_hierarchy', 'deceptive_curvature', 'false_persistence', 'hybrid_null_monster']:
        data, meta = generate_adversarial(sys_type, n=50, dimensions=10, seed=42)
        print(f"{sys_type}: shape={data.shape}")
    
    print("\nAdversarial systems working.")