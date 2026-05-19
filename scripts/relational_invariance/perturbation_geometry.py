"""
Perturbation Geometry Engine

NO consciousness, SFH, ontology, or metaphysical terminology.

Perturbations:
A. Gaussian noise injection
B. topology destruction
C. edge rewiring
D. partial node deletion
E. temporal scrambling
F. scale scrambling
G. adversarial spoof insertion

Output: trajectory tables + perturbation logs
"""

import numpy as np
from scipy.spatial import KDTree
import json
import hashlib
from typing import Dict, List, Tuple


class PerturbationBase:
    """Base class for perturbations."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
    
    def apply(self, data: np.ndarray) -> np.ndarray:
        """Apply perturbation to data."""
        raise NotImplementedError
    
    def get_params(self) -> Dict:
        return {'type': self.__class__.__name__}


class GaussianNoisePerturbation(PerturbationBase):
    """
    A. GAUSSIAN NOISE INJECTION
    """
    
    def __init__(self, strength: float = 0.1, seed: int = 42):
        super().__init__(seed)
        self.strength = strength
    
    def apply(self, data: np.ndarray) -> np.ndarray:
        noise = self.rng.normal(0, self.strength, size=data.shape)
        return data + noise
    
    def get_params(self) -> Dict:
        return {'type': 'gaussian_noise', 'strength': self.strength}


class TopologyDestructionPerturbation(PerturbationBase):
    """
    B. TOPOLOGY DESTRUCTION
    Shuffle dimension assignments.
    """
    
    def __init__(self, seed: int = 42):
        super().__init__(seed)
    
    def apply(self, data: np.ndarray) -> np.ndarray:
        n, d = data.shape
        result = data.copy()
        
        for dim in range(d):
            result[:, dim] = self.rng.permutation(result[:, dim])
        
        return result
    
    def get_params(self) -> Dict:
        return {'type': 'topology_destruction'}


class EdgeRewiringPerturbation(PerturbationBase):
    """
    C. EDGE REWIRING
    Randomize neighbor relationships.
    """
    
    def __init__(self, rewiring_rate: float = 0.5, k: int = 5, seed: int = 42):
        super().__init__(seed)
        self.rewiring_rate = rewiring_rate
        self.k = k
    
    def apply(self, data: np.ndarray) -> np.ndarray:
        # First compute original kNN
        tree = KDTree(data)
        distances, indices = tree.query(data, k=self.k + 1)
        
        n = data.shape[0]
        
        # Build rewired version
        result = data.copy()
        
        n_rewire = int(n * self.rewiring_rate)
        rewire_nodes = self.rng.choice(n, size=n_rewire, replace=False)
        
        for node in rewire_nodes:
            # Replace some neighbors with random nodes
            n_replace = self.rng.integers(1, self.k)
            new_neighbors = self.rng.choice(n, size=n_replace, replace=False)
            
            for j in new_neighbors:
                # Add edge by moving point towards neighbor
                direction = (data[j] - data[node]) * 0.1
                result[node] += direction
        
        return result
    
    def get_params(self) -> Dict:
        return {'type': 'edge_rewiring', 'rewiring_rate': self.rewiring_rate}


class PartialDeletionPerturbation(PerturbationBase):
    """
    D. PARTIAL NODE DELETION
    Remove subset of points.
    """
    
    def __init__(self, deletion_rate: float = 0.2, seed: int = 42):
        super().__init__(seed)
        self.deletion_rate = deletion_rate
    
    def apply(self, data: np.ndarray) -> np.ndarray:
        n = data.shape[0]
        n_keep = int(n * (1 - self.deletion_rate))
        
        keep_indices = self.rng.choice(n, size=n_keep, replace=False)
        keep_indices = np.sort(keep_indices)
        
        return data[keep_indices]
    
    def get_params(self) -> Dict:
        return {'type': 'partial_deletion', 'deletion_rate': self.deletion_rate}


class TemporalScramblingPerturbation(PerturbationBase):
    """
    E. TEMPORAL SCRAMBLING
    Shuffle time ordering.
    """
    
    def __init__(self, seed: int = 42):
        super().__init__(seed)
    
    def apply(self, data: np.ndarray) -> np.ndarray:
        # If data is trajectory (time x features)
        if data.shape[0] > 1:
            shuffled_indices = self.rng.permutation(data.shape[0])
            return data[shuffled_indices]
        return data
    
    def get_params(self) -> Dict:
        return {'type': 'temporal_scrambling'}


class ScaleScramblingPerturbation(PerturbationBase):
    """
    F. SCALE SCRAMBLING
    Randomly scale dimensions.
    """
    
    def __init__(self, scale_variance: float = 0.5, seed: int = 42):
        super().__init__(seed)
        self.scale_variance = scale_variance
    
    def apply(self, data: np.ndarray) -> np.ndarray:
        n, d = data.shape
        
        scales = self.rng.normal(1.0, self.scale_variance, size=d)
        scales = np.clip(scales, 0.1, 10.0)
        
        return data * scales
    
    def get_params(self) -> Dict:
        return {'type': 'scale_scrambling', 'scale_variance': self.scale_variance}


class AdversarialSpoofPerturbation(PerturbationBase):
    """
    G. ADVERSARIAL SPOOF INSERTION
    Inject synthetic patterns.
    """
    
    def __init__(self, n_spoof: int = 10, seed: int = 42):
        super().__init__(seed)
        self.n_spoof = n_spoof
    
    def apply(self, data: np.ndarray) -> np.ndarray:
        n, d = data.shape
        
        # Create synthetic patterns at extremes
        spoof = self.rng.normal(0, 3, size=(self.n_spoof, d))
        
        return np.vstack([data, spoof])
    
    def get_params(self) -> Dict:
        return {'type': 'adversarial_spoof', 'n_spoof': self.n_spoof}


class PerturbationGeometryEngine:
    """
    Main perturbation engine that runs multiple perturbations.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        self.perturbations = {
            'gaussian_noise': GaussianNoisePerturbation,
            'topology_destruction': TopologyDestructionPerturbation,
            'edge_rewiring': EdgeRewiringPerturbation,
            'partial_deletion': PartialDeletionPerturbation,
            'temporal_scrambling': TemporalScramblingPerturbation,
            'scale_scrambling': ScaleScramblingPerturbation,
            'adversarial_spoof': AdversarialSpoofPerturbation
        }
    
    def run_perturbation_series(self, data: np.ndarray, 
                                 perturbation_configs: List[Dict]) -> List[Tuple[np.ndarray, Dict]]:
        """
        Run a series of perturbations.
        
        Args:
            data: Original data
            perturbation_configs: List of {perturbation_type, params}
        
        Returns:
            List of (perturbed_data, perturbation_info)
        """
        results = []
        
        for config in perturbation_configs:
            ptype = config.get('type', 'gaussian_noise')
            params = config.get('params', {})
            
            if ptype not in self.perturbations:
                print(f"Unknown perturbation: {ptype}")
                continue
            
            perturb = self.perturbations[ptype](**params, seed=self.seed)
            perturbed = perturb.apply(data)
            
            results.append((perturbed, {
                'perturbation_type': ptype,
                'params': perturb.get_params(),
                'output_shape': perturbed.shape,
                'data_hash': hashlib.sha256(perturbed.tobytes()).hexdigest()[:16]
            }))
        
        return results
    
    def compute_perturbation_trajectory(self, data: np.ndarray,
                                         perturbation_type: str,
                                         n_steps: int = 10) -> Dict:
        """
        Compute trajectory of perturbations from weak to strong.
        """
        results = []
        
        strengths = np.linspace(0.01, 0.5, n_steps)
        
        for strength in strengths:
            if perturbation_type == 'gaussian_noise':
                p = GaussianNoisePerturbation(strength=strength, seed=self.seed)
            elif perturbation_type == 'scale_scrambling':
                p = ScaleScramblingPerturbation(scale_variance=strength, seed=self.seed)
            elif perturbation_type == 'adversarial_spoof':
                p = AdversarialSpoofPerturbation(n_spoof=int(strength * 20), seed=self.seed)
            else:
                break
            
            perturbed = p.apply(data)
            
            results.append({
                'strength': strength,
                'data': perturbed,
                'hash': hashlib.sha256(perturbed.tobytes()).hexdigest()[:16]
            })
        
        return {
            'perturbation_type': perturbation_type,
            'trajectory': results,
            'n_steps': n_steps
        }


if __name__ == '__main__':
    print("Perturbation Geometry Engine")
    print("=" * 50)
    
    import sys
    sys.path.insert(0, '../')
    from synthetic_systems import generate_system
    
    data, _ = generate_system('hierarchical', n=50, depth=3, seed=42)
    
    engine = PerturbationGeometryEngine(seed=42)
    
    # Test each perturbation type
    configs = [
        {'type': 'gaussian_noise', 'params': {'strength': 0.1}},
        {'type': 'topology_destruction', 'params': {}},
        {'type': 'edge_rewiring', 'params': {'rewiring_rate': 0.3}},
        {'type': 'scale_scrambling', 'params': {'scale_variance': 0.2}},
    ]
    
    results = engine.run_perturbation_series(data, configs)
    
    print(f"Applied {len(results)} perturbations:")
    for i, (perturbed, info) in enumerate(results):
        print(f"  {i+1}. {info['perturbation_type']}: {perturbed.shape}")
    
    print("\nPerturbation engine working.")