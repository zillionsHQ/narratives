"""
Core data models for narrative detection system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class RegimeType(Enum):
    """Economic regime types that influence narrative effectiveness."""
    
    EXPANSION = "expansion"  # Economic growth, rising markets
    RECESSION = "recession"  # Economic contraction, risk-off
    INFLATION = "inflation"  # Rising prices, monetary tightening
    DEFLATION = "deflation"  # Falling prices, deleveraging
    VOLATILITY = "volatility"  # High uncertainty, regime transition
    STABILITY = "stability"  # Low volatility, established trends


class LifecycleStage(Enum):
    """Narrative lifecycle stages from formation to saturation."""
    
    FORMATION = "formation"  # Early stage, pre-consensus (HIGH ALPHA)
    ACCELERATION = "acceleration"  # Growing momentum, capital influx
    MATURITY = "maturity"  # Peak attention, maximum capital
    SATURATION = "saturation"  # Consensus pricing, diminishing returns
    DECAY = "decay"  # Narrative breakdown, capital outflow


@dataclass
class CapitalFlow:
    """Tracks capital movement related to a narrative."""
    
    narrative_id: str
    timestamp: datetime
    inflow: float  # Positive values indicate capital entering
    outflow: float  # Positive values indicate capital exiting
    net_flow: float  # Net capital movement (inflow - outflow)
    volume: float  # Total trading volume
    sources: List[str] = field(default_factory=list)  # Capital sources (retail, institutional, etc.)
    
    @property
    def flow_momentum(self) -> float:
        """Calculate flow momentum indicator."""
        if self.volume == 0:
            return 0.0
        return self.net_flow / self.volume


@dataclass
class Narrative:
    """Represents a financial market narrative."""
    
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    
    # Core metrics
    lifecycle_stage: LifecycleStage
    regime_alignment: Dict[RegimeType, float]  # Alignment scores by regime
    capital_flows: List[CapitalFlow] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    related_assets: List[str] = field(default_factory=list)
    sentiment_score: float = 0.0  # -1 to 1 scale
    attention_score: float = 0.0  # 0 to 1 scale
    
    # Derived metrics (calculated)
    alpha_score: float = 0.0  # Opportunity score (higher = better)
    rank: int = 0  # Relative ranking among narratives
    
    def get_net_capital_flow(self, lookback_hours: int = 24) -> float:
        """Calculate net capital flow over specified time period."""
        if not self.capital_flows:
            return 0.0
        
        # In production, would filter by time window
        # For now, use the most recent flows up to lookback_hours count
        recent_flows = self.capital_flows[-lookback_hours:]
        return sum(flow.net_flow for flow in recent_flows)
    
    def get_flow_momentum(self) -> float:
        """Get the most recent flow momentum."""
        if not self.capital_flows:
            return 0.0
        return self.capital_flows[-1].flow_momentum
    
    def is_early_stage(self) -> bool:
        """Check if narrative is in early stage (alpha opportunity)."""
        return self.lifecycle_stage in [LifecycleStage.FORMATION, LifecycleStage.ACCELERATION]
    
    def get_regime_score(self, current_regime: RegimeType) -> float:
        """Get alignment score for current market regime."""
        return self.regime_alignment.get(current_regime, 0.0)
