# Architecture Overview

## Project Overview
BioSignalFoundry is an applied AI project focused on decision-making for biotech stocks. The system is designed to gather structured evidence from multiple data providers to answer questions like "Should I BUY, SELL, HOLD, or AVOID a given biotech stock?". The project emphasizes signals, reasoning, determinism, and auditability.

## Repository Structure

```
biosignalfoundry/
├── .gitignore                    # Git ignore rules
├── config.py                     # Centralized configuration management
├── llm_provider.py               # LLM provider setup (Ollama or DeepSeek, via LLM_PROVIDER env)
├── pyproject.toml                # uv dependencies and project config
├── uv.lock                       # Locked dependency versions
├── README.md                     # Project documentation
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Docker services configuration (PostgreSQL, Redis)
├── app.py                        # FastAPI application entry point (/analyze, /health, /ready)
│
├── src/                          # Main application source code
│   ├── __init__.py
│   ├── biosignalfoundry.py       # Main deep agent (orchestrator) using deepagents
│   │
│   ├── agents/                   # Agent implementations for decision-making
│   │   ├── clinical_pipeline_agent.py     # Agent that analyzes the clinical/regulatory pipeline (CompiledSubAgent; no tools yet)
│   │   └── financial_health_agent.py      # Agent that analyzes financial health (CompiledSubAgent)
│   │
│   ├── agent_tools/              # Tools and utilities for agents to use
│   │   ├── __init__.py
│   │   ├── clinical_pipeline_agent_tools.py        # Tools for clinical trial analysis
│   │   ├── financial_health_agent_tools.py         # Tools for financial metrics analysis
│   │   ├── macro_context_agent_tools.py            # Tools for macroeconomic context
│   │   └── market_sentiment_agent_tools.py         # Tools for market sentiment analysis
│   │
│   ├── data_providers/           # API wrappers for external data sources
│   │   ├── __init__.py
│   │   ├── base.py               # Base class for all data providers
│   │   ├── cache.py              # Shared Redis response cache (OpenFDA, SEC)
│   │   ├── alphavantage.py       # Stock price and technical analysis data
│   │   ├── finnhub.py            # Financial market data and company info
│   │   ├── fred.py               # Federal Reserve economic data
│   │   ├── sec_edgar.py          # SEC filings and corporate data
│   │   ├── openfda.py            # FDA drug and clinical data
│   │   ├── marketstack.py        # Market data provider
│   │   └── massive.py            # OHLCV aggregate bars via the massive SDK
│   │
│   ├── core/                     # Core utilities and infrastructure
│   │   ├── db.py                 # Async SQLAlchemy engine, SessionLocal, declarative Base
│   │   ├── redis_client.py       # Shared Redis client (caching, rate limiting)
│   │   ├── logging_config.py     # structlog configuration (JSON or coloured output)
│   │   ├── rate_limiter.py       # Per-IP rate limits + global daily analysis budget (Redis)
│   │   ├── streaming_callback.py # Callback pushing tool-progress events to the SSE stream
│   │   ├── ticker_gate.py        # Deterministic company-name/ticker resolution + biotech gate
│   │   ├── subagent_capture.py   # Captures each subagent's typed structured response during a run
│   │   ├── tool_manifest.py      # Hash of the tool interfaces (name, description, args) a version pins
│   │   ├── version_registry.py   # Named system versions (v1.0.0, ...) as code-defined configs + DB registration
│   │   └── versioning.py         # system_version label (git sha + prompt hash) for paper trades
│   │
│   ├── middleware/               # LangChain agent middleware
│   │   ├── __init__.py
│   │   └── logging_middleware.py # LoggingMiddleware: logs agent input/output and tool timing
│   │
│   ├── prompts/                  # Prompt templates for LLMs
│   │   ├── biosignalfoundry_prompt.py               # Main system prompt (v1.0.0)
│   │   ├── biosignalfoundry_v2_prompt.py            # Main system prompt (v2.0.0, mentions clinical pipeline agent)
│   │   ├── clinical_pipeline_agent_prompt.py        # Clinical pipeline agent prompt
│   │   └── financial_health_agent_prompt.py         # Financial health agent prompt
│   │
│   └── evaluation/                # Signal evaluation framework for paper trading
│       ├── __init__.py
│       ├── types.py              # DecisionLabel enum
│       ├── price_loader.py       # Historical price data loader (+ latest_common_date)
│       ├── watchlist.py          # WATCHLIST (30 biotech tickers) and the XBI/IBB benchmarks
│       ├── recorder.py           # record_batch: runs versions over the watchlist, stores signals
│       ├── evaluator.py          # evaluate_matured: prices matured signals at 7/30/90 days
│       ├── metrics.py            # pure metric functions over paper_trade_returns rows
│       ├── models.py             # SQLAlchemy models: SystemVersion, PaperTrade, PaperTradeEvaluation
│       └── repository.py         # upsert_signal: re-running a batch updates instead of duplicating
│    
│
├── scripts/                      # Paper trading CLI scripts
│   ├── record_signal.py          # CLI for recorder.record_batch: one batch, several versions
│   ├── evaluate_signals.py       # CLI for evaluator.evaluate_matured
│   └── report_metrics.py         # Read-only metrics report per version and horizon
│
├── alembic.ini                   # Alembic configuration
├── alembic/                      # Database migrations (Alembic, async)
│   └── versions/                 # One file per schema change; apply with `alembic upgrade head`
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Shared fixtures; stubs heavy deps (llm_provider, deepagents) via sys.modules
│   ├── unit/                      # Mock-based tests, no live services
│   └── integration/               # Tests that hit real Redis and Postgres
│
├── docs/                         # Documentation
│   ├── architecture_docs/        # Architecture and design documentation
│   │   └── architecture_overview.md     # This file - overall system architecture
│   │
│   └── api_reference/            # External API references
│       ├── alphavantage_api.md
│       ├── finnhub_api.md
│       ├── fred_api.md
│       ├── marketstack_api.md
│       ├── massive_api.md
│       ├── openfda.md
│       └── sec_edgar.md
│
└── ui/                           # User interface (frontend)
```

