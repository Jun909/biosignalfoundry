# AGENTS.md

## Project
BioSignalFoundry: a LangChain/deepagents system that answers BUY/SELL/HOLD/AVOID
for a biotech stock from deterministic signal extraction + LLM reasoning.
FastAPI backend (`app.py`) + React/TS frontend (`ui/`). Not a trading bot.
Full architecture: `docs/architecture_docs/architecture_overview.md`.
Project philosophy and roadmap: `README.md`.

## Setup
- Python deps: `uv sync --locked --extra dev` (uv, not poetry/pip — requires 3.11–3.14)
- Frontend deps: `cd ui && npm install`
- Local infra: `docker-compose up` (Postgres + Redis; Redis is required for caching,
  Postgres stores paper trades)
- Database: `uv run alembic upgrade head` applies migrations. After changing
  `src/evaluation/models.py`, generate one with
  `uv run alembic revision --autogenerate -m "..."` and review it before committing
- Secrets in `.env` (gitignored, never commit): `ALPHAVANTAGE_API_KEY`, `FINNHUB_API_KEY`,
  `FRED_API_KEY`, `MARKETSTACK_API_KEY`, `MASSIVE_API_KEY`, `OPENFDA_API_KEY`,
  `OPENAI_API_KEY`/`DEEPSEEK_API_KEY`, `LLM_PROVIDER`, `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB`, `REDIS_*`, `ALLOWED_ORIGINS`

## Run
- Backend: `uv run uvicorn app:app --reload`
- Frontend: `npm run dev` (Vite; must match `ALLOWED_ORIGINS` for CORS)

## Test (mirrors `.github/workflows/test.yml` — run these, not ad hoc invocations)
- `uv lock --check` — run after any `pyproject.toml` change
- `uv run pytest tests/unit/ -v` — mocked, no live services
- `uv run pytest tests/integration/ -v` — needs Redis and Postgres running (DB tests use a
  separate `<POSTGRES_DB>_test` database, or `TEST_DATABASE_URL`, and skip if Postgres is down)
- Frontend: `npm run lint`, `npm run build`, `npm run test` (Vitest + React Testing Library;
  `npm run test:watch` for local dev)

## Code style
- `black` + `isort` are project deps (`uv run black .`, `uv run isort .`) — not
  currently enforced in CI, but keep code formatted with them
- Use `structlog` (`src/core/logging_config.py`) for logging, not `print`
- Structured I/O via Pydantic models, following the `BioSignalFoundryOutput` pattern

## Test-writing notes
- `tests/conftest.py` stubs `llm_provider` and `deepagents` via `sys.modules`
  *before* collection so `import app` / `import src.*` don't blow up on missing
  env vars. Don't re-stub these inside individual test files.
- `tests/unit/` = no network/live services. `tests/integration/` = real Redis and Postgres,
  external APIs/LLM still mocked.

## Known rough edges (don't "fix" these without checking first)
- `src/evaluation/` deliberately does NOT do classic historical backtesting —
  read the README's "On Backtesting" section before touching it; paper trading
  (`scripts/record_signal.py` + `scripts/evaluate_signals.py`) is the intended
  evaluation method instead.
- Paper trades are unique per `(ticker, signal_date, system_version)`; `record_signal.py`
  upserts, so a same-day re-run replaces that day's signal and clears its evaluation.

## Commits/PRs
- Squash-merged, plain imperative titles (see `git log`), no conventional-commits
  prefix enforced.
