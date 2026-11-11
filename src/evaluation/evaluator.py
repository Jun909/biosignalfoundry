"""Evaluate matured paper trades: price every signal at 7, 30 and 90 days.

Horizons count from the trade's ``entry_price_date`` (the day the entry price was
taken), not from ``signal_date``, so a signal recorded on a weekend is still
measured over a full 7/30/90 days.

For each matured (signal, horizon) without an evaluation row this fetches the
stock, XBI and IBB in a single download per ticker and stores the exit prices
*and* the entry prices from that same download. yfinance prices are adjusted for
splits and dividends as of the download, so an entry price recorded weeks ago is
not comparable with a fresh exit price; the re-fetched ``*_entry_price_adj`` are.

Safe to run late or repeatedly: existing evaluations are never touched, and a
horizon with no usable close yet is left pending for the next run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import Callable, Sequence

import structlog
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from src.core.db import SessionLocal
from src.evaluation.models import PaperTrade, PaperTradeEvaluation
from src.evaluation.price_loader import PriceMap, load_prices
from src.evaluation.watchlist import BENCHMARKS

logger = structlog.get_logger()

HORIZONS: tuple[int, ...] = (7, 30, 90)
# How many days after the target date to look for a trading day (weekends, holidays).
EXIT_LOOKAHEAD_DAYS = 5


@dataclass
class EvaluationReport:
    created: list[tuple[str, str, int]] = field(
        default_factory=list
    )  # label, ticker, h
    pending: list[tuple[str, str, int]] = field(default_factory=list)
    failed: list[tuple[str, str, int, str]] = field(default_factory=list)  # + error


def _price(value: float) -> Decimal:
    return Decimal(str(round(value, 4)))


def first_common_date(
    price_maps: Sequence[PriceMap], on_or_after: date, before: date
) -> date | None:
    """First day in ``[on_or_after, on_or_after + lookahead]`` present in every map
    and strictly before ``before`` (so today's unfinished session is never used)."""
    for offset in range(EXIT_LOOKAHEAD_DAYS + 1):
        d = on_or_after + timedelta(days=offset)
        if d >= before:
            return None
        if all(d in prices for prices in price_maps):
            return d
    return None


async def evaluate_matured(
    horizons: Sequence[int] = HORIZONS,
    batch: str | None = None,
    labels: Sequence[str] | None = None,
    today: date | None = None,
    session_factory=SessionLocal,
    price_fn: Callable[[str, date, date], PriceMap] = load_prices,
) -> EvaluationReport:
    today = today or date.today()
    report = EvaluationReport()

    async with session_factory() as session:
        stmt = select(PaperTrade).order_by(
            PaperTrade.ticker, PaperTrade.entry_price_date
        )
        if batch:
            stmt = stmt.where(PaperTrade.batch == batch)
        if labels:
            stmt = stmt.where(PaperTrade.version_label.in_(labels))
        trades = list((await session.scalars(stmt)).all())
        existing = {
            (row.paper_trade_id, row.horizon_days)
            for row in (
                await session.execute(
                    select(
                        PaperTradeEvaluation.paper_trade_id,
                        PaperTradeEvaluation.horizon_days,
                    )
                )
            ).all()
        }

    # (trade, horizon, target_date) still to do; skip horizons that cannot have a
    # close yet without downloading anything.
    todo: list[tuple[PaperTrade, int, date]] = []
    for trade in trades:
        for horizon in horizons:
            if (trade.id, horizon) in existing:
                continue
            target = trade.entry_price_date + timedelta(days=horizon)
            if target >= today:
                report.pending.append((trade.version_label, trade.ticker, horizon))
            else:
                todo.append((trade, horizon, target))
    if not todo:
        return report

    # One download per symbol covering every window it needs.
    def window(items: list[tuple[PaperTrade, int, date]]) -> tuple[date, date]:
        return (
            min(t.entry_price_date for t, _, _ in items),
            min(
                max(tg for _, _, tg in items) + timedelta(days=EXIT_LOOKAHEAD_DAYS),
                today,
            ),
        )

    benchmark_prices = {b: price_fn(b, *window(todo)) for b in BENCHMARKS}
    by_ticker: dict[str, list[tuple[PaperTrade, int, date]]] = {}
    for item in todo:
        by_ticker.setdefault(item[0].ticker, []).append(item)

    rows: list[dict] = []
    for ticker, items in by_ticker.items():
        try:
            stock_prices = price_fn(ticker, *window(items))
        except Exception as exc:  # network / provider errors
            for trade, horizon, _ in items:
                report.failed.append((trade.version_label, ticker, horizon, str(exc)))
            continue

        for trade, horizon, target in items:
            key = (trade.version_label, ticker, horizon)
            xbi, ibb = (benchmark_prices[b] for b in BENCHMARKS)
            maps = [stock_prices, xbi, ibb]
            entry_day = trade.entry_price_date
            if not all(entry_day in m for m in maps):
                report.failed.append(
                    (*key, f"No price on entry date {entry_day} for stock/XBI/IBB")
                )
                continue
            price_date = first_common_date(maps, target, today)
            if price_date is None:
                if target + timedelta(days=EXIT_LOOKAHEAD_DAYS) < today:
                    report.failed.append(
                        (*key, f"No common trading day on/after {target}")
                    )
                else:
                    report.pending.append(key)
                continue
            rows.append(
                dict(
                    paper_trade_id=trade.id,
                    horizon_days=horizon,
                    target_date=target,
                    price_date=price_date,
                    exit_price=_price(stock_prices[price_date]),
                    xbi_exit_price=_price(xbi[price_date]),
                    ibb_exit_price=_price(ibb[price_date]),
                    entry_price_adj=_price(stock_prices[entry_day]),
                    xbi_entry_price_adj=_price(xbi[entry_day]),
                    ibb_entry_price_adj=_price(ibb[entry_day]),
                    _key=key,
                )
            )

    if rows:
        async with session_factory() as session:
            for row in rows:
                key = row.pop("_key")
                result = await session.execute(
                    insert(PaperTradeEvaluation)
                    .values(**row)
                    .on_conflict_do_nothing(constraint="uq_evaluation_horizon")
                    .returning(PaperTradeEvaluation.id)
                )
                if result.first() is not None:
                    report.created.append(key)
            await session.commit()
    for label, ticker, horizon in report.created:
        logger.info(
            "evaluation recorded", version=label, ticker=ticker, horizon=horizon
        )
    return report
