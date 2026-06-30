"""
Trajectory analysis for Phase 005A Division 1.

Implements descriptive trajectory analysis for collapse dynamics.
Provides pattern identification without causal attribution or
universal law formulation.
"""

__version__ = "0.1.0"
__author__ = "SGP Core V2 Research Team"
__date__ = "2026-06-29"

import numpy as np
from typing import List, Tuple, Dict, Optional
from enum import Enum

from .collapse_dynamics import CollapsePattern, CollapseState
from .metrics import VelocityMetrics, AccelerationMetrics, CurvatureMetrics
class PatternClassifier:
    """
    Descriptive pattern classifier for collapse trajectories.
    
    Identifies empirical patterns without theoretical assumptions or
    universal law claims.
    """
    
    def __init__(self, velocity_threshold: float = 0.15, acceleration_threshold: float = 0.1):
        self.velocity_threshold = velocity_threshold
        self.acceleration_threshold = acceleration_threshold
        
    def classify_velocity_pattern(self, velocities: np.ndarray) -> str:
        """
        Classify velocity trajectory pattern for descriptive analysis.
        
        Args:
            velocities: Array of velocity values along trajectory
            
        Returns:
            Descriptive pattern classification
        """
        if len(velocities) < 3:
            return "insufficient_data"
            
        # Calculate descriptive statistics
        mean_velocity = np.mean(velocities)
        std_velocity = np.std(velocities)
        max_velocity = np.max(velocities)
        
        # Velocity change rate analysis
        velocity_changes = np.diff(velocities)
        mean_change_rate = np.mean(np.abs(velocity_changes))
        
        # Pattern classification
        if max_velocity < 0.1:
            return "minimal_velocity_change"
        elif std_velocity / (mean_velocity + 1e-10) < 0.1:
            return "stable_velocity"
        elif mean_change_rate > self.velocity_threshold:
            return "rapid_velocity_change"
        else:
            return "gradual_velocity_evolution"
    
    def classify_acceleration_pattern(self, accelerations: np.ndarray) -> str:
        """
        Classify acceleration trajectory pattern for descriptive analysis.
        
        Args:
            accelerations: Array of acceleration values
            
        Returns:
            Descriptive pattern classification
        """
        if len(accelerations) < 2:
            return "insufficient_data"
            
        # Calculate descriptive statistics
        mean_acceleration = np.mean(np.abs(accelerations))
        acceleration_sign_changes = np.sum(np.diff(np.sign(accelerations)) != 0)
        
        # Pattern classification
        if mean_acceleration < 0.05:
            return "minimal_acceleration"
        elif acceleration_sign_changes == 0:
            return "consistent_acceleration"
        elif acceleration_sign_changes > len(accelerations) / 3:
            return "oscillatory_acceleration"
        else:
            return "variable_acceleration"
