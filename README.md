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

The MVP is shipped. The system runs end-to-end: a user asks a question about a biotech stock and receives a structured investment decision with reasoning in real time.

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
* Persistent storage of decisions and signals (PostgreSQL + Alembic)
* Integration test suite and CI/CD pipeline
* Health and readiness endpoints

### Phase 2 — Signal Completeness
* Wire remaining subagents: clinical (OpenFDA), macro (FRED), sentiment (Finnhub)
* Paper trading loop: record decisions and track returns over time
* Data quality validation layer

### Phase 3 — Scalability
* Async task queue for agent execution (Celery + Redis)
* Circuit breakers and retry logic per data provider

### Phase 4 — Observability
* LLM tracing (LangSmith or Langfuse)
* Metrics and centralized log aggregation

### Phase 5 — ML Feedback Loop
* Outcome tracking: link paper trades to actual price outcomes
* Prompt versioning and A/B testing
* Fine-tuning on accumulated decision/outcome data

## Disclaimer
Nothing in this repository constitutes to financial advice or a recommendation to trade securities.

## Author
* GitHub: [@Jun909](https://github.com/Jun909)
* LinkedIn: [Jun Siang Pang](https://www.linkedin.com/in/jun-siang-pang-2640071b0/)