"""
Integration tests for the evaluation tables (system_versions, paper_trades,
paper_trade_evaluations).

These run against a real Postgres in a dedicated test database (see the
fixtures in conftest.py), so they never touch real data. Tests are skipped when
Postgres is unreachable.

Run with:  pytest tests/integration/test_paper_trades_db.py
Requires:  docker-compose up postgres
"""

import uuid
from datetime import date
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from src.core import version_registry as vr
from src.core.db import Base
from src.evaluation.models import PaperTrade, PaperTradeEvaluation, SystemVersion
from src.evaluation.repository import upsert_signal
from src.evaluation.types import DecisionLabel


@pytest_asyncio.fixture
async def session(engine):
    async with AsyncSession(engine, expire_on_commit=False) as session:
        # signals reference a registered version
        for label in ("v1.0", "v2.0"):
            session.add(
                SystemVersion(label=label, description=f"test {label}", config={})
            )
        await session.commit()
        yield session


def make_values(**overrides) -> dict:
    values = dict(
        batch="2026-05-a",
        version_label="v1.0",
        ticker="MRNA",
        signal_date=date(2026, 5, 25),
        decision=DecisionLabel.BUY,
        confidence=Decimal("0.75"),
        rationale="first rationale",
        agent_output={"financial_health": {"score": 4}},
        entry_price_date=date(2026, 5, 22),
        entry_price=Decimal("46.8800"),
        xbi_entry_price=Decimal("90.1000"),
        ibb_entry_price=Decimal("140.2500"),
    )
    values.update(overrides)
    return values


def make_evaluation(trade_id, **overrides) -> PaperTradeEvaluation:
    values = dict(
        paper_trade_id=trade_id,
        horizon_days=7,
        target_date=date(2026, 6, 1),
        price_date=date(2026, 6, 1),
        exit_price=Decimal("50.0000"),
        xbi_exit_price=Decimal("91.0000"),
        ibb_exit_price=Decimal("141.0000"),
        entry_price_adj=Decimal("40.0000"),
        xbi_entry_price_adj=Decimal("90.0000"),
        ibb_entry_price_adj=Decimal("140.0000"),
    )
    values.update(overrides)
    return PaperTradeEvaluation(**values)


async def count_rows(session: AsyncSession, model=PaperTrade) -> int:
    return await session.scalar(select(func.count()).select_from(model))


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
async def test_migrations_match_models(engine):
    """The Alembic migrations produce exactly the schema the models describe."""

    def diff(sync_conn):
        return compare_metadata(MigrationContext.configure(sync_conn), Base.metadata)

    async with engine.connect() as conn:
        assert await conn.run_sync(diff) == []


async def test_insert_roundtrip_uses_uuid_decimals_and_json(session):
    session.add(PaperTrade(**make_values()))
    await session.commit()

    row = (await session.scalars(select(PaperTrade))).one()
    assert isinstance(row.id, uuid.UUID)
    assert row.entry_price == Decimal("46.8800")
    assert row.xbi_entry_price == Decimal("90.1000")
    assert row.confidence == Decimal("0.7500")
    assert row.decision is DecisionLabel.BUY
    assert row.agent_output == {"financial_health": {"score": 4}}
    assert row.recorded_at is not None


# ---------------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------------
async def test_duplicate_batch_version_ticker_is_rejected(session):
    session.add(PaperTrade(**make_values()))
    await session.commit()

    session.add(PaperTrade(**make_values(rationale="duplicate")))
    with pytest.raises(IntegrityError):
        await session.commit()


@pytest.mark.parametrize("confidence", [Decimal("1.5"), Decimal("-0.1")])
async def test_confidence_out_of_range_is_rejected(session, confidence):
    session.add(PaperTrade(**make_values(confidence=confidence)))
    with pytest.raises(IntegrityError):
        await session.commit()


async def test_unregistered_version_is_rejected(session):
    session.add(PaperTrade(**make_values(version_label="v9.9")))
    with pytest.raises(IntegrityError):
        await session.commit()


async def test_duplicate_horizon_for_a_trade_is_rejected(session):
    session.add(PaperTrade(**make_values()))
    await session.commit()
    trade = (await session.scalars(select(PaperTrade))).one()

    session.add(make_evaluation(trade.id))
    await session.commit()
    session.add(make_evaluation(trade.id))
    with pytest.raises(IntegrityError):
        await session.commit()


async def test_non_positive_horizon_is_rejected(session):
    session.add(PaperTrade(**make_values()))
    await session.commit()
    trade = (await session.scalars(select(PaperTrade))).one()

    session.add(make_evaluation(trade.id, horizon_days=0))
    with pytest.raises(IntegrityError):
        await session.commit()


