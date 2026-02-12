"""
Narrative ranking system for identifying alpha opportunities.
"""

from typing import List, Optional

from .models import Narrative, LifecycleStage, RegimeType


class NarrativeRanker:
    """
    Ranks narratives by alpha potential based on capital flows, regime alignment,
    and lifecycle stage. Identifies opportunities before consensus pricing.
    """
    
    def __init__(self, current_regime: RegimeType = RegimeType.STABILITY):
        self.current_regime = current_regime
        
        # Weights for alpha score calculation
        self.weights = {
            'lifecycle': 0.40,  # Early stage = higher alpha
            'capital_flow': 0.30,  # Positive flows = momentum
            'regime_alignment': 0.20,  # Regime fit = higher probability
            'flow_momentum': 0.10,  # Flow acceleration = conviction
        }
    
    def calculate_alpha_score(self, narrative: Narrative) -> float:
        """
        Calculate alpha score for a narrative.
        
        Alpha exists in the early phase before consensus pricing. Score components:
        - Lifecycle stage (40%): Formation/Acceleration = high alpha
        - Capital flows (30%): Net flows indicate conviction
        - Regime alignment (20%): Fit with current regime
        - Flow momentum (10%): Acceleration indicates growing conviction
        
        Returns:
            Alpha score from 0 to 100 (higher = better opportunity)
        """
        # 1. Lifecycle score (early stage = high alpha)
        lifecycle_scores = {
            LifecycleStage.FORMATION: 1.0,  # Highest alpha potential
            LifecycleStage.ACCELERATION: 0.8,  # Strong alpha potential
            LifecycleStage.MATURITY: 0.4,  # Moderate opportunity
            LifecycleStage.SATURATION: 0.1,  # Low alpha (consensus pricing)
            LifecycleStage.DECAY: 0.0,  # No alpha (exit signal)
        }
        lifecycle_score = lifecycle_scores.get(narrative.lifecycle_stage, 0.5)
        
        # 2. Capital flow score (normalized)
        net_flow = narrative.get_net_capital_flow()
        # Normalize to 0-1 scale (assuming max meaningful flow = 100M)
        flow_score = min(max(net_flow / 100_000_000, 0.0), 1.0)
        
        # 3. Regime alignment score
        regime_score = narrative.get_regime_score(self.current_regime)
        
        # 4. Flow momentum score
        momentum = narrative.get_flow_momentum()
        # Normalize to 0-1 scale
        momentum_score = min(max((momentum + 1) / 2, 0.0), 1.0)
        
        # Calculate weighted alpha score
        alpha_score = (
            lifecycle_score * self.weights['lifecycle'] +
            flow_score * self.weights['capital_flow'] +
            regime_score * self.weights['regime_alignment'] +
            momentum_score * self.weights['flow_momentum']
        )
        
        # Scale to 0-100 for readability
        return alpha_score * 100
    
    def rank_narratives(
        self,
        narratives: List[Narrative],
        filter_early_stage: bool = False,
        min_alpha_score: Optional[float] = None,
    ) -> List[Narrative]:
        """
        Rank narratives by alpha potential.
        
        Args:
            narratives: List of narratives to rank
            filter_early_stage: If True, only include Formation/Acceleration stages
            min_alpha_score: Optional minimum alpha score threshold
            
        Returns:
            Sorted list of narratives (highest alpha first)
        """
        # Calculate alpha scores
        for narrative in narratives:
            narrative.alpha_score = self.calculate_alpha_score(narrative)
        
        # Filter by criteria
        filtered = narratives
        
        if filter_early_stage:
            filtered = [n for n in filtered if n.is_early_stage()]
        
        if min_alpha_score is not None:
            filtered = [n for n in filtered if n.alpha_score >= min_alpha_score]
        
        # Sort by alpha score (descending)
        ranked = sorted(filtered, key=lambda n: n.alpha_score, reverse=True)
        
        # Assign ranks
        for i, narrative in enumerate(ranked, start=1):
            narrative.rank = i
        
        return ranked
    
    def get_top_opportunities(
        self,
        narratives: List[Narrative],
        top_n: int = 10,
        early_stage_only: bool = True,
    ) -> List[Narrative]:
        """
        Get top alpha opportunities.
        
        Args:
            narratives: List of narratives to analyze
            top_n: Number of top opportunities to return
            early_stage_only: Only include early-stage narratives
            
        Returns:
            Top N narratives by alpha score
        """
        ranked = self.rank_narratives(
            narratives,
            filter_early_stage=early_stage_only
        )
        
        return ranked[:top_n]
    
    def set_current_regime(self, regime: RegimeType) -> None:
        """Update the current market regime for alignment scoring."""
        self.current_regime = regime
    
    def explain_ranking(self, narrative: Narrative) -> dict:
        """
        Provide detailed explanation of a narrative's ranking.
        
        Returns:
            Dictionary with score components and reasoning
        """
        lifecycle_scores = {
            LifecycleStage.FORMATION: 1.0,
            LifecycleStage.ACCELERATION: 0.8,
            LifecycleStage.MATURITY: 0.4,
            LifecycleStage.SATURATION: 0.1,
            LifecycleStage.DECAY: 0.0,
        }
        
        net_flow = narrative.get_net_capital_flow()
        flow_score = min(max(net_flow / 100_000_000, 0.0), 1.0)
        regime_score = narrative.get_regime_score(self.current_regime)
        momentum = narrative.get_flow_momentum()
        momentum_score = min(max((momentum + 1) / 2, 0.0), 1.0)
        lifecycle_score = lifecycle_scores.get(narrative.lifecycle_stage, 0.5)
        
        return {
            'alpha_score': narrative.alpha_score,
            'rank': narrative.rank,
            'components': {
                'lifecycle': {
                    'stage': narrative.lifecycle_stage.value,
                    'score': lifecycle_score,
                    'weight': self.weights['lifecycle'],
                    'contribution': lifecycle_score * self.weights['lifecycle'] * 100,
                },
                'capital_flow': {
                    'net_flow': net_flow,
                    'score': flow_score,
                    'weight': self.weights['capital_flow'],
                    'contribution': flow_score * self.weights['capital_flow'] * 100,
                },
                'regime_alignment': {
                    'current_regime': self.current_regime.value,
                    'score': regime_score,
                    'weight': self.weights['regime_alignment'],
                    'contribution': regime_score * self.weights['regime_alignment'] * 100,
                },
                'flow_momentum': {
                    'momentum': momentum,
                    'score': momentum_score,
                    'weight': self.weights['flow_momentum'],
                    'contribution': momentum_score * self.weights['flow_momentum'] * 100,
                },
            },
            'reasoning': self._generate_reasoning(narrative),
        }
    
    def _generate_reasoning(self, narrative: Narrative) -> str:
        """Generate human-readable reasoning for ranking."""
        reasons = []
        
        if narrative.is_early_stage():
            reasons.append(
                f"Early stage ({narrative.lifecycle_stage.value}) indicates "
                "high alpha potential before consensus pricing"
            )
        else:
            reasons.append(
                f"Late stage ({narrative.lifecycle_stage.value}) suggests "
                "limited alpha as consensus pricing may be established"
            )
        
        net_flow = narrative.get_net_capital_flow()
        if net_flow > 0:
            reasons.append(f"Positive capital flows (${net_flow:,.0f}) show conviction")
        else:
            reasons.append(f"Negative capital flows (${net_flow:,.0f}) indicate weakness")
        
        regime_score = narrative.get_regime_score(self.current_regime)
        if regime_score > 0.7:
            reasons.append(
                f"Strong regime alignment ({regime_score:.1%}) with "
                f"current {self.current_regime.value} regime"
            )
        elif regime_score < 0.4:
            reasons.append(
                f"Weak regime alignment ({regime_score:.1%}) with "
                f"current {self.current_regime.value} regime"
            )
        
        return "; ".join(reasons)