## Directory Descriptions

### **src/** - Main Application Source
The core application code organized by functional domain.

### **`app.py`**
FastAPI application entry point (CORS origins come from `ALLOWED_ORIGINS`):
- `POST /analyze`: accepts a company name or ticker (`user_input`, 1–2000 chars) and streams Server-Sent Events: `progress` events while tools run, then a `result` event carrying a structured `BioSignalFoundryOutput` (ticker, decision, confidence, reasoning). See *Request path* for the guard sequence in front of the agent.
- `GET /health`: liveness; always returns `ok`.
- `GET /ready`: readiness; pings Redis and returns 503 if it is unreachable.

### **`src/biosignalfoundry.py`**
Defines `BioSignalFoundryOutput` and `build_agent(label, model=None)`, which builds the top-level deep agent (`deepagents.create_deep_agent`) for a registered version from `core/version_registry.py`: it verifies the version's prompts and tool interfaces against their pinned hashes (`VersionDrift` on an in-place edit), builds the version's LLM with `make_llm` (unless `model` overrides it), builds each enabled subagent through `SUBAGENT_BUILDERS`, and enforces the structured output schema via `AutoStrategy`. The module-level `biosignalfoundry` served by the API is `build_agent(DEFAULT_VERSION, model=llm)`, i.e. the default version on the LLM chosen by `LLM_PROVIDER`; paper trading builds versions without the override so each uses the LLM it pins. `SUBAGENT_BUILDERS` and `SUBAGENT_TOOLS` (subagent → the tool objects its builder uses, defined once in the agent module) are the only lists of subagents; `build_agent` raises `VersionError` if a version names a subagent with no builder, and a unit test checks every registered version.

### **src/agents/**
Contains agent implementations that orchestrate decision-making pipelines. Each agent uses tools from `agent_tools/` to gather and analyze data. Agents are wrapped as `CompiledSubAgent` instances so they can be composed into the top-level deep agent.
- `financial_health_agent.py`: Agent for analyzing biotech company financial health. Exposes `build_financial_health_subagent(llm, system_prompt)`, which returns a `CompiledSubAgent`.
- `clinical_pipeline_agent.py`: Agent for the clinical and regulatory pipeline (stage, catalysts, FDA history). Exposes `build_clinical_pipeline_subagent(llm, system_prompt)` and `CLINICAL_PIPELINE_TOOLS`, which is currently empty: tools are added later, after each one's response is verified, as a new version. Enabled from `v2.0.0` (`v1.0.0` + this subagent).

### **src/agent_tools/**
Provides specialized functions (tools) that agents can invoke. The tools further filter and extract data from src/data_providers. Each tool file corresponds to a decision pipeline:
- **clinical_pipeline_agent_tools.py**: Clinical trial analysis tools
- **financial_health_agent_tools.py**: Financial metrics, revenue, cash flow analysis
- **macro_context_agent_tools.py**: Macroeconomic indicators and context
- **market_sentiment_agent_tools.py**: Market sentiment and investor sentiment analysis

