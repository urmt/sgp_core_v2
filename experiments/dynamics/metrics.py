"""
Collapse metrics for Phase 005A Division 1.

Implements empirical velocity, acceleration, curvature, and hysteresis metrics
for system collapse dynamics. Provides descriptive measurement frameworks
without theoretical or ontological commitments.
"""

__version__ = "0.1.0"
__author__ = "SGP Core V2 Research Team"
__date__ = "2026-06-29"

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
class VelocityMetrics:
    """
    Velocity analysis for collapse trajectories.
    
    Measures temporal rate of change in system parameters
    for descriptive collapse pattern identification.
    """
    
    @staticmethod
    def calculate_velocity(
        trajectory: List[Tuple[float, ...]],
        time_steps: Optional[List[float]] = None
    ) -> np.ndarray:
        """
        Calculate velocity along trajectory from temporal observations.
        
        Args:
            trajectory: Sequence of system state vectors
            time_steps: Optional time intervals (defaults to uniform)
            
        Returns:
            Array of velocity magnitudes
        """
        if len(trajectory) < 2:
            return np.array([])
            
        if time_steps is None:
            time_steps = np.ones(len(trajectory) - 1)
            
        velocities = []
        for i in range(len(trajectory) - 1):
            displacement = np.array(trajectory[i + 1]) - np.array(trajectory[i])
            dt = time_steps[i] if i < len(time_steps) else 1.0
            velocity = np.linalg.norm(displacement) / dt if dt > 0 else 0.0
            velocities.append(velocity)
            
        return np.array(velocities)
    
    @staticmethod
    def velocity_change_rate(velocities: np.ndarray) -> np.ndarray:
        """
        Calculate rate of velocity change from velocity sequence.
        
        Descriptive measure of acceleration in collapse trajectory.
        
        Args:
            velocities: Array of velocity values
            
        Returns:
            Array of velocity change rates
        """
        if len(velocities) < 2:
            return np.array([])
            
        change_rates = []
        for i in range(len(velocities) - 1):
            if velocities[i] > 0:
                rate = (velocities[i + 1] - velocities[i]) / velocities[i]
            else:
                rate = 0.0
            change_rates.append(rate)
            
        return np.array(change_rates)
class AccelerationMetrics:
    """
    Acceleration analysis for collapse dynamics.
    
    Measures temporal rate of change in velocity for descriptive pattern
    identification in system collapse trajectories.
    """
    
    @staticmethod
    def calculate_acceleration(velocities: np.ndarray, time_steps: Optional[List[float]] = None) -> np.ndarray:
        """
        Calculate acceleration from velocity sequence.
        
        Args:
            velocities: Array of velocity values
            time_steps: Optional time intervals (defaults to uniform)
            
        Returns:
            Array of acceleration values
        """
        if len(velocities) < 2:
            return np.array([])
            
        if time_steps is None:
            time_steps = np.ones(len(velocities) - 1)
            
        accelerations = []
        for i in range(len(velocities) - 1):
            delta_v = velocities[i + 1] - velocities[i]
            dt = time_steps[i] if i < len(time_steps) else 1.0
            acceleration = delta_v / dt if dt > 0 else 0.0
            accelerations.append(acceleration)
            
        return np.array(accelerations)
    
    @staticmethod
    def acceleration_change_rate(accelerations: np.ndarray) -> np.ndarray:
        """
        Calculate rate of acceleration change for pattern recognition.
        
        Args:
            accelerations: Array of acceleration values
            
        Returns:
            Array of acceleration change rates
        """
        if len(accelerations) < 2:
            return np.array([])
            
        return np.diff(accelerations)
class CurvatureMetrics:
    """
    Curvature analysis for collapse trajectory description.
    
    Measures pathway curvature in state space for descriptive pattern identification.
    """
    
    @staticmethod
    def calculate_curvature(trajectory: List[Tuple[float, ...]]) -> np.ndarray:
        """
        Calculate curvature along collapse trajectory.
        
        Provides descriptive measurement of pathway complexity.
        
        Args:
            trajectory: Sequence of state vectors
            
        Returns:
            Array of curvature values along trajectory
        """
        if len(trajectory) < 3:
            return np.array([])
            
        curvatures = []
        for i in range(1, len(trajectory) - 1):
            p0 = np.array(trajectory[i - 1])
            p1 = np.array(trajectory[i])
            p2 = np.array(trajectory[i + 1])
            
            v1 = p1 - p0
            v2 = p2 - p1
            
            if np.linalg.norm(v1) < 1e-10 or np.linalg.norm(v2) < 1e-10:
                curvatures.append(0.0)
                continue
                
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.arccos(cos_angle)
            curvature = angle / (np.linalg.norm(v1) + np.linalg.norm(v2))
            
            curvatures.append(curvature)
            
        # Pad first and last with zeros
        curvatures = [0.0] + curvatures + [0.0]
        return np.array(curvatures)
