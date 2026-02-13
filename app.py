#!/usr/bin/env python3
"""
Web interface for the Narratives detection and ranking system.
"""

import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request

from narratives import (
    Narrative,
    CapitalFlow,
    RegimeType,
    LifecycleStage,
    NarrativeDetector,
    NarrativeRanker,
)

app = Flask(__name__)

# ── Global state ──────────────────────────────────────────────────────────────
detector = NarrativeDetector()
ranker = NarrativeRanker()
current_regime = RegimeType.EXPANSION
detector.set_current_regime(current_regime)
ranker.set_current_regime(current_regime)


def _build_narratives():
    """Create & analyse example narratives (same data as example.py)."""
    now = datetime.now()

    specs = [
        {
            "id": "ai-revolution-2024",
            "name": "AI Revolution",
            "desc": "Artificial intelligence transforming productivity and business models",
            "created": now - timedelta(hours=12),
            "stage": LifecycleStage.FORMATION,
            "tags": ["tech", "innovation", "growth", "ai", "productivity"],
            "assets": ["NVDA", "MSFT", "META"],
            "sentiment": 0.8,
            "attention": 0.6,
            "flows": [(500_000 + i * 100_000, 200_000, 300_000 + i * 100_000,
                        1_000_000 + i * 200_000, ["institutional", "retail"])
                       for i in range(10)],
            "params": {"capital_velocity": 0.7, "attention_velocity": 0.5,
                       "time_active_hours": 12.0},
        },
        {
            "id": "energy-transition-2024",
            "name": "Energy Transition",
            "desc": "Shift to renewable energy and infrastructure buildout",
            "created": now - timedelta(days=30),
            "stage": LifecycleStage.ACCELERATION,
            "tags": ["energy", "infrastructure", "commodities", "sustainability"],
            "assets": ["ENPH", "FSLR", "NEE"],
            "sentiment": 0.6,
            "attention": 0.7,
            "flows": [(2_000_000 + i * 500_000, 800_000, 1_200_000 + i * 500_000,
                        5_000_000 + i * 1_000_000, ["institutional"])
                       for i in range(10)],
            "params": {"capital_velocity": 0.6, "attention_velocity": 0.4,
                       "time_active_hours": 720.0},
        },
        {
            "id": "mag7-tech-2024",
            "name": "Magnificent 7 Tech Dominance",
            "desc": "Large cap tech stocks dominating market returns",
            "created": now - timedelta(days=365),
            "stage": LifecycleStage.SATURATION,
            "tags": ["tech", "mega-cap", "momentum"],
            "assets": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"],
            "sentiment": 0.3,
            "attention": 0.9,
            "flows": [(50_000_000, 48_000_000, 2_000_000,
                        100_000_000, ["institutional", "retail", "etf"])
                       for _ in range(10)],
            "params": {"capital_velocity": -0.1, "attention_velocity": 0.1,
                       "time_active_hours": 8760.0},
        },
        {
            "id": "crypto-winter-recovery-2024",
            "name": "Crypto Winter Recovery",
            "desc": "Cryptocurrency market recovery after extended bear market",
            "created": now - timedelta(hours=48),
            "stage": LifecycleStage.FORMATION,
            "tags": ["crypto", "digital-assets", "hedge", "innovation"],
            "assets": ["BTC", "ETH", "COIN"],
            "sentiment": 0.4,
            "attention": 0.3,
            "flows": [(800_000 + i * 150_000, 400_000, 400_000 + i * 150_000,
                        2_000_000 + i * 300_000, ["retail", "hedge-funds"])
                       for i in range(10)],
            "params": {"capital_velocity": 0.8, "attention_velocity": 0.3,
                       "time_active_hours": 48.0},
        },
        {
            "id": "defensive-rotation-2024",
            "name": "Defensive Rotation",
            "desc": "Rotation into defensive sectors amid economic uncertainty",
            "created": now - timedelta(days=7),
            "stage": LifecycleStage.ACCELERATION,
            "tags": ["defensive", "quality", "safe-haven", "value"],
            "assets": ["JNJ", "PG", "KO", "WMT"],
            "sentiment": 0.2,
            "attention": 0.5,
            "flows": [(3_000_000 + i * 400_000, 1_500_000,
                        1_500_000 + i * 400_000, 6_000_000 + i * 800_000,
                        ["institutional"])
                       for i in range(10)],
            "params": {"capital_velocity": 0.5, "attention_velocity": 0.4,
                       "time_active_hours": 168.0},
        },
    ]

    narratives = []
    for s in specs:
        n = Narrative(
            id=s["id"], name=s["name"], description=s["desc"],
            created_at=s["created"], updated_at=now,
            lifecycle_stage=s["stage"], regime_alignment={},
            tags=s["tags"], related_assets=s["assets"],
            sentiment_score=s["sentiment"], attention_score=s["attention"],
        )
        for i, (inf, outf, net, vol, src) in enumerate(s["flows"]):
            n.capital_flows.append(CapitalFlow(
                narrative_id=n.id,
                timestamp=now - timedelta(hours=10 - i),
                inflow=inf, outflow=outf, net_flow=net,
                volume=vol, sources=src,
            ))
        detector.add_narrative(n)
        detector.update_narrative(n, **s["params"])
        narratives.append(n)

    return narratives