### **src/data_providers/**
Wrapper modules for external APIs. Each provider normalizes API responses into consistent JSON format with metadata.
- **base.py**: Abstract base class defining provider interface
- **alphavantage.py**: Stock prices, moving averages, technical indicators
- **finnhub.py**: Company fundamentals, earnings, market cap
- **fred.py**: Federal Reserve economic data (inflation, interest rates, etc.)
- **cache.py**: `cached_call(key, ttl, fetch)`, the Redis cache used by `openfda.py` and `sec_edgar.py`. Only `ok` responses are cached and Redis errors count as a miss. TTLs: `REDIS_CACHE_TTL_SECONDS_OPENFDA` (1 day) and `REDIS_CACHE_TTL_SECONDS_SEC_EDGAR` (6 hours). Cached entries are not invalidated when parsing code changes, so clear the `sec_edgar:*` / `openfda:*` keys after changing how a response is built.
- **sec_edgar.py**: SEC filings (10-K, 10-Q, 8-K) via `edgartools`; requires `SEC_EDGAR_IDENTITY`. `get_8k_data` is the validated path: items come from the filing's own item list, section text is parsed from the heading layout (including thin-space headings and stacked headings that share a body), and press releases are returned from the `EX-99.x` exhibit in `press_release`. Only US filers have 8-Ks; foreign filers (20-F/6-K) return no filings. Failures use the standard `_make_error` shape.
- **openfda.py**: FDA data via `query()` (cached; a no-match 404 is `ok=True` with empty results; the API key is redacted from errors) and `query_all()` (pages through every match). Responses carry `total` and `truncated`. `company_search_keys()` and `matches_company()` map a listed company name to OpenFDA sponsor/company names (e.g. "Intra-Cellular" vs `INTRACELLULAR`). `drug/drugsfda` covers NDAs and ANDAs only, not biologics (BLAs). `transparency/crl` includes letters for applications that were later approved, so check `approval_status`.
- **marketstack.py**: General market data
- **massive.py**: OHLCV aggregate bars via the `massive` SDK

### **src/core/**
Shared infrastructure used by `app.py`, the agents and the scripts. Nothing here calls an LLM.

- **redis_client.py**: Module-level `redis_client` (`decode_responses=True`) built from `REDIS_HOST/PORT/DB` and `Settings.redis_password`. Used for the `/analyze` result cache, the rate limiter, the readiness probe, and the data-provider response caches.
- **db.py**: Async SQLAlchemy `engine` (`pool_pre_ping=True`), `SessionLocal` (`expire_on_commit=False`) and declarative `Base`, built from `Settings.database_url` (asyncpg). `Base.metadata` is also what Alembic autogenerates against.
- **logging_config.py**: `setup_logging()` configures structlog once for the whole application (idempotent). Coloured console output in development, JSON lines when `ENV=production`.
- **rate_limiter.py**: Redis fixed-window counters (`INCR` + `EXPIRE NX` in one pipeline, so one round trip per check).
  - `check_rate_limit(client_ip, per_minute, per_day) → (allowed, retry_after_seconds)`: per-IP limits.
  - `check_and_consume_daily_budget(cap) → bool`: a global daily cap on uncached agent runs, to bound LLM spend.
  - Fixed windows allow a burst across a window boundary; acceptable for abuse/cost control. Both functions raise `RedisError` and leave the fail-open/closed policy to the caller (`app.py` currently fails open).
  - Limits come from `RATE_LIMIT_PER_MINUTE` (5), `RATE_LIMIT_PER_DAY` (50) and `DAILY_ANALYSIS_BUDGET_CAP` (500).
- **ticker_gate.py**: `resolve_biotech_ticker(user_input) → ResolvedTicker(ticker, company_name, industry)`. Runs before any LLM call.
  1. *Resolve*: a ticker-shaped input is looked up directly. Otherwise the normalized name is matched against the SEC company list bundled with `edgartools` (offline, Nasdaq/NYSE/CBOE only, at most 5 candidates).
  2. *Gate*: every candidate's Finnhub `finnhubIndustry` must be in `BIOTECH_INDUSTRIES` (`Biotechnology`, `Pharmaceuticals`). Checking all candidates lets an ambiguous name such as "Vertex" resolve to the biotech one.
  - Raises `TickerRejected` (bad/ambiguous/non-biotech input; message is safe to show the user, mapped to HTTP 422) or `GateUnavailable` (Finnhub failed; mapped to 503 and never cached as an answer).
  - Blocking Finnhub calls run via `asyncio.to_thread`.