class CollapseMetrics:
    """
    Unified collapse metrics wrapper providing all metric computations.

    Aggregates VelocityMetrics, AccelerationMetrics, CurvatureMetrics,
    and HysteresisMetrics into a single interface.
    """

    def __init__(self, velocity_threshold: float = 0.15, acceleration_threshold: float = 0.1):
        self.velocity_threshold = velocity_threshold
        self.acceleration_threshold = acceleration_threshold

    def compute_all(self, trajectory):
        return collapse_trajectory_metrics(trajectory)

    def compute_velocity(self, trajectory):
        return VelocityMetrics.calculate_velocity(trajectory)

    def compute_acceleration(self, velocities):
        return AccelerationMetrics.calculate_acceleration(velocities)

    def compute_curvature(self, trajectory):
        return CurvatureMetrics.calculate_curvature(trajectory)

    def compute_hysteresis(self, trajectory):
        return HysteresisMetrics.calculate_hysteresis_indicator(trajectory)

class HysteresisMetrics:
    """
    Hysteresis analysis for descriptive path dependence.
    
    Measures path dependence and history effects in collapse dynamics.
    """
    
    @staticmethod
    def calculate_hysteresis_indicator(trajectory: List[Tuple[float, ...]]) -> np.ndarray:
        """
        Calculate hysteresis indicator along trajectory.
        
        Provides descriptive measure of path dependence.
        
        Args:
            trajectory: Sequence of state vectors
            
        Returns:
            Array of hysteresis indicators along trajectory
        """
        if len(trajectory) < 3:
            return np.array([])
            
        hysteresis = []
        for i in range(1, len(trajectory) - 1):
            p0 = np.array(trajectory[i - 1])
            p1 = np.array(trajectory[i])
            p2 = np.array(trajectory[i + 1])
            
            displacement_backward = np.linalg.norm(p1 - p0)
            displacement_forward = np.linalg.norm(p2 - p1)
            
            if displacement_backward < 1e-10:
                hysteresis.append(0.0)
                continue
                
            hysteresis_value = abs(displacement_forward - displacement_backward) / displacement_backward
            hysteresis.append(min(hysteresis_value, 1.0))
            
        # Pad endpoints
        hysteresis = [0.0] + hysteresis + [0.0]
        return np.array(hysteresis)


def collapse_trajectory_metrics(
    trajectory: List[Tuple[float, ...]],
    time_steps: Optional[List[float]] = None
) -> Dict[str, np.ndarray]:
    """
    Calculate all collapse trajectory metrics for empirical analysis.
    
    Args:
        trajectory: System trajectory through state space
        time_steps: Optional time intervals
        
    Returns:
        Dictionary containing velocity, acceleration, curvature, hysteresis metrics
    """
    metrics = {}
    
    # Calculate velocity and related metrics
    velocities = VelocityMetrics.calculate_velocity(trajectory, time_steps)
    metrics['velocity'] = velocities
    metrics['velocity_change_rate'] = VelocityMetrics.velocity_change_rate(velocities)
    
    # Calculate acceleration metrics
    accelerations = AccelerationMetrics.calculate_acceleration(velocities, time_steps)
    metrics['acceleration'] = accelerations
    metrics['acceleration_change_rate'] = AccelerationMetrics.acceleration_change_rate(accelerations)
    
    # Calculate curvature metrics
    metrics['curvature'] = CurvatureMetrics.calculate_curvature(trajectory)
    
    # Calculate hysteresis metrics
    metrics['hysteresis'] = HysteresisMetrics.calculate_hysteresis_indicator(trajectory)
    
    return metrics


if __name__ == "__main__":
    print("Collapse metrics module - Phase 005A Division 1")
    print("Provides empirical measurement frameworks without theoretical assumptions")
