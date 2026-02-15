# Product Specification & High‑Level Architecture for a Narrative‑Driven Crypto Analytics Platform

## 1. Overview

This document specifies the first phase of a **narrative‑driven crypto analytics platform** inspired by leading products like Santiment and CryptoQuant.  The platform ingests diverse market, on‑chain, social and development data, normalises and stores it, computes metrics and narrative scores through an interpreter layer, and presents the results through interactive dashboards and an education hub.  Scientific rigour and transparency are emphasised throughout: all metrics and narrative scores should be accompanied by definitions, formulas, assumptions, failure modes and references.  The system is designed to be modular and extensible, allowing additional data sources, metrics and analytics to be integrated over time.

Economic narratives—stories that spread virally through populations and influence economic outcomes—are the central organising principle【939038864967448†L20-L59】.  Narratives have lifecycles (emergence, acceleration, consensus, decline)【939038864967448†L44-L46】, and financial markets exhibit reflexive feedback loops where beliefs influence prices and prices reinforce beliefs【939038864967448†L67-L97】.  The platform’s purpose is to detect, measure and explain these narrative dynamics in crypto markets and to provide investors and researchers with actionable insights.


## 2. User Personas & Value Proposition

1. **Professional and Retail Investors** – need timely data and tools to spot emerging themes, manage risk and improve trading decisions.  They value comprehensive on‑chain metrics, narrative scores and alerts.  
2. **Analysts and Researchers** – require high‑quality data, transparent methodology and reproducible analytics for reporting or academic work.  They benefit from a structured metric library and an education hub with scientific references.  
3. **Crypto Project Teams** – monitor sentiment and adoption around their own projects and competitors.  Developer activity metrics and narrative clustering help them understand market perception.  
4. **Institutional Integrators** – use the API to build bespoke dashboards or incorporate signals into trading models.  They need robust documentation, authentication and rate‑limiting.

The platform differentiates itself through:

- Early detection of narrative changes using a hybrid of social, on‑chain and market signals.  
- Transparent metrics and narrative scoring methodology grounded in narrative economics【939038864967448†L20-L59】, reflexivity【939038864967448†L67-L97】, adaptive markets【939038864967448†L101-L132】 and information cascades【939038864967448†L134-L164】.  
- An education section that clearly explains every concept, including assumptions, limitations and citations.


## 3. Functional Requirements

### 3.1 Data Ingestion & Connectors

- **Pluggable connectors** to ingest raw data from multiple sources.  Each connector must implement `fetch()`, `parse()`, `validate()` and `upsert()` methods and include provenance metadata (source, timestamp, confidence).  
- **Initial connectors** (choose at least two to implement in Phase 1; design for more):
  1. **Market data** – price and volume from exchanges (e.g., Binance or Coinbase).  
  2. **On‑chain basics** – network activity, fees and flows for one blockchain (Bitcoin or Ethereum).  
  3. **Social/news** – Reddit posts, RSS feeds and, if keys are available, X/Twitter.  
  4. **Developer activity** – GitHub events (commits, issues, stars) for selected repositories.  
  5. **Macro proxies** – indexes like DXY or interest‑rate proxies (optional).  

- **Scraping rules**: respect robots.txt, throttle requests, store raw HTML snapshots, use a proper user‑agent, implement retry with exponential backoff and detect blocks.

### 3.2 Normalisation & Storage

- A unified schema for events, metrics and narratives.  Data is stored in PostgreSQL/TimescaleDB for time‑series efficiency.  Raw documents are stored in object storage (e.g., S3 or MinIO) with references in the database.  
- **Entity resolution** maps symbols, chains, exchanges and topics to canonical IDs; deduplication uses hashing; confidence scores reflect parser validation and source reliability.  
- **Migration scripts** to create and evolve the database schema.  

### 3.3 Metric Library

- A registry of metrics with fields: `key`, `name`, `description`, `unit`, `cadence`, `formula`, `assumptions`, `failure_modes` and `references`.  
- At least 25 metrics covering categories such as price/market (returns, realised volatility, drawdown), exchange flows (netflows, balance changes), derivatives (open interest, funding rates), network activity (active addresses, transactions, fees), social/news (mention volume, sentiment proxy) and development activity (commit count, active contributors).  
- Each metric must have a reproducible formula, link to underlying data, assumptions and interpretation guidelines.

