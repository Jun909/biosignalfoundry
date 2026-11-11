"""
record_batch against a real Postgres, with the agent and the price source faked
(no LLM, no network).
"""

import json
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain.messages import AIMessage, ToolMessage
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.biosignalfoundry import BioSignalFoundryOutput
from src.core import version_registry as vr
from src.evaluation.models import (PaperTrade, PaperTradeEvaluation,
                                   SystemVersion)
from src.evaluation.recorder import BatchError, record_batch
from src.evaluation.types import DecisionLabel

SIGNAL_DATE = date(2026, 11, 6)
PRICES = {
    "MRNA": 46.88,
    "GILD": 120.5,
    "XBI": 100.0,
    "IBB": 140.0,
}


@pytest.fixture
def session_factory(engine):
    return lambda: AsyncSession(engine, expire_on_commit=False)


@pytest.fixture
def two_versions(monkeypatch):
    """v1.0 plus an identical-config v1.1 so a batch has more than one version."""
    monkeypatch.setitem(vr.VERSIONS, "v1.1", vr.get_version("v1.0"))


def price_fn(ticker: str, start: date, end: date) -> dict:
    if ticker not in PRICES:
        return {}
    return {
        date(2026, 11, 5): PRICES[ticker] - 1,
        SIGNAL_DATE: PRICES[ticker],
    }


def structured(ticker: str, decision: str = "Buy", confidence: int = 80):
    return BioSignalFoundryOutput(
        ticker=ticker,
        decision=decision,
        confidence=confidence,
        reasoning=f"reasoning for {ticker}",
    )


def make_agent(decision: str = "Buy", fail_for: frozenset[str] = frozenset()):
    """A fake supervisor whose ainvoke mimics deepagents' result shape."""
    agent = MagicMock(name="agent")

    async def ainvoke(payload):
        ticker = payload["messages"][0].content.split()[-1]
        if ticker in fail_for:
            raise RuntimeError(f"agent blew up on {ticker}")
        return {
            "structured_response": structured(ticker, decision),
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "task",
                            "id": f"call-{ticker}",
                            "args": {
                                "subagent_type": "financial_health_agent",
                                "description": f"analyse {ticker}",
                            },
                        }
                    ],
                ),
                ToolMessage(
                    content=json.dumps({"score": 4}), tool_call_id=f"call-{ticker}"
                ),
            ],
        }

    agent.ainvoke = AsyncMock(side_effect=ainvoke)
    return agent


def run(session_factory, agents, **overrides):
    kwargs = dict(
        batch="test-1",
        labels=["v1.0"],
        tickers=["MRNA", "GILD"],
        signal_date=SIGNAL_DATE,
        session_factory=session_factory,
        agent_factory=lambda label: agents[label],
        price_fn=price_fn,
    )
    kwargs.update(overrides)
    return record_batch(**kwargs)


async def all_trades(session_factory) -> list[PaperTrade]:
    async with session_factory() as session:
        return list(
            (
                await session.scalars(
                    select(PaperTrade).order_by(
                        PaperTrade.version_label, PaperTrade.ticker
                    )
                )
            ).all()
        )


async def count(session_factory, model) -> int:
    async with session_factory() as session:
        return await session.scalar(select(func.count()).select_from(model))


async def test_records_every_version_and_ticker_with_shared_entry_prices(
    session_factory, two_versions
):
    agents = {"v1.0": make_agent(), "v1.1": make_agent()}

    report = await run(session_factory, agents, labels=["v1.0", "v1.1"])

    assert len(report.recorded) == 4 and not report.failed and not report.skipped
    trades = await all_trades(session_factory)
    assert [(t.version_label, t.ticker) for t in trades] == [
        ("v1.0", "GILD"),
        ("v1.0", "MRNA"),
        ("v1.1", "GILD"),
        ("v1.1", "MRNA"),
    ]
    # Versions of the same ticker share exactly the same entry prices.
    by_ticker = {}
    for t in trades:
        by_ticker.setdefault(t.ticker, set()).add(
            (t.entry_price_date, t.entry_price, t.xbi_entry_price, t.ibb_entry_price)
        )
    assert all(len(prices) == 1 for prices in by_ticker.values())
    mrna = next(t for t in trades if t.ticker == "MRNA")
    assert mrna.entry_price == Decimal("46.8800")
    assert mrna.xbi_entry_price == Decimal("100.0000")
    assert mrna.ibb_entry_price == Decimal("140.0000")
    assert mrna.entry_price_date == SIGNAL_DATE


async def test_stores_decision_confidence_and_agent_output(session_factory):
    await run(session_factory, {"v1.0": make_agent("Avoid")}, tickers=["MRNA"])

    (trade,) = await all_trades(session_factory)
    assert trade.decision is DecisionLabel.AVOID
    assert trade.confidence == Decimal("0.8000")
    assert trade.rationale == "reasoning for MRNA"
    assert trade.batch == "test-1" and trade.signal_date == SIGNAL_DATE
    assert trade.agent_output["supervisor"]["decision"] == "Avoid"
    assert trade.agent_output["subagents"] == [
        {
            "subagent": "financial_health_agent",
            "task": "analyse MRNA",
            "output": {"score": 4},
        }
    ]


