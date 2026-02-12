"""
Narrative detection engine for identifying and analyzing market narratives.
"""

from datetime import datetime
from typing import Dict, List, Optional

from .models import Narrative, CapitalFlow, LifecycleStage, RegimeType


class NarrativeDetector:
    """
    Detects and analyzes financial market narratives by tracking capital flows,
    regime alignment, and lifecycle stages.
    """
    
    def __init__(self):
        self.narratives: Dict[str, Narrative] = {}
        self.current_regime: RegimeType = RegimeType.STABILITY
    
    def detect_lifecycle_stage(
        self,
        narrative: Narrative,
        capital_velocity: float,
        attention_velocity: float,
        time_active_hours: float,
    ) -> LifecycleStage:
        """
        Classify narrative lifecycle stage based on capital and attention dynamics.
        
        Args:
            narrative: The narrative to classify
            capital_velocity: Rate of capital flow change
            attention_velocity: Rate of attention change
            time_active_hours: Time since narrative formation
            
        Returns:
            LifecycleStage classification
        """
        net_flow = narrative.get_net_capital_flow()
        
        # Formation: Early stage, low capital, low attention, positive velocity
        if time_active_hours < 24 and net_flow < 1_000_000 and capital_velocity > 0:
            return LifecycleStage.FORMATION
        
        # Acceleration: Growing momentum, increasing flows and attention
        if capital_velocity > 0.5 and attention_velocity > 0.3 and net_flow > 0:
            return LifecycleStage.ACCELERATION
        
        # Maturity: Peak levels, slowing velocity
        if net_flow > 10_000_000 and abs(capital_velocity) < 0.2:
            return LifecycleStage.MATURITY
        
        # Saturation: High capital, declining velocity
        if net_flow > 10_000_000 and capital_velocity < 0:
            return LifecycleStage.SATURATION
        
        # Decay: Negative flows, declining attention
        if net_flow < 0 and capital_velocity < -0.3:
            return LifecycleStage.DECAY
        
        # Default to acceleration if unclear
        return LifecycleStage.ACCELERATION
    
    def calculate_regime_alignment(
        self,
        narrative: Narrative,
        historical_performance: Optional[Dict[RegimeType, float]] = None,
    ) -> Dict[RegimeType, float]:
        """
        Calculate how well a narrative aligns with different economic regimes.
        
        Args:
            narrative: The narrative to analyze
            historical_performance: Optional historical performance by regime
            
        Returns:
            Dictionary mapping regime types to alignment scores (0-1)
        """
        if historical_performance:
            return historical_performance
        
        # Default heuristic-based alignment scores
        # In production, this would use historical correlation analysis
        alignment = {}
        
        # Use tags to infer regime alignment
        tags_lower = [tag.lower() for tag in narrative.tags]
        
        # Expansion regime favors growth narratives
        if any(tag in tags_lower for tag in ['growth', 'tech', 'innovation', 'expansion']):
            alignment[RegimeType.EXPANSION] = 0.8
        else:
            alignment[RegimeType.EXPANSION] = 0.4
        
        # Recession regime favors defensive narratives
        if any(tag in tags_lower for tag in ['defensive', 'value', 'quality', 'safe-haven']):
            alignment[RegimeType.RECESSION] = 0.8
        else:
            alignment[RegimeType.RECESSION] = 0.3
        
        # Inflation regime favors real assets
        if any(tag in tags_lower for tag in ['commodities', 'real-estate', 'pricing-power']):
            alignment[RegimeType.INFLATION] = 0.8
        else:
            alignment[RegimeType.INFLATION] = 0.4
        
        # Deflation regime favors bonds/cash
        if any(tag in tags_lower for tag in ['bonds', 'cash', 'treasuries', 'quality']):
            alignment[RegimeType.DEFLATION] = 0.7
        else:
            alignment[RegimeType.DEFLATION] = 0.3
        
        # Volatility regime favors hedges
        if any(tag in tags_lower for tag in ['hedge', 'options', 'volatility', 'protection']):
            alignment[RegimeType.VOLATILITY] = 0.9
        else:
            alignment[RegimeType.VOLATILITY] = 0.3
        
        # Stability regime favors momentum
        if any(tag in tags_lower for tag in ['momentum', 'trend', 'growth']):
            alignment[RegimeType.STABILITY] = 0.7
        else:
            alignment[RegimeType.STABILITY] = 0.5
        
        return alignment
    
    def add_capital_flow(self, narrative_id: str, flow: CapitalFlow) -> None:
        """Add a capital flow observation to a narrative."""
        if narrative_id in self.narratives:
            self.narratives[narrative_id].capital_flows.append(flow)
            self.narratives[narrative_id].updated_at = datetime.now()
    
    def update_narrative(
        self,
        narrative: Narrative,
        capital_velocity: float = 0.0,
        attention_velocity: float = 0.0,
        time_active_hours: float = 24.0,
    ) -> Narrative:
        """
        Update narrative with latest lifecycle stage and regime alignment.
        
        Args:
            narrative: Narrative to update
            capital_velocity: Rate of capital flow change
            attention_velocity: Rate of attention change  
            time_active_hours: Time since narrative formation
            
        Returns:
            Updated narrative
        """
        # Update lifecycle stage
        narrative.lifecycle_stage = self.detect_lifecycle_stage(
            narrative, capital_velocity, attention_velocity, time_active_hours
        )
        
        # Update regime alignment
        narrative.regime_alignment = self.calculate_regime_alignment(narrative)
        
        narrative.updated_at = datetime.now()
        
        return narrative
    
    def set_current_regime(self, regime: RegimeType) -> None:
        """Set the current market regime."""
        self.current_regime = regime
    
    def get_narrative(self, narrative_id: str) -> Optional[Narrative]:
        """Retrieve a narrative by ID."""
        return self.narratives.get(narrative_id)
    
    def add_narrative(self, narrative: Narrative) -> None:
        """Add or update a narrative in the detection system."""
        self.narratives[narrative.id] = narrative
    
    def get_all_narratives(self) -> List[Narrative]:
        """Get all tracked narratives."""
        return list(self.narratives.values())