### 3.4 Interpreter Engine

- **Event processing pipeline**: normalisation → entity resolution → metric computation.  
- **Narrative detection**: collect textual signals (headlines, posts, updates), clean and deduplicate them, embed them (using local or API embeddings), cluster them (e.g., HDBSCAN with justification), label clusters (LLM‑assisted with citation guardrails) and assign life‑cycle phases.  
- **Scoring**: compute a convergence score (0–100) for each narrative and asset–narrative pair using weighted components such as attention velocity (growth rate of social/news mentions), capital/flow proxies (exchange and derivatives anomalies), market confirmation (trend/volatility regime), fundamental catalysts (tagged events) and cross‑source agreement.  The score must be reproducible, logged, debuggable and backtestable.  
- **Explainability**: for each metric or score, provide a “Why?” panel summarising the inputs, their relative contributions and the evidence; highlight potential invalidating signals.

### 3.5 Visualiser & Front‑End

- A responsive web application built with Next.js (TypeScript, App Router) and TailwindCSS with shadcn/ui components.  Use ECharts or Recharts for charts (choose one and justify).  
- **Core pages**: Home (market pulse, top narratives, anomalies), Narrative Leaderboard, Narrative Detail, Asset List and Detail (tabs for on‑chain, flows, derivatives, social, dev), Metric Library, Alerts, Watchlists, Education Hub, Admin Console.  
- UI patterns: top navigation with search; global filters (timeframe, asset, chain, exchange); charts with tooltips, zoom, overlays, CSV export; sortable/paginated tables; evidence feeds with source links and timestamps; empty states and skeleton loaders; optional dark mode.  
- **Alert system**: allow users to configure threshold, rate‑of‑change, anomaly and narrative‑score alerts; deliver notifications via in‑app messages or email (out of scope for Phase 1).  
- **Watchlists**: users can monitor custom sets of assets and narratives.

### 3.6 Education Hub

- An educational centre offering: 
  - **Glossary** – concise definitions of terms.  
  - **Deep‑dive articles** – longer explanations with references to academic literature and industry reports.  
  - **Method cards** – for each metric and algorithm, provide definition, formula, assumptions, limitations, common misinterpretations and references.  
  - **“How we score narratives” explainer** – document the objective, methodology, component definitions, calibration/backtesting approach and caveats.  

### 3.7 Admin & Operations

- Protected admin console with RBAC (roles: user, admin).  
- Views for connector status, scraping health, ingestion backlog, manual re‑run triggers, user management.  
- Audit logging for admin actions.  
- Observability: structured logs, metrics endpoint (Prometheus), error tracking (Sentry or similar).  

### 3.8 API & Documentation

- RESTful API built with FastAPI (Python) or NestJS (Node).  FastAPI is recommended for rich typing and data‑science integration; choose Node only if the team has strong TypeScript expertise.  
- Endpoints for metrics, narrative scores, assets, events, search and user management.  
- OpenAPI/Swagger specification auto‑generated.  
- Rate limiting and input validation.  

### 3.9 Non‑Functional Requirements

- **Performance** – dashboards should load within ~1 s for cached queries; ingestion pipeline should process new data within minutes.  
- **Scalability** – architecture should support additional data sources, chains and users; separate microservices where necessary (API server, ingestion workers).  
- **Reliability** – handle partial failures gracefully; implement retries; provide health checks; maintain data quality checks for missing or anomalous data.  
- **Security** – implement authentication (email magic link or OAuth), RBAC, rate limiting, CSRF protection, encryption at rest and in transit, secret management via environment variables.  
- **Compliance & Disclaimers** – clearly state that the platform does not provide financial advice; abide by data‑source terms; respect privacy laws.


## 4. Data Model (Schema Overview)

The core schema will be implemented in PostgreSQL/TimescaleDB.  Keys and types are illustrative; migrations should enforce indexing on time-series columns.

