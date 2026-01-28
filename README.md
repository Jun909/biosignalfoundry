# Biothrone - Biotech Stock Decision System (Early Stage)

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

## Planned Roadmap (Post-MVP)

The following items are **explicitly our of MVP scope** and will be implemented gradually after the MVP is validated:

* Backtesting against historical biotech events
* Paper trading simulations
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