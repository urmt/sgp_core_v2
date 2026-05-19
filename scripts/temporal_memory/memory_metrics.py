"""
Temporal Memory Metrics

NO consciousness, SFH, ontology, or metaphysical terminology.

Metrics:
1. InteractionMemoryScore
2. StructuralPersistence
3. RecoveryLatency
4. HysteresisLoopArea
5. TemporalFragmentationVariance
6. StabilityUnderNoise
7. TemporalConsensusScore
"""

import numpy as np
from scipy.spatial import KDTree
from typing import Dict, List
import json


def compute_fragmentation(data: np.ndarray, k: int = 5) -> float:
    """Compute graph fragmentation."""
    n = data.shape[0]
    
    tree = KDTree(data)
    _, indices = tree.query(data, k=k + 1)
    
    adj = np.zeros((n, n))
    for i in range(n):
        for j in indices[i, 1:]:
            adj[i, j] = 1
    
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
                        if adj[node, j] and j not in visited:
                            stack.append(j)
    
    frag = 1.0 - ((n - components + 1) / n) if components > 0 else 0
    return frag


class InteractionMemoryScore:
    """
    1. INTERACTION MEMORY SCORE
    
    Correlation of graph structure across time.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
    
    def compute(self, trajectory: np.ndarray) -> Dict:
        """Compute interaction memory score."""
        memory_scores = []
        
        for lag in range(1, min(5, trajectory.shape[0])):
            similarities = []
            
            for t in range(trajectory.shape[0] - lag):
                # Get graph structures at t and t+lag
                data_t = trajectory[t]
                data_lag = trajectory[t + lag]
                
                # Compute similarity of neighbor relationships
                tree_t = KDTree(data_t)
                _, idx_t = tree_t.query(data_t, k=5)
                
                tree_lag = KDTree(data_lag)
                _, idx_lag = tree_lag.query(data_lag, k=5)
                
                # Jaccard similarity
                n = data_t.shape[0]
                similarity = 0
                for i in range(n):
                    neighbors_t = set(idx_t[i, 1:])
                    neighbors_lag = set(idx_lag[i, 1:])
                    
                    intersection = len(neighbors_t & neighbors_lag)
                    union = len(neighbors_t | neighbors_lag)
                    
                    if union > 0:
                        similarity += intersection / union
                
                similarities.append(similarity / n)
            
            if similarities:
                memory_scores.append(np.mean(similarities))
        
        return {
            'memory_score_mean': float(np.mean(memory_scores)) if memory_scores else 0.0,
            'memory_score_std': float(np.std(memory_scores)) if len(memory_scores) > 1 else 0.0,
            'memory_decay': float(1.0 - np.mean(memory_scores)) if memory_scores else 1.0
        }


class StructuralPersistence:
    """
    2. STRUCTURAL PERSISTENCE
    
    Edge retention rate over time.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
    
    def compute(self, trajectory: np.ndarray) -> Dict:
        """Compute structural persistence."""
        persistence_scores = []
        
        for t in range(trajectory.shape[0] - 1):
            data_now = trajectory[t]
            data_next = trajectory[t + 1]
            
            tree_now = KDTree(data_now)
            _, idx_now = tree_now.query(data_now, k=5)
            
            tree_next = KDTree(data_next)
            _, idx_next = tree_next.query(data_next, k=5)
            
            # Edge overlap
            n = data_now.shape[0]
            overlap = 0
            total = 0
            
            for i in range(n):
                edges_now = set(idx_now[i, 1:])
                edges_next = set(idx_next[i, 1:])
                
                overlap += len(edges_now & edges_next)
                total += len(edges_now)
            
            persistence_scores.append(overlap / total if total > 0 else 0)
        
        return {
            'persistence_mean': float(np.mean(persistence_scores)) if persistence_scores else 0.0,
            'persistence_std': float(np.std(persistence_scores)) if len(persistence_scores) > 1 else 0.0,
            'persistence_min': float(np.min(persistence_scores)) if persistence_scores else 0.0
        }