| Table | Key fields | Notes |
|---|---|---|
| **assets** | `id` (PK), `symbol`, `name`, `chain`, `decimals`, `tags` | List of tradable assets or tokens. |
| **sources** | `id` (PK), `name`, `type`, `base_url`, `auth_type` | Registered data connectors. |
| **ingestions** | `id` (PK), `source_id` (FK), `status`, `started_at`, `ended_at`, `error`, `stats` | Track ingestion jobs. |
| **raw_documents** | `id` (PK), `source_id` (FK), `fetched_at`, `content_type`, `storage_uri`, `hash` | Raw HTML or JSON snapshots stored in object storage. |
| **events** | `id` (PK), `type`, `asset_id` (FK, nullable), `narrative_id` (FK, nullable), `ts`, `payload_json`, `source_id` (FK), `confidence` | Normalised units of information (e.g., a trade, a social post). |
| **metrics** | `id` (PK), `key`, `name`, `description`, `unit`, `cadence`, `formula_md`, `assumptions_md`, `references_json` | Registry of metrics. |
| **metric_points** | `metric_id` (FK), `asset_id` (FK), `ts`, `value`, `dimensions_json`, `provenance_json` | Time‑series values.  Index on (`metric_id`, `asset_id`, `ts`). |
| **narratives** | `id` (PK), `title`, `summary`, `created_at`, `updated_at`, `status` | Persistent narrative clusters. |
| **narrative_evidence** | `narrative_id` (FK), `event_id` (FK), `weight`, `rationale` | Links events to narratives. |
| **narrative_scores** | `narrative_id` (FK), `ts`, `score_total`, `components_json` | Historical narrative scores. |
| **users** | `id` (PK), `email`, `role`, `created_at`, `last_login` | User accounts. |
| **alerts** | `id` (PK), `user_id` (FK), `type`, `config_json`, `created_at`, `enabled` | User‑configured alerts. |
| **alert_firings** | `id` (PK), `alert_id` (FK), `ts`, `context_json` | Records of alert triggers. |
| **watchlists** | `id` (PK), `user_id` (FK), `name` | Named watchlists. |
| **watchlist_items** | `watchlist_id` (FK), `asset_id` (FK), `narrative_id` (FK, nullable) | Items in watchlists. |

All writes must include provenance metadata (source, timestamp, confidence).  Additional tables can be introduced as new data sources or features (e.g., user annotations, backtesting runs).


## 5. System Architecture

The platform follows a **modular microservice architecture** with clearly defined boundaries between ingestion, processing and presentation layers.

1. **Data Ingestion Layer**  
   - Implemented as a set of worker services (e.g., Celery workers in Python) connected via a job queue (Redis + RQ).  
   - Each worker runs connectors on a schedule, fetches raw data, parses and validates it, stores raw documents in object storage and writes normalised events into the database.  
   - Job metadata is recorded in the `ingestions` table.  Circuit breakers and exponential backoff prevent misbehaving sources from affecting system stability.

2. **Processing & Interpreter Layer**  
   - Runs either as part of the API service or as a separate worker service depending on load.  
   - Consumes events and metric points from the database to compute metrics and narrative scores.  
   - Uses a local embedding model (e.g., Sentence Transformers) or an external API to embed textual data; clusters embeddings with HDBSCAN; labels clusters using a large language model with careful prompts and evidence citations; calculates score components and final scores.  
   - Stores computed metric points and narrative scores back into the database.

3. **API & Backend Service**  
   - Built with FastAPI (Python).  Exposes REST endpoints for assets, metrics, events, narratives, scores, alerts, watchlists and authentication.  
   - Performs request validation (Pydantic models) and enforces rate limiting and RBAC.  
   - Supports WebSocket subscriptions for live updates (optional for future phases).  

4. **Front‑End Application**  
   - Next.js (App Router) with TypeScript and TailwindCSS.  Uses shadcn/ui for consistent components and ECharts for interactive charts (ECharts is preferred for rich time‑series and candlestick support; Recharts is simpler but less powerful).  
   - Communicates with the API via fetch hooks; implements global state management (e.g., React Context or Redux) for filters and user sessions.  
   - Implements SSR/ISR for marketing pages (landing, education hub) and client‑side rendering for the interactive dashboards.  

5. **Storage & Infrastructure**  
   - PostgreSQL/TimescaleDB for relational and time‑series data.  
   - Redis for caching, rate limiting and job queueing.  
   - Object storage (S3 or MinIO) for raw HTML/documents and file exports.  
   - Containers orchestrated via Docker Compose locally; production deployments could use Kubernetes or a platform‑as‑a‑service.  
   - Observability with structured logging (e.g., Python’s `structlog`), metrics endpoint (Prometheus), and error tracking (Sentry).  

