# Narratives — Financial Alpha Discovery

A concept-validation tool that detects, scores, and ranks financial market **narratives** to surface alpha opportunities *before* consensus pricing eliminates the edge.

> **Status:** Proof-of-concept / concept validation — not production software yet. The goal is to prove that a simple narrative-economics model can highlight investable themes earlier than traditional screens.

---

## What Problem Does This Solve?

Most investors react to **headlines and price action** — by the time CNBC is talking about a theme, everybody is already positioned, and the alpha is gone.

This project flips the approach: instead of watching prices, it tracks **capital flows**, **economic regime context**, and **narrative lifecycle stage** to find themes while they are still forming — the phase where informational edge actually exists.

### The Core Idea (Narrative Economics)

Every market theme ("AI boom", "energy transition", "crypto recovery", …) goes through a lifecycle:

| Stage | What Happens | Alpha Potential |
|---|---|---|
| **Formation** | Early movers, pre-consensus, small capital flows | 🔥 High |
| **Acceleration** | Growing momentum, institutional inflows | ✅ Good |
| **Maturity** | Peak attention, crowded positioning | ⚠️ Moderate |
| **Saturation** | Everyone is in — consensus pricing | ❌ Low |
| **Decay** | Capital outflows, narrative breaking down | 🚫 Exit |

The system scores each narrative on a 0-100 **Alpha Score** using four weighted signals:

- **Lifecycle Stage (40%)** — earlier = higher score
- **Capital Flows (30%)** — net inflows signal conviction
- **Regime Alignment (20%)** — does the narrative fit the current economic regime (expansion, recession, inflation, …)?
- **Flow Momentum (10%)** — accelerating flows = growing conviction

---

## See It in Action (Web Dashboard)

The fastest way to understand what this does is to **run the web dashboard**. It ships with built-in example data so you can explore immediately — no API keys or external data needed.

### Prerequisites

You need **Python 3.8+** installed. Check with:

```bash
python3 --version
```

### Step-by-step

```bash
# 1. Clone the repo (skip if you already have it)
git clone https://github.com/zillionsHQ/narratives.git
cd narratives

# 2. (Recommended) Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install the project and its dependencies
pip install -e .
pip install flask               # needed for the web dashboard

# 4. Start the web server
python app.py
```

You should see output like:

```
 * Running on http://0.0.0.0:5000
```

**Open your browser** and go to **http://localhost:5000**. You will see:

- A **dashboard** showing all tracked narratives ranked by alpha score
- A **bar chart** comparing alpha scores side by side
- Cards for each narrative showing lifecycle stage, capital flows, regime fit, sentiment, and related assets
- Click any narrative card to see its **detail page** with full breakdown

> **Tip (Codespaces / dev containers):** If you're running inside GitHub Codespaces or a dev container, the port will be forwarded automatically — look for the popup or check the "Ports" tab.

### CLI Example (No Browser Needed)

If you prefer a terminal-only demo:

```bash
python example.py
```

This prints a full analysis to the console — narrative rankings, alpha scores, lifecycle stages, and regime alignment — using the same built-in data.

---

## What Data Is Used?

Right now the system runs on **built-in example data** defined in `app.py` and `example.py`. No external API calls are made. The example narratives are:

| Narrative | Stage | Related Assets | Description |
|---|---|---|---|
| AI Revolution | Formation | NVDA, MSFT, META | Early-stage AI productivity theme |
| Energy Transition | Acceleration | ENPH, FSLR, NEE | Renewable energy infrastructure buildout |
| Magnificent 7 Tech | Saturation | AAPL, MSFT, GOOGL, … | Mega-cap tech dominance (late, consensus) |
| Crypto Winter Recovery | Formation | BTC, ETH, COIN | Post-bear-market crypto recovery |
| Defensive Rotation | Acceleration | JNJ, PG, KO, WMT | Flight to quality / safe havens |

Each narrative has **simulated capital flow data** (inflows, outflows, volumes) to demonstrate how the scoring engine works. The economic regime is set to **Expansion** by default.

In a future MVP, this data would come from real market feeds (capital flow APIs, sentiment feeds, etc.).

---

## Project Structure