async def test_trade_can_have_one_evaluation_per_horizon(session):
    session.add(PaperTrade(**make_values()))
    await session.commit()
    trade = (await session.scalars(select(PaperTrade))).one()

    session.add_all([make_evaluation(trade.id, horizon_days=h) for h in (7, 30, 90)])
    await session.commit()

    assert await count_rows(session, PaperTradeEvaluation) == 3


# ---------------------------------------------------------------------------
# upsert_signal — re-running the same batch/version/ticker
# ---------------------------------------------------------------------------
async def test_rerun_updates_instead_of_duplicating(session):
    assert await upsert_signal(session, make_values()) is True
    await session.commit()

    second = make_values(
        decision=DecisionLabel.SELL,
        confidence=Decimal("0.55"),
        rationale="second rationale",
        agent_output={"financial_health": {"score": 2}},
        entry_price=Decimal("47.1000"),
    )
    assert await upsert_signal(session, second) is False
    await session.commit()

    assert await count_rows(session) == 1
    row = (await session.scalars(select(PaperTrade))).one()
    assert row.decision is DecisionLabel.SELL
    assert row.confidence == Decimal("0.5500")
    assert row.rationale == "second rationale"
    assert row.agent_output == {"financial_health": {"score": 2}}
    assert row.entry_price == Decimal("47.1000")


async def test_rerun_deletes_previous_evaluations(session):
    await upsert_signal(session, make_values())
    await session.commit()
    trade = (await session.scalars(select(PaperTrade))).one()
    session.add(make_evaluation(trade.id))
    await session.commit()

    await upsert_signal(session, make_values(rationale="re-recorded"))
    await session.commit()

    assert await count_rows(session) == 1
    assert await count_rows(session, PaperTradeEvaluation) == 0


@pytest.mark.parametrize(
    "overrides",
    [
        {"ticker": "GILD"},
        {"batch": "2026-06-a"},
        {"version_label": "v2.0"},
    ],
)
async def test_different_ticker_batch_or_version_creates_new_row(session, overrides):
    await upsert_signal(session, make_values())
    assert await upsert_signal(session, make_values(**overrides)) is True
    await session.commit()

    assert await count_rows(session) == 2


# ---------------------------------------------------------------------------
# paper_trade_returns view
# ---------------------------------------------------------------------------
async def test_returns_view_uses_adjusted_entry_prices(session):
    session.add(PaperTrade(**make_values()))
    await session.commit()
    trade = (await session.scalars(select(PaperTrade))).one()
    session.add(make_evaluation(trade.id))
    await session.commit()

    row = (
        (await session.execute(text("SELECT * FROM paper_trade_returns")))
        .mappings()
        .one()
    )
    # 50 / 40 - 1, not 50 / 46.88 - 1: the recorded entry price is ignored.
    assert row["forward_return"] == Decimal("0.25")
    assert row["xbi_return"] == pytest.approx(Decimal("91") / Decimal("90") - 1)
    assert row["excess_return_xbi"] == pytest.approx(
        Decimal("1.25") - Decimal("91") / Decimal("90")
    )
    assert row["version_label"] == "v1.0" and row["horizon_days"] == 7


async def test_returns_view_omits_unevaluated_trades(session):
    session.add(PaperTrade(**make_values()))
    await session.commit()

    rows = (await session.execute(text("SELECT * FROM paper_trade_returns"))).all()
    assert rows == []


# ---------------------------------------------------------------------------
# register_version against the real table
# ---------------------------------------------------------------------------
async def test_register_version_roundtrips_through_postgres(engine):
    async with AsyncSession(engine, expire_on_commit=False) as first:
        await vr.register_version(first, "v1.0")
        await first.commit()

    # A fresh session reads the JSONB back from the database, so equality below
    # proves the stored config really matches the in-code snapshot.
    async with AsyncSession(engine, expire_on_commit=False) as second:
        row = await vr.register_version(second, "v1.0")
        assert row.config == vr.get_version("v1.0").snapshot()
        assert await count_rows(second, SystemVersion) == 1


async def test_register_version_detects_drift_in_stored_row(engine):
    async with AsyncSession(engine, expire_on_commit=False) as session:
        row = await vr.register_version(session, "v1.0")
        row.config = {**row.config, "subagents": {}}
        await session.commit()

    async with AsyncSession(engine, expire_on_commit=False) as session:
        with pytest.raises(vr.VersionDrift):
            await vr.register_version(session, "v1.0")
