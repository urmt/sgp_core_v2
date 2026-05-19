"""
Advanced Temporal Adversaries

NO consciousness, SFH, ontology, or metaphysical terminology.

Adversaries that attempt to fool temporal metrics:
A. replay-memory-spoof
B. delayed-random-coherence
C. periodic-fake-recovery
D. fragmentation-smoothing
E. synthetic hysteresis injection
F. temporal camouflage hierarchy
G. phase-shift replay
H. scale-dependent spoofing
"""

import numpy as np
from typing import Dict, Tuple


class ReplayMemorySpoof:
    """
    A. REPLAY-MEMORY-SPOOF
    
    Replay the same pattern to fake high memory.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.n = n
        self.dimensions = dimensions
        self.n_timesteps = n_timesteps
    
    def generate(self) -> np.ndarray:
        # Create base pattern
        base = self.rng.normal(0, 1, size=(self.n, self.dimensions))
        
        # Replay with slight variation
        trajectory = []
        
        for t in range(self.n_timesteps):
            replayed = base + self.rng.normal(0, 0.01, size=base.shape)
            trajectory.append(replayed)
        
        return np.array(trajectory)


class DelayedRandomCoherence:
    """
    B. DELAYED-RANDOM-COHERENCE
    
    Start random, then slowly add coherence.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, coherence_start: int = 30,
                 seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.n = n
        self.dimensions = dimensions
        self.n_timesteps = n_timesteps
        self.coherence_start = coherence_start
    
    def generate(self) -> np.ndarray:
        trajectory = []
        
        centers = self.rng.normal(0, 1, size=(5, self.dimensions))
        current_state = self.rng.choice(5, size=self.n)
        
        for t in range(self.n_timesteps):
            if t < self.coherence_start:
                # Random phase
                state = self.rng.normal(0, 1, size=(self.n, self.dimensions))
            else:
                # Coherent phase - fake persistence
                state = np.zeros((self.n, self.dimensions))
                for i in range(self.n):
                    state[i] = centers[current_state[i]] + self.rng.normal(0, 0.3, size=self.dimensions)
                
                # Maintain state
                if t > self.coherence_start and self.rng.random() > 0.05:
                    current_state = current_state
                else:
                    current_state = self.rng.choice(5, size=self.n)
            
            trajectory.append(state)
        
        return np.array(trajectory)


class PeriodicFakeRecovery:
    """
    C. PERIODIC-FAKE-RECOVERY
    
    Regular fake recovery pattern.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, period: int = 15,
                 seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.n = n
        self.dimensions = dimensions
        self.n_timesteps = n_timesteps
        self.period = period
    
    def generate(self) -> np.ndarray:
        trajectory = []
        
        base = self.rng.normal(0, 1, size=(self.n, self.dimensions))
        
        for t in range(self.n_timesteps):
            phase = (t % self.period) / self.period
            
            if phase < 0.3:
                # High perturbation
                state = self.rng.normal(0, 2, size=(self.n, self.dimensions))
            elif phase < 0.6:
                # Rapid "recovery"
                state = base + self.rng.normal(0, 0.2, size=base.shape)
            else:
                # Degrade again
                state = base + self.rng.normal(0, 0.5, size=base.shape)
            
            trajectory.append(state)
        
        return np.array(trajectory)


class FragmentationSmoothing:
    """
    D. FRAGMENTATION-SMOOTHING
    
    Keep fragmentation artificially constant.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, target_frag: float = 0.1,
                 seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.n = n
        self.dimensions = dimensions
        self.n_timesteps = n_timesteps
        self.target_frag = target_frag
    
    def generate(self) -> np.ndarray:
        # Keep cluster structure constant
        centers = self.rng.normal(0, 1, size=(3, self.dimensions))
        
        trajectory = []
        
        for t in range(self.n_timesteps):
            # Maintain similar fragmentation
            assignments = self.rng.choice(3, size=self.n)
            
            state = np.zeros((self.n, self.dimensions))
            for i in range(self.n):
                state[i] = centers[assignments[i]] + self.rng.normal(0, 0.2, size=self.dimensions)
            
            trajectory.append(state)
        
        return np.array(trajectory)


