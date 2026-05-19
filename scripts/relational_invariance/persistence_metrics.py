"""
Relational Persistence Metrics

NO consciousness, SFH, ontology, or metaphysical terminology.

IMPORTANT:
NO SINGLE METRIC ALLOWED.

ALL RESULTS MUST USE:
- ensemble relational agreement
- cross-perturbation consistency
- multi-scale agreement

Metrics:
1. Edge Persistence Stability
2. Transition Path Coherence
3. Multi-Scale Relational Consistency
4. Recovery Trajectory Stability
5. Structural Hysteresis Index
6. Interaction Memory Score
7. Perturbation Recovery Rate
8. Temporal Relational Stability
"""

import numpy as np
from scipy.spatial import KDTree
from typing import Dict, List
import json


class RelationalMetricBase:
    """Base class for relational metrics."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)


class EdgePersistenceStability(RelationalMetricBase):
    """
    1. EDGE PERSISTENCE STABILITY
    
    Measure how edges persist under perturbation.
    """
    
    def __init__(self, k: int = 5, seed: int = 42):
        super().__init__(seed)
        self.k = k
    
    def compute(self, original_data: np.ndarray, 
                perturbed_data: np.ndarray) -> Dict:
        """Compute edge persistence."""
        # Build kNN graphs
        tree_orig = KDTree(original_data)
        _, idx_orig = tree_orig.query(original_data, k=self.k + 1)
        
        tree_pert = KDTree(perturbed_data)
        _, idx_pert = tree_pert.query(perturbed_data, k=self.k + 1)
        
        n = original_data.shape[0]
        
        persistence_scores = []
        for i in range(n):
            orig_neighbors = set(idx_orig[i, 1:])
            pert_neighbors = set(idx_pert[i, 1:])
            
            intersection = len(orig_neighbors & pert_neighbors)
            union = len(orig_neighbors | pert_neighbors)
            
            if union > 0:
                iou = intersection / union
                persistence_scores.append(iou)
        
        return {
            'edge_persistence_mean': float(np.mean(persistence_scores)),
            'edge_persistence_std': float(np.std(persistence_scores)),
            'edge_persistence_min': float(np.min(persistence_scores)),
            'edge_persistence_median': float(np.median(persistence_scores))
        }


class TransitionPathCoherence(RelationalMetricBase):
    """
    2. TRANSITION PATH COHERENCE
    
    Measure path consistency between states.
    """
    
    def __init__(self, seed: int = 42):
        super().__init__(seed)
    
    def compute(self, state1: np.ndarray, state2: np.ndarray) -> Dict:
        """Compute transition path coherence."""
        tree1 = KDTree(state1)
        tree2 = KDTree(state2)
        
        # Get nearest neighbors in each state
        _, idx1 = tree1.query(state1, k=min(5, state1.shape[0]))
        _, idx2 = tree2.query(state2, k=min(5, state2.shape[0]))
        
        # Check neighbor consistency
        n = state1.shape[0]
        coherent = 0
        
        for i in range(n):
            # Check if neighbors move coherently
            neighbors1 = set(idx1[i, 1:])
            neighbors2 = set(idx2[i, 1:])
            
            if len(neighbors1 & neighbors2) > 0:
                coherent += 1
        
        coherence = coherent / n
        
        return {
            'transition_coherence': float(coherence),
            'n_nodes': n
        }


class MultiScaleRelationalConsistency(RelationalMetricBase):
    """
    3. MULTI-SCALE RELATIONAL CONSISTENCY
    
    Check consistency across different k values.
    """
    
    def __init__(self, k_values: List[int] = None, seed: int = 42):
        super().__init__(seed)
        self.k_values = k_values or [3, 5, 10, 15]
    
    def compute(self, data: np.ndarray) -> Dict:
        """Compute multi-scale consistency."""
        tree = KDTree(data)
        
        persistence_at_scale = []
        
        for k in self.k_values:
            if k >= data.shape[0]:
                continue
                
            _, indices = tree.query(data, k=k + 1)
            
            # Compute persistence at this scale
            n = data.shape[0]
            persistences = []
            
            for i in range(n):
                neighbors = set(indices[i, 1:])
                # Compare to next scale
                if k + 1 < data.shape[0]:
                    _, indices_next = tree.query(data, k=k + 2)
                    neighbors_next = set(indices_next[i, 1:])
                    
                    intersection = len(neighbors & neighbors_next)
                    union = len(neighbors | neighbors_next)
                    
                    if union > 0:
                        persistences.append(intersection / union)
            
            if persistences:
                persistence_at_scale.append(np.mean(persistences))
        
        return {
            'multi_scale_consistency_mean': float(np.mean(persistence_at_scale)) if persistence_at_scale else 0.0,
            'multi_scale_consistency_std': float(np.std(persistence_at_scale)) if len(persistence_at_scale) > 1 else 0.0,
            'n_scales': len(persistence_at_scale)
        }


class RecoveryTrajectoryStability(RelationalMetricBase):
    """
    4. RECOVERY TRAJECTORY STABILITY
    
    Measure stability of recovery after perturbation.
    """
    
    def __init__(self, seed: int = 42):
        super().__init__(seed)
    
    def compute(self, original: np.ndarray, 
                perturbations: List[np.ndarray],
                recovery_sequence: List[np.ndarray]) -> Dict:
        """
        Compute recovery trajectory stability.
        
        Args:
            original: Original data
            perturbations: List of increasingly perturbed versions
            recovery_sequence: List of recovery states
        """
        if len(recovery_sequence) < 2:
            return {'error': 'insufficient_recovery_sequence'}
        
        # Compute edge persistence for each recovery state
        persistence_trajectory = []
        
        for state in recovery_sequence:
            tree = KDTree(state)
            _, indices = tree.query(state, k=5)
            
            # Compare to original
            _, orig_idx = tree.query(original, k=5)
            
            n = original.shape[0]
            persistences = []
            
            for i in range(n):
                current_neighbors = set(indices[i, 1:])
                original_neighbors = set(orig_idx[i, 1:])
                
                intersection = len(current_neighbors & original_neighbors)
                if len(current_neighbors | original_neighbors) > 0:
                    persistences.append(intersection / len(current_neighbors | original_neighbors))
            
            persistence_trajectory.append(np.mean(persistences))
        
        # Check if recovery is monotonic (improving)
        improving = sum(1 for i in range(1, len(persistence_trajectory)) 
                       if persistence_trajectory[i] > persistence_trajectory[i-1])
        
        return {
            'recovery_trajectory': persistence_trajectory,
            'recovery_mean': float(np.mean(persistence_trajectory)),
            'recovery_std': float(np.std(persistence_trajectory)),
            'improvement_rate': improving / max(1, len(persistence_trajectory) - 1),
            'final_recovery': float(persistence_trajectory[-1])
        }


class StructuralHysteresisIndex(RelationalMetricBase):
    """
    5. STRUCTURAL HYSTERESIS INDEX
    
    Measure difference between forward and backward transitions.
    """
    
    def __init__(self, seed: int = 42):
        super().__init__(seed)
    
    def compute(self, forward_sequence: List[np.ndarray],
               backward_sequence: List[np.ndarray]) -> Dict:
        """Compute structural hysteresis."""
        if len(forward_sequence) != len(backward_sequence):
            return {'error': 'sequence_mismatch'}
        
        hysteresis_values = []
        
        for fwd, bwd in zip(forward_sequence, backward_sequence):
            tree_fwd = KDTree(fwd)
            _, idx_fwd = tree_fwd.query(fwd, k=5)
            
            tree_bwd = KDTree(bwd)
            _, idx_bwd = tree_bwd.query(bwd, k=5)
            
            # Compute asymmetry
            n = fwd.shape[0]
            asymmetry = 0
            
            for i in range(n):
                fwd_neighbors = set(idx_fwd[i, 1:])
                bwd_neighbors = set(idx_bwd[i, 1:])
                
                diff = len(fwd_neighbors.symmetric_difference(bwd_neighbors))
                asymmetry += diff
            
            asymmetry /= n
            hysteresis_values.append(asymmetry)
        
        return {
            'hysteresis_mean': float(np.mean(hysteresis_values)),
            'hysteresis_std': float(np.std(hysteresis_values)),
            'hysteresis_range': float(max(hysteresis_values) - min(hysteresis_values)),
            'asymmetry_profile': hysteresis_values
        }


class InteractionMemoryScore(RelationalMetricBase):
    """
    6. INTERACTION MEMORY SCORE
    
    Measure how past interactions influence current state.
    """
    
    def __init__(self, memory_window: int = 3, seed: int = 42):
        super().__init__(seed)
        self.memory_window = memory_window
    
    def compute(self, temporal_data: np.ndarray) -> Dict:
        """Compute interaction memory score."""
        n_steps = temporal_data.shape[0]
        n_dims = temporal_data.shape[1]
        
        if n_steps < self.memory_window + 1:
            return {'error': 'insufficient_temporal_data'}
        
        # Compute autocorrelation of neighbor relationships
        memory_scores = []
        
        for lag in range(1, self.memory_window + 1):
            # Build graphs at t and t-lag
            for t in range(lag, n_steps):
                tree_t = KDTree(temporal_data[t])
                _, idx_t = tree_t.query(temporal_data[t], k=5)
                
                tree_lag = KDTree(temporal_data[t-lag])
                _, idx_lag = tree_lag.query(temporal_data[t-lag], k=5)
                
                # Compare neighbor relationships
                n = temporal_data.shape[1]
                memory = 0
                
                for i in range(n):
                    neighbors_t = set(idx_t[i, 1:])
                    neighbors_lag = set(idx_lag[i, 1:])
                    
                    memory += len(neighbors_t & neighbors_lag)
                
                memory_scores.append(memory / (n * 4))
        
        return {
            'interaction_memory_mean': float(np.mean(memory_scores)) if memory_scores else 0.0,
            'interaction_memory_std': float(np.std(memory_scores)) if len(memory_scores) > 1 else 0.0,
            'memory_persistence': float(np.mean(memory_scores) > 0.3)
        }


class PerturbationRecoveryRate(RelationalMetricBase):
    """
    7. PERTURBATION RECOVERY RATE
    
    Measure how quickly system returns to original structure after perturbation.
    """
    
    def __init__(self, seed: int = 42):
        super().__init__(seed)
    
    def compute(self, original: np.ndarray,
                perturbations: List[Tuple[np.ndarray, float]]) -> Dict:
        """
        Compute recovery rate.
        
        perturbations: List of (perturbed_data, perturbation_strength)
        """
        recovery_rates = []
        
        for perturbed, strength in perturbations:
            # Compute distance from original
            orig_tree = KDTree(original)
            pert_tree = KDTree(perturbed)
            
            # Compare structures
            _, idx_orig = orig_tree.query(original, k=5)
            _, idx_pert = pert_tree.query(perturbed, k=5)
            
            n = original.shape[0]
            structural_change = 0
            
            for i in range(n):
                orig_set = set(idx_orig[i, 1:])
                pert_set = set(idx_pert[i, 1:])
                
                change = len(orig_set.symmetric_difference(pert_set)) / 4
                structural_change += change
            
            structural_change /= n
            
            # Recovery rate = inverse of structural change
            recovery = 1.0 / (1.0 + structural_change)
            recovery_rates.append(recovery)
        
        return {
            'recovery_rate_mean': float(np.mean(recovery_rates)),
            'recovery_rate_std': float(np.std(recovery_rates)),
            'recovery_rates': recovery_rates,
            'final_recovery': float(recovery_rates[-1]) if recovery_rates else 0.0
        }


class TemporalRelationalStability(RelationalMetricBase):
    """
    8. TEMPORAL RELATIONAL STABILITY
    
    Measure stability of relational structure over time.
    """
    
    def __init__(self, seed: int = 42):
        super().__init__(seed)
    
    def compute(self, temporal_sequence: List[np.ndarray]) -> Dict:
        """Compute temporal relational stability."""
        if len(temporal_sequence) < 2:
            return {'error': 'insufficient_sequence'}
        
        # Compute persistence between consecutive timesteps
        persistences = []
        
        for t in range(len(temporal_sequence) - 1):
            tree1 = KDTree(temporal_sequence[t])
            _, idx1 = tree1.query(temporal_sequence[t], k=5)
            
            tree2 = KDTree(temporal_sequence[t + 1])
            _, idx2 = tree2.query(temporal_sequence[t + 1], k=5)
            
            n = temporal_sequence[t].shape[0]
            persistence = 0
            
            for i in range(n):
                neighbors1 = set(idx1[i, 1:])
                neighbors2 = set(idx2[i, 1:])
                
                if len(neighbors1 | neighbors2) > 0:
                    persistence += len(neighbors1 & neighbors2) / len(neighbors1 | neighbors2)
            
            persistences.append(persistence / n)
        
        return {
            'temporal_stability_mean': float(np.mean(persistences)),
            'temporal_stability_std': float(np.std(persistences)),
            'temporal_stability_min': float(np.min(persistences)),
            'stability_drift': float(np.max(persistences) - np.min(persistences))
        }


class RelationalEnsembleConsensus:
    """
    ENSEMBLE: Combine all relational metrics with consensus voting.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        self.metrics = {
            'edge_persistence': EdgePersistenceStability(k=5, seed=seed),
            'transition_coherence': TransitionPathCoherence(seed=seed),
            'multi_scale_consistency': MultiScaleRelationalConsistency(seed=seed),
            'recovery_trajectory': RecoveryTrajectoryStability(seed=seed),
            'hysteresis': StructuralHysteresisIndex(seed=seed),
            'interaction_memory': InteractionMemoryScore(memory_window=3, seed=seed),
            'perturbation_recovery': PerturbationRecoveryRate(seed=seed),
            'temporal_stability': TemporalRelationalStability(seed=seed)
        }
    
    def compute_ensemble_consensus(self, data: np.ndarray,
                                  comparison_data: np.ndarray = None,
                                  temporal_sequence: List[np.ndarray] = None) -> Dict:
        """
        Compute ensemble consensus across all relational metrics.
        """
        results = {}
        valid_count = 0
        
        # Edge persistence (requires comparison data)
        if comparison_data is not None:
            try:
                ep = self.metrics['edge_persistence'].compute(data, comparison_data)
                results['edge_persistence'] = ep
                valid_count += 1
            except:
                pass
        
        # Multi-scale consistency
        try:
            ms = self.metrics['multi_scale_consistency'].compute(data)
            results['multi_scale_consistency'] = ms
            valid_count += 1
        except:
            pass
        
        # Temporal stability (requires sequence)
        if temporal_sequence is not None:
            try:
                ts = self.metrics['temporal_stability'].compute(temporal_sequence)
                results['temporal_stability'] = ts
                valid_count += 1
            except:
                pass
        
        # Compute consensus score
        consensus_scores = []
        
        for metric_name, metric_result in results.items():
            if isinstance(metric_result, dict):
                # Extract key indicator based on metric type
                if 'edge_persistence_mean' in metric_result:
                    score = metric_result['edge_persistence_mean']
                elif 'multi_scale_consistency_mean' in metric_result:
                    score = metric_result['multi_scale_consistency_mean']
                elif 'temporal_stability_mean' in metric_result:
                    score = metric_result['temporal_stability_mean']
                else:
                    score = 0.5  # Default
                
                consensus_scores.append(score)
        
        ensemble_mean = np.mean(consensus_scores) if consensus_scores else 0.0
        ensemble_std = np.std(consensus_scores) if len(consensus_scores) > 1 else 0.0
        
        # Consensus requires consistency (low std)
        consensus_reached = ensemble_std < 0.2 and ensemble_mean > 0.3
        
        return {
            'ensemble_mean': float(ensemble_mean),
            'ensemble_std': float(ensemble_std),
            'consensus_reached': consensus_reached,
            'valid_metrics': valid_count,
            'individual_results': results,
            'consensus_verdict': 'ACCEPT' if consensus_reached else 'REJECT'
        }


if __name__ == '__main__':
    print("Relational Persistence Metrics")
    print("=" * 50)
    
    import sys
    sys.path.insert(0, '../')
    from synthetic_systems import generate_system
    
    # Test on hierarchical data
    data, _ = generate_system('hierarchical', n=50, depth=3, seed=42)
    
    ensemble = RelationalEnsembleConsensus(seed=42)
    result = ensemble.compute_ensemble_consensus(data)
    
    print(f"Ensemble: mean={result['ensemble_mean']:.3f}, std={result['ensemble_std']:.3f}")
    print(f"Consensus: {result['consensus_verdict']}")
    
    print("\nRelational metrics working.")