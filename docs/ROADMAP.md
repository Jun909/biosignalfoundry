# Roadmap

Phase-by-phase plan for BioSignalFoundry. For what the project is and why, see the
[README](../README.md).

## Phase 1 — Stabilization
* ~~Persistent storage of decisions and signals (PostgreSQL + Alembic) — also unblocks
  the automated paper trading loop in Phase 2~~ ✅ Done — paper trades live in the
  `paper_trades` table (`src/evaluation/models.py`, migrations in `alembic/`); re-running
  a signal for the same batch/version/ticker updates it instead of duplicating
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
* ~~Explicit version registry: named versions (`v1.0`, `v1.1`, ...) defined as
  configurations (subagents, tools, prompts, model), replacing the git SHA + prompt hash
  label as the identifier~~ ✅ Done — see `src/core/version_registry.py` (a version is a
  supervisor prompt, a subagent → prompt map and an LLM, with a pinned prompt hash that
  makes an in-place prompt edit an error) and `build_agent(label)` in
  `src/biosignalfoundry.py`. Only `v1.0` (financial health baseline) exists so far; the
  `/analyze` cache key includes the served version. Tools are not part of a version's
  config: a changed tool becomes a new version by giving its subagent a new name (see
  AGENTS.md). See [Evaluation](../README.md#evaluation)
* ~~Rebuild the database schema for the new evaluation design~~ ✅ Done — three tables
  (`system_versions`, `paper_trades`, `paper_trade_evaluations`) and the
  `paper_trade_returns` view, in a single Alembic migration (`src/evaluation/models.py`).
  Only observations are stored; forward, XBI, IBB and excess returns are derived by the
  view from split/dividend-adjusted entry prices re-fetched at evaluation time. The old
  single-table layout and its data were dropped
* ~~Rewrite `scripts/record_signal.py` for the new schema: run a registered version over a
  30-ticker watchlist (the current 15 plus 15 more, checked against the ticker/sector
  gate) and store the decision, the agent's structured output and the entry prices for the
  stock, XBI and IBB, grouped by `batch`~~ ✅ Done — `scripts/record_signal.py` is a thin
  CLI over `src/evaluation/recorder.py`; the 30 tickers are in `src/evaluation/watchlist.py`
  (all pass the gate and have prices). Versions in a batch share one date and one set of
  entry prices; re-running a batch resumes it. The first real run should be checked to
  confirm `agent_output.subagents` is populated as expected
* ~~Rewrite `scripts/evaluate_signals.py` for the new schema: for every matured horizon
  (7/30/90 days) without an evaluation row, fetch the exit prices and the re-fetched
  adjusted entry prices for the stock, XBI and IBB, and insert a `paper_trade_evaluations`
  row (idempotent; can be run late or repeatedly)~~ ✅ Done — `scripts/evaluate_signals.py`
  over `src/evaluation/evaluator.py`; horizons count from `entry_price_date`
* `src/evaluation/metrics.py`: pure functions over rows from `paper_trade_returns` for
  excess return, BUY vs SELL/AVOID spread, hit rate, baselines (always-BUY, always-HOLD,
  random, benchmark), confusion matrix, confidence calibration and loss profile. Unit
  tested without a database; metric definitions and thresholds live here, not in stored
  data
* `scripts/report_metrics.py`: queries `paper_trade_returns` (filter by batch, version
  and horizon), feeds the rows to `metrics.py` and prints the results, including how many
  signals are evaluated per horizon so a partial 90-day result is not read as final.
  Writes nothing. Also decide whether `src/evaluation/engine.py` and its `Backtest*`
  types, left over from before paper trading, can be removed
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
  changes). Superseded as the identifier by the explicit version registry above; it
  stays as metadata (`git_sha`, `prompt_hash`)
* RAG over SEC filings (10-K/10-Q) for grounded, citable reasoning
* Data quality validation layer
* Define versioning

## Phase 3 — Scalability
* Async task queue for agent execution (Celery + Redis)
* Circuit breakers and retry logic per data provider
* Move data-provider and Redis calls to true async I/O instead of blocking the
  event loop

## Phase 4 — Observability & Parallel Evaluation
* LLM tracing (Langfuse)
* Metrics and centralized log aggregation
* Cost and token usage tracking per request (Langfuse), so versions can be compared on
  cost as well as accuracy
* Test run evaluation for v1.0
* Consideration of input snapshot for parallel version evaluation
* Parallel version evaluation instead of a scheduled weekly loop: once all subagents are
  wired and the versions are assigned (Phase 2) and cost tracking is in place, run every
  version on the same watchlist and signal date, score at 7/30/90-day horizons, repeat
  for a few batches, and measure run-to-run noise (same version run twice). Builds on the
  rewritten recording/evaluation scripts and schema from Phase 2

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

## Long-Term Vision
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
