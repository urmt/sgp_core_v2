"""
Interaction Graph Representations for Relational Invariance

NO consciousness, SFH, ontology, or metaphysical terminology.

Graph types:
A. kNN interaction graphs
B. weighted interaction graphs
C. temporal interaction graphs
D. scale-transition graphs
E. perturbation response graphs
"""

import numpy as np
from scipy.spatial import KDTree
from scipy.sparse import csr_matrix
import hashlib
import json
from typing import Dict, List, Tuple, Optional


class InteractionGraphBase:
    """Base class for interaction graphs."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        self._graph = None
        self._hash = None
    
    def build(self, data: np.ndarray) -> np.ndarray:
        """Build adjacency matrix."""
        raise NotImplementedError
    
    def get_adjacency(self) -> np.ndarray:
        return self._graph
    
    def get_hash(self) -> str:
        if self._hash is None and self._graph is not None:
            self._hash = hashlib.sha256(self._graph.tobytes()).hexdigest()[:16]
        return self._hash


class KNNInteractionGraph(InteractionGraphBase):
    """
    A. kNN INTERACTION GRAPH
    
    Build k-nearest neighbor interaction graph.
    """
    
    def __init__(self, k: int = 5, seed: int = 42):
        super().__init__(seed)
        self.k = k
    
    def build(self, data: np.ndarray) -> np.ndarray:
        """Build kNN adjacency matrix."""
        n = data.shape[0]
        
        tree = KDTree(data)
        distances, indices = tree.query(data, k=self.k + 1)
        distances = distances[:, 1:]
        indices = indices[:, 1:]
        
        adj = np.zeros((n, n))
        
        for i in range(n):
            for j_idx in range(len(indices[i])):
                j = indices[i, j_idx]
                dist = distances[i, j_idx]
                adj[i, j] = 1.0 / (1.0 + dist)
        
        self._graph = adj
        return adj
    
    def get_edge_persistence(self, perturbation_data: np.ndarray) -> Dict:
        """Compute edge persistence under perturbation."""
        if self._graph is None:
            return {'error': 'no_graph'}
        
        orig_adj = (self._graph > 0).astype(int)
        
        tree = KDTree(perturbation_data)
        distances, indices = tree.query(perturbation_data, k=self.k + 1)
        distances = distances[:, 1:]
        indices = indices[:, 1:]
        
        pert_adj = np.zeros_like(orig_adj)
        for i in range(pert_adj.shape[0]):
            for j_idx in range(len(indices[i])):
                j = indices[i, j_idx]
                pert_adj[i, j] = 1
        
        persistence = np.sum(orig_adj * pert_adj) / (np.sum(orig_adj) + 1e-10)
        
        return {
            'edge_persistence': float(persistence),
            'original_edges': int(np.sum(orig_adj)),
            'perturbed_edges': int(np.sum(pert_adj)),
            'common_edges': int(np.sum(orig_adj * pert_adj))
        }


class WeightedInteractionGraph(InteractionGraphBase):
    """
    B. WEIGHTED INTERACTION GRAPH
    
    Build weighted graph based on distance decay.
    """
    
    def __init__(self, decay: float = 1.0, threshold: float = 0.1, seed: int = 42):
        super().__init__(seed)
        self.decay = decay
        self.threshold = threshold
    
    def build(self, data: np.ndarray) -> np.ndarray:
        """Build weighted adjacency matrix."""
        n = data.shape[0]
        
        tree = KDTree(data)
        distances, _ = tree.query(data, k=min(20, n))
        distances = distances[:, 1:]
        
        weights = np.exp(-self.decay * distances)
        weights = (weights > self.threshold).astype(float) * weights
        
        adj = np.zeros((n, n))
        for i in range(n):
            adj[i] = weights[i]
        
        self._graph = adj
        return adj
    
    def get_edge_entropy(self) -> Dict:
        """Compute edge weight entropy."""
        if self._graph is None:
            return {'error': 'no_graph'}
        
        edges = self._graph.flatten()
        edges = edges[edges > 0]
        
        if len(edges) == 0:
            return {'edge_entropy': 0.0}
        
        hist, _ = np.histogram(edges, bins=10, density=True)
        hist = hist / (hist.sum() + 1e-10)
        
        entropy = -np.sum(hist * np.log(hist + 1e-10))
        
        return {
            'edge_entropy': float(entropy),
            'n_edges': len(edges),
            'mean_weight': float(np.mean(edges)),
            'std_weight': float(np.std(edges))
        }


class TemporalInteractionGraph(InteractionGraphBase):
    """
    C. TEMPORAL INTERACTION GRAPH
    
    Build graph from temporal trajectory.
    """
    
    def __init__(self, window: int = 10, seed: int = 42):
        super().__init__(seed)
        self.window = window
    
    def build(self, trajectory: np.ndarray) -> np.ndarray:
        """Build temporal interaction graph."""
        n_steps = trajectory.shape[0]
        n_nodes = trajectory.shape[1]
        
        adj = np.zeros((n_nodes, n_nodes))
        
        for t in range(n_steps - self.window):
            window_data = trajectory[t:t+self.window]
            
            tree = KDTree(window_data)
            distances, indices = tree.query(window_data, k=min(5, self.window))
            
            for i in range(n_nodes):
                for j_idx in range(len(indices[i])):
                    j = indices[i, j_idx]
                    if i != j:
                        adj[i, j] += 1
        
        self._graph = adj
        return adj
    
    def get_graph_curvature(self) -> Dict:
        """Compute graph-theoretic curvature."""
        if self._graph is None:
            return {'error': 'no_graph'}
        
        adj = (self._graph > 0).astype(int)
        degrees = adj.sum(axis=1)
        
        avg_degree = np.mean(degrees)
        degree_variance = np.var(degrees)
        
        return {
            'avg_degree': float(avg_degree),
            'degree_variance': float(degree_variance),
            'connectivity': float(np.sum(adj) / (adj.shape[0] * adj.shape[0]))
        }


class ScaleTransitionGraph(InteractionGraphBase):
    """
    D. SCALE-TRANSITION GRAPH
    
    Track graph structure across different k values.
    """
    
    def __init__(self, k_range: List[int] = None, seed: int = 42):
        super().__init__(seed)
        self.k_range = k_range or [3, 5, 10, 15]
    
    def build_scale_series(self, data: np.ndarray) -> List[np.ndarray]:
        """Build graph series across scales."""
        graphs = []
        
        for k in self.k_range:
            knn_graph = KNNInteractionGraph(k=k, seed=self.seed)
            adj = knn_graph.build(data)
            graphs.append(adj)
        
        self._graph = graphs[0]  # Store last
        return graphs
    
    def get_graph_fragmentation(self, scale_idx: int = -1) -> Dict:
        """Compute graph fragmentation at given scale."""
        if not isinstance(self._graph, list):
            graphs = [self._graph]
        else:
            graphs = self._graph
        
        if len(graphs) == 0:
            return {'error': 'no_graphs'}
        
        adj = graphs[scale_idx]
        adj_binary = (adj > 0).astype(int)
        
        components = self._count_components(adj_binary)
        largest_component = self._largest_component_size(adj_binary)
        n_nodes = adj.shape[0]
        
        fragmentation = 1.0 - (largest_component / n_nodes)
        
        return {
            'n_components': components,
            'largest_component_size': largest_component,
            'fragmentation': fragmentation,
            'scale': self.k_range[scale_idx] if abs(scale_idx) < len(self.k_range) else 'unknown'
        }
    
    def _count_components(self, adj: np.ndarray) -> int:
        n = adj.shape[0]
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
        return components
    
    def _largest_component_size(self, adj: np.ndarray) -> int:
        n = adj.shape[0]
        visited = set()
        max_size = 0
        
        for i in range(n):
            if i not in visited:
                component = []
                stack = [i]
                while stack:
                    node = stack.pop()
                    if node not in visited:
                        visited.add(node)
                        component.append(node)
                        for j in range(n):
                            if adj[node, j] and j not in visited:
                                stack.append(j)
                max_size = max(max_size, len(component))
        return max_size


class PerturbationResponseGraph(InteractionGraphBase):
    """
    E. PERTURBATION RESPONSE GRAPH
    
    Track how graph responds to perturbations.
    """
    
    def __init__(self, perturbation_type: str = 'noise', seed: int = 42):
        super().__init__(seed)
        self.perturbation_type = perturbation_type
    
    def build_perturbation_response(self, data: np.ndarray, 
                                   perturbation_strength: float = 0.1) -> Dict:
        """Build perturbation response graph."""
        n = data.shape[0]
        
        # Original graph
        tree_orig = KDTree(data)
        _, indices_orig = tree_orig.query(data, k=5)
        
        # Perturbed data
        noise = self.rng.normal(0, perturbation_strength, size=data.shape)
        perturbed = data + noise
        
        tree_pert = KDTree(perturbed)
        _, indices_pert = tree_pert.query(perturbed, k=5)
        
        # Response graph
        response = np.zeros((n, n))
        for i in range(n):
            orig_set = set(indices_orig[i])
            pert_set = set(indices_pert[i])
            
            # Count preserved neighbors
            preserved = len(orig_set & pert_set)
            lost = len(orig_set - pert_set)
            gained = len(pert_set - orig_set)
            
            response[i, 0] = preserved
            response[i, 1] = lost
            response[i, 2] = gained
        
        self._graph = response
        return response
    
    def get_response_statistics(self) -> Dict:
        """Get perturbation response statistics."""
        if self._graph is None:
            return {'error': 'no_graph'}
        
        preserved = self._graph[:, 0]
        lost = self._graph[:, 1]
        gained = self._graph[:, 2]
        
        total = preserved + lost
        
        persistence = np.sum(preserved) / (np.sum(total) + 1e-10)
        churn = np.sum(lost + gained) / (np.sum(total) + 1e-10)
        
        return {
            'persistence_rate': float(persistence),
            'churn_rate': float(churn),
            'avg_preserved': float(np.mean(preserved)),
            'avg_lost': float(np.mean(lost)),
            'avg_gained': float(np.mean(gained))
        }


def build_interaction_representation(data: np.ndarray, 
                                    graph_type: str,
                                    **kwargs) -> Tuple[np.ndarray, Dict]:
    """Factory function for building interaction graphs."""
    builders = {
        'knn': KNNInteractionGraph,
        'weighted': WeightedInteractionGraph,
        'temporal': TemporalInteractionGraph,
        'scale_transition': ScaleTransitionGraph,
        'perturbation': PerturbationResponseGraph
    }
    
    if graph_type not in builders:
        raise ValueError(f"Unknown graph type: {graph_type}")
    
    builder = builders[graph_type](**kwargs)
    graph = builder.build(data)
    metadata = builder.get_metadata() if hasattr(builder, 'get_metadata') else {}
    
    return graph, metadata


if __name__ == '__main__':
    print("Interaction Graph Representations")
    print("=" * 50)
    
    import sys
    sys.path.insert(0, '../')
    from synthetic_systems import generate_system
    
    # Test on hierarchical data
    data, _ = generate_system('hierarchical', n=50, depth=3, seed=42)
    
    # Test kNN graph
    knn = KNNInteractionGraph(k=5, seed=42)
    adj = knn.build(data)
    print(f"kNN Graph: {adj.shape}, edges={np.sum(adj > 0)}")
    
    # Test weighted graph
    weighted = WeightedInteractionGraph(decay=1.0, seed=42)
    w_adj = weighted.build(data)
    entropy = weighted.get_edge_entropy()
    print(f"Weighted Graph: edge_entropy={entropy['edge_entropy']:.3f}")
    
    # Test scale transition
    scale = ScaleTransitionGraph(k_range=[3, 5, 10], seed=42)
    graphs = scale.build_scale_series(data)
    frag = scale.get_graph_fragmentation(-1)
    print(f"Scale Transition: fragmentation={frag['fragmentation']:.3f}")
    
    print("\nGraph representations working.")