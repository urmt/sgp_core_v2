"""
Core collapse dynamics engine for Phase 005A Division 1.

This module provides descriptive pattern analysis of system collapse dynamics
without ontological claims, causal attribution, or universal law formulations.
"""

__version__ = "0.1.0"
__author__ = "SGP Core V2 Research Team"
__date__ = "2026-06-29"

from .collapse_dynamics import CollapseDynamics, CollapsePattern, CollapseState
from .metrics import collapse_trajectory_metrics, VelocityMetrics, AccelerationMetrics, CurvatureMetrics, HysteresisMetrics
from .analysis import TrajectoryAnalysis, PatternClassifier
from .validation import ConstraintValidator
from .output import CollapseResults, ResultExporter

__all__ = [
    "CollapseDynamics",
    "CollapsePattern",
    "CollapseState",
    "collapse_trajectory_metrics",
    "VelocityMetrics",
    "AccelerationMetrics",
    "CurvatureMetrics",
    "HysteresisMetrics",
    "TrajectoryAnalysis",
    "PatternClassifier",
    "ConstraintValidator",
    "CollapseResults",
    "ResultExporter",
]
