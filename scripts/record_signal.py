"""
Record a paper trading signal: run the agent for a ticker,
fetch today's entry price, and append to the signal log.

Usage:
    poetry run python scripts/record_signal.py            # run all tickers in WATCHLIST
    poetry run python scripts/record_signal.py MRNA       # single ticker
    poetry run python scripts/record_signal.py MRNA --holding-days 14
"""

import argparse
import asyncio
import json
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from langchain.messages import HumanMessage

from src.backtesting.price_loader import load_prices, nearest_price_backward
from src.backtesting.types import DecisionLabel
from src.biosignalfoundry import BioSignalFoundryOutput, biosignalfoundry

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
    "AMGN",   # Amgen — large-cap benchmark
    "GILD",   # Gilead Sciences
    "REGN",   # Regeneron
    "VRTX",   # Vertex Pharmaceuticals
    "BIIB",   # Biogen
    "ALNY",   # Alnylam — RNA therapeutics
    "SRPT",   # Sarepta Therapeutics
    "BMRN",   # BioMarin Pharmaceutical
    "IONS",   # Ionis Pharmaceuticals
    "EXEL",   # Exelixis
    "MRNA",   # Moderna
    "HALO",   # Halozyme Therapeutics
    "ACAD",   # ACADIA Pharmaceuticals
    "RARE",   # Ultragenyx
    "PTGX",   # Protagonist Therapeutics
]

LOG_PATH = Path(__file__).resolve().parents[1] / "data" / "paper_trades.json"


def load_log() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    return json.loads(LOG_PATH.read_text())


def save_log(records: list[dict]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(records, indent=2, default=str))


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


def record_one(ticker: str, holding_days: int, records: list[dict]) -> None:
    signal_date = date.today()

    output = asyncio.run(get_decision(ticker))
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

    record = {
        "id": str(uuid.uuid4())[:8],
        "system_version": SYSTEM_VERSION,
        "ticker": ticker,
        "signal_date": signal_date.isoformat(),
        "exit_date": exit_date.isoformat(),
        "holding_days": holding_days,
        "decision": str(decision),
        "confidence": round(output.confidence / 100, 2),
        "rationale": output.reasoning,
        "entry_price": entry_price,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "outcome": None,  # filled in by evaluate_signals.py once exit_date is reached
    }

    records.append(record)

    width = 55
    print(f"\n{'=' * width}")
    print(f"  Signal recorded for {ticker}")
    print(f"  Version  : {SYSTEM_VERSION}")
    print(f"  Date     : {signal_date}  (entry)")
    print(f"  Exit     : {exit_date}  ({holding_days} days later)")
    print(f"  Decision : {decision}  (confidence: {output.confidence}%)")
    print(f"  Entry    : ${entry_price:.2f}")
    print(f"  Log      : {LOG_PATH}")
    print(f"{'=' * width}")
    print(f"  Run evaluate_signals.py on or after {exit_date} to see the result.")
    print(f"{'=' * width}\n")


def main() -> None:
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
    holding_days = args.holding_days

    records = load_log()
    errors: list[tuple[str, str]] = []

    for ticker in tickers:
        try:
            record_one(ticker, holding_days, records)
        except Exception as exc:
            print(f"\n  [!] {ticker} failed: {exc}")
            errors.append((ticker, str(exc)))

    save_log(records)

    if errors:
        print(f"\n  {len(errors)} ticker(s) failed: {', '.join(t for t, _ in errors)}")


if __name__ == "__main__":
    main()