```
narratives/
├── app.py                  ← Web dashboard (Flask). Run this to see the UI.
├── example.py              ← CLI demo. Run this for a terminal-only walkthrough.
├── setup.py                ← Package config & dependencies.
├── README.md               ← You are here.
│
├── src/narratives/         ← Core library (the actual engine)
│   ├── __init__.py         ← Public API — exports all key classes.
│   ├── models.py           ← Data models: Narrative, CapitalFlow, RegimeType, LifecycleStage.
│   ├── detector.py         ← NarrativeDetector — lifecycle classification & regime alignment.
│   └── ranker.py           ← NarrativeRanker — alpha scoring & ranking logic.
│
├── templates/              ← HTML templates for the web dashboard
│   ├── index.html          ← Main dashboard page (all narratives + chart).
│   └── detail.html         ← Single-narrative deep-dive page.
│
├── build/                  ← Build artifacts (auto-generated, can be ignored).
├── LICENSE                 ← MIT License.
└── SECURITY.md             ← Security policy.
```

### Key Files Explained

| File | What It Does |
|---|---|
| `src/narratives/models.py` | Defines the data structures — what a "narrative" is, what a "capital flow" record looks like, the enum of lifecycle stages and economic regimes. Start here to understand the domain model. |
| `src/narratives/detector.py` | The **NarrativeDetector** class. Takes a narrative + its flow data and classifies which lifecycle stage it's in, then calculates how well it aligns with the current economic regime. |
| `src/narratives/ranker.py` | The **NarrativeRanker** class. Takes a list of narratives and produces a ranked list scored by alpha potential (the 0-100 composite score). Also provides human-readable explanations of each ranking. |
| `app.py` | A Flask web app that wires the engine to a browser UI. Builds example narratives on startup, runs the detector and ranker, and serves the results as HTML pages and JSON API endpoints. |
| `example.py` | A standalone script that does the same analysis but prints results to the terminal. Good for understanding the Python API without a browser. |

---

## How the Engine Works (Step by Step)

1. **Define narratives** — each has a name, description, lifecycle stage, tags, related assets, and sentiment/attention scores.
2. **Add capital flow data** — timestamped records of inflows, outflows, net flows, and volume per narrative.
3. **Detect lifecycle stage** — the `NarrativeDetector` uses capital velocity, attention velocity, and time active to classify each narrative into Formation → Acceleration → Maturity → Saturation → Decay.
4. **Calculate regime alignment** — the detector scores how well a narrative fits each possible economic regime (expansion, recession, inflation, etc.).
5. **Rank by alpha** — the `NarrativeRanker` computes a weighted alpha score and sorts narratives from highest opportunity to lowest.
6. **Surface opportunities** — the dashboard (or CLI) shows the ranked results with visual indicators so you can spot early-stage, high-alpha themes at a glance.

### Economic Regimes

The system considers six regime types:

| Regime | Description |
|---|---|
| **Expansion** | Growth, rising markets |
| **Recession** | Contraction, risk-off |
| **Inflation** | Rising prices, monetary tightening |
| **Deflation** | Falling prices, deleveraging |
| **Volatility** | High uncertainty, regime transitions |
| **Stability** | Low volatility, established trends |

Different narratives perform better in different regimes — that context is baked into the scoring.

---

## API Endpoints

The web app also exposes a simple JSON API:

| Endpoint | Returns |
|---|---|
| `GET /api/narratives` | All narratives, ranked, as JSON |
| `GET /api/narrative/<id>` | Single narrative detail as JSON |

Example:

```bash
curl http://localhost:5000/api/narratives | python3 -m json.tool
```

---

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run the web dashboard in debug mode
python app.py        # auto-reloads on code changes
```

---

## Roadmap / Next Steps

This is a concept validation. To move toward an MVP:

- [ ] Connect to real capital flow data sources (e.g., fund flow APIs, on-chain data)
- [ ] Add real-time sentiment feeds (news, social, filings)
- [ ] Implement regime detection from macro indicators
- [ ] Add historical backtesting to validate alpha signals
- [ ] User-defined narratives and watchlists
- [ ] Alerts when a narrative transitions lifecycle stages

---

## Philosophy

> "The best time to invest in a narrative is when capital is starting to flow but headlines haven't formed consensus yet. By the time CNBC is talking about it, alpha is gone."

This system helps identify that inflection point.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please open an issue or pull request.