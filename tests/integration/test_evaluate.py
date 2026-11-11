"""evaluate_matured against a real Postgres with a fake price source (no network)."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import version_registry as vr
from src.evaluation.evaluator import evaluate_matured, first_common_date
from src.evaluation.models import PaperTrade, PaperTradeEvaluation
from src.evaluation.repository import upsert_signal
from src.evaluation.types import DecisionLabel

ENTRY = date(2026, 11, 6)  # a Friday


@pytest.fixture
def session_factory(engine):
    return lambda: AsyncSession(engine, expire_on_commit=False)


def make_prices(base: float, drift: float = 1.0, start=ENTRY, days=120):
    """Business-day closes starting at ``start`` (weekends missing)."""
    prices, d, i = {}, start, 0
    while i < days:
        if d.weekday() < 5:
            prices[d] = base + drift * i
            i += 1
        d += timedelta(days=1)
    return prices


PRICES = {
    "MRNA": make_prices(50),
    "XBI": make_prices(100, 0.5),
    "IBB": make_prices(140, 0.5),
}


def price_fn(ticker, start, end):
    return {d: p for d, p in PRICES.get(ticker, {}).items() if start <= d <= end}


async def add_trade(session_factory, ticker="MRNA", label="v1.0", batch="b1"):
    async with session_factory() as session:
        await vr.register_version(session, label)
        await upsert_signal(
            session,
            dict(
                batch=batch,
                version_label=label,
                ticker=ticker,
                signal_date=ENTRY,
                decision=DecisionLabel.BUY,
                confidence=Decimal("0.8"),
                rationale="r",
                agent_output={},
                entry_price_date=ENTRY,
                entry_price=Decimal("50"),
                xbi_entry_price=Decimal("100"),
                ibb_entry_price=Decimal("140"),
            ),
        )
        await session.commit()


async def evaluations(session_factory):
    async with session_factory() as session:
        return list(
            (
                await session.scalars(
                    select(PaperTradeEvaluation).order_by(
                        PaperTradeEvaluation.horizon_days
                    )
                )
            ).all()
        )


def run(session_factory, today, **kw):
    return evaluate_matured(
        today=today, session_factory=session_factory, price_fn=price_fn, **kw
    )


async def test_only_matured_horizons_are_evaluated_from_entry_price_date(
    session_factory,
):
    await add_trade(session_factory)

    report = await run(session_factory, ENTRY + timedelta(days=8))

    assert [h for _, _, h in report.created] == [7]
    assert sorted(h for _, _, h in report.pending) == [30, 90]
    (ev,) = await evaluations(session_factory)
    assert ev.target_date == ENTRY + timedelta(days=7)  # Friday 11-13
    assert ev.price_date == date(2026, 11, 13)
    assert ev.exit_price == Decimal("55.0000")  # 5 business days after entry
    assert ev.entry_price_adj == Decimal("50.0000")
    assert ev.xbi_exit_price == Decimal("102.5000")
    assert ev.ibb_entry_price_adj == Decimal("140.0000")


async def test_target_on_weekend_uses_next_trading_day(session_factory):
    await add_trade(session_factory)
    # 30 days after Fri 11-06 is Sun 12-06 -> priced on Mon 12-07
    await run(session_factory, ENTRY + timedelta(days=40))
    ev = next(e for e in await evaluations(session_factory) if e.horizon_days == 30)
    assert ev.target_date == date(2026, 12, 6)
    assert ev.price_date == date(2026, 12, 7)


async def test_rerun_is_idempotent_and_fills_in_later_horizons(session_factory):
    await add_trade(session_factory)
    await run(session_factory, ENTRY + timedelta(days=8))
    again = await run(session_factory, ENTRY + timedelta(days=8))
    assert not again.created

    later = await run(session_factory, ENTRY + timedelta(days=100))
    assert sorted(h for _, _, h in later.created) == [30, 90]
    assert len(await evaluations(session_factory)) == 3


async def test_todays_unfinished_session_is_never_used(session_factory):
    await add_trade(session_factory)
    # target (Fri 11-13) == today: the close is not final, so stay pending
    report = await run(session_factory, ENTRY + timedelta(days=7))
    assert not report.created and (("v1.0", "MRNA", 7) in report.pending)


async def test_missing_prices_fail_without_blocking_others(session_factory):
    await add_trade(session_factory, "MRNA")
    await add_trade(session_factory, "ZZZZ")
    report = await run(session_factory, ENTRY + timedelta(days=8))
    assert [(t, h) for _, t, h in report.created] == [("MRNA", 7)]
    assert report.failed[0][:3] == ("v1.0", "ZZZZ", 7)


async def test_filters_by_batch_and_horizon(session_factory):
    await add_trade(session_factory, batch="b1")
    await add_trade(session_factory, batch="b2")
    report = await run(
        session_factory, ENTRY + timedelta(days=100), batch="b2", horizons=[30]
    )
    assert len(report.created) == 1
    async with session_factory() as session:
        trade_batch = await session.scalar(
            select(PaperTrade.batch)
            .join(PaperTradeEvaluation)
            .where(PaperTradeEvaluation.horizon_days == 30)
        )
        assert trade_batch == "b2"
        assert (
            await session.scalar(select(func.count()).select_from(PaperTradeEvaluation))
            == 1
        )


def test_first_common_date_skips_gaps_and_today():
    a = {date(2026, 12, 7): 1.0}
    assert first_common_date([a, a], date(2026, 12, 6), date(2026, 12, 20)) == date(
        2026, 12, 7
    )
    assert first_common_date([a, a], date(2026, 12, 6), date(2026, 12, 7)) is None
    assert first_common_date([a, {}], date(2026, 12, 6), date(2026, 12, 20)) is None


async def test_load_return_rows_reads_the_view_and_filters(session_factory):
    from src.evaluation.repository import count_trades, load_return_rows

    await add_trade(session_factory, batch="b1")
    await add_trade(session_factory, batch="b2")
    await run(session_factory, ENTRY + timedelta(days=40))

    async with session_factory() as session:
        rows = await load_return_rows(session, batch="b1", horizons=[7])
        assert len(rows) == 1
        r = rows[0]
        assert r.decision is DecisionLabel.BUY and r.confidence == pytest.approx(0.8)
        assert r.forward_return == pytest.approx(55 / 50 - 1)
        assert r.xbi_return == pytest.approx(102.5 / 100 - 1)
        assert len(await load_return_rows(session)) == 4  # 2 trades x horizons 7 and 30
        assert await count_trades(session, batch="b1") == {"v1.0": 1}