# Build data once on startup
all_narratives = _build_narratives()
ranked = ranker.rank_narratives(list(all_narratives))

# Pre-compute explanations
explanations = {n.id: ranker.explain_ranking(n) for n in ranked}

# ── Helpers ───────────────────────────────────────────────────────────────────

STAGE_COLORS = {
    "formation": "#10b981",
    "acceleration": "#3b82f6",
    "maturity": "#f59e0b",
    "saturation": "#ef4444",
    "decay": "#6b7280",
}

STAGE_LABELS = {
    "formation": "Formation",
    "acceleration": "Acceleration",
    "maturity": "Maturity",
    "saturation": "Saturation",
    "decay": "Decay",
}


def narrative_to_dict(n: Narrative) -> dict:
    exp = explanations.get(n.id, {})
    flows = [
        {"timestamp": f.timestamp.strftime("%H:%M"),
         "inflow": f.inflow, "outflow": f.outflow,
         "net_flow": f.net_flow, "volume": f.volume}
        for f in n.capital_flows
    ]
    return {
        "id": n.id,
        "name": n.name,
        "description": n.description,
        "rank": n.rank,
        "alpha_score": round(n.alpha_score, 1),
        "lifecycle_stage": n.lifecycle_stage.value,
        "stage_color": STAGE_COLORS.get(n.lifecycle_stage.value, "#6b7280"),
        "stage_label": STAGE_LABELS.get(n.lifecycle_stage.value, n.lifecycle_stage.value),
        "net_flow": n.get_net_capital_flow(),
        "flow_momentum": round(n.get_flow_momentum(), 4),
        "regime_score": round(n.get_regime_score(current_regime), 2),
        "sentiment_score": n.sentiment_score,
        "attention_score": n.attention_score,
        "tags": n.tags,
        "related_assets": n.related_assets,
        "is_early_stage": n.is_early_stage(),
        "created_at": n.created_at.strftime("%Y-%m-%d %H:%M"),
        "flows": flows,
        "explanation": exp,
        "regime_alignment": {k.value: round(v, 2) for k, v in n.regime_alignment.items()},
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    data = [narrative_to_dict(n) for n in ranked]
    early = [d for d in data if d["is_early_stage"]]
    return render_template(
        "index.html",
        narratives=data,
        early_stage=early,
        current_regime=current_regime.value,
        regime_types=[r.value for r in RegimeType],
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.route("/narrative/<narrative_id>")
def narrative_detail(narrative_id):
    n = detector.get_narrative(narrative_id)
    if n is None:
        return "Narrative not found", 404
    data = narrative_to_dict(n)
    return render_template("detail.html", n=data, current_regime=current_regime.value)


@app.route("/api/narratives")
def api_narratives():
    return jsonify([narrative_to_dict(n) for n in ranked])


@app.route("/api/narrative/<narrative_id>")
def api_narrative(narrative_id):
    n = detector.get_narrative(narrative_id)
    if n is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(narrative_to_dict(n))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
