"""
Anti-Spoof Detectors

NO consciousness, SFH, ontology, or metaphysical terminology.

Detectors for synthetic artifacts that can fool single metrics.
"""

import numpy as np
from scipy import stats
from scipy.spatial import KDTree
from typing import Dict, Tuple


class SyntheticElbowDetector:
    """
    Detect synthetic elbow injection (from V2_005).
    """
    
    def __init__(self, threshold: float = 0.01):
        self.threshold = threshold
    
    def detect(self, data: np.ndarray, metrics: Dict) -> Dict:
        """Detect synthetic elbow injection."""
        suspicion = 0.0
        evidence = []
        
        # Check for high curvature (key indicator)
        if 'curvature_entropy' in metrics:
            curv = metrics['curvature_entropy'].get('curvature_variance', 0)
            if curv > self.threshold:
                suspicion += 0.6 * (curv / 0.07)  # Scaled
                evidence.append(f'high_curvature:{curv:.6f}')
        
        # Check for non-uniform variance in regions
        if data.shape[0] > 20:
            sections = 5
            section_size = data.shape[0] // sections
            variances = []
            for i in range(sections):
                section_var = np.var(data[i*section_size:(i+1)*section_size])
                variances.append(section_var)
            
            var_ratio = max(variances) / (min(variances) + 1e-10)
            if var_ratio > 3.0:
                suspicion += 0.3
                evidence.append(f'variable_variance_ratio:{var_ratio:.2f}')
        
        return {
            'detector': 'synthetic_elbow',
            'suspicion': min(suspicion, 1.0),
            'confidence': 'HIGH' if suspicion > 0.5 else ('MEDIUM' if suspicion > 0.2 else 'LOW'),
            'evidence': evidence
        }


class DuplicatePointDetector:
    """
    Detect duplicated point clouds (fake persistence).
    """
    
    def __init__(self, distance_threshold: float = 0.01):
        self.threshold = distance_threshold
    
    def detect(self, data: np.ndarray, metrics: Dict) -> Dict:
        """Detect point duplication."""
        suspicion = 0.0
        evidence = []
        
        # Check for very close neighbor pairs
        tree = KDTree(data)
        distances, _ = tree.query(data, k=2)
        distances = distances[:, 1]  # Exclude self
        
        close_pairs = np.sum(distances < self.threshold)
        close_ratio = close_pairs / len(data)
        
        if close_ratio > 0.1:  # More than 10% very close
            suspicion += 0.5
            evidence.append(f'close_pairs_ratio:{close_ratio:.3f}')
        
        # Check for persistence (if duplicated, persistence is artificially high)
        if 'topological_persistence' in metrics:
            persist = metrics['topological_persistence']
            if isinstance(persist, dict):
                persist_mean = persist.get('persistence_mean', 0)
                if persist_mean > 0.95:
                    suspicion += 0.3
                    evidence.append(f'high_persistence:{persist_mean:.3f}')
        
        return {
            'detector': 'duplicate_points',
            'suspicion': min(suspicion, 1.0),
            'confidence': 'HIGH' if suspicion > 0.5 else ('MEDIUM' if suspicion > 0.2 else 'LOW'),
            'evidence': evidence
        }


class WarpedGaussianDetector:
    """
    Detect warped Gaussian mixture artifacts.
    """
    
    def __init__(self):
        pass
    
    def detect(self, data: np.ndarray, metrics: Dict) -> Dict:
        """Detect warped Gaussian patterns."""
        suspicion = 0.0
        evidence = []
        
        # Check for unusual kurtosis (warping creates heavy tails)
        flat_data = data.flatten()
        kurt = stats.kurtosis(flat_data)
        
        if abs(kurt) > 3.0:  # Heavy tails
            suspicion += 0.4
            evidence.append(f'kurtosis:{kurt:.2f}')
        
        # Check for asymmetry
        skew = stats.skew(flat_data)
        if abs(skew) > 2.0:
            suspicion += 0.3
            evidence.append(f'skew:{skew:.2f}')
        
        return {
            'detector': 'warped_gaussian',
            'suspicion': min(suspicion, 1.0),
            'confidence': 'HIGH' if suspicion > 0.5 else ('MEDIUM' if suspicion > 0.2 else 'LOW'),
            'evidence': evidence
        }


