"""
Temporal Dynamics Engine

NO consciousness, SFH, ontology, or metaphysical terminology.

Systems:
A. Stable evolving hierarchy
B. Random temporal noise  
C. Oscillatory graph switching
D. Perturb-and-recover systems
E. Slowly degrading systems
F. Sudden collapse systems
"""

import numpy as np
from scipy.spatial import KDTree
from typing import Dict, List, Tuple
import hashlib
import json


class TemporalSystemBase:
    """Base class for temporal systems."""
    
    def __init__(self, seed: int = 42, n_timesteps: int = 50):
        self.rng = np.random.RandomState(seed)
        self.seed = seed
        self.n_timesteps = n_timesteps
        self.trajectory = None
    
    def evolve(self) -> np.ndarray:
        """Generate temporal trajectory."""
        raise NotImplementedError
    
    def get_snapshot(self, t: int) -> np.ndarray:
        """Get state at time t."""
        if self.trajectory is None:
            self.trajectory = self.evolve()
        return self.trajectory[t]
    
    def get_all_snapshots(self) -> np.ndarray:
        """Get full trajectory."""
        if self.trajectory is None:
            self.trajectory = self.evolve()
        return self.trajectory


class StableEvolvingHierarchy(TemporalSystemBase):
    """
    A. STABLE EVOLVING HIERARCHY
    
    Graph that maintains hierarchy while slowly evolving.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10, 
                 n_timesteps: int = 50, evolution_rate: float = 0.05,
                 seed: int = 42):
        super().__init__(seed, n_timesteps)
        self.n = n
        self.dimensions = dimensions
        self.evolution_rate = evolution_rate
    
    def evolve(self) -> np.ndarray:
        """Generate stable evolving hierarchy."""
        # Start with hierarchical structure
        centers = self.rng.normal(0, 1, size=(5, self.dimensions))
        
        trajectory = []
        current_state = self.rng.choice(5, size=self.n)
        
        for t in range(self.n_timesteps):
            state = np.zeros((self.n, self.dimensions))
            
            for i in range(self.n):
                center = centers[current_state[i]]
                state[i] = center + self.rng.normal(0, 0.3, size=self.dimensions)
            
            # Slowly evolve centers
            centers += self.rng.normal(0, self.evolution_rate, size=centers.shape)
            
            # Maintain cluster membership most of the time
            if t > 0 and self.rng.random() > 0.1:
                current_state = current_state  # Keep same
            else:
                current_state = self.rng.choice(5, size=self.n)
            
            trajectory.append(state)
        
        return np.array(trajectory)


class RandomTemporalNoise(TemporalSystemBase):
    """
    B. RANDOM TEMPORAL NOISE
    
    Pure random evolution - no persistence.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, seed: int = 42):
        super().__init__(seed, n_timesteps)
        self.n = n
        self.dimensions = dimensions
    
    def evolve(self) -> np.ndarray:
        """Generate random temporal noise."""
        return self.rng.normal(0, 1, size=(self.n_timesteps, self.n, self.dimensions))


class OscillatoryGraphSwitching(TemporalSystemBase):
    """
    C. OSCILLATORY GRAPH SWITCHING
    
    Periodic switching between graph states.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, period: int = 10,
                 seed: int = 42):
        super().__init__(seed, n_timesteps)
        self.n = n
        self.dimensions = dimensions
        self.period = period
    
    def evolve(self) -> np.ndarray:
        """Generate oscillatory switching."""
        trajectory = []
        
        for t in range(self.n_timesteps):
            phase = (t % self.period) / self.period
            
            # Two states oscillating
            if phase < 0.5:
                state = self.rng.normal(0, 1, size=(self.n, self.dimensions))
            else:
                state = self.rng.normal(2, 1, size=(self.n, self.dimensions))
            
            trajectory.append(state)
        
        return np.array(trajectory)


class PerturbAndRecoverSystem(TemporalSystemBase):
    """
    D. PERTURB-AND-RECOVER SYSTEMS
    
    Strong perturbation followed by gradual recovery.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, perturb_time: int = 20,
                 recovery_rate: float = 0.2, seed: int = 42):
        super().__init__(seed, n_timesteps)
        self.n = n
        self.dimensions = dimensions
        self.perturb_time = perturb_time
        self.recovery_rate = recovery_rate
    
    def evolve(self) -> np.ndarray:
        """Generate perturb-and-recover trajectory."""
        base_state = self.rng.normal(0, 1, size=(self.n, self.dimensions))
        
        trajectory = []
        
        for t in range(self.n_timesteps):
            if t < self.perturb_time:
                state = base_state + self.rng.normal(0, 0.1, size=base_state.shape)
            else:
                # Recovery - gradually return to base
                recovery_progress = (t - self.perturb_time) / (self.n_timesteps - self.perturb_time)
                noise = self.rng.normal(0, 1 - recovery_progress * self.recovery_rate, 
                                       size=base_state.shape)
                state = base_state + noise
            
            trajectory.append(state)
        
        return np.array(trajectory)


