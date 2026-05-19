"""
Ensemble Metric System for Anti-Spoof

NO consciousness, SFH, ontology, or metaphysical terminology.

Combines multiple metrics with:
- Weighted z-score normalization
- Bootstrap averaging
- Multi-scale coherence
- Temporal-geometric agreement
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class MetricConsensusScore:
    """
    A. METRIC CONSENSUS SCORE
    
    Combine multiple metrics with weighted z-score normalization.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        # Weights for each metric (can be tuned)
        self.weights = {
            'curvature': 0.25,
            'instability': 0.25,
            'persistence': 0.25,
            'spectral': 0.25
        }
    
    def compute(self, metric_values: Dict[str, float]) -> Dict:
        """
        Compute consensus score from multiple metrics.
        
        Args:
            metric_values: Dict of {metric_name: value}
        
        Returns:
            consensus_score, confidence, component_z_scores
        """
        # Z-score normalization
        z_scores = {}
        for name, value in metric_values.items():
            # Use robust z-score (median, MAD)
            median = np.median(list(metric_values.values()))
            mad = np.median(np.abs(np.array(list(metric_values.values())) - median))
            if mad > 0:
                z_scores[name] = 0.6745 * (value - median) / mad
            else:
                z_scores[name] = 0.0
        
        # Weighted consensus
        consensus = 0.0
        for name, z in z_scores.items():
            weight = self.weights.get(name, 0.25)
            consensus += weight * z
        
        # Confidence = agreement between metrics
        z_array = np.array(list(z_scores.values()))
        confidence = 1.0 / (1.0 + np.std(z_array))
        
        return {
            'consensus_score': float(consensus),
            'confidence': float(confidence),
            'z_scores': z_scores,
            'metric_agreement': float(np.std(z_array))
        }


class SpoofPenaltyScore:
    """
    B. SPOOF PENALTY SCORE
    
    Detect suspicious metric patterns that might indicate spoofing.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
    
    def compute(self, metric_values: Dict[str, float], 
                raw_metrics: Dict) -> Dict:
        """
        Compute spoof penalty based on suspicious patterns.
        
        Patterns that trigger penalty:
        1. Single metric dominates (others near zero)
        2. Extreme values in one metric
        3. Suspicious ratio between related metrics
        """
        penalty = 0.0
        triggers = []
        
        # Check for single-metric dominance
        values = np.array(list(metric_values.values()))
        values = values[values > 0]  # Exclude zeros
        if len(values) > 1:
            max_ratio = np.max(values) / (np.min(values) + 1e-10)
            if max_ratio > 100:  # Extreme dominance
                penalty += 0.3
                triggers.append('single_metric_dominance')
        
        # Check for extreme curvature (deceptive curvature pattern)
        if 'curvature' in metric_values:
            curv = metric_values['curvature']
            # Deceptive curvature has very high values
            if curv > 0.01:  # Threshold for suspicion
                penalty += 0.4 * (curv / 0.07)  # Scaled penalty
                triggers.append('extreme_curvature')
        
        # Check for unstable persistence
        if 'persistence' in raw_metrics:
            persist = raw_metrics['persistence']
            if isinstance(persist, dict):
                if 'persistence_std' in persist and persist.get('persistence_std', 0) < 0.01:
                    penalty += 0.2
                    triggers.append('unstable_persistence')
        
        # Normalize penalty to [0, 1]
        penalty = min(penalty, 1.0)
        
        return {
            'spoof_penalty': float(penalty),
            'triggers': triggers,
            'suspicion_level': 'HIGH' if penalty > 0.5 else ('MEDIUM' if penalty > 0.2 else 'LOW')
        }


class MultiScaleCoherenceIndex:
    """
    C. MULTI-SCALE COHERENCE INDEX
    
    Measure consistency of structure across scales.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
    
    def compute(self, k_values: List[int], dk_values: np.ndarray) -> Dict:
        """
        Compute coherence across scales.
        
        Real organization should show consistent patterns across scales.
        Synthetic tricks often show scale-specific anomalies.
        """
        if len(k_values) < 3:
            return {'coherence': 0.0, 'error': 'insufficient_scales'}
        
        # Split into low, mid, high scales
        n = len(k_values)
        third = n // 3
        
        low_scales = dk_values[:third]
        mid_scales = dk_values[third:2*third]
        high_scales = dk_values[2*third:]
        
        # Compute coherence as correlation between scale segments
        if len(low_scales) > 1 and len(mid_scales) > 1:
            # Use minimum length for correlation
            min_len = min(len(low_scales), len(mid_scales))
            corr_low_mid = np.corrcoef(low_scales[:min_len], mid_scales[:min_len])[0, 1] if min_len > 1 else 0
            
            min_len2 = min(len(mid_scales), len(high_scales))
            corr_mid_high = np.corrcoef(mid_scales[:min_len2], high_scales[:min_len2])[0, 1] if min_len2 > 1 else 0
            
            coherence = (corr_low_mid + corr_mid_high) / 2
            
            # Also check variance consistency
            var_consistency = 1.0 / (1.0 + np.abs(np.var(low_scales) - np.var(high_scales)))
            
            return {
                'coherence': float(coherence) if not np.isnan(coherence) else 0.0,
                'var_consistency': float(var_consistency),
                'scale_correlations': {
                    'low_mid': float(corr_low_mid) if not np.isnan(corr_low_mid) else 0.0,
                    'mid_high': float(corr_mid_high) if not np.isnan(corr_mid_high) else 0.0
                }
            }
        else:
            return {'coherence': 0.0, 'error': 'insufficient_data'}