6. **Security & Compliance**  
   - Use a modern authentication flow (e.g., passwordless email magic link or OAuth via Google/GitHub).  
   - Implement RBAC at the API and UI layers.  
   - Store secrets in environment variables; avoid hard‑coding keys.  
   - Apply rate limiting and input validation.  
   - Provide terms of use and “not financial advice” disclaimer.  


## 6. Implementation Plan (Phases)

1. **Phase 1 – Product Specification & Information Architecture** (this document)  
   - Finalise functional requirements, user personas, data sources and non‑functional requirements.  
   - Draft wireframe‑level page definitions and navigation structure.  

2. **Phase 2 – Architecture & Data Model**  
   - Implement database schema and migrations.  
   - Set up the repository structure (monorepo with `frontend`, `backend`, `ingestion`, `docs`).  
   - Configure Docker Compose for local development with PostgreSQL, Redis and MinIO.  

3. **Phase 3 – Backend API & Authentication**  
   - Implement the FastAPI server with user authentication and RBAC.  
   - Build endpoints for assets, metrics, events and users.  
   - Add unit tests and code linting.  

4. **Phase 4 – Connectors & Ingestion Scheduler**  
   - Implement at least two connectors (e.g., Binance price/volume and Ethereum on‑chain basics).  
   - Integrate job scheduler (e.g., `APScheduler` or Celery beat) to run connectors.  
   - Store raw documents and write normalised events.  

5. **Phase 5 – Metric Engine**  
   - Populate the metric registry with formulas, assumptions and references.  
   - Compute metric points from events and store them in `metric_points`.  
   - Write unit tests for metric calculations.  

6. **Phase 6 – Narrative Clustering & Scoring**  
   - Implement text ingestion and embedding pipeline.  
   - Integrate clustering and LLM‑assisted labelling; store narrative clusters and evidence.  
   - Compute narrative scores and explainability outputs.  

7. **Phase 7 – Front‑End Dashboards & Search**  
   - Build pages for Home, Asset List/Detail, Narrative Leaderboard/Detail, Metric Library and Watchlists.  
   - Implement global filters, charts, tables and search functionality.  

8. **Phase 8 – Education Hub & Method Cards**  
   - Auto‑generate method cards from the metric registry.  
   - Add glossary and deep‑dive articles with citations (including material on narrative economics and behavioural finance【939038864967448†L20-L59】【939038864967448†L67-L97】).  
   - Create a “How we score narratives” explainer page.  

9. **Phase 9 – Admin Console & Observability**  
   - Implement admin dashboards for connectors, ingestion jobs and user management.  
   - Integrate structured logging, metrics endpoint and error tracking.  
   - Harden security (rate limiting, CSP, etc.).  

10. **Phase 10 – Final QA & Deployment**  
    - Conduct end‑to‑end testing; seed demo data; fix bugs.  
    - Prepare documentation: architecture diagram, setup instructions, runbooks, threat model.  
    - Deploy to a cloud environment and monitor initial usage.  


## 7. Assumptions and Future Enhancements

- **Data access**: The prototype will rely on publicly available APIs; commercial or proprietary feeds can be integrated later.  
- **Machine learning**: Clustering and sentiment models will use existing open‑source solutions initially; custom models can be trained when more data becomes available.  
- **Scoring weights**: Default component weights in narrative scores will be based on expert judgement and backtesting; they will be adjustable by administrators.  
- **Paid tiers**: The pricing page can be stubbed in Phase 1; future phases may implement subscription management and feature gating.  
- **Real‑time alerts**: Email/SMS notifications are out of scope initially; the system will record alert firings for retrieval in the UI.  
- **Multi‑chain support**: Only one chain is implemented in Phase 1; additional blockchains will require new connectors and schema updates.  
- **Backtest sandbox & correlation explorer**: These optional extras can be developed after the core platform is stable.  

## 8. Summary

This specification outlines a narrative‑driven crypto analytics platform that leverages principles from narrative economics【939038864967448†L20-L59】, reflexivity【939038864967448†L67-L97】, adaptive markets【939038864967448†L101-L132】 and information cascade theory【939038864967448†L134-L164】 to detect and quantify the impact of stories on crypto markets.  By combining rigorous data ingestion, modular metric computation, sophisticated narrative clustering and a rich educational centre, the platform aims to empower investors, analysts and project teams with deeper insights and transparency.
