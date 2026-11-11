"""Record one paper-trading batch: run each version over the watchlist and store
the decisions with entry prices for the stock, XBI and IBB.

All versions in a batch share one signal date and one set of entry prices per
ticker, so they can be compared stock by stock. A failure on one signal is
reported and does not stop the batch; re-running the same batch skips signals
that are already recorded.
"""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Callable, Sequence

import structlog
from langchain.messages import HumanMessage, ToolMessage
from sqlalchemy import select

from src.biosignalfoundry import BioSignalFoundryOutput
from src.biosignalfoundry import build_agent as default_build_agent
from src.core.db import SessionLocal
from src.core.subagent_capture import capture_subagent_outputs
from src.core.version_registry import register_version
from src.evaluation.models import PaperTrade
from src.evaluation.price_loader import (PriceMap, latest_common_date,
                                         load_prices)
from src.evaluation.repository import upsert_signal
from src.evaluation.types import DecisionLabel
from src.evaluation.watchlist import BENCHMARKS

logger = structlog.get_logger()

ENTRY_LOOKBACK_DAYS = 7
BATCH_NAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
TICKER_RE = re.compile(r"^[A-Z][A-Z0-9.\-]{0,15}$")

DECISION_MAP: dict[str, DecisionLabel] = {
    "buy": DecisionLabel.BUY,
    "sell": DecisionLabel.SELL,
    "hold": DecisionLabel.HOLD,
    "avoid": DecisionLabel.AVOID,
}


class BatchError(Exception):
    """The batch cannot be started (bad arguments or a conflicting existing batch)."""


@dataclass
class BatchReport:
    recorded: list[tuple[str, str]] = field(default_factory=list)  # (label, ticker)
    skipped: list[tuple[str, str]] = field(default_factory=list)
    failed: list[tuple[str, str, str]] = field(default_factory=list)  # + error


@dataclass(frozen=True)
class EntryPrices:
    price_date: date
    stock: Decimal
    xbi: Decimal
    ibb: Decimal


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------
def validate_batch_name(batch: str) -> str:
    if not BATCH_NAME_RE.match(batch):
        raise BatchError(
            f"Invalid batch name {batch!r}: use 1-64 letters, digits, '.', '_' or '-'"
        )
    return batch


def normalize_tickers(tickers: Sequence[str]) -> list[str]:
    result = list(dict.fromkeys(t.strip().upper() for t in tickers if t.strip()))
    if not result:
        raise BatchError("No tickers given")
    for ticker in result:
        if not TICKER_RE.match(ticker):
            raise BatchError(f"Invalid ticker {ticker!r}")
    return result


def parse_decision(raw: str) -> DecisionLabel:
    decision = DECISION_MAP.get(raw.strip().lower())
    if decision is None:
        raise ValueError(
            f"Unknown decision from agent: {raw!r}. Expected one of {list(DECISION_MAP)}"
        )
    return decision


def parse_confidence(raw: int) -> Decimal:
    """Agent confidence is 0-100; the database stores 0-1."""
    if not 0 <= raw <= 100:
        raise ValueError(f"Confidence out of range 0-100: {raw!r}")
    return (Decimal(raw) / 100).quantize(Decimal("0.01"))


def _price(value: float) -> Decimal:
    return Decimal(str(round(value, 4)))


def _maybe_json(content: Any) -> Any:
    if isinstance(content, str):
        try:
            return json.loads(content)
        except ValueError:
            return content
    return content


def extract_subagent_outputs(messages: Sequence[Any]) -> list[dict]:
    """Each subagent's result, recovered from the supervisor's message history.

    deepagents hands a subagent's last message back to the supervisor as the
    ``ToolMessage`` of a ``task`` tool call, so match those calls to their results.
    The content is parsed as JSON when possible and kept as raw text otherwise.
    """
    calls: dict[str, dict] = {}
    for message in messages:
        for call in getattr(message, "tool_calls", None) or []:
            if call.get("name") == "task":
                calls[call["id"]] = call.get("args") or {}

    outputs = []
    for message in messages:
        if isinstance(message, ToolMessage) and message.tool_call_id in calls:
            args = calls[message.tool_call_id]
            outputs.append(
                {
                    "subagent": args.get("subagent_type"),
                    "task": args.get("description"),
                    "output": _maybe_json(message.content),
                }
            )
    return outputs


# ---------------------------------------------------------------------------
# Prices
# ---------------------------------------------------------------------------
def fetch_entry_prices(
    ticker: str,
    signal_date: date,
    benchmark_prices: dict[str, PriceMap],
    price_fn: Callable[[str, date, date], PriceMap] = load_prices,
) -> EntryPrices:
    """Entry prices for a stock and both benchmarks on one shared trading day."""
    start = signal_date - timedelta(days=ENTRY_LOOKBACK_DAYS)
    stock_prices = price_fn(ticker, start, signal_date)
    if not stock_prices:
        raise RuntimeError(f"No price data for {ticker} in the last 7 days")

    xbi, ibb = (benchmark_prices[b] for b in BENCHMARKS)
    price_date = latest_common_date(
        [stock_prices, xbi, ibb], signal_date, ENTRY_LOOKBACK_DAYS
    )
    if price_date is None:
        raise RuntimeError(
            f"No trading day in the last {ENTRY_LOOKBACK_DAYS} days with prices for "
            f"{ticker}, {BENCHMARKS[0]} and {BENCHMARKS[1]}"
        )
    return EntryPrices(
        price_date=price_date,
        stock=_price(stock_prices[price_date]),
        xbi=_price(xbi[price_date]),
        ibb=_price(ibb[price_date]),
    )


