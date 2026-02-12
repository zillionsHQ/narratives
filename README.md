# Narratives: Financial Market Narrative Detection System

A Python system for detecting, analyzing, and ranking financial market narratives to identify alpha opportunities before consensus pricing eliminates informational edge.

## Overview

Financial markets are economic regimes. Most investors enter too late because they react to headlines and price action instead of tracking capital flows and regime shifts. **Alpha exists in the early phase of narrative formation**, before capital coordination saturates and consensus pricing eliminates informational edge.

This system detects and ranks active narratives by measuring:
- **Capital Flows**: Track where money is moving to identify conviction
- **Regime Alignment**: Score narratives against current economic regime
- **Lifecycle Stage**: Classify narratives from formation to saturation

## Key Concepts

### Lifecycle Stages

Narratives evolve through distinct stages:

1. **Formation** (🔥 HIGH ALPHA): Early stage, pre-consensus, low capital flows
2. **Acceleration** (✅ GOOD ALPHA): Growing momentum, capital influx, rising attention
3. **Maturity** (⚠️ MODERATE): Peak attention, maximum capital allocation
4. **Saturation** (❌ LOW ALPHA): Consensus pricing, diminishing returns
5. **Decay** (🚫 EXIT): Narrative breakdown, capital outflow

### Economic Regimes

The system considers six regime types:
- **Expansion**: Growth, rising markets
- **Recession**: Contraction, risk-off
- **Inflation**: Rising prices, monetary tightening
- **Deflation**: Falling prices, deleveraging
- **Volatility**: High uncertainty, regime transitions
- **Stability**: Low volatility, established trends

### Alpha Scoring

The system calculates an alpha score (0-100) based on:
- **Lifecycle Stage (40%)**: Early stage = higher alpha potential
- **Capital Flows (30%)**: Net flows indicate conviction
- **Regime Alignment (20%)**: Fit with current regime
- **Flow Momentum (10%)**: Acceleration shows growing conviction

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from datetime import datetime
from narratives import (
    Narrative,
    CapitalFlow,
    RegimeType,
    LifecycleStage,
    NarrativeDetector,
    NarrativeRanker,
)

# Initialize detector and ranker
detector = NarrativeDetector()
ranker = NarrativeRanker()

# Set current market regime
detector.set_current_regime(RegimeType.EXPANSION)
ranker.set_current_regime(RegimeType.EXPANSION)

# Create a narrative
narrative = Narrative(
    id="ai-revolution",
    name="AI Revolution",
    description="AI transforming productivity",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    lifecycle_stage=LifecycleStage.FORMATION,
    regime_alignment={},
    tags=["tech", "innovation", "growth"],
    related_assets=["NVDA", "MSFT"],
)

# Add capital flow data
flow = CapitalFlow(
    narrative_id=narrative.id,
    timestamp=datetime.now(),
    inflow=1_000_000,
    outflow=300_000,
    net_flow=700_000,
    volume=2_000_000,
    sources=["institutional"],
)
narrative.capital_flows.append(flow)

# Analyze and update
detector.add_narrative(narrative)
detector.update_narrative(narrative)

# Rank narratives
ranked = ranker.rank_narratives([narrative])

# Get top opportunities
opportunities = ranker.get_top_opportunities(
    [narrative],
    top_n=10,
    early_stage_only=True
)
```

## Example Usage

Run the example script to see the system in action:

```bash
python example.py
```

This demonstrates:
- Creating narratives with different lifecycle stages
- Adding capital flow data
- Detecting lifecycle stages
- Calculating regime alignment
- Ranking by alpha potential
- Identifying top opportunities

## Architecture

### Core Components

1. **Models** (`models.py`):
   - `Narrative`: Core narrative data structure
   - `CapitalFlow`: Capital flow tracking
   - `RegimeType`: Economic regime enum
   - `LifecycleStage`: Narrative lifecycle enum

2. **Detector** (`detector.py`):
   - `NarrativeDetector`: Analyzes narratives
   - Classifies lifecycle stages
   - Calculates regime alignment scores

3. **Ranker** (`ranker.py`):
   - `NarrativeRanker`: Ranks narratives by alpha potential
   - Calculates composite alpha scores
   - Identifies top opportunities

## Alpha Strategy

The system implements a systematic approach to finding alpha:

### 1. Track Capital Flows
Monitor where institutional and retail capital is moving. Early flows signal conviction before headlines emerge.

### 2. Identify Lifecycle Stage
Focus on Formation and Acceleration stages where alpha still exists. Avoid Saturation and Decay where consensus pricing has eliminated edge.

### 3. Match Regime Context
Narratives perform differently in different regimes. Energy works in inflation; tech thrives in expansion; defensive shines in recession.

### 4. Monitor Flow Momentum
Accelerating flows indicate growing conviction and increased probability of narrative success.

## Use Cases

- **Portfolio Management**: Identify emerging themes before they become consensus
- **Risk Management**: Detect narrative saturation and decay signals
- **Market Analysis**: Understand capital flows and regime dynamics
- **Research**: Analyze narrative evolution and effectiveness

## Philosophy

> "The best time to invest in a narrative is when capital is starting to flow but headlines haven't formed consensus yet. By the time CNBC is talking about it, alpha is gone."

This system helps identify that inflection point.

## Development

Run tests:
```bash
pytest
```

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please open an issue or PR.

---

**Remember**: Alpha exists in the early phase of narrative formation. Track capital flows, not headlines.