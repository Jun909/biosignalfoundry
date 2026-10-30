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
│   │   └── versioning.py         # system_version label (git sha + prompt hash) for paper trades
│   │
│   ├── middleware/               # LangChain agent middleware
│   │   ├── __init__.py
│   │   └── logging_middleware.py # LoggingMiddleware: logs agent input/output and tool timing
│   │
│   ├── prompts/                  # Prompt templates for LLMs
│   │   ├── biosignalfoundry_prompt.py               # Main system prompt
│   │   └── financial_health_agent_prompt.py         # Financial health agent prompt
│   │
│   └── evaluation/                # Signal evaluation framework for paper trading
│       ├── __init__.py
│       ├── types.py              # Data structures (BacktestRequest, Signal, BacktestObservation, BacktestResult)
│       ├── engine.py             # Evaluation engine
│       ├── price_loader.py       # Historical price data loader
│       ├── models.py             # SQLAlchemy PaperTrade model (paper_trades table)
│       └── repository.py         # upsert_signal: same-day re-run updates instead of duplicating
│    
│
├── scripts/                      # Paper trading CLI scripts
│   ├── record_signal.py          # Runs the agent for a ticker, logs a signal + entry price
│   ├── evaluate_signals.py       # Evaluates matured signals against actual exit prices
│   └── import_paper_trades.py    # One-time import of the legacy JSON log into Postgres
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
Defines the top-level `biosignalfoundry` agent using `deepagents.create_deep_agent`. Composes the `financial_health_subagent` and enforces a structured output schema (`BioSignalFoundryOutput`) via `AutoStrategy`.

### **src/agents/**
Contains agent implementations that orchestrate decision-making pipelines. Each agent uses tools from `agent_tools/` to gather and analyze data. Agents are wrapped as `CompiledSubAgent` instances so they can be composed into the top-level deep agent.
- `financial_health_agent.py`: Agent for analyzing biotech company financial health. Exposes `financial_health_subagent` (a `CompiledSubAgent`).

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
- **sec_edgar.py**: SEC filings (10-K, 10-Q, 8-K)
- **openfda.py**: FDA drug approvals, clinical trial data
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

### **src/middleware/**
LangChain `AgentMiddleware` implementations applied at agent construction time:
- **logging_middleware.py**: `LoggingMiddleware` — logs the agent's input message, every model decision (tool calls or final answer), each tool execution with elapsed time, and the final agent response. Applied to both `biosignalfoundry` and `financial_health_agent`.

### **src/prompts/**
LLM prompt templates:
- **biosignalfoundry_prompt.py**: Master system prompt defining BioSignalFoundry's decision-making framework
- **financial_health_agent_prompt.py**: Specialized prompt for the financial health agent

### **src/evaluation/**
Signal evaluation framework for validating paper trading signals against price data. Evaluates how well `BUY / SELL / HOLD / AVOID` signals predicted actual forward returns:
- **models.py**: SQLAlchemy `PaperTrade` model (`paper_trades` table), unique on `(ticker, signal_date, system_version)`.
- **repository.py**: `upsert_signal`; a same-day re-run replaces that day's signal and clears its evaluation.
- **types.py**: Core data structures — `BacktestRequest`, `Signal`, `DecisionLabel`, `BacktestObservation`, `BacktestResult`
- **engine.py**: `run(request, signals) → BacktestResult`. For each signal, looks up entry price at `as_of_date` and exit price at `as_of_date + holding_period_days`, then computes `forward_return` and `is_correct` based on configurable `buy_threshold` / `sell_threshold`. Aggregates per-observation results into summary stats (`total_observations`, `correct_observations`, `accuracy`).
- **price_loader.py**: `load_prices(ticker, start, end) → dict[date, float]` — fetches historical OHLCV data via MarketStack and returns a `{date: close_price}` map used by the engine.

### **scripts/**
CLI entry points for the paper trading loop described in the README's "On Backtesting" section:
- **record_signal.py**: Runs the agent for a ticker (or the whole watchlist), records today's price as the entry point, and upserts the signal into the `paper_trades` table (a same-day re-run replaces that day's signal).
- **evaluate_signals.py**: Evaluates signals whose holding period has elapsed against actual exit prices, writing the result back to the same `paper_trades` row so each signal is only evaluated once.
- **import_paper_trades.py**: One-time, re-runnable import of the legacy `data/paper_trades.json` into Postgres.

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
- **llm_provider.py**: Instantiates the LLM based on the `LLM_PROVIDER` environment variable. Supported values: `ollama` (Mistral via Ollama) and `deepseek` (DeepSeek Chat via `langchain_deepseek`).
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
4. **Result cache**: looks up `biosignalfoundry:analyze:<TICKER>` in Redis (keyed on the resolved ticker, so "Moderna" and "MRNA" share an entry). A hit is streamed back immediately.
5. **Daily budget** (`rate_limiter.check_and_consume_daily_budget`): only cache misses consume it. Over the cap returns 503. Redis errors fail open.
6. The request is forwarded to **`biosignalfoundry`** (`src/biosignalfoundry.py`) — a `deepagents` deep agent that acts as the supervisor — with a `StreamingProgressCallback` attached so tool starts reach the client as `progress` events
7. The supervisor delegates to **`financial_health_subagent`** (`src/agents/financial_health_agent.py`) via the `CompiledSubAgent` interface
8. The sub-agent calls **Agent Tools** (`src/agent_tools/financial_health_agent_tools.py`) to gather specific data points
9. Agent Tools call **Data Providers** (`src/data_providers/`) which hit external APIs and cache responses in **Redis**
10. The sub-agent returns a structured `FinancialHealthAgentOutput` to the supervisor
11. The supervisor interprets the financial health score and produces a final `BioSignalFoundryOutput` (BUY/SELL/HOLD/AVOID + confidence + reasoning), which is cached in Redis and sent as the `result` event

### Paper-trade path
`scripts/record_signal.py` calls the agent per ticker and upserts a `paper_trades` row stamped with `core.versioning.system_version()`. `scripts/evaluate_signals.py` later fills in the exit price and correctness. Both use `core.db.SessionLocal`.

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