class DensityInflationDetector:
    """
    Detect density inflation artifacts.
    """
    
    def __init__(self):
        pass
    
    def detect(self, data: np.ndarray, metrics: Dict) -> Dict:
        """Detect density inflation."""
        suspicion = 0.0
        evidence = []
        
        # Check for density anomalies
        tree = KDTree(data)
        distances, _ = tree.query(data, k=5)
        mean_distances = distances[:, 1:].mean(axis=1)
        
        # Very low variance in distances indicates density inflation
        dist_variance = np.var(mean_distances)
        if dist_variance < 0.01:
            suspicion += 0.4
            evidence.append(f'low_dist_variance:{dist_variance:.6f}')
        
        # Check for artificial clustering
        if 'topological_persistence' in metrics:
            persist = metrics['topological_persistence']
            if isinstance(persist, dict):
                cluster_count = persist.get('final_cluster_count', 0)
                if cluster_count < data.shape[0] * 0.1:  # Very few clusters
                    suspicion += 0.3
                    evidence.append(f'few_clusters:{cluster_count}')
        
        return {
            'detector': 'density_inflation',
            'suspicion': min(suspicion, 1.0),
            'confidence': 'HIGH' if suspicion > 0.5 else ('MEDIUM' if suspicion > 0.2 else 'LOW'),
            'evidence': evidence
        }


class FilteredNoiseDetector:
    """
    Detect filtered noise (fake temporal coherence).
    """
    
    def __init__(self):
        pass
    
    def detect(self, data: np.ndarray, metrics: Dict) -> Dict:
        """Detect filtered noise patterns."""
        suspicion = 0.0
        evidence = []
        
        # If data is time series
        if data.shape[1] > 1:  # Multi-dimensional = likely temporal
            # Check for suspiciously smooth transitions
            if data.shape[0] > 10:
                diffs = np.diff(data, axis=0)
                diff_variance = np.var(diffs)
                
                if diff_variance < 0.1:
                    suspicion += 0.4
                    evidence.append(f'low_diff_variance:{diff_variance:.4f}')
        
        return {
            'detector': 'filtered_noise',
            'suspicion': min(suspicion, 1.0),
            'confidence': 'HIGH' if suspicion > 0.5 else ('MEDIUM' if suspicion > 0.2 else 'LOW'),
            'evidence': evidence
        }


class AntiSpoofSystem:
    """
    Combined anti-spoof system with all detectors.
    """
    
    def __init__(self):
        self.detectors = [
            SyntheticElbowDetector(),
            DuplicatePointDetector(),
            WarpedGaussianDetector(),
            DensityInflationDetector(),
            FilteredNoiseDetector()
        ]
    
    def run_all(self, data: np.ndarray, metrics: Dict) -> Dict:
        """Run all detectors."""
        results = []
        total_suspicion = 0.0
        
        for detector in self.detectors:
            result = detector.detect(data, metrics)
            results.append(result)
            total_suspicion += result['suspicion']
        
        # Average suspicion
        avg_suspicion = total_suspicion / len(results)
        
        return {
            'overall_suspicion': min(avg_suspicion, 1.0),
            'max_suspicion': max(r['suspicion'] for r in results),
            'detector_results': results,
            'rejected': avg_suspicion > 0.5
        }


if __name__ == '__main__':
    print("Anti-Spoof Detectors")
    print("=" * 50)
    
    import sys
    sys.path.insert(0, '../')
    from scripts.core.synthetic_systems import generate_system
    from scripts.core.universal_dk_pipeline import UniversalDkPipeline
    from scripts.core.metric_redesign.new_metrics import MetricRedesignSuite
    
    # Test on legitimate vs deceptive
    print("\nTesting detectors...")
    
    anti_spoof = AntiSpoofSystem()
    
    for sys_type, params in [('hierarchical', {'n': 100, 'depth': 3}),
                               ('random_gaussian', {'n': 100, 'dimensions': 10})]:
        data, _ = generate_system(sys_type, **params, seed=42)
        
        pipeline = UniversalDkPipeline(seed=42)
        dk = pipeline.run_full_analysis(data, k_values=list(range(1, 11)))
        
        suite = MetricRedesignSuite(seed=42)
        raw_metrics = suite.compute_all(data, dk['participation_ratio']['k_values'],
                                       np.array(dk['participation_ratio']['dk_values']))
        
        result = anti_spoof.run_all(data, raw_metrics)
        
        print(f"\n{sys_type}:")
        print(f"  Suspicion: {result['overall_suspicion']:.3f} [{'REJECTED' if result['rejected'] else 'ACCEPTED'}]")
    
    print("\nDetectors working.")