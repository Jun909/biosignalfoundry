# Roadmap

Phase-by-phase plan for BioSignalFoundry. For what the project is and why, see the
[README](../README.md).

## Phase 1 — Stabilization
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

## Phase 2 — Signal Completeness
* Wire remaining subagents: clinical (OpenFDA), macro (FRED), sentiment (Finnhub)
* Paper trading: record decisions and track returns over time (manual today via
  `scripts/record_signal.py` / `scripts/evaluate_signals.py`, both backed by Postgres)
* Explicit version registry: named versions (`v1.0`, `v1.1`, ...) defined as
  configurations (subagents, tools, prompts, model), replacing the git SHA + prompt hash
  label as the identifier (see [Evaluation](../README.md#evaluation))
* Parallel version evaluation instead of a scheduled weekly loop: run every version
  on the same watchlist and date, score at 7/30/90-day horizons, repeat for a few batches.
  Needs a schema migration for per-horizon evaluations, benchmark prices and the agent's
  structured output
* ~~Deterministic ticker resolution ahead of agent reasoning, instead of relying on
  the LLM to infer tickers~~ ✅ Done — see `src/core/ticker_gate.py`; input is a single
  company name or ticker, matched against the SEC company list bundled with
  `edgartools` (offline, no API quota). The agent now only ever receives
  `Analyze <TICKER>`, and the `/analyze` cache is keyed on the resolved ticker
* ~~Reject unresolvable or non-biotech queries before invoking the agent~~ — ~~a ticker~~
  + ~~sector gate (Finnhub `finnhubIndustry`) ahead of the paid LLM call, doubling as~~
  ~~cost control~~ ✅ Done — rejected queries return HTTP 422 before the cache, daily
  budget or agent are touched; a Finnhub outage returns 503 instead of guessing
* ~~System/prompt versioning derived automatically (git SHA + prompt hash) instead of
  the manually-bumped `SYSTEM_VERSION` constant~~ ✅ Done — see `src/core/versioning.py`;
  paper trades are labelled `<git sha>-<prompt hash>` (plus `-dirty` for uncommitted
  changes) and `record_signal.py` uses it automatically. Rows recorded before this
  carry the legacy `v1.0` label
* Evaluation metrics: XBI/IBB benchmark and excess return, BUY vs SELL/AVOID spread,
  hit rate, baselines (always-BUY, always-HOLD, random), confusion matrix and
  calibration, so accuracy is measured against a baseline instead of read in isolation
  (see [Evaluation](../README.md#evaluation))
* RAG over SEC filings (10-K/10-Q) for grounded, citable reasoning
* Data quality validation layer

## Phase 3 — Scalability
* Async task queue for agent execution (Celery + Redis)
* Circuit breakers and retry logic per data provider
* Move data-provider and Redis calls to true async I/O instead of blocking the
  event loop

## Phase 4 — Observability
* LLM tracing (LangSmith or Langfuse)
* Metrics and centralized log aggregation
* Cost and token usage tracking per request

## Phase 5 — ML Feedback Loop
* Outcome tracking: link paper trades to actual price outcomes
* A/B testing across prompt variants (building on the deterministic versioning
  from Phase 2)
* Fine-tuning on accumulated decision/outcome data

## Phase 6 — Trust & Product Surface
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
