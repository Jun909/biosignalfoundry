# BioSignalFoundry - Biotech Stock Decision System

This repository is a long term applied AI project focused on biotech stock decision making. The MVP is complete and the system is live: a signal-driven AI agent that answers the question:

> Should I BUY, SELL, HOLD, or AVOID a given biotech stock - and why?

## Project Philosophy
This project has a few core principles

* **Signals > Models**

    Clean, meaningful signals matter way more than fancy architectures or models

* **Reasoning > Prediction**

    The system does not predict prices. It gathers structured evidence that is currently available into decisions.

* **Deterministic before agentic**

    Deterministic pipelines and explicit signals extraction come before multi-agent systems.

* **Auditability**

    Every decision made should be explainable, traceable and debuggable.

This is not a trading bot nor financial advice.

## Current State

The MVP is shipped. Check it out here: https://biosignalfoundry-two.vercel.app The system runs end-to-end: a user asks a question about a biotech stock and receives a structured investment decision with reasoning in real time.

**Backend** (`app.py`) — FastAPI service with:
* A LangChain-based AI reasoning agent that pulls from multiple data providers
* Server-Sent Events (SSE) for real-time streaming progress to the client
* Redis caching of completed analyses to avoid redundant agent runs
* Structured JSON output validated against a typed schema

**Frontend** (`ui/`) — React + TypeScript UI with:
* Free-text input and curated suggestion prompts
* Live progress updates streamed from the backend during analysis
* Decision badge (BUY / SELL / HOLD / AVOID), confidence bar, and full reasoning display

**Data Providers**
* Alphavantage, Finnhub, FRED, SEC (via edgartools), OpenFDA, Marketstack, Massive

Detailed, provider-specific request/response examples can be found in
[`docs/api_reference/`](docs/api_reference/)

Entire repo architecture can be found in
[`docs/architecture_docs/`](docs/architecture_docs/)

## What was built (MVP)

The pipeline is intentionally minimal and linear:

> Data Sources → Signal Extraction → LLM Reasoning Agent → Structured Decision Output

For any biotech company the system returns:

* **Decision**: BUY / SELL / HOLD / AVOID
* **Confidence**: numeric score (0–100)
* **Reasoning**: short, structured explanation traceable to the underlying signals

## What this project is *NOT*

This project does **not** aim to:

* Predict short-term stock prices
* Replace financial financial advice
* Use reinforcement learning or black-box optimization

## On Backtesting

Traditional backtesting — replaying historical signal dates and evaluating decisions against past prices is intentionally not implemented in this project. This is a deliberate design decision, not an oversight.

There are four compounding reasons why proper historical backtesting is not feasible here:

1. **Hallucination risk from date-parameterized tools.** Passing a specific historical date to agent tools and asking the LLM to restrict itself to data available on that date introduces hallucination risk. LLMs are unreliable at consistently honoring such constraints when reasoning over tool outputs.

2. **APIs do not support point-in-time historical data.** Several data providers used in this project (AlphaVantage, Finnhub) return the latest available data regardless of any date argument and causes data leakage. There is no way to retrieve what the income statement or company profile looked like on an arbitrary past date through these APIs.

3. **LLM training data contamination.** Even if perfect point-in-time financial data were available, a general-purpose LLM has already seen news, filings, and market commentary about any historically significant biotech stock up to its training cutoff. The model cannot simulate the genuine uncertainty that existed on a past signal date as it has already seen how things turned out.

4. **Point-in-time financial databases are out of scope.** Services that correctly snapshot what financial data was publicly available on any given date (e.g. Bloomberg, Compustat) are expensive, proprietary, and not appropriate for an early-stage open project.

For these reasons, the evaluation strategy used here is **paper trading**: the agent makes a decision using current data, that decision is recorded with today's price as the entry point, and it is evaluated against real prices after the holding period elapses. This is honest, reproducible, and free of look-ahead bias.

## Planned Roadmap

### Phase 1 — Stabilization
* ~~Persistent storage of decisions and signals (PostgreSQL + Alembic) — also unblocks
  the automated paper trading loop in Phase 2~~ ✅ Done — paper trades live in the
  `paper_trades` table (`src/evaluation/models.py`, migrations in `alembic/`); re-running
  a signal for the same ticker/day/version updates it instead of duplicating