class TemporalGeometricAgreement:
    """
    D. TEMPORAL-GEOMETRIC AGREEMENT
    
    Check whether temporal organization matches geometric organization.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
    
    def compute(self, geometric_metrics: Dict, temporal_metrics: Dict = None) -> Dict:
        """
        Check agreement between static geometry and temporal structure.
        
        Deceptive static geometry should fail temporal consistency.
        """
        if temporal_metrics is None:
            return {'agreement': 1.0, 'note': 'no_temporal_data'}
        
        # Compare stability indicators
        geo_stability = geometric_metrics.get('instability', 0)
        temp_stability = temporal_metrics.get('stability_index', 1.0)
        
        # Agreement = inverse of discrepancy
        if geo_stability > 0 and temp_stability > 0:
            ratio = min(geo_stability, temp_stability) / max(geo_stability, temp_stability)
        else:
            ratio = 0.0
        
        return {
            'agreement': float(ratio),
            'geo_stability': float(geo_stability),
            'temp_stability': float(temp_stability),
            'consistent': ratio > 0.5
        }


class EnsembleMetricSystem:
    """
    Combined ensemble system with all components.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        self.consensus = MetricConsensusScore(seed)
        self.spoof_penalty = SpoofPenaltyScore(seed)
        self.coherence = MultiScaleCoherenceIndex(seed)
        self.temporal_geo = TemporalGeometricAgreement(seed)
    
    def compute_ensemble(self, data: np.ndarray, k_values: List[int],
                        dk_values: np.ndarray, raw_metrics: Dict,
                        temporal_data: np.ndarray = None) -> Dict:
        """
        Compute full ensemble analysis.
        """
        # Extract metric values
        metric_values = {}
        if 'curvature_entropy' in raw_metrics:
            metric_values['curvature'] = raw_metrics['curvature_entropy'].get('curvature_variance', 0)
        if 'scale_transition' in raw_metrics:
            metric_values['instability'] = raw_metrics['scale_transition'].get('instability', 0)
        if 'topological_persistence' in raw_metrics and 'error' not in raw_metrics['topological_persistence']:
            metric_values['persistence'] = raw_metrics['topological_persistence'].get('persistence_mean', 0)
        if 'spectral_drift' in raw_metrics and 'error' not in raw_metrics['spectral_drift']:
            metric_values['spectral'] = raw_metrics['spectral_drift'].get('spectral_velocity_mean', 0)
        
        # Compute ensemble components
        consensus_result = self.consensus.compute(metric_values)
        spoof_result = self.spoof_penalty.compute(metric_values, raw_metrics)
        coherence_result = self.coherence.compute(k_values, dk_values)
        
        # Temporal-geometric agreement (if temporal data provided)
        temporal_metrics = None
        if temporal_data is not None:
            from scripts.core.metric_redesign.new_metrics import TemporalStabilityIndex
            temp_calc = TemporalStabilityIndex(seed=self.seed)
            temporal_metrics = temp_calc.compute(temporal_data)
        
        agreement_result = self.temporal_geo.compute(raw_metrics, temporal_metrics)
        
        # Final ensemble score (weighted combination)
        base_score = consensus_result['consensus_score']
        spoof_adjusted = base_score * (1.0 - spoof_result['spoof_penalty'])
        coherence_weighted = spoof_adjusted * (0.5 + 0.5 * coherence_result.get('coherence', 0.5))
        
        final_score = coherence_weighted * (0.7 + 0.3 * agreement_result.get('agreement', 1.0))
        
        return {
            'final_ensemble_score': float(final_score),
            'consensus': consensus_result,
            'spoof_penalty': spoof_result,
            'coherence': coherence_result,
            'temporal_agreement': agreement_result,
            'metric_values': metric_values
        }


if __name__ == '__main__':
    print("Ensemble Metric System")
    print("=" * 50)
    
    import sys
    sys.path.insert(0, '../')
    from scripts.core.synthetic_systems import generate_system
    from scripts.core.universal_dk_pipeline import UniversalDkPipeline
    from scripts.core.metric_redesign.new_metrics import MetricRedesignSuite
    
    # Test on legitimate vs adversarial
    print("\nTesting ensemble...")
    
    for sys_type in ['random_gaussian', 'hierarchical']:
        data, _ = generate_system(sys_type, n=100, dimensions=10, seed=42)
        
        pipeline = UniversalDkPipeline(seed=42)
        dk = pipeline.run_full_analysis(data, k_values=list(range(1, 11)))
        
        suite = MetricRedesignSuite(seed=42)
        raw_metrics = suite.compute_all(data, dk['participation_ratio']['k_values'],
                                       np.array(dk['participation_ratio']['dk_values']))
        
        ensemble = EnsembleMetricSystem(seed=42)
        result = ensemble.compute_ensemble(
            data, 
            dk['participation_ratio']['k_values'],
            np.array(dk['participation_ratio']['dk_values']),
            raw_metrics
        )
        
        print(f"\n{sys_type}:")
        print(f"  Final score: {result['final_ensemble_score']:.4f}")
        print(f"  Consensus: {result['consensus']['consensus_score']:.4f}")
        print(f"  Spoof penalty: {result['spoof_penalty']['spoof_penalty']:.4f} [{result['spoof_penalty']['suspicion_level']}]")
        print(f"  Coherence: {result['coherence'].get('coherence', 0):.4f}")
    
    print("\nEnsemble system working.")