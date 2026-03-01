# Architecture Overview

## Project Overview
Biothrone is an applied AI project focused on decision-making for biotech stocks. The system is designed to gather structured evidence from multiple data providers to answer questions like "Should I BUY, SELL, HOLD, or AVOID a given biotech stock?". The project emphasizes signals, reasoning, determinism, and auditability.

## Core Components

### 1. Data Providers
The `data_providers` module contains Python wrappers for various APIs. These wrappers normalize responses into JSON-friendly formats and add metadata. Implemented providers include:
- Alphavantage
- Finnhub
- FRED
- SEC Edgar
- OpenFDA
- Marketstack
- Massive

### 2. Agent Tools
The `agent_tools` module contains tools for specific decision-making pipelines:
- `clinical_pipeline_agent_tools.py`: Focuses on clinical trial data.
- `financial_health_agent_tools.py`: Analyzes financial health metrics.
- `macro_context_agent_tools.py`: Provides macroeconomic context.
- `market_sentiment_agent_tools.py`: Assesses market sentiment.

### 3. Core Utilities
The `core` module includes essential utilities like:
- `redis_client.py`: Manages Redis connections for caching and state management.

### 4. Application Entry Point
The `src/app.py` file serves as the main entry point for the application. (Currently empty.)

### 5. Configuration
- `config.py`: Centralized configuration management.
- `.env`: Environment variables for sensitive data.

### 6. Dockerized Services
The project uses Docker Compose to manage services:
- PostgreSQL for data storage.
- Redis for caching.

### 7. Documentation
API references for data providers are located in `docs/api_reference/`.

## Future Directions
- Decision logic and models.
- Multi-agent systems.
- Enhanced auditability features.