"""
SGP-CORE V2 Metric Redesign Module
"""
from .new_metrics import (
    LocalCurvatureEntropy,
    ScaleTransitionInstability,
    MultiScaleSpectralDrift,
    TopologicalPersistenceProxy,
    TemporalStabilityIndex,
    MetricRedesignSuite
)

__all__ = [
    'LocalCurvatureEntropy',
    'ScaleTransitionInstability', 
    'MultiScaleSpectralDrift',
    'TopologicalPersistenceProxy',
    'TemporalStabilityIndex',
    'MetricRedesignSuite'
]