- **streaming_callback.py**: `StreamingProgressCallback`, a LangChain `AsyncCallbackHandler`. On each tool start it puts `{"type": "progress", "message": <label>}` on an `asyncio.Queue` that `/analyze` drains into the SSE stream. Labels come from `TOOL_LABELS`; unmapped tools fall back to `Running <name>...`. Add an entry when you add a tool the user should see named.
- **versioning.py**: `system_version()` returns `<git sha>-<prompt hash>[-dirty]`, recorded on every paper trade so results can be attributed to a code and prompt state.
  - git sha: from `GIT_SHA` if set (Docker builds without `.git`), else `git rev-parse`, else `nogit`.
  - prompt hash: 8-char SHA-256 over the normalized text of every prompt in `PROMPTS`. **Register new agent prompts in `PROMPTS`** or prompt edits won't change the version.
  - `-dirty`: uncommitted tracked changes exist (untracked files are ignored).
- **subagent_capture.py**: deepagents drops a subagent's `structured_response` and gives the supervisor only a text repr. `build_agent` wraps each subagent's runnable with `capture_structured_output`, which records the typed output into a collector opened by `capture_subagent_outputs()` (used by the recorder) and returns the result unchanged, so the supervisor's behaviour is identical. Stored in `paper_trades.agent_output.subagents`; without a collector it does nothing.
- **version_registry.py**: the named versions used by paper trading (`VERSIONS`, `DEFAULT_VERSION`). A version is a `VersionConfig`: a supervisor prompt, enabled subagents (name → prompt name; prompt names are keys of `versioning.PROMPTS`), declared `tools` (subagent name → tool names), LLM provider/model/temperature, and pinned `prompt_hash` and `tool_hash`. Imports no agent or LLM code.
  - `verify_prompts(label)` raises `VersionDrift` if a prompt the version uses was edited in place; copy it under a new `PROMPTS` name and register a new version instead.
  - `verify_tools(label, tools_by_subagent)` raises `VersionDrift` if the tools a subagent really exposes differ from the declared names, or if the hash of their interfaces (`core/tool_manifest.py`: name, whitespace-normalized description, argument schema) differs from `tool_hash`. The implementation is not hashed, so fixes meant for every version stay allowed; `git_sha` points at the code. `build_agent` calls it with `SUBAGENT_TOOLS`.
  - `register_version(session, label)` inserts the `system_versions` row on first use and raises `VersionDrift` if the stored config later differs. The caller commits.
  - `get_version` / `resolve_labels` look up a label or parse a CLI value (`all`, `v1.0.0,v1.0.1`).

### **src/middleware/**
LangChain `AgentMiddleware` implementations applied at agent construction time:
- **logging_middleware.py**: `LoggingMiddleware` — logs the agent's input message, every model decision (tool calls or final answer), each tool execution with elapsed time, and the final agent response. Applied to `biosignalfoundry` and each subagent (`financial_health_agent`, `clinical_pipeline_agent`).

### **src/prompts/**
LLM prompt templates:
- **biosignalfoundry_prompt.py**: Master system prompt defining BioSignalFoundry's decision-making framework
- **financial_health_agent_prompt.py**: Specialized prompt for the financial health agent
- **biosignalfoundry_v2_prompt.py**: Supervisor prompt for `v2.0.0`, a copy of the v1.0.0 prompt that also delegates to the clinical pipeline agent
- **clinical_pipeline_agent_prompt.py**: Specialized prompt for the clinical pipeline agent

