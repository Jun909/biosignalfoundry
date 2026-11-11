# AGENTS.md

## Project
BioSignalFoundry: a LangChain/deepagents system that answers BUY/SELL/HOLD/AVOID
for a biotech stock from deterministic signal extraction + LLM reasoning.
FastAPI backend (`app.py`) + React/TS frontend (`ui/`). Not a trading bot.
Full architecture: `docs/architecture_docs/architecture_overview.md`.
Project philosophy: `README.md`. Roadmap: `docs/ROADMAP.md`.

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
- Paper trades are unique per `(batch, version_label, ticker)`. Re-running a batch with
  `record_signal.py` skips signals already recorded; `--force` replaces them (upsert) and
  deletes their evaluations. A batch must keep one signal date, so start a new batch name
  on a new day.

## Versions: wiring a new agent, tool or version
Every change that alters what the system decides is a new **version** (`v1.0`, `v1.1`, ...).
Versions are defined in code in `src/core/version_registry.py` and compared by running them
in parallel paper-trading batches (see README "Evaluation"), so a version must stay
reproducible once it has trades.
- **Never edit in place** a prompt a registered version uses, or its `VERSIONS` entry. Prompts
  are pinned by hash: an edit raises `VersionDrift`, `build_agent` refuses to build (so the API
  won't start), and `register_version` refuses a changed config. Copy the prompt under a new
  name and register a new version instead.
- **New subagent** (always a new version):
  1. Tools in `src/agent_tools/`; agent in `src/agents/<name>_agent.py` exposing
     `build_<name>_subagent(llm, system_prompt)`.
  2. Prompt file in `src/prompts/`, plus a copy of the supervisor prompt under a new name
     (it must mention the new subagent). Register both in `PROMPTS` in `src/core/versioning.py`.
  3. Register the builder in `SUBAGENT_BUILDERS` in `src/biosignalfoundry.py` (the only list
     of subagents).
  4. Add a `VERSIONS` entry: `supervisor_prompt`, `subagents` (name → prompt name), `llm`,
     `prompt_hash`. Put a placeholder hash, run `uv run pytest tests/unit/test_version_registry.py`,
     and copy the real value from the `VersionDrift` message.
  5. Optionally add the tool/agent labels to `TOOL_LABELS` in `src/core/streaming_callback.py`.
  6. Update `docs/architecture_docs/architecture_overview.md`.
- **New or changed tool on an existing subagent:** a version selects subagents by name, not
  tools, so editing a subagent's tools changes every version that uses it from then on. To
  compare before and after, give the changed subagent a new name (e.g. `financial_health_v2`)
  with its own builder and prompt, and point the new version at it. Edit in place only for
  fixes that should apply to all versions.
- **Prompt, LLM or temperature change only:** a new `VERSIONS` entry (and a new prompt name if
  a prompt changed); no other code.
- The version registry records configuration and prompts, not tool code; `git_sha` on the
  `system_versions` row is the commit that first registered it.
- `DEFAULT_VERSION` is what the API serves. The `/analyze` cache key includes the version
  label, so changing it starts a fresh cache.

## Docs
- When you add or change a module in `src/core/`, an agent, a tool, a data provider, an
  endpoint, or a step in the `/analyze` request path, update
  `docs/architecture_docs/architecture_overview.md` in the same change.

## Commits/PRs
- Squash-merged, plain imperative titles (see `git log`), no conventional-commits
  prefix enforced.
