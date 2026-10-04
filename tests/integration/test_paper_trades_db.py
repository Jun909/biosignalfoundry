"""
Integration tests for the paper_trades table.

These run against a real Postgres, in a dedicated `<POSTGRES_DB>_test` database
(created on demand and migrated with Alembic), so they never touch real data.
The test database URL comes from TEST_DATABASE_URL if set, otherwise it is built
from POSTGRES_* in .env. Tests are skipped when Postgres is unreachable.

Run with:  pytest tests/integration/test_paper_trades_db.py
Requires:  docker-compose up postgres
"""

import os
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path

import asyncpg
import pytest
import pytest_asyncio
from dotenv import dotenv_values
from sqlalchemy import func, select, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from src.core.db import Base
from src.evaluation.models import PaperTrade
from src.evaluation.repository import upsert_signal
from src.evaluation.types import DecisionLabel

PROJECT_ROOT = Path(__file__).resolve().parents[2]


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
        await conn.execute(text("TRUNCATE paper_trades"))
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


def make_values(**overrides) -> dict:
    values = dict(
        system_version="v1.0",
        ticker="MRNA",
        signal_date=date(2026, 5, 25),
        exit_date=date(2026, 6, 1),
        holding_days=7,
        decision=DecisionLabel.BUY,
        confidence=Decimal("0.75"),
        rationale="first rationale",
        entry_price=Decimal("46.8800"),
    )
    values.update(overrides)
    return values


async def count_rows(session: AsyncSession) -> int:
    return await session.scalar(select(func.count()).select_from(PaperTrade))


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
async def test_migrations_match_models(engine):
    """The Alembic migrations produce exactly the schema the models describe."""

    def diff(sync_conn):
        return compare_metadata(MigrationContext.configure(sync_conn), Base.metadata)

    async with engine.connect() as conn:
        assert await conn.run_sync(diff) == []


async def test_insert_roundtrip_uses_uuid_and_exact_decimals(session):
    session.add(PaperTrade(**make_values()))
    await session.commit()

    row = (await session.scalars(select(PaperTrade))).one()
    assert isinstance(row.id, uuid.UUID)
    assert row.entry_price == Decimal("46.8800")
    assert row.confidence == Decimal("0.7500")
    assert row.decision is DecisionLabel.BUY
    assert row.recorded_at is not None
    assert row.exit_price is None and row.evaluated_at is None


# ---------------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------------
async def test_duplicate_ticker_day_version_is_rejected(session):
    session.add(PaperTrade(**make_values()))
    await session.commit()

    session.add(PaperTrade(**make_values(rationale="duplicate")))
    with pytest.raises(IntegrityError):
        await session.commit()


@pytest.mark.parametrize(
    "overrides",
    [
        {"confidence": Decimal("1.5")},
        {"confidence": Decimal("-0.1")},
        {"holding_days": 0},
    ],
)
async def test_check_constraints_reject_bad_values(session, overrides):
    session.add(PaperTrade(**make_values(**overrides)))
    with pytest.raises(IntegrityError):
        await session.commit()


# ---------------------------------------------------------------------------
# upsert_signal — the same-day re-run behaviour
# ---------------------------------------------------------------------------
async def test_same_day_rerun_updates_instead_of_duplicating(session):
    assert await upsert_signal(session, make_values()) is True
    await session.commit()

    second = make_values(
        decision=DecisionLabel.SELL,
        confidence=Decimal("0.55"),
        rationale="second rationale",
        entry_price=Decimal("47.1000"),
        holding_days=14,
        exit_date=date(2026, 6, 8),
    )
    assert await upsert_signal(session, second) is False
    await session.commit()

    assert await count_rows(session) == 1
    row = (await session.scalars(select(PaperTrade))).one()
    assert row.decision is DecisionLabel.SELL
    assert row.confidence == Decimal("0.5500")
    assert row.rationale == "second rationale"
    assert row.entry_price == Decimal("47.1000")
    assert row.holding_days == 14 and row.exit_date == date(2026, 6, 8)


async def test_rerun_clears_previous_evaluation(session):
    await upsert_signal(session, make_values())
    await session.commit()

    row = (await session.scalars(select(PaperTrade))).one()
    row.exit_price = Decimal("50.0000")
    row.forward_return = Decimal("0.066553")
    row.is_correct = True
    row.evaluated_at = func.now()
    await session.commit()

    await upsert_signal(session, make_values(rationale="re-recorded"))
    await session.commit()
    await session.refresh(row)

    assert row.exit_price is None
    assert row.forward_return is None
    assert row.is_correct is None
    assert row.evaluated_at is None


@pytest.mark.parametrize(
    "overrides",
    [
        {"ticker": "GILD"},
        {"signal_date": date(2026, 6, 1)},
        {"system_version": "v2.0"},
    ],
)
async def test_different_ticker_day_or_version_creates_new_row(session, overrides):
    await upsert_signal(session, make_values())
    assert await upsert_signal(session, make_values(**overrides)) is True
    await session.commit()

    assert await count_rows(session) == 2
