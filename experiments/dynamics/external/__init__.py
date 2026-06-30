"""
External system adapters for Phase 005A Division 5 Tier 1 benchmarks.
"""

from .hopfield_recall import HopfieldRecallSystem
from .kuramoto_grid import KuramotoGridSystem
from .reservoir_echo import ReservoirSystem
from .gene_regulatory import GeneRegulatorySystem

__all__ = [
    "HopfieldRecallSystem",
    "KuramotoGridSystem",
    "ReservoirSystem",
    "GeneRegulatorySystem",
]