class TrajectoryAnalysis:
    """
    Descriptive trajectory analysis for collapse dynamics.
    
    Provides empirical pattern identification without causal attribution
    or universal law formulation.
    """
    
    def __init__(self, velocity_threshold: float = 0.15, acceleration_threshold: float = 0.1):
        self.velocity_threshold = velocity_threshold
        self.acceleration_threshold = acceleration_threshold
        self.pattern_classifier = PatternClassifier(velocity_threshold, acceleration_threshold)
        
    def segment_collapse_trajectory(self, observations: List) -> List[Dict]:
        """
        Segment collapse trajectory into descriptive phases.
        
        Identifies segments without theoretical phase definitions.
        
        Args:
            observations: List of CollapseObservation objects
            
        Returns:
            List of segment dictionaries with descriptive characteristics
        """
        if len(observations) < 3:
            return []
            
        segments = []
        current_segment = {
            'start_step': observations[0].step,
            'start_velocity': observations[0].velocity_magnitude,
            'start_acceleration': observations[0].acceleration_magnitude,
            'mean_velocity': 0.0,
            'mean_acceleration': 0.0,
            'velocity_variance': 0.0,
            'acceleration_variance': 0.0,
            'duration_steps': 0
        }
        
        for obs in observations:
            current_segment['mean_velocity'] += obs.velocity_magnitude
            current_segment['mean_acceleration'] += obs.acceleration_magnitude
            current_segment['duration_steps'] += 1
            
        # Calculate means
        current_segment['mean_velocity'] /= current_segment['duration_steps']
        current_segment['mean_acceleration'] /= current_segment['duration_steps']
        
        segments.append(current_segment)
        return segments
    
    def identify_collapse_pattern(self, trajectory: List[Tuple[float, ...]]) -> Dict:
        """
        Identify empirical collapse pattern from trajectory.
        
        Returns descriptive pattern without theoretical attribution.
        
        Args:
            trajectory: Sequence of state vectors
            
        Returns:
            Dict with pattern identification results
        """
        # Extract metrics for analysis
        velocities = VelocityMetrics.calculate_velocity(trajectory)
        accelerations = AccelerationMetrics.calculate_acceleration(velocities)
        curvatures = CurvatureMetrics.calculate_curvature(trajectory)
        
        if len(velocities) < 3:
            return {
                'pattern': 'insufficient_data',
                'confidence': 0.0,
                'characteristic_velocity': 0.0,
                'distinctive_features': []
            }
        
        # Classify patterns descriptively
        velocity_pattern = self.pattern_classifier.classify_velocity_pattern(velocities)
        acceleration_pattern = self.pattern_classifier.classify_acceleration_pattern(accelerations)
        
        # Combine patterns into descriptive classification
        pattern_mapping = {
            ('minimal_velocity_change', 'minimal_acceleration'): 'steady_state',
            ('stable_velocity', 'consistent_acceleration'): 'balanced_dynamics',
            ('rapid_velocity_change', 'variable_acceleration'): 'turbulent_collapse',
            ('gradual_velocity_evolution', 'oscillatory_acceleration'): 'oscillatory_collapse',
            ('rapid_velocity_change', 'oscillatory_acceleration'): 'chaotic_collapse',
            ('gradual_velocity_evolution', 'consistent_acceleration'): 'systematic_collapse'
        }
        
        combined_pattern = pattern_mapping.get(
            (velocity_pattern, acceleration_pattern),
            'mixed_pattern'
        )
        
        return {
            'pattern': combined_pattern,
            'confidence': self._calculate_pattern_confidence(
                velocities, accelerations, curvatures
            ),
            'characteristic_velocity': float(np.mean(velocities)),
            'distinctive_features': [
                velocity_pattern,
                acceleration_pattern,
                f'curvature_range_{np.min(curvatures):.4f}_{np.max(curvatures):.4f}'
            ]
        }
    
    def _calculate_pattern_confidence(self, velocities: np.ndarray, accelerations: np.ndarray, curvatures: np.ndarray) -> float:
        """
        Calculate confidence in pattern identification.
        
        Descriptive measure of pattern distinctiveness.
        
        Args:
            velocities: Velocity array
            accelerations: Acceleration array  
            curvatures: Curvature array
            
        Returns:
            Confidence value between 0 and 1
        """
        if len(velocities) < 2:
            return 0.0
            
        # Calculate variance-based distinctiveness measures
        velocity_distinctiveness = np.std(velocities) / (np.mean(np.abs(velocities)) + 1e-10)
        acceleration_distinctiveness = np.std(accelerations) / (np.mean(np.abs(accelerations)) + 1e-10)
        curvature_distinctiveness = np.std(curvatures) / (np.mean(np.abs(curvatures)) + 1e-10)
        
        # Combine distinctiveness measures
        combined = (velocity_distinctiveness + acceleration_distinctiveness + curvature_distinctiveness) / 3
        return min(combined, 1.0)
    
    def analyze_transitional_dynamics(self, observations: List) -> Dict:
        """
        Analyze transitional dynamics between collapse phases.
        
        Descriptive analysis without theoretical phase definitions.
        
        Args:
            observations: Sequential collapse observations
            
        Returns:
            Dict with transition analysis results
        """
        if len(observations) < 4:
            return {
                'transitions_identified': 0,
                'transition_characteristics': [],
                'stability_intervals': [],
                'regime_changes': []
            }
        
        transitions = []
        regime_changes = []
        stability_intervals = []
        
        for i in range(len(observations) - 1):
            current = observations[i]
            next_obs = observations[i + 1]
            
            # Calculate descriptive transition metrics
            velocity_change = abs(next_obs.velocity_magnitude - current.velocity_magnitude)
            acceleration_change = abs(next_obs.acceleration_magnitude - current.acceleration_magnitude)
            
            # Detect significant transitions
            if velocity_change > self.velocity_threshold or acceleration_change > self.acceleration_threshold:
                transition = {
                    'from_step': current.step,
                    'to_step': next_obs.step,
                    'velocity_change_magnitude': velocity_change,
                    'acceleration_change_magnitude': acceleration_change,
                    'state_change': f"{current.state.value} -> {next_obs.state.value}"
                }
                transitions.append(transition)
                regime_changes.append({
                    'step': next_obs.step,
                    'regime_type': 'regime_change' if transition['velocity_change_magnitude'] > self.velocity_threshold else 'evolution',
                    'change_magnitude': max(transition['velocity_change_magnitude'], transition['acceleration_change_magnitude'])
                })
        
        # Identify stability intervals
        for i in range(len(observations)):
            if i > 0 and i < len(observations) - 1:
                # Check if this point represents a stable interval
                prev_vel = observations[i - 1].velocity_magnitude
                current_vel = observations[i].velocity_magnitude
                next_vel = observations[i + 1].velocity_magnitude
                
                velocity_variation = max(abs(current_vel - prev_vel), abs(next_vel - current_vel))
                if velocity_variation < self.velocity_threshold * 0.5:
                    stability_intervals.append({
                        'start_step': max(0, i - 1),
                        'end_step': min(len(observations) - 1, i + 1),
                        'stability_measure': 1.0 - (velocity_variation / self.velocity_threshold)
                    })
        
        return {
            'transitions_identified': len(transitions),
            'transition_characteristics': transitions,
            'stability_intervals': stability_intervals,
            'regime_changes': regime_changes
        }