### **src/evaluation/**
Signal evaluation framework for validating paper trading signals against price data. Evaluates how well `BUY / SELL / HOLD / AVOID` signals predicted actual forward returns:
- **models.py**: SQLAlchemy models. `SystemVersion` (`system_versions`): registered version label + config. `PaperTrade` (`paper_trades`): one decision per `(batch, version_label, ticker)` with the agent's JSON output and entry prices for the stock, XBI and IBB. `PaperTradeEvaluation` (`paper_trade_evaluations`): one row per trade and horizon with exit prices, plus entry prices re-fetched in the same download (`*_entry_price_adj`) so splits/dividends between signal and exit cancel out. Only observations are stored; returns and verdicts are derived at report time via the `paper_trade_returns` view (created in the migration, not an ORM model), which must be used instead of the raw entry prices.
- **repository.py**: `upsert_signal` (re-running the same batch/version/ticker replaces the signal and deletes its evaluations), plus the read-only `load_return_rows` and `count_trades` used by the metrics report.
- **types.py**: `DecisionLabel` (BUY / SELL / HOLD / AVOID)
- **watchlist.py / recorder.py**: `WATCHLIST` (30 tickers; every one must pass the ticker/sector gate and have prices) and `BENCHMARKS` (`XBI`, `IBB`). `recorder.record_batch(...)` implements the batch flow above; its pure helpers (`parse_decision`, `parse_confidence`, `extract_subagent_outputs` (text fallback), `fetch_entry_prices`) are unit tested, and the whole flow is integration tested with a fake agent and price source.
- **price_loader.py**: `load_prices(ticker, start, end) → dict[date, float]` — fetches historical OHLCV data via MarketStack and returns a `{date: close_price}` map used by the recorder and evaluator.

### **scripts/**
CLI entry points for the paper trading loop described in the README's "On Backtesting" section:
- **metrics.py / report_metrics.py**: `metrics.py` holds every metric definition as pure functions over `ReturnRow`s (a row of the `paper_trade_returns` view): excess return vs XBI/IBB, BUY vs SELL/AVOID spread, hit rate, baselines (always-BUY, always-HOLD, random, benchmark), confusion matrix, confidence calibration and loss profile, each with N and a rough 95% interval. HOLD is excluded from the headline metrics. Unit tested without a database. `repository.load_return_rows` / `count_trades` read the view; `scripts/report_metrics.py [--batch] [--versions] [--horizons] [--benchmark xbi|ibb] [--detail]` groups rows by version and horizon and prints them with evaluated-vs-recorded counts. It writes nothing.
- **record_signal.py**: Thin CLI over `evaluation/recorder.py`: `--batch <name> --versions all|v1.0.0,v1.0.1 [--tickers ...] [--force] [--concurrency N]`. Every version runs over the watchlist on one signal date with shared entry prices for the stock, XBI and IBB (one common trading day), so versions compare stock by stock. Re-running a batch skips signals already recorded (resume after failures); `--force` replaces them and deletes their evaluations. A batch whose existing signals have a different date is refused. Exit code 1 if any signal failed, 2 for bad arguments. Run after the US market close.
- **evaluator.py / evaluate_signals.py**: `evaluator.evaluate_matured(...)` finds every (signal, horizon in 7/30/90) whose target date (`entry_price_date` + horizon) is before today and has no `paper_trade_evaluations` row, downloads stock/XBI/IBB once per symbol, and inserts a row with the exit prices on the first common trading day on or after the target (`price_date`) plus entry prices re-fetched in the same download (`*_entry_price_adj`, split/dividend safe). Today's unfinished session is never used; horizons without a close yet stay pending, missing data is reported as failed. Inserts use `ON CONFLICT DO NOTHING`, so it is safe to run late or repeatedly. The script takes `[--batch] [--versions] [--horizons]` and exits 1 if anything failed.

### **alembic/**
Database migrations. `alembic/env.py` reads the connection URL from `config.Settings.database_url` and the schema from `src.core.db.Base.metadata`, so models and migrations share one source of truth. `src/core/db.py` holds the async engine and session factory.

