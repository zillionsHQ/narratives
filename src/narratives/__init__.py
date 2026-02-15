"""
Narratives: Financial narrative detection and ranking system.

This package provides tools for detecting, analyzing, and ranking financial market
narratives based on capital flows, regime alignment, and lifecycle stages.  It also
provides a hierarchical claim architecture — a DAG of economic propositions ranked
by influence magnitude.
"""

from .models import Narrative, CapitalFlow, RegimeType, LifecycleStage
from .detector import NarrativeDetector
from .ranker import NarrativeRanker
from .claims import Claim, ClaimTier, CausalDirection, ClaimGraph, CrossTreeInteraction

__version__ = "0.1.0"

__all__ = [
    "Narrative",
    "CapitalFlow",
    "RegimeType",
    "LifecycleStage",
    "NarrativeDetector",
    "NarrativeRanker",
    "Claim",
    "ClaimTier",
    "CausalDirection",
    "ClaimGraph",
    "CrossTreeInteraction",
]
