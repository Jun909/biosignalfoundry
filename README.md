# BioSignalFoundry - Biotech Stock Decision System (Early Stage)

This repository is the foundation of a long term applied AI project focused on biotech stocks decision making. The current codebase contains API wrappers that standardize data access across multiple financial, regulatory and macroeconomic data providers.

The end goal is to create a signal driven AI system that helps answer the question:

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

The repository currently provides **thin, standardized Python wrappers** around multiple public and freemium data providers. Each wrapper:

* Normalizes provider responses into a **JSON-friendly, structured format**
* Adds metadata such as provider name, endpoint, timestamp and ticker

Detailed, provider-specific request/response examples can be found in
[`docs/api_reference/`](docs/api_reference/)

Entire repo architecture can be found in
[`docs/architecture_docs/`](docs/architecture_docs/)

## Implemented Data Providers

* Alphavantage
* Finnhub
* FRED
* SEC via edgartools
* OpenFDA
* Marketstack
* Massive

At this stage, no **decision logic or models are applied yet**. The focus is correctness, consistency and extensibility of data access.

## Short-term goal (MVP)

The MVP will be intentionally minimal and opinionated.

## MVP Objectives

* Improve data quality for high impact sources (e.g. SEC filings, FDA data)
* Extract **explicit, structured signals** from raw data
* Build a simple, linear pipeline:

> Data Sources
>
> -> Signal Extraction
>
> -> Lightweight LLM Reasoning
>
> -> Decision Output

## MVP Output
For a selected biotech company, the system will return:

* **Decision**: BUY / SELL / HOLD / AVOID
* **Confidence**: numeric score (0-1)
* **Explanation**: short, structured reasoning

A minimal REACT UI will allow users to select a ticker and view the result.

## What this project is *NOT*

This project does **not** aim to:

* Predict short-term stock prices
* Replace financial financial advice
* Use reinforcement learning or black-box optimization

## On Backtesting

Traditional backtesting — replaying historical signal dates and evaluating decisions against past prices — is intentionally not implemented in this project. This is a deliberate design decision, not an oversight.

There are four compounding reasons why proper historical backtesting is not feasible here:

1. **Hallucination risk from date-parameterized tools.** Passing a specific historical date to agent tools and asking the LLM to restrict itself to data available on that date introduces hallucination risk. LLMs are unreliable at consistently honoring such constraints when reasoning over tool outputs.

2. **APIs do not support point-in-time historical data.** Several data providers used in this project (AlphaVantage, Finnhub) return the latest available data regardless of any date argument. There is no way to retrieve what the income statement or company profile looked like on an arbitrary past date through these APIs.

3. **LLM training data contamination.** Even if perfect point-in-time financial data were available, a general-purpose LLM has already seen news, filings, and market commentary about any historically significant biotech stock up to its training cutoff. The model cannot simulate the genuine uncertainty that existed on a past signal date — it has already seen how things turned out.

4. **Point-in-time financial databases are out of scope.** Services that correctly snapshot what financial data was publicly available on any given date (e.g. Bloomberg, Compustat) are expensive, proprietary, and not appropriate for an early-stage open project.

For these reasons, the evaluation strategy used here is **paper trading**: the agent makes a decision using current data, that decision is recorded with today's price as the entry point, and it is evaluated against real prices after the holding period elapses. This is honest, reproducible, and free of look-ahead bias.

## Planned Roadmap (Post-MVP)

The following items are **explicitly out of MVP scope** and will be implemented gradually after the MVP is validated:

* Paper trading simulations and signal logging
* Continuous improvement of scraping and data quality
* Architectural evolution (workflow vs swarm)
* Multi-agent reasoning (if justified by failure modes)
* Structured logging and observability
* LLM tracing (e.g Langfuse)
* CI/CD and automated testing
* Persistent storage of decisions and signals
* Optional RAG for large document corpora
* Optional model fine-tuning
* UI/UX iteration

The roadmap is deliberately staged to prevent premature over-engineering

## Disclaimer
Nothing in this repository constitutes to financial advice or a recommendation to trade securities.

## Author
* GitHub: [@Jun909](https://github.com/Jun909)
* LinkedIn: [Jun Siang Pang](https://www.linkedin.com/in/jun-siang-pang-2640071b0/)