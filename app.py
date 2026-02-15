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
    Claim,
    ClaimTier,
    CausalDirection,
    ClaimGraph,
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


# ── Claim hierarchy ───────────────────────────────────────────────────────────
claim_graph = ClaimGraph()


def _build_claim_hierarchy():
    """Build the example hierarchical claim tree described in the issue."""
    now = datetime.now()

    # ── Root 1: Fed tightening ────────────────────────────────────────────
    claim_graph.add_claim(Claim(
        id="fed-tightening",
        text="Fed holding rates higher for longer than market expects",
        asset_classes=["Rates", "FX", "Equities", "Credit", "EM"],
        created_at=now - timedelta(days=90),
        persistence_days=90,
        expected_duration="cyclical",
        trend="stable",
    ))

    # Level 1
    claim_graph.add_claim(Claim(
        id="usd-strengthening",
        text="US dollar is strengthening against major currencies",
        asset_classes=["FX"],
        related_assets=["DXY", "EUR/USD"],
        created_at=now - timedelta(days=60),
        persistence_days=60,
        expected_duration="cyclical",
        trend="rising",
    ))
    claim_graph.add_claim(Claim(
        id="credit-tightening",
        text="Credit conditions are tightening",
        asset_classes=["Credit"],
        related_assets=["HYG", "LQD"],
        created_at=now - timedelta(days=45),
        persistence_days=45,
        expected_duration="cyclical",
        trend="rising",
    ))
    claim_graph.add_claim(Claim(
        id="duration-repricing",
        text="Duration-sensitive assets are repricing",
        asset_classes=["Rates", "Equities"],
        related_assets=["TLT", "IEF"],
        created_at=now - timedelta(days=30),
        persistence_days=30,
        expected_duration="cyclical",
        trend="stable",
    ))
    claim_graph.add_claim(Claim(
        id="rate-differential",
        text="US-EU rate differential widening",
        asset_classes=["Rates", "FX"],
        related_assets=["EUR/USD"],
        created_at=now - timedelta(days=30),
        persistence_days=30,
        expected_duration="cyclical",
        trend="rising",
    ))

    claim_graph.add_edge("fed-tightening", "usd-strengthening")
    claim_graph.add_edge("fed-tightening", "credit-tightening")
    claim_graph.add_edge("fed-tightening", "duration-repricing")
    claim_graph.add_edge("fed-tightening", "rate-differential")

    # Level 2
    claim_graph.add_claim(Claim(
        id="em-debt-stress",
        text="Emerging market dollar-denominated debt is under stress",
        asset_classes=["EM", "Credit"],
        related_assets=["EMB", "EEM"],
        created_at=now - timedelta(days=20),
        persistence_days=20,
        expected_duration="cyclical",
        trend="rising",
    ))
    claim_graph.add_claim(Claim(
        id="housing-contracting",
        text="Housing demand is contracting",
        asset_classes=["Equities"],
        related_assets=["XHB", "ITB"],
        created_at=now - timedelta(days=15),
        persistence_days=15,
        expected_duration="cyclical",
        trend="stable",
    ))
    claim_graph.add_claim(Claim(
        id="growth-underperform",
        text="Growth equities are underperforming value",
        asset_classes=["Equities"],
        related_assets=["IWF", "IWD", "ARKK", "SPY"],
        created_at=now - timedelta(days=25),
        persistence_days=25,
        expected_duration="cyclical",
        trend="stable",
    ))
    claim_graph.add_claim(Claim(
        id="credit-spreads-widening",
        text="Credit spreads widening in leveraged loans",
        asset_classes=["Credit"],
        related_assets=["BKLN", "HYG"],
        created_at=now - timedelta(days=10),
        persistence_days=10,
        expected_duration="cyclical",
        trend="rising",
    ))
    claim_graph.add_claim(Claim(
        id="eur-usd-declining",
        text="EUR/USD declining toward parity",
        asset_classes=["FX"],
        related_assets=["EUR/USD"],
        created_at=now - timedelta(days=14),
        persistence_days=14,
        expected_duration="cyclical",
        trend="rising",
    ))

    claim_graph.add_edge("usd-strengthening", "em-debt-stress")
    claim_graph.add_edge("credit-tightening", "housing-contracting")
    claim_graph.add_edge("duration-repricing", "growth-underperform")
    claim_graph.add_edge("credit-tightening", "credit-spreads-widening")
    claim_graph.add_edge("rate-differential", "eur-usd-declining")

    # Level 3
    claim_graph.add_claim(Claim(
        id="em-currency-crisis",
        text="EM currency crises risk rising",
        asset_classes=["FX", "EM"],
        related_assets=["BRL", "ZAR", "TRY"],
        created_at=now - timedelta(days=7),
        persistence_days=7,
        expected_duration="transient",
        trend="rising",
    ))
    claim_graph.add_claim(Claim(
        id="homebuilders-falling",
        text="Homebuilder stocks falling",
        asset_classes=["Equities"],
        related_assets=["DHI", "LEN", "TOL"],
        created_at=now - timedelta(days=5),
        persistence_days=5,
        expected_duration="cyclical",
        trend="stable",
    ))
    claim_graph.add_claim(Claim(
        id="pe-exit-declining",
        text="Private equity exit activity declining",
        asset_classes=["Credit", "Equities"],
        related_assets=["BX", "KKR", "APO"],
        created_at=now - timedelta(days=10),
        persistence_days=10,
        expected_duration="cyclical",
        trend="fading",
    ))
    claim_graph.add_claim(Claim(
        id="regional-bank-stress",
        text="Regional bank CRE exposure under stress",
        asset_classes=["Equities", "Credit"],
        related_assets=["KRE", "NYCB"],
        created_at=now - timedelta(days=12),
        persistence_days=12,
        expected_duration="cyclical",
        trend="rising",
    ))

    claim_graph.add_edge("em-debt-stress", "em-currency-crisis")
    claim_graph.add_edge("housing-contracting", "homebuilders-falling")
    claim_graph.add_edge("credit-spreads-widening", "pe-exit-declining")
    claim_graph.add_edge("credit-spreads-widening", "regional-bank-stress")

    # ── Root 2: AI infrastructure buildout ────────────────────────────────
    claim_graph.add_claim(Claim(
        id="ai-buildout",
        text="AI infrastructure buildout exceeding all forecasts",
        asset_classes=["Equities", "Commodities", "Energy"],
        created_at=now - timedelta(days=120),
        persistence_days=120,
        expected_duration="structural",
        trend="rising",
    ))

    # Level 1
    claim_graph.add_claim(Claim(
        id="power-demand",
        text="Power demand growth inflecting upward",
        asset_classes=["Energy", "Commodities"],
        related_assets=["NEE", "SO", "DUK"],
        created_at=now - timedelta(days=60),
        persistence_days=60,
        expected_duration="structural",
        trend="rising",
    ))
    claim_graph.add_claim(Claim(
        id="semi-bottleneck",
        text="Semiconductor supply chain bottleneck forming",
        asset_classes=["Equities"],
        related_assets=["NVDA", "AMD", "TSM"],
        created_at=now - timedelta(days=45),
        persistence_days=45,
        expected_duration="cyclical",
        trend="stable",
    ))

    claim_graph.add_edge("ai-buildout", "power-demand")
    claim_graph.add_edge("ai-buildout", "semi-bottleneck")

    # Level 2
    claim_graph.add_claim(Claim(
        id="natgas-demand",
        text="Natural gas demand exceeding supply models",
        asset_classes=["Commodities", "Energy"],
        related_assets=["UNG", "FCG"],
        created_at=now - timedelta(days=20),
        persistence_days=20,
        expected_duration="cyclical",
        trend="rising",
    ))
    claim_graph.add_claim(Claim(
        id="nuclear-rehab",
        text="Nuclear energy political rehabilitation",
        asset_classes=["Energy"],
        related_assets=["CCJ", "URA"],
        created_at=now - timedelta(days=30),
        persistence_days=30,
        expected_duration="structural",
        trend="rising",
    ))
    claim_graph.add_claim(Claim(
        id="tsmc-pricing",
        text="TSMC pricing power increasing",
        asset_classes=["Equities"],
        related_assets=["TSM"],
        created_at=now - timedelta(days=14),
        persistence_days=14,
        expected_duration="cyclical",
        trend="stable",
    ))
    claim_graph.add_claim(Claim(
        id="packaging-scarce",
        text="Advanced packaging becoming scarce",
        asset_classes=["Equities"],
        related_assets=["ASX", "AMKR"],
        created_at=now - timedelta(days=10),
        persistence_days=10,
        expected_duration="cyclical",
        trend="rising",
    ))

    claim_graph.add_edge("power-demand", "natgas-demand")
    claim_graph.add_edge("power-demand", "nuclear-rehab")
    claim_graph.add_edge("semi-bottleneck", "tsmc-pricing")
    claim_graph.add_edge("semi-bottleneck", "packaging-scarce")

    # ── Root 3: China stimulus ────────────────────────────────────────────
    claim_graph.add_claim(Claim(
        id="china-stimulus",
        text="China stimulus insufficient to offset property deflation",
        asset_classes=["EM", "Commodities", "FX"],
        created_at=now - timedelta(days=180),
        persistence_days=180,
        expected_duration="structural",
        trend="stable",
    ))

    claim_graph.add_claim(Claim(
        id="china-commodity-demand",
        text="Chinese commodity demand structurally lower",
        asset_classes=["Commodities"],
        related_assets=["BHP", "RIO", "VALE"],
        created_at=now - timedelta(days=90),
        persistence_days=90,
        expected_duration="structural",
        trend="stable",
    ))
    claim_graph.add_claim(Claim(
        id="cny-weakening",
        text="Yuan weakening pressuring Asian FX",
        asset_classes=["FX", "EM"],
        related_assets=["CNY", "KRW", "TWD"],
        created_at=now - timedelta(days=60),
        persistence_days=60,
        expected_duration="cyclical",
        trend="stable",
    ))
    claim_graph.add_claim(Claim(
        id="em-equities-outflows",
        text="EM equity outflows accelerating",
        asset_classes=["EM", "Equities"],
        related_assets=["EEM", "VWO", "FXI"],
        created_at=now - timedelta(days=30),
        persistence_days=30,
        expected_duration="cyclical",
        trend="rising",
    ))

    claim_graph.add_edge("china-stimulus", "china-commodity-demand")
    claim_graph.add_edge("china-stimulus", "cny-weakening")
    claim_graph.add_edge("china-stimulus", "em-equities-outflows")

    # Compute influence scores
    claim_graph.compute_influence()


_build_claim_hierarchy()


# ── Claim routes ─────────────────────────────────────────────────────────────

TIER_COLORS = {
    "tier_1": "#ef4444",
    "tier_2": "#f59e0b",
    "tier_3": "#6b7280",
}

TIER_LABELS = {
    "tier_1": "Tier 1 — Root Macro Driver",
    "tier_2": "Tier 2 — Consequence",
    "tier_3": "Tier 3 — Observable Effect",
}

TREND_ICONS = {
    "rising": "↑",
    "stable": "→",
    "fading": "↓",
}


@app.route("/claims")
def claims_index():
    roots = claim_graph.get_roots()
    roots.sort(key=lambda c: c.influence_score, reverse=True)
    trees = []
    for root in roots:
        tree = claim_graph.tree_to_dict(root.id)
        if tree is not None:
            trees.append(tree)
    interactions = claim_graph.find_cross_tree_interactions()
    ix_dicts = [claim_graph.interaction_to_dict(ix) for ix in interactions]
    return render_template(
        "claims.html",
        trees=trees,
        interactions=ix_dicts,
        tier_colors=TIER_COLORS,
        tier_labels=TIER_LABELS,
        trend_icons=TREND_ICONS,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.route("/claim/<claim_id>")
def claim_detail(claim_id):
    claim = claim_graph.get_claim(claim_id)
    if claim is None:
        return "Claim not found", 404
    data = claim_graph.claim_to_dict(claim)
    parents = [claim_graph.claim_to_dict(p) for p in claim_graph.get_parents(claim_id)]
    children = [claim_graph.claim_to_dict(c) for c in claim_graph.get_children(claim_id)]
    subtree = claim_graph.tree_to_dict(claim_id)
    return render_template(
        "claim_detail.html",
        claim=data,
        parents=parents,
        children=children,
        subtree=subtree,
        tier_colors=TIER_COLORS,
        tier_labels=TIER_LABELS,
        trend_icons=TREND_ICONS,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.route("/api/claims")
def api_claims():
    roots = claim_graph.get_roots()
    roots.sort(key=lambda c: c.influence_score, reverse=True)
    trees = [claim_graph.tree_to_dict(r.id) for r in roots]
    return jsonify([t for t in trees if t is not None])


@app.route("/api/claim/<claim_id>")
def api_claim(claim_id):
    claim = claim_graph.get_claim(claim_id)
    if claim is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(claim_graph.claim_to_dict(claim))


@app.route("/api/claims/interactions")
def api_claim_interactions():
    interactions = claim_graph.find_cross_tree_interactions()
    return jsonify([claim_graph.interaction_to_dict(ix) for ix in interactions])


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
