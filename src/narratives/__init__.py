"""
Narratives: Financial narrative detection and ranking system.

This package provides tools for detecting, analyzing, and ranking financial market
narratives based on capital flows, regime alignment, and lifecycle stages.
"""

from .models import Narrative, CapitalFlow, RegimeType
from .detector import NarrativeDetector
from .ranker import NarrativeRanker

__version__ = "0.1.0"

__all__ = [
    "Narrative",
    "CapitalFlow",
    "RegimeType",
    "NarrativeDetector",
    "NarrativeRanker",
]