# ---------------------------------------------------------------------------
# Batch
# ---------------------------------------------------------------------------
async def _run_agent(agent, ticker: str) -> tuple[BioSignalFoundryOutput, list[dict]]:
    with capture_subagent_outputs() as captured:
        result = await agent.ainvoke({"messages": [HumanMessage(f"Analyze {ticker}")]})
    output = result.get("structured_response")
    if not isinstance(output, BioSignalFoundryOutput):
        raise RuntimeError(
            f"Agent did not return a structured response. Keys: {list(result.keys())}"
        )
    # Prefer each subagent's own typed output; fall back to the text the supervisor
    # received for subagents without structured output.
    return output, captured or extract_subagent_outputs(result.get("messages", []))


async def record_batch(
    *,
    batch: str,
    labels: Sequence[str],
    tickers: Sequence[str],
    signal_date: date,
    force: bool = False,
    concurrency: int = 1,
    session_factory=SessionLocal,
    agent_factory: Callable[[str], Any] = default_build_agent,
    price_fn: Callable[[str, date, date], PriceMap] = load_prices,
) -> BatchReport:
    """Run every version in ``labels`` over ``tickers`` and store the signals.

    Raises ``BatchError`` before any paid call if the batch already holds signals
    from a different date, since versions must share one date to be comparable.
    """
    validate_batch_name(batch)
    tickers = normalize_tickers(tickers)
    report = BatchReport()

    # Fail fast, before spending anything: unknown version, prompt drift, missing key.
    agents = {label: agent_factory(label) for label in labels}

    async with session_factory() as session:
        for label in labels:
            await register_version(session, label)
        await session.commit()

        existing = (
            await session.execute(
                select(
                    PaperTrade.version_label, PaperTrade.ticker, PaperTrade.signal_date
                ).where(PaperTrade.batch == batch)
            )
        ).all()

    other_dates = {row.signal_date for row in existing} - {signal_date}
    if other_dates:
        raise BatchError(
            f"Batch {batch!r} already has signals dated "
            f"{', '.join(sorted(d.isoformat() for d in other_dates))}. Versions in a "
            "batch must share one date, so use a new batch name."
        )
    done = {(row.version_label, row.ticker) for row in existing}

    pending = [
        (label, ticker)
        for ticker in tickers
        for label in labels
        if force or (label, ticker) not in done
    ]
    pending_set = set(pending)
    report.skipped = [
        (label, ticker)
        for ticker in tickers
        for label in labels
        if (label, ticker) not in pending_set
    ]
    if not pending:
        return report

    start = signal_date - timedelta(days=ENTRY_LOOKBACK_DAYS)
    benchmark_prices = {b: price_fn(b, start, signal_date) for b in BENCHMARKS}

    entries: dict[str, EntryPrices | Exception] = {}
    for ticker in dict.fromkeys(t for _, t in pending):
        try:
            entries[ticker] = fetch_entry_prices(
                ticker, signal_date, benchmark_prices, price_fn
            )
        except Exception as exc:  # reported per signal below
            entries[ticker] = exc

    semaphore = asyncio.Semaphore(max(1, concurrency))

    async def record_one(label: str, ticker: str) -> None:
        entry = entries[ticker]
        if isinstance(entry, Exception):
            report.failed.append((label, ticker, str(entry)))
            return
        async with semaphore:
            try:
                output, subagents = await _run_agent(agents[label], ticker)
                values = dict(
                    batch=batch,
                    version_label=label,
                    ticker=ticker,
                    signal_date=signal_date,
                    decision=parse_decision(output.decision),
                    confidence=parse_confidence(output.confidence),
                    rationale=output.reasoning,
                    agent_output={
                        "supervisor": output.model_dump(),
                        "subagents": subagents,
                    },
                    entry_price_date=entry.price_date,
                    entry_price=entry.stock,
                    xbi_entry_price=entry.xbi,
                    ibb_entry_price=entry.ibb,
                )
                async with session_factory() as session:
                    await upsert_signal(session, values)
                    await session.commit()
            except Exception as exc:
                logger.warning(
                    "signal failed", version=label, ticker=ticker, error=str(exc)
                )
                report.failed.append((label, ticker, str(exc)))
                return
        logger.info(
            "signal recorded",
            version=label,
            ticker=ticker,
            decision=values["decision"].value,
            confidence=str(values["confidence"]),
        )
        report.recorded.append((label, ticker))

    await asyncio.gather(*(record_one(label, ticker) for label, ticker in pending))
    return report