class SyntheticHysteresisInjection:
    """
    E. SYNTHETIC HYSTERESIS INJECTION
    
    Inject fake hysteresis patterns.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, strength: float = 0.5,
                 seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.n = n
        self.dimensions = dimensions
        self.n_timesteps = n_timesteps
        self.strength = strength
    
    def generate(self) -> np.ndarray:
        # Create forward then backward paths with bias
        forward = self.rng.normal(0, 1, size=(self.n_timesteps // 2, self.n, self.dimensions))
        
        backward = forward[::-1] + self.rng.normal(0, self.strength, 
                           size=(self.n_timesteps // 2, self.n, self.dimensions))
        
        return np.vstack([forward, backward])


class TemporalCamouflageHierarchy:
    """
    F. TEMPORAL CAMOUFLAGE HIERARCHY
    
    Hierarchy that looks stable but has no real memory.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.n = n
        self.dimensions = dimensions
        self.n_timesteps = n_timesteps
    
    def generate(self) -> np.ndarray:
        # Appears hierarchical but random assignments
        trajectory = []
        
        for t in range(self.n_timesteps):
            centers = self.rng.normal(0, 1, size=(5, self.dimensions))
            
            # Random assignment - no persistence
            assignments = self.rng.choice(5, size=self.n)
            
            state = np.zeros((self.n, self.dimensions))
            for i in range(self.n):
                state[i] = centers[assignments[i]] + self.rng.normal(0, 0.3, size=self.dimensions)
            
            trajectory.append(state)
        
        return np.array(trajectory)


class PhaseShiftReplay:
    """
    G. PHASE-SHIFT REPLAY
    
    Same pattern with phase shifts.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, phase_shifts: int = 3,
                 seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.n = n
        self.dimensions = dimensions
        self.n_timesteps = n_timesteps
        self.phase_shifts = phase_shifts
    
    def generate(self) -> np.ndarray:
        # Base pattern
        base = self.rng.normal(0, 1, size=(self.n_timesteps // self.phase_shifts, self.n, self.dimensions))
        
        trajectory = []
        
        for phase in range(self.phase_shifts):
            # Same pattern with phase shift
            phase_shift = self.rng.uniform(-0.5, 0.5, size=self.dimensions)
            
            shifted = base.copy()
            for t in range(shifted.shape[0]):
                shifted[t] += phase_shift
            
            trajectory.extend(shifted)
        
        return np.array(trajectory[:self.n_timesteps])


class ScaleDependentSpoofing:
    """
    H. SCALE-DEPENDENT SPOOFING
    
    Different behavior at different scales.
    """
    
    def __init__(self, n: int = 50, dimensions: int = 10,
                 n_timesteps: int = 50, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.n = n
        self.dimensions = dimensions
        self.n_timesteps = n_timesteps
    
    def generate(self) -> np.ndarray:
        # At small N look organized, at large N random
        if self.n < 40:
            # Organized small
            centers = self.rng.normal(0, 0.5, size=(5, self.dimensions))
            assignments = self.rng.choice(5, size=self.n)
            return np.array([centers[a] + self.rng.normal(0, 0.1, size=self.dimensions) 
                           for a in assignments] * self.n_timesteps).reshape(self.n_timesteps, self.n, self.dimensions)
        else:
            # Random large
            return self.rng.normal(0, 1, size=(self.n_timesteps, self.n, self.dimensions))


def generate_temporal_adversary(system_type: str, **kwargs) -> Tuple[np.ndarray, Dict]:
    """Factory for temporal adversaries."""
    systems = {
        'replay_memory_spoof': ReplayMemorySpoof,
        'delayed_random_coherence': DelayedRandomCoherence,
        'periodic_fake_recovery': PeriodicFakeRecovery,
        'fragmentation_smoothing': FragmentationSmoothing,
        'synthetic_hysteresis': SyntheticHysteresisInjection,
        'temporal_camouflage': TemporalCamouflageHierarchy,
        'phase_shift_replay': PhaseShiftReplay,
        'scale_dependent_spoof': ScaleDependentSpoofing
    }
    
    if system_type not in systems:
        raise ValueError(f"Unknown: {system_type}")
    
    gen = systems[system_type](**kwargs)
    data = gen.generate()
    return data, {'system_type': system_type, 'params': kwargs}


if __name__ == '__main__':
    print("Advanced Temporal Adversaries")
    print("=" * 50)
    
    for name in ['replay_memory_spoof', 'delayed_random_coherence', 'temporal_camouflage']:
        data, meta = generate_temporal_adversary(name, n=30, dimensions=5, n_timesteps=20, seed=42)
        print(f"{name}: {data.shape}")
    
    print("\nAdversaries working.")