async def test_registers_the_versions_it_records(session_factory, two_versions):
    agents = {"v1.0": make_agent(), "v1.1": make_agent()}
    await run(session_factory, agents, labels=["v1.0", "v1.1"], tickers=["MRNA"])

    async with session_factory() as session:
        labels = set((await session.scalars(select(SystemVersion.label))).all())
    assert labels == {"v1.0", "v1.1"}


async def test_rerun_skips_signals_already_recorded(session_factory):
    agent = make_agent()
    await run(session_factory, {"v1.0": agent})
    assert agent.ainvoke.await_count == 2

    report = await run(session_factory, {"v1.0": agent})

    assert agent.ainvoke.await_count == 2  # no new paid calls
    assert len(report.skipped) == 2 and not report.recorded
    assert await count(session_factory, PaperTrade) == 2


async def test_one_failing_signal_does_not_stop_the_batch_and_can_be_retried(
    session_factory,
):
    flaky = make_agent(fail_for=frozenset({"MRNA"}))
    report = await run(session_factory, {"v1.0": flaky})

    assert report.recorded == [("v1.0", "GILD")]
    assert [(f[0], f[1]) for f in report.failed] == [("v1.0", "MRNA")]
    assert "blew up" in report.failed[0][2]

    healthy = make_agent()
    retry = await run(session_factory, {"v1.0": healthy})

    assert retry.recorded == [("v1.0", "MRNA")]
    assert healthy.ainvoke.await_count == 1  # GILD was skipped, not re-run
    assert await count(session_factory, PaperTrade) == 2


async def test_ticker_without_prices_fails_without_calling_the_agent(session_factory):
    agent = make_agent()
    report = await run(session_factory, {"v1.0": agent}, tickers=["MRNA", "ZZZZ"])

    assert report.recorded == [("v1.0", "MRNA")]
    assert report.failed[0][:2] == ("v1.0", "ZZZZ")
    assert "No price data" in report.failed[0][2]
    assert agent.ainvoke.await_count == 1


async def test_missing_structured_response_is_a_failure(session_factory):
    agent = MagicMock()
    agent.ainvoke = AsyncMock(return_value={"messages": []})

    report = await run(session_factory, {"v1.0": agent}, tickers=["MRNA"])

    assert not report.recorded
    assert "structured response" in report.failed[0][2]
    assert await count(session_factory, PaperTrade) == 0


async def test_unknown_decision_label_is_a_failure(session_factory):
    report = await run(
        session_factory, {"v1.0": make_agent("Moonshot")}, tickers=["MRNA"]
    )
    assert "Unknown decision" in report.failed[0][2]
    assert await count(session_factory, PaperTrade) == 0


async def test_batch_with_signals_from_another_date_is_refused(session_factory):
    await run(session_factory, {"v1.0": make_agent()}, tickers=["MRNA"])

    agent = make_agent()
    with pytest.raises(BatchError, match="new batch name"):
        await run(
            session_factory,
            {"v1.0": agent},
            tickers=["GILD"],
            signal_date=date(2026, 11, 7),
        )
    agent.ainvoke.assert_not_awaited()


async def test_force_replaces_signals_and_deletes_their_evaluations(session_factory):
    await run(session_factory, {"v1.0": make_agent("Buy")}, tickers=["MRNA"])
    (trade,) = await all_trades(session_factory)
    async with session_factory() as session:
        session.add(
            PaperTradeEvaluation(
                paper_trade_id=trade.id,
                horizon_days=7,
                target_date=date(2026, 11, 13),
                price_date=date(2026, 11, 13),
                exit_price=Decimal("50"),
                xbi_exit_price=Decimal("101"),
                ibb_exit_price=Decimal("141"),
                entry_price_adj=Decimal("46.88"),
                xbi_entry_price_adj=Decimal("100"),
                ibb_entry_price_adj=Decimal("140"),
            )
        )
        await session.commit()

    report = await run(
        session_factory, {"v1.0": make_agent("Sell")}, tickers=["MRNA"], force=True
    )

    assert report.recorded == [("v1.0", "MRNA")]
    (replaced,) = await all_trades(session_factory)
    assert replaced.decision is DecisionLabel.SELL
    assert await count(session_factory, PaperTradeEvaluation) == 0


async def test_unbuildable_version_fails_before_anything_is_recorded(session_factory):
    def broken_factory(label):
        raise vr.VersionDrift("prompts changed")

    with pytest.raises(vr.VersionDrift):
        await run(session_factory, {}, agent_factory=broken_factory)

    assert await count(session_factory, PaperTrade) == 0
    assert await count(session_factory, SystemVersion) == 0


async def test_invalid_batch_name_is_rejected(session_factory):
    with pytest.raises(BatchError, match="Invalid batch name"):
        await run(session_factory, {"v1.0": make_agent()}, batch="bad name")


async def test_concurrent_run_records_the_same_signals(session_factory):
    report = await run(session_factory, {"v1.0": make_agent()}, concurrency=4)
    assert sorted(report.recorded) == [("v1.0", "GILD"), ("v1.0", "MRNA")]
    assert await count(session_factory, PaperTrade) == 2
