#!/usr/bin/env python3
"""
Example usage of the narratives detection and ranking system.

This demonstrates how to detect, analyze, and rank financial market narratives
to identify alpha opportunities before consensus pricing.
"""

from datetime import datetime, timedelta
from narratives import (
    Narrative,
    CapitalFlow,
    RegimeType,
    LifecycleStage,
    NarrativeDetector,
    NarrativeRanker,
)


def create_example_narratives():
    """Create example narratives with different characteristics."""
    
    now = datetime.now()
    
    # Narrative 1: AI Revolution (Early Formation - High Alpha)
    ai_narrative = Narrative(
        id="ai-revolution-2024",
        name="AI Revolution",
        description="Artificial intelligence transforming productivity and business models",
        created_at=now - timedelta(hours=12),
        updated_at=now,
        lifecycle_stage=LifecycleStage.FORMATION,
        regime_alignment={},
        tags=["tech", "innovation", "growth", "ai", "productivity"],
        related_assets=["NVDA", "MSFT", "META"],
        sentiment_score=0.8,
        attention_score=0.6,
    )
    
    # Add capital flows showing early momentum
    for i in range(10):
        flow = CapitalFlow(
            narrative_id=ai_narrative.id,
            timestamp=now - timedelta(hours=10-i),
            inflow=500_000 + i * 100_000,
            outflow=200_000,
            net_flow=300_000 + i * 100_000,
            volume=1_000_000 + i * 200_000,
            sources=["institutional", "retail"],
        )
        ai_narrative.capital_flows.append(flow)
    
    # Narrative 2: Energy Transition (Acceleration - Good Alpha)
    energy_narrative = Narrative(
        id="energy-transition-2024",
        name="Energy Transition",
        description="Shift to renewable energy and infrastructure buildout",
        created_at=now - timedelta(days=30),
        updated_at=now,
        lifecycle_stage=LifecycleStage.ACCELERATION,
        regime_alignment={},
        tags=["energy", "infrastructure", "commodities", "sustainability"],
        related_assets=["ENPH", "FSLR", "NEE"],
        sentiment_score=0.6,
        attention_score=0.7,
    )
    
    for i in range(10):
        flow = CapitalFlow(
            narrative_id=energy_narrative.id,
            timestamp=now - timedelta(hours=10-i),
            inflow=2_000_000 + i * 500_000,
            outflow=800_000,
            net_flow=1_200_000 + i * 500_000,
            volume=5_000_000 + i * 1_000_000,
            sources=["institutional"],
        )
        energy_narrative.capital_flows.append(flow)
    
    # Narrative 3: Magnificent 7 Tech (Saturation - Low Alpha)
    mag7_narrative = Narrative(
        id="mag7-tech-2024",
        name="Magnificent 7 Tech Dominance",
        description="Large cap tech stocks dominating market returns",
        created_at=now - timedelta(days=365),
        updated_at=now,
        lifecycle_stage=LifecycleStage.SATURATION,
        regime_alignment={},
        tags=["tech", "mega-cap", "momentum"],
        related_assets=["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"],
        sentiment_score=0.3,
        attention_score=0.9,
    )
    
    for i in range(10):
        flow = CapitalFlow(
            narrative_id=mag7_narrative.id,
            timestamp=now - timedelta(hours=10-i),
            inflow=50_000_000,
            outflow=48_000_000,
            net_flow=2_000_000,
            volume=100_000_000,
            sources=["institutional", "retail", "etf"],
        )
        mag7_narrative.capital_flows.append(flow)
    
    # Narrative 4: Crypto Winter Recovery (Formation - High Alpha)
    crypto_narrative = Narrative(
        id="crypto-winter-recovery-2024",
        name="Crypto Winter Recovery",
        description="Cryptocurrency market recovery after extended bear market",
        created_at=now - timedelta(hours=48),
        updated_at=now,
        lifecycle_stage=LifecycleStage.FORMATION,
        regime_alignment={},
        tags=["crypto", "digital-assets", "hedge", "innovation"],
        related_assets=["BTC", "ETH", "COIN"],
        sentiment_score=0.4,
        attention_score=0.3,
    )
    
    for i in range(10):
        flow = CapitalFlow(
            narrative_id=crypto_narrative.id,
            timestamp=now - timedelta(hours=10-i),
            inflow=800_000 + i * 150_000,
            outflow=400_000,
            net_flow=400_000 + i * 150_000,
            volume=2_000_000 + i * 300_000,
            sources=["retail", "hedge-funds"],
        )
        crypto_narrative.capital_flows.append(flow)
    
    # Narrative 5: Defensive Rotation (Acceleration - Moderate Alpha)
    defensive_narrative = Narrative(
        id="defensive-rotation-2024",
        name="Defensive Rotation",
        description="Rotation into defensive sectors amid economic uncertainty",
        created_at=now - timedelta(days=7),
        updated_at=now,
        lifecycle_stage=LifecycleStage.ACCELERATION,
        regime_alignment={},
        tags=["defensive", "quality", "safe-haven", "value"],
        related_assets=["JNJ", "PG", "KO", "WMT"],
        sentiment_score=0.2,
        attention_score=0.5,
    )
    
    for i in range(10):
        flow = CapitalFlow(
            narrative_id=defensive_narrative.id,
            timestamp=now - timedelta(hours=10-i),
            inflow=3_000_000 + i * 400_000,
            outflow=1_500_000,
            net_flow=1_500_000 + i * 400_000,
            volume=6_000_000 + i * 800_000,
            sources=["institutional"],
        )
        defensive_narrative.capital_flows.append(flow)
    
    return [
        ai_narrative,
        energy_narrative,
        mag7_narrative,
        crypto_narrative,
        defensive_narrative,
    ]


def main():
    """Run the narrative detection and ranking example."""
    
    print("=" * 80)
    print("NARRATIVE DETECTION AND RANKING SYSTEM")
    print("Financial Alpha Discovery Through Regime-Aware Capital Flow Analysis")
    print("=" * 80)
    print()
    
    # Initialize detector and ranker
    detector = NarrativeDetector()
    ranker = NarrativeRanker()
    
    # Set current market regime
    current_regime = RegimeType.EXPANSION
    detector.set_current_regime(current_regime)
    ranker.set_current_regime(current_regime)
    
    print(f"Current Market Regime: {current_regime.value.upper()}")
    print()
    
    # Create and analyze example narratives
    narratives = create_example_narratives()
    
    print(f"Analyzing {len(narratives)} market narratives...")
    print()
    
    # Update each narrative with detector (with narrative-specific parameters)
    update_params = {
        "ai-revolution-2024": {
            "capital_velocity": 0.7,
            "attention_velocity": 0.5,
            "time_active_hours": 12.0,
        },
        "energy-transition-2024": {
            "capital_velocity": 0.6,
            "attention_velocity": 0.4,
            "time_active_hours": 720.0,  # 30 days
        },
        "mag7-tech-2024": {
            "capital_velocity": -0.1,
            "attention_velocity": 0.1,
            "time_active_hours": 8760.0,  # 365 days
        },
        "crypto-winter-recovery-2024": {
            "capital_velocity": 0.8,
            "attention_velocity": 0.3,
            "time_active_hours": 48.0,
        },
        "defensive-rotation-2024": {
            "capital_velocity": 0.5,
            "attention_velocity": 0.4,
            "time_active_hours": 168.0,  # 7 days
        },
    }
    
    for narrative in narratives:
        detector.add_narrative(narrative)
        params = update_params.get(narrative.id, {
            "capital_velocity": 0.5,
            "attention_velocity": 0.3,
            "time_active_hours": 24.0,
        })
        detector.update_narrative(narrative, **params)
    
    # Rank narratives
    ranked_narratives = ranker.rank_narratives(narratives)
    
    print("-" * 80)
    print("ALL NARRATIVES (Ranked by Alpha Score)")
    print("-" * 80)
    print()
    
    for narrative in ranked_narratives:
        print(f"#{narrative.rank} - {narrative.name}")
        print(f"   Alpha Score: {narrative.alpha_score:.1f}/100")
        print(f"   Lifecycle: {narrative.lifecycle_stage.value.upper()}")
        print(f"   Net Capital Flow: ${narrative.get_net_capital_flow():,.0f}")
        print(f"   Regime Alignment: {narrative.get_regime_score(current_regime):.1%}")
        print(f"   Related Assets: {', '.join(narrative.related_assets[:5])}")
        print()
    
    # Get top opportunities (early stage only)
    print("-" * 80)
    print("TOP ALPHA OPPORTUNITIES (Early Stage Only)")
    print("-" * 80)
    print()
    
    opportunities = ranker.get_top_opportunities(
        narratives,
        top_n=5,
        early_stage_only=True
    )
    
    if not opportunities:
        print("No early-stage opportunities found.")
    else:
        for narrative in opportunities:
            print(f"🎯 {narrative.name}")
            print(f"   Alpha Score: {narrative.alpha_score:.1f}/100")
            print(f"   Stage: {narrative.lifecycle_stage.value}")
            
            # Get detailed explanation
            explanation = ranker.explain_ranking(narrative)
            print(f"   Reasoning: {explanation['reasoning']}")
            print()
            print("   Score Breakdown:")
            for component, details in explanation['components'].items():
                print(f"      • {component}: {details['contribution']:.1f} pts "
                      f"(score: {details['score']:.2f}, weight: {details['weight']:.0%})")
            print()
    
    print("-" * 80)
    print("KEY INSIGHTS")
    print("-" * 80)
    print()
    print("✓ Alpha exists in FORMATION and ACCELERATION stages")
    print("✓ SATURATION and DECAY stages indicate consensus pricing")
    print("✓ Early capital flows signal conviction before headlines")
    print("✓ Regime alignment increases probability of narrative success")
    print("✓ Investors who react to headlines enter too late")
    print()
    print("The system prioritizes narratives with:")
    print("  1. Early lifecycle stage (Formation/Acceleration)")
    print("  2. Positive capital flows indicating conviction")
    print("  3. Alignment with current market regime")
    print("  4. Accelerating flow momentum")
    print()


if __name__ == "__main__":
    main()