### **docs/**
Project documentation split into two sections:
- **architecture_docs/**: Design and system architecture
- **api_reference/**: External API documentation and examples

### **tests/**
Split into `unit/` and `integration/`, matching the two CI jobs in `.github/workflows/test.yml`. `conftest.py` at the `tests/` root stubs heavy dependencies (`llm_provider`, `deepagents`) via `sys.modules` injection *before* test collection begins, so any test importing `app` or `src.*` gets safe mocks instead of raising on missing env vars or LLM setup.

- **unit/**: No live services required; runs via `uv run pytest tests/unit/ -v`. Test files are named after the module they cover (e.g. `test_ticker_gate.py` ↔ `src/core/ticker_gate.py`).
- **integration/**: Requires real Redis and Postgres (see the `redis` service container in CI, or `docker-compose up` locally); runs via `uv run pytest tests/integration/ -v`. DB tests use a separate `_test` database. External APIs/LLM are still mocked.

### **Configuration Files**
- **config.py**: Centralized configuration via a pydantic-settings `Settings` object (`settings`, loaded from `.env`). Covers Redis and Postgres connection settings (and the derived `database_url`), provider API keys, `LLM_PROVIDER` (validated: `DEEPSEEK_API_KEY` is required for `deepseek`), `LOG_LEVEL`, `ENV`, `ALLOWED_ORIGINS`, and the rate-limit/budget settings. Also exports the Redis settings and per-provider cache TTL constants (e.g. `REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY`) used by the cache layers.
- **llm_provider.py**: `make_llm(provider, model, temperature)` builds a chat model (`ollama` via `langchain_ollama`, `deepseek` via `langchain_deepseek`). The module-level `llm` is the API's default, chosen by the `LLM_PROVIDER` environment variable (Mistral via Ollama, or DeepSeek Chat).
- **pyproject.toml**: Project metadata, dependencies, uv configuration

### **Docker**
- **Dockerfile**: Container image for the application
- **docker-compose.yml**: Orchestration for PostgreSQL (data storage) and Redis (caching)

### **ui/** - User Interface
The `ui` folder contains the frontend code for the BioSignalFoundry project. It is built using React framework

## Data Flow

### Request path
Steps 2–5 are cheap, deterministic guards in `src/core/` that run before any LLM spend:

1. `app.py` (FastAPI) receives a `POST /analyze` request with a natural-language `user_input`
2. **Rate limit** (`rate_limiter.check_rate_limit`): per-IP, per-minute and per-day. Exceeding returns 429 with `Retry-After`. Redis errors fail open.
3. **Ticker gate** (`ticker_gate.resolve_biotech_ticker`): resolves the input to one biotech ticker. `TickerRejected` returns 422, `GateUnavailable` returns 503.
4. **Result cache**: looks up `biosignalfoundry:analyze:<DEFAULT_VERSION>:<TICKER>` in Redis (keyed on the resolved ticker, so "Moderna" and "MRNA" share an entry, and on the version, so changing `DEFAULT_VERSION` never serves the previous version's answer). A hit is streamed back immediately.
5. **Daily budget** (`rate_limiter.check_and_consume_daily_budget`): only cache misses consume it. Over the cap returns 503. Redis errors fail open.
6. The request is forwarded to **`biosignalfoundry`** (`src/biosignalfoundry.py`) — a `deepagents` deep agent that acts as the supervisor — with a `StreamingProgressCallback` attached so tool starts reach the client as `progress` events
7. The supervisor delegates to the **financial health subagent** (`src/agents/financial_health_agent.py`) via the `CompiledSubAgent` interface (from `v2.0.0` the supervisor also delegates to the **clinical pipeline subagent**, `src/agents/clinical_pipeline_agent.py`, which has no tools yet)
8. The sub-agent calls **Agent Tools** (`src/agent_tools/financial_health_agent_tools.py`) to gather specific data points
9. Agent Tools call **Data Providers** (`src/data_providers/`) which hit external APIs and cache responses in **Redis**
10. The sub-agent returns a structured `FinancialHealthAgentOutput` to the supervisor
11. The supervisor interprets the financial health score and produces a final `BioSignalFoundryOutput` (BUY/SELL/HOLD/AVOID + confidence + reasoning), which is cached in Redis and sent as the `result` event

### Paper-trade path
`scripts/record_signal.py` calls `evaluation.recorder.record_batch`, which builds each requested version with `build_agent(label)`, registers it in `system_versions`, fetches shared entry prices (stock, XBI, IBB) once per ticker, runs the agent per version and ticker, and upserts a `paper_trades` row holding the decision, the agent's structured output (including each subagent's result recovered from the `task` tool messages) and the entry prices. `scripts/evaluate_signals.py` (via `evaluation.evaluator`) later adds per-horizon `paper_trade_evaluations` rows. Both use `core.db.SessionLocal`.

### Data provider call chain
```
External API SDK
      ↓
BaseClient._call()     # Calls SDK, serializes response to plain dict + metadata
      ↓
Provider method        # Thin wrapper; applies Redis caching around _call()
      ↓
Agent tool (@tool)     # Filters/normalizes the provider response for the agent
      ↓
Agent (LLM)            # Interprets the structured tool output
```

### Logging
`LoggingMiddleware` is attached to each agent. It emits structured log events (via structlog) at each stage: agent start, model decision, tool call with timing, and agent response. Log format is controlled by `src/core/logging_config.py`.

## Future Directions
- Additional agent types and decision pipelines
- Enhanced auditability and reasoning logs
- Database integration for historical decisions
- UI/Dashboard for decision visualization