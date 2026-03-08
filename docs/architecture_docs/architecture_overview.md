# Architecture Overview

## Project Overview
Biothrone is an applied AI project focused on decision-making for biotech stocks. The system is designed to gather structured evidence from multiple data providers to answer questions like "Should I BUY, SELL, HOLD, or AVOID a given biotech stock?". The project emphasizes signals, reasoning, determinism, and auditability.

## Repository Structure

```
biothrone/
├── .env                          # Environment variables (secrets, API keys)
├── .gitignore                    # Git ignore rules
├── config.py                     # Centralized configuration management
├── llm_provider.py               # LLM provider setup and configuration
├── pyproject.toml                # Poetry dependencies and project config
├── poetry.lock                   # Locked dependency versions
├── README.md                     # Project documentation
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Docker services configuration (PostgreSQL, Redis)
│
├── src/                          # Main application source code
│   ├── __init__.py
│   ├── app.py                    # Application entry point (main execution)
│   │
│   ├── agents/                   # Agent implementations for decision-making
│   │   └── financial_health_agent.py      # Agent that analyzes financial health
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
│   │   └── massive.py            # (Describe when known)
│   │
│   ├── core/                     # Core utilities and infrastructure
│   │   └── redis_client.py       # Redis client for caching and state management
│   │
│   ├── prompts/                  # Prompt templates for LLMs
│   │   ├── biothrone_prompt.py                      # Main system prompt
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
└── ui/                           # User interface (frontend, TBD)
```

## Directory Descriptions

### **src/** - Main Application Source
The core application code organized by functional domain.

### **src/agents/**
Contains agent implementations that orchestrate decision-making pipelines. Each agent uses tools from `agent_tools/` to gather and analyze data.
- `financial_health_agent.py`: Main agent for analyzing biotech company financial health

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

### **src/prompts/**
LLM prompt templates:
- **biothrone_prompt.py**: Master system prompt defining Biothrone's decision-making framework
- **financial_health_agent_prompt.py**: Specialized prompt for the financial health agent

### **docs/**
Project documentation split into two sections:
- **architecture_docs/**: Design and system architecture
- **api_reference/**: External API documentation and examples

### **tests/**
Unit and integration tests (currently minimal structure)

### **Configuration Files**
- **config.py**: Centralized app configuration (API endpoints, cache settings, etc.)
- **pyproject.toml**: Project metadata, dependencies, poetry configuration
- **.env**: Runtime environment variables (API keys, secrets) - not in git

### **Docker**
- **Dockerfile**: Container image for the application
- **docker-compose.yml**: Orchestration for PostgreSQL (data storage) and Redis (caching)

## Data Flow

1. **Agents** (`src/agents/`) initiate analysis
2. **Agents** call **Agent Tools** (`src/agent_tools/`) to gather specific insights
3. **Agent Tools** delegate to **Data Providers** (`src/data_providers/`)
4. **Data Providers** call external APIs and cache results in **Redis** (`src/core/redis_client.py`)
5. Results are aggregated and processed using **LLM Prompts** (`src/prompts/`)
6. Final decision (BUY/SELL/HOLD/AVOID) is produced

Visual example:
```
AlphaVantage SDK
      ↓
BaseClient (_call) # implement logging here for silent failures
      ↓
API wrapper (cache) # should move caching into BaseClient(?)
      ↓
Tool processing
      ↓
Agent tool
```

## Future Directions
- Additional agent types and decision pipelines
- Enhanced auditability and reasoning logs
- Database integration for historical decisions
- UI/Dashboard for decision visualization