def analyze_collapse_dynamics(
    trajectory: List[Tuple[float, ...]],
    velocity_threshold: float = 0.15,
    acceleration_threshold: float = 0.1
) -> Dict:
    """
    Comprehensive collapse dynamics analysis.
    
    Args:
        trajectory: System trajectory through state space
        velocity_threshold: Velocity threshold for pattern identification
        acceleration_threshold: Acceleration threshold for pattern identification
        
    Returns:
        Dict with comprehensive analysis results
    """
    analyzer = TrajectoryAnalysis(velocity_threshold, acceleration_threshold)
    
    # Basic trajectory metrics
    velocities = VelocityMetrics.calculate_velocity(trajectory)
    accelerations = AccelerationMetrics.calculate_acceleration(velocities)
    
    # Pattern identification
    pattern_results = analyzer.identify_collapse_pattern(trajectory)
    
    # Transition analysis
    transition_results = analyzer.analyze_transitional_dynamics([])
    
    # Segment analysis
    segments = analyzer.segment_collapse_trajectory([])
    
    return {
        'trajectory_length': len(trajectory),
        'velocity_statistics': {
            'mean': float(np.mean(velocities) if len(velocities) > 0 else 0.0),
            'std': float(np.std(velocities) if len(velocities) > 0 else 0.0),
            'max': float(np.max(velocities) if len(velocities) > 0 else 0.0),
            'min': float(np.min(velocities) if len(velocities) > 0 else 0.0)
        },
        'acceleration_statistics': {
            'mean': float(np.mean(np.abs(accelerations)) if len(accelerations) > 0 else 0.0),
            'std': float(np.std(accelerations) if len(accelerations) > 0 else 0.0),
            'max': float(np.max(np.abs(accelerations)) if len(accelerations) > 0 else 0.0)
        },
        'pattern_identification': pattern_results,
        'transitional_dynamics': transition_results,
        'trajectory_segments': segments
    }


if __name__ == "__main__":
    print("Trajectory analysis module - Phase 005A Division 1")
    print("Provides descriptive trajectory analysis without theoretical assumptions")
