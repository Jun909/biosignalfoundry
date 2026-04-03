# Architecture Overview

## Project Overview
BioSignalFoundry is an applied AI project focused on decision-making for biotech stocks. The system is designed to gather structured evidence from multiple data providers to answer questions like "Should I BUY, SELL, HOLD, or AVOID a given biotech stock?". The project emphasizes signals, reasoning, determinism, and auditability.

## Repository Structure

```
biosignalfoundry/
├── .gitignore                    # Git ignore rules
├── config.py                     # Centralized configuration management
├── llm_provider.py               # LLM provider setup (Ollama or DeepSeek, via LLM_PROVIDER env)
├── pyproject.toml                # Poetry dependencies and project config
├── poetry.lock                   # Locked dependency versions
├── README.md                     # Project documentation
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Docker services configuration (PostgreSQL, Redis)
├── app.py                        # FastAPI application entry point (exposes /analyze endpoint)
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
│   │   ├── alphavintage.py       # Stock price and technical analysis data
│   │   ├── finnhub.py            # Financial market data and company info
│   │   ├── fred.py               # Federal Reserve economic data
│   │   ├── sec_edgar.py          # SEC filings and corporate data
│   │   ├── openfda.py            # FDA drug and clinical data
│   │   ├── marketstack.py        # Market data provider
│   │   └── massive.py            # (Purpose TBD)
│   │
│   ├── core/                     # Core utilities and infrastructure
│   │   ├── redis_client.py       # Redis client for caching and state management
│   │   └── logging_config.py     # structlog configuration (JSON or coloured output)
│   │
│   ├── middleware/               # LangChain agent middleware
│   │   ├── __init__.py
│   │   └── logging_middleware.py # LoggingMiddleware: logs agent input/output and tool timing
│   │
│   ├── prompts/                  # Prompt templates for LLMs
│   │   ├── biosignalfoundry_prompt.py               # Main system prompt
│   │   └── financial_health_agent_prompt.py         # Financial health agent prompt
│   │
│
├── tests/                        # Test suite
│   └── __init__.py
│
├── docs/                         # Documentation
│   ├── architecture_docs/        # Architecture and design documentation
│   │   └── architecture_overview.md     # This file - overall system architecture
│   │
│   └── api_reference/            # External API references
│       ├── alphavintage_api.md
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
FastAPI application entry point. Exposes a single `POST /analyze` endpoint that accepts a natural-language query, invokes the `biosignalfoundry` deep agent, and returns a structured `BioSignalFoundryOutput` (ticker, decision, confidence, reasoning).

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
- **alphavintage.py**: Stock prices, moving averages, technical indicators
- **finnhub.py**: Company fundamentals, earnings, market cap
- **fred.py**: Federal Reserve economic data (inflation, interest rates, etc.)
- **sec_edgar.py**: SEC filings (10-K, 10-Q, 8-K)
- **openfda.py**: FDA drug approvals, clinical trial data
- **marketstack.py**: General market data
- **massive.py**: (Purpose TBD)

### **src/core/**
Common utilities and infrastructure:
- **redis_client.py**: Redis connection management, caching layer for API responses
- **logging_config.py**: `setup_logging()` configures structlog for the whole application. Outputs human-readable coloured logs in development and JSON lines in production (controlled by the `ENV` environment variable).

### **src/middleware/**
LangChain `AgentMiddleware` implementations applied at agent construction time:
- **logging_middleware.py**: `LoggingMiddleware` — logs the agent's input message, every model decision (tool calls or final answer), each tool execution with elapsed time, and the final agent response. Applied to both `biosignalfoundry` and `financial_health_agent`.

### **src/prompts/**
LLM prompt templates:
- **biosignalfoundry_prompt.py**: Master system prompt defining BioSignalFoundry's decision-making framework
- **financial_health_agent_prompt.py**: Specialized prompt for the financial health agent

### **docs/**
Project documentation split into two sections:
- **architecture_docs/**: Design and system architecture
- **api_reference/**: External API documentation and examples

### **tests/**
Unit and integration tests (currently minimal structure)

### **Configuration Files**
- **config.py**: Centralized app configuration. Currently defines Redis connection settings (`REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`), per-provider cache TTLs (`REDIS_CACHE_TTL_SECONDS_ALPHAVANTAGE`, `REDIS_CACHE_TTL_SECONDS_MARKETSTACK`), and reads `ALPHAVANTAGE_API_KEY` / `FINNHUB_API_KEY` from the environment.
- **llm_provider.py**: Instantiates the LLM based on the `LLM_PROVIDER` environment variable. Supported values: `ollama` (Mistral via Ollama) and `deepseek` (DeepSeek Chat via `langchain_deepseek`).
- **pyproject.toml**: Project metadata, dependencies, poetry configuration

### **Docker**
- **Dockerfile**: Container image for the application
- **docker-compose.yml**: Orchestration for PostgreSQL (data storage) and Redis (caching)

### **ui/** - User Interface
The `ui` folder contains the frontend code for the BioSignalFoundry project. It is built using React framework

## Data Flow

### Request path
1. `app.py` (FastAPI) receives a `POST /analyze` request with a natural-language `user_input`
2. The request is forwarded to **`biosignalfoundry`** (`src/biosignalfoundry.py`) — a `deepagents` deep agent that acts as the supervisor
3. The supervisor delegates to **`financial_health_subagent`** (`src/agents/financial_health_agent.py`) via the `CompiledSubAgent` interface
4. The sub-agent calls **Agent Tools** (`src/agent_tools/financial_health_agent_tools.py`) to gather specific data points
5. Agent Tools call **Data Providers** (`src/data_providers/`) which hit external APIs and cache responses in **Redis**
6. The sub-agent returns a structured `FinancialHealthAgentOutput` to the supervisor
7. The supervisor interprets the financial health score and produces a final `BioSignalFoundryOutput` (BUY/SELL/HOLD/AVOID + confidence + reasoning)

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
- Backtesting