class SlowlyDegradingSystem(TemporalSystemBase):
    """
    E. SLOWLY DEGRADING SYSTEMS
    
    Gradual loss of structure over time.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, degradation_rate: float = 0.05,
                 seed: int = 42):
        super().__init__(seed, n_timesteps)
        self.n = n
        self.dimensions = dimensions
        self.degradation_rate = degradation_rate
    
    def evolve(self) -> np.ndarray:
        """Generate slowly degrading trajectory."""
        # Start with tight clusters
        centers = self.rng.normal(0, 1, size=(5, self.dimensions))
        
        trajectory = []
        
        for t in range(self.n_timesteps):
            degradation = 1.0 + t * self.degradation_rate
            
            state = np.zeros((self.n, self.dimensions))
            assignments = self.rng.choice(5, size=self.n)
            
            for i in range(self.n):
                center = centers[assignments[i]]
                state[i] = center + self.rng.normal(0, degradation, size=self.dimensions)
            
            trajectory.append(state)
        
        return np.array(trajectory)


class SuddenCollapseSystem(TemporalSystemBase):
    """
    F. SUDDEN COLLAPSE SYSTEMS
    
    Stable then sudden structural collapse.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, collapse_time: int = 35,
                 seed: int = 42):
        super().__init__(seed, n_timesteps)
        self.n = n
        self.dimensions = dimensions
        self.collapse_time = collapse_time
    
    def evolve(self) -> np.ndarray:
        """Generate sudden collapse trajectory."""
        base_state = self.rng.normal(0, 1, size=(self.n, self.dimensions))
        random_state = self.rng.normal(0, 5, size=(self.n, self.dimensions))
        
        trajectory = []
        
        for t in range(self.n_timesteps):
            if t < self.collapse_time:
                state = base_state + self.rng.normal(0, 0.1, size=base_state.shape)
            else:
                state = random_state + self.rng.normal(0, 0.5, size=random_state.shape)
            
            trajectory.append(state)
        
        return np.array(trajectory)


def generate_temporal_system(system_type: str, **kwargs) -> Tuple[np.ndarray, Dict]:
    """Factory function for temporal systems."""
    systems = {
        'stable_hierarchy': StableEvolvingHierarchy,
        'random_temporal': RandomTemporalNoise,
        'oscillatory': OscillatoryGraphSwitching,
        'perturb_recover': PerturbAndRecoverSystem,
        'degrading': SlowlyDegradingSystem,
        'collapse': SuddenCollapseSystem
    }
    
    if system_type not in systems:
        raise ValueError(f"Unknown temporal system: {system_type}")
    
    gen = systems[system_type](**kwargs)
    trajectory = gen.evolve()
    metadata = {
        'system_type': f'temporal_{system_type}',
        'params': kwargs,
        'shape': trajectory.shape,
        'hash': hashlib.sha256(trajectory.tobytes()).hexdigest()[:16]
    }
    
    return trajectory, metadata


if __name__ == '__main__':
    print("Temporal Dynamics Engine")
    print("=" * 50)
    
    # Test each system
    systems = [
        ('stable_hierarchy', {'n': 30, 'dimensions': 5, 'n_timesteps': 20}),
        ('random_temporal', {'n': 30, 'dimensions': 5, 'n_timesteps': 20}),
        ('perturb_recover', {'n': 30, 'dimensions': 5, 'n_timesteps': 20}),
        ('degrading', {'n': 30, 'dimensions': 5, 'n_timesteps': 20}),
        ('collapse', {'n': 30, 'dimensions': 5, 'n_timesteps': 20})
    ]
    
    for sys_type, params in systems:
        traj, meta = generate_temporal_system(sys_type, **params, seed=42)
        print(f"{sys_type}: {traj.shape}")
    
    print("\nTemporal systems working.")