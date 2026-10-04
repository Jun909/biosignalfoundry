"""
Record a paper trading signal: run the agent for a ticker,
fetch today's entry price, and upsert it into the paper_trades table.
Re-running for the same ticker on the same day (and system version)
replaces that day's signal instead of creating a duplicate.

Usage:
    uv run python scripts/record_signal.py            # run all tickers in WATCHLIST
    uv run python scripts/record_signal.py MRNA       # single ticker
    uv run python scripts/record_signal.py MRNA --holding-days 14
"""

import argparse
import asyncio
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from langchain.messages import HumanMessage
from sqlalchemy import func, literal_column
from sqlalchemy.dialects.postgresql import insert

from src.biosignalfoundry import BioSignalFoundryOutput, biosignalfoundry
from src.core.db import SessionLocal, engine
from src.evaluation.models import PaperTrade
from src.evaluation.price_loader import load_prices, nearest_price_backward
from src.evaluation.types import DecisionLabel

DECISION_MAP: dict[str, DecisionLabel] = {
    "buy": DecisionLabel.BUY,
    "sell": DecisionLabel.SELL,
    "hold": DecisionLabel.HOLD,
    "avoid": DecisionLabel.AVOID,
}

# Bump this manually whenever you add/remove agents or tools so you can
# compare performance across system versions later.
SYSTEM_VERSION = "v1.0"

# Fixed watchlist for unbiased weekly coverage.
# Edit this list to add/remove tickers; run with no positional argument to process all of them.
WATCHLIST: list[str] = [
    "AMGN",  # Amgen — large-cap benchmark
    "GILD",  # Gilead Sciences
    "REGN",  # Regeneron
    "VRTX",  # Vertex Pharmaceuticals
    "BIIB",  # Biogen
    "ALNY",  # Alnylam — RNA therapeutics
    "SRPT",  # Sarepta Therapeutics
    "BMRN",  # BioMarin Pharmaceutical
    "IONS",  # Ionis Pharmaceuticals
    "EXEL",  # Exelixis
    "MRNA",  # Moderna
    "HALO",  # Halozyme Therapeutics
    "ACAD",  # ACADIA Pharmaceuticals
    "RARE",  # Ultragenyx
    "PTGX",  # Protagonist Therapeutics
]


async def get_decision(ticker: str) -> BioSignalFoundryOutput:
    print(f"Invoking agent for {ticker}... (this may take a moment)")
    result = await biosignalfoundry.ainvoke(
        {"messages": [HumanMessage(f"Analyze {ticker}")]}
    )
    output = result.get("structured_response")
    if not isinstance(output, BioSignalFoundryOutput):
        raise RuntimeError(
            f"Agent did not return a structured response. Keys: {list(result.keys())}"
        )
    return output


async def record_one(ticker: str, holding_days: int) -> None:
    signal_date = date.today()

    output = await get_decision(ticker)
    decision = DECISION_MAP.get(output.decision.strip().lower())
    if decision is None:
        raise ValueError(
            f"Unknown decision from agent: {output.decision!r}. "
            f"Expected one of {list(DECISION_MAP)}"
        )

    prices = load_prices(ticker, signal_date - timedelta(days=7), signal_date)
    entry_price = nearest_price_backward(prices, signal_date)
    if entry_price is None:
        raise RuntimeError(
            f"Could not fetch entry price for {ticker} near {signal_date}. "
            "No trading data found in the last 7 days."
        )

    exit_date = signal_date + timedelta(days=holding_days)
    confidence = (Decimal(output.confidence) / 100).quantize(Decimal("0.01"))

    stmt = insert(PaperTrade).values(
        system_version=SYSTEM_VERSION,
        ticker=ticker,
        signal_date=signal_date,
        exit_date=exit_date,
        holding_days=holding_days,
        decision=decision,
        confidence=confidence,
        rationale=output.reasoning,
        entry_price=Decimal(str(round(entry_price, 4))),
    )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_paper_trade_signal",
        set_={
            "exit_date": stmt.excluded.exit_date,
            "holding_days": stmt.excluded.holding_days,
            "decision": stmt.excluded.decision,
            "confidence": stmt.excluded.confidence,
            "rationale": stmt.excluded.rationale,
            "entry_price": stmt.excluded.entry_price,
            "recorded_at": func.now(),
            # a re-recorded signal invalidates any earlier evaluation
            "exit_price": None,
            "forward_return": None,
            "is_correct": None,
            "evaluated_at": None,
        },
    ).returning(literal_column("(xmax = 0)").label("inserted"))

    async with SessionLocal() as session:
        inserted = (await session.execute(stmt)).scalar_one()
        await session.commit()

    width = 55
    print(f"\n{'=' * width}")
    print(
        f"  Signal {'recorded' if inserted else 'updated (same-day re-run)'} for {ticker}"
    )
    print(f"  Version  : {SYSTEM_VERSION}")
    print(f"  Date     : {signal_date}  (entry)")
    print(f"  Exit     : {exit_date}  ({holding_days} days later)")
    print(f"  Decision : {decision}  (confidence: {output.confidence}%)")
    print(f"  Entry    : ${entry_price:.2f}")
    print(f"{'=' * width}")
    print(f"  Run evaluate_signals.py on or after {exit_date} to see the result.")
    print(f"{'=' * width}\n")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Record a paper trading signal")
    parser.add_argument(
        "ticker",
        type=str,
        nargs="?",
        help="Biotech stock ticker, e.g. MRNA, GILD, REGN. Omit to run the full WATCHLIST.",
    )
    parser.add_argument(
        "--holding-days",
        type=int,
        default=7,
        help="Holding period in calendar days (default: 7)",
    )
    args = parser.parse_args()

    tickers = [args.ticker.upper()] if args.ticker else WATCHLIST
    errors: list[tuple[str, str]] = []

    try:
        for ticker in tickers:
            try:
                await record_one(ticker, args.holding_days)
            except Exception as exc:
                print(f"\n  [!] {ticker} failed: {exc}")
                errors.append((ticker, str(exc)))
    finally:
        await engine.dispose()

    if errors:
        print(f"\n  {len(errors)} ticker(s) failed: {', '.join(t for t, _ in errors)}")


if __name__ == "__main__":
    asyncio.run(main())