* ~~Integration test suite and CI/CD pipeline~~ ✅ Done — see `.github/workflows/test.yml`
* ~~Health and readiness endpoints~~ ✅ Done — see `GET /health` and `GET /ready` in `app.py`
* ~~Rate limiting and abuse/cost control on `/analyze` (currently unauthenticated, and
  a cache miss triggers a paid LLM run)~~ ✅ Done — per-IP rate limits + a global daily
  budget cap on non-cached runs, see `src/core/rate_limiter.py` and `POST /analyze` in
  `app.py`
* ~~Fail-fast config validation at startup (e.g. `pydantic-settings`) instead of silent
  failures on missing or misspelled env vars~~ ✅ Done — see `Settings` in `config.py`
* ~~Graceful Redis degradation — a cache outage should fall back to a cache miss, not
  a 500~~ ✅ Done — `/analyze` treats Redis read/write failures as a cache miss/skip
* ~~Frontend test suite (Vitest + React Testing Library) — currently no tests on
  the UI at all~~ ✅ Done — see `ui/src/App.test.tsx` and
  `ui/src/api/biosignalfoundry.test.ts`, run with `npm run test` in `ui/`
* ~~Hardening: lint/format/type-check CI job~~ ✅ Done (frontend) — `.github/workflows/test.yml`
  now runs `npm run lint`, `npm run build`, `npm run test`; Python `black`/`isort`/type-check
  still not enforced in CI, ~~fix the `alphavintage` → `alphavantage`
  naming~~ ✅ Done, ~~rename `src/backtesting/` → `src/evaluation/` to match the "no classic
  backtesting" design decision below~~ ✅ Done

### Phase 2 — Signal Completeness
* Wire remaining subagents: clinical (OpenFDA), macro (FRED), sentiment (Finnhub)
* Paper trading loop: record decisions and track returns over time (manual today via
  `scripts/record_signal.py` / `scripts/evaluate_signals.py`, both backed by Postgres)
* Automate the paper trading loop to run on a schedule instead of by hand
  (mechanism TBD; depends on Phase 1's persistent storage)
* Deterministic ticker resolution (e.g. AlphaVantage symbol search) ahead of agent
  reasoning, instead of relying on the LLM to infer tickers
* Reject unresolvable or non-biotech queries before invoking the agent — a ticker
  + sector gate (Finnhub `finnhubIndustry`) ahead of the paid LLM call, doubling as
  cost control
* System/prompt versioning derived automatically (git SHA + prompt hash) instead of
  the manually-bumped `SYSTEM_VERSION` constant
* Benchmark comparison in evaluation (always-BUY, random, sector return) so paper
  trading accuracy is measured against a baseline instead of read in isolation
* RAG over SEC filings (10-K/10-Q) for grounded, citable reasoning
* Data quality validation layer

### Phase 3 — Scalability
* Async task queue for agent execution (Celery + Redis)
* Circuit breakers and retry logic per data provider
* Move data-provider and Redis calls to true async I/O instead of blocking the
  event loop

### Phase 4 — Observability
* LLM tracing (LangSmith or Langfuse)
* Metrics and centralized log aggregation
* Cost and token usage tracking per request

### Phase 5 — ML Feedback Loop
* Outcome tracking: link paper trades to actual price outcomes
* A/B testing across prompt variants (building on the deterministic versioning
  from Phase 2)
* Fine-tuning on accumulated decision/outcome data

### Phase 6 — Trust & Product Surface
* Public track record dashboard showing paper trading performance, wins and
  losses included
* Surface the signal-level reasoning breakdown in the UI, not just the final
  decision text

## Beyond MVP / Long-Term Vision
Directional ideas for after Phases 1–6 are done — not scoped or scheduled yet,
kept separate from the roadmap above on purpose.

* **User accounts & personal dashboards** — auth, saved watchlists, per-user
  decision history
* **Automated monitoring & notifications** — scheduled/event-driven checks over
  a user's watchlist, pushed via email
* **AI with memory** — recommendations informed by a user's history and
  preferences, not just a single stateless query (depends on user accounts
  existing first)
* **Discovery / news feed** — surfacing new biotech companies and sector news,
  not just answering direct queries

## Disclaimer
Nothing in this repository constitutes to financial advice or a recommendation to trade securities.

## Author
* GitHub: [@Jun909](https://github.com/Jun909)
* LinkedIn: [Jun Siang Pang](https://www.linkedin.com/in/jun-siang-pang-2640071b0/)