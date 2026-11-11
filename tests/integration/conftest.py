import os
from pathlib import Path

import asyncpg
import pytest
import pytest_asyncio
from dotenv import dotenv_values
from redis import ConnectionError as RedisConnectionError
from sqlalchemy import text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from alembic import command
from alembic.config import Config
from src.core.redis_client import redis_client

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def require_redis():
    """Skip any integration test when Redis is not reachable."""
    try:
        redis_client.ping()
    except RedisConnectionError:
        pytest.skip(
            "Redis not available — start one with: docker run -p 6379:6379 redis:7"
        )


@pytest.fixture
def tracked_keys():
    """Yields a mutable list. Every key appended to it is deleted after the test."""
    keys: list[str] = []
    yield keys
    if keys:
        redis_client.delete(*keys)


# ---------------------------------------------------------------------------
# Postgres: a dedicated `<POSTGRES_DB>_test` database, migrated with Alembic and
# truncated after every test, so tests never touch real data. The URL comes from
# TEST_DATABASE_URL if set, otherwise from POSTGRES_* in .env. Tests are skipped
# when Postgres is unreachable (start it with: docker-compose up postgres).
# ---------------------------------------------------------------------------
def _test_database_url() -> URL:
    explicit = os.environ.get("TEST_DATABASE_URL")
    if explicit:
        return make_url(explicit)
    env = dotenv_values(PROJECT_ROOT / ".env")
    user, password, db = (
        env.get(k) for k in ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB")
    )
    if not (user and password and db):
        pytest.skip(
            "No Postgres credentials: set TEST_DATABASE_URL or POSTGRES_* in .env"
        )
    return URL.create(
        "postgresql+asyncpg",
        username=user,
        password=password,
        host=env.get("POSTGRES_HOST", "localhost"),
        port=int(env.get("POSTGRES_PORT", 5432)),
        database=f"{db}_test",
    )


async def _ensure_database(url: URL) -> None:
    admin = await asyncpg.connect(
        user=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        database="postgres",
    )
    try:
        exists = await admin.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", url.database
        )
        if not exists:
            await admin.execute(f'CREATE DATABASE "{url.database}"')
    finally:
        await admin.close()


@pytest.fixture(scope="session")
def test_db_url() -> URL:
    import asyncio

    url = _test_database_url()
    try:
        asyncio.run(_ensure_database(url))
    except (OSError, asyncpg.PostgresError) as exc:
        pytest.skip(
            f"Postgres not available — start it with: docker-compose up postgres ({exc})"
        )

    cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    cfg.attributes["database_url"] = url.render_as_string(hide_password=False)
    command.upgrade(cfg, "head")
    return url


@pytest_asyncio.fixture
async def engine(test_db_url):
    engine = create_async_engine(test_db_url, poolclass=NullPool)
    yield engine
    async with engine.begin() as conn:
        await conn.execute(
            text("TRUNCATE paper_trade_evaluations, paper_trades, system_versions")
        )
    await engine.dispose()