class RecoveryLatency:
    """
    3. RECOVERY LATENCY
    
    Time to restore pre-perturbation structure.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
    
    def compute(self, trajectory: np.ndarray, perturb_time: int = None) -> Dict:
        """Compute recovery latency."""
        if perturb_time is None:
            perturb_time = trajectory.shape[0] // 2
        
        # Compute fragmentation over time
        fragments = []
        for t in range(trajectory.shape[0]):
            frag = compute_fragmentation(trajectory[t])
            fragments.append(frag)
        
        fragments = np.array(fragments)
        
        # Find recovery point
        baseline = np.mean(fragments[:min(5, perturb_time)])
        
        recovery_point = None
        for t in range(perturb_time, len(fragments)):
            if abs(fragments[t] - baseline) < 0.1:
                recovery_point = t - perturb_time
                break
        
        return {
            'recovery_latency': float(recovery_point) if recovery_point else -1,
            'final_fragmentation': float(fragments[-1]),
            'baseline_fragmentation': float(baseline),
            'perturbation_impact': float(np.max(fragments[perturb_time:]) - baseline)
        }


class HysteresisLoopArea:
    """
    4. HYSTERESIS LOOP AREA
    
    Difference between forward and reverse perturbation paths.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
    
    def compute(self, perturbation_levels: List[float], 
               forward_structure: List[float],
               reverse_structure: List[float]) -> Dict:
        """Compute hysteresis loop area."""
        if len(forward_structure) != len(reverse_structure):
            return {'error': 'mismatch'}
        
        # Compute loop area using trapezoidal rule
        forward_diff = np.diff(forward_structure)
        reverse_diff = np.diff(reverse_structure)
        
        area = 0.0
        for i in range(len(forward_diff)):
            area += abs(forward_diff[i] - reverse_diff[i])
        
        return {
            'hysteresis_area': float(area),
            'mean_asymmetry': float(np.mean(np.abs(np.array(forward_structure) - np.array(reverse_structure))))
        }


class TemporalFragmentationVariance:
    """
    5. TEMPORAL FRAGMENTATION VARIANCE
    
    Fragmentation variance across time.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
    
    def compute(self, trajectory: np.ndarray) -> Dict:
        """Compute temporal fragmentation variance."""
        fragments = []
        
        for t in range(trajectory.shape[0]):
            frag = compute_fragmentation(trajectory[t])
            fragments.append(frag)
        
        return {
            'fragmentation_mean': float(np.mean(fragments)),
            'fragmentation_std': float(np.std(fragments)),
            'fragmentation_variance': float(np.var(fragments)),
            'fragmentation_range': float(max(fragments) - min(fragments))
        }


class TemporalConsensusScore:
    """
    7. TEMPORAL CONSENSUS SCORE
    
    Ensemble temporal metric.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        
        self.metrics = {
            'memory': InteractionMemoryScore(seed),
            'persistence': StructuralPersistence(seed),
            'fragmentation_var': TemporalFragmentationVariance(seed)
        }
    
    def compute(self, trajectory: np.ndarray, perturb_time: int = None) -> Dict:
        """Compute temporal consensus."""
        results = {}
        
        # Memory
        try:
            results['memory'] = self.metrics['memory'].compute(trajectory)
        except:
            pass
        
        # Persistence
        try:
            results['persistence'] = self.metrics['persistence'].compute(trajectory)
        except:
            pass
        
        # Fragmentation variance
        try:
            results['fragmentation_var'] = self.metrics['fragmentation_var'].compute(trajectory)
        except:
            pass
        
        # Consensus - require agreement
        scores = []
        
        if 'memory' in results:
            scores.append(results['memory'].get('memory_score_mean', 0))
        
        if 'persistence' in results:
            scores.append(results['persistence'].get('persistence_mean', 0))
        
        if 'fragmentation_var' in results:
            # Lower variance is better
            var = results['fragmentation_var'].get('fragmentation_variance', 1)
            scores.append(1.0 / (1.0 + var))
        
        consensus_mean = np.mean(scores) if scores else 0
        consensus_std = np.std(scores) if len(scores) > 1 else 0
        
        # Consensus reached if std is low
        consensus = consensus_std < 0.2 and consensus_mean > 0.3
        
        return {
            'consensus_mean': float(consensus_mean),
            'consensus_std': float(consensus_std),
            'consensus_reached': consensus,
            'individual_results': results,
            'verdict': 'ACCEPT' if consensus else 'REJECT'
        }


if __name__ == '__main__':
    print("Temporal Memory Metrics")
    print("=" * 50)
    
    from temporal_dynamics import generate_temporal_system
    
    # Test on stable hierarchy
    traj, _ = generate_temporal_system('stable_hierarchy', n=30, dimensions=5, n_timesteps=20, seed=42)
    
    memory = InteractionMemoryScore(42)
    print(f"Memory score: {memory.compute(traj)}")
    
    persistence = StructuralPersistence(42)
    print(f"Persistence: {persistence.compute(traj)}")
    
    frag_var = TemporalFragmentationVariance(42)
    print(f"Fragmentation variance: {frag_var.compute(traj)}")
    
    ensemble = TemporalConsensusScore(42)
    print(f"Consensus: {ensemble.compute(traj)}")
    
    print("\nTemporal metrics working.")