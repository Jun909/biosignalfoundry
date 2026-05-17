"""
Run a real backtest: invoke the LLM agent for a ticker, then evaluate
the decision against real MarketStack prices.

Usage:
    python3 scripts/run_backtest.py MRNA
    python3 scripts/run_backtest.py MRNA --signal-date 2025-03-01 --holding-days 30
"""

import argparse
import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from langchain.messages import HumanMessage

from src.backtesting.engine import run
from src.backtesting.types import (BacktestRequest, BacktestResult,
                                   DecisionLabel, Signal)
from src.biosignalfoundry import BioSignalFoundryOutput, biosignalfoundry

DECISION_MAP: dict[str, DecisionLabel] = {
    "buy": DecisionLabel.BUY,
    "sell": DecisionLabel.SELL,
    "hold": DecisionLabel.HOLD,
    "avoid": DecisionLabel.AVOID,
}


async def get_signal(ticker: str, signal_date: date) -> Signal:
    print(f"Invoking agent for {ticker}... (this may take a moment)")
    result = await biosignalfoundry.ainvoke(
        {"messages": [HumanMessage(f"Analyze {ticker}")]}
    )

    output: BioSignalFoundryOutput | None = result.get("structured_response")
    if not isinstance(output, BioSignalFoundryOutput):
        raise RuntimeError(
            f"Agent did not return a structured response. Keys: {list(result.keys())}"
        )

    decision = DECISION_MAP.get(output.decision.strip().lower())
    if decision is None:
        raise ValueError(
            f"Unknown decision from agent: {output.decision!r}. Expected one of {list(DECISION_MAP)}"
        )

    return Signal(
        ticker=ticker,
        as_of_date=signal_date,
        decision=decision,
        rationale=output.reasoning,
        confidence=output.confidence / 100,
    )


def print_result(result: BacktestResult, signal: Signal) -> None:
    width = 57
    exit_date = signal.as_of_date + timedelta(days=result.request.holding_period_days)

    print(f"\n{'=' * width}")
    print(f"  Ticker   : {result.request.ticker}")
    print(f"  Signal   : {signal.as_of_date}  (entry)")
    print(
        f"  Exit     : {exit_date}  ({result.request.holding_period_days} days later)"
    )
    print(
        f"  Decision : {signal.decision}  (confidence: {(signal.confidence or 0) * 100:.0f}%)"
    )
    if signal.rationale:
        words, line, lines = signal.rationale.split(), "", []
        for word in words:
            if len(line) + len(word) + 1 > 50:
                lines.append(line)
                line = word
            else:
                line = f"{line} {word}".strip()
        if line:
            lines.append(line)
        print(f"  Rationale: {lines[0]}")
        for ln in lines[1:]:
            print(f"             {ln}")
    print(f"{'=' * width}")

    if not result.observations:
        print(
            f"  No result — exit date {exit_date} may be in the future or prices are missing."
        )
        print(f"{'=' * width}\n")
        return

    obs = result.observations[0]
    print(f"  Entry price : ${obs.entry_price:.2f}")
    print(f"  Exit price  : ${obs.exit_price:.2f}")
    print(f"  Return      : {obs.forward_return * 100:+.1f}%")
    print(f"  Correct     : {'✓' if obs.is_correct else '✗'}")
    print(f"{'=' * width}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a real backtest using the LLM agent"
    )
    parser.add_argument(
        "ticker", type=str, help="Biotech stock ticker, e.g. MRNA, GILD, REGN"
    )
    parser.add_argument(
        "--signal-date",
        type=date.fromisoformat,
        default=date.today() - timedelta(days=30),
        help="Date the signal is generated for (default: 30 days ago)",
    )
    parser.add_argument(
        "--holding-days",
        type=int,
        default=20,
        help="Holding period in calendar days (default: 20)",
    )
    args = parser.parse_args()

    ticker = args.ticker.upper()
    signal_date: date = args.signal_date
    holding_days: int = args.holding_days

    signal = asyncio.run(get_signal(ticker, signal_date))

    request = BacktestRequest(
        ticker=ticker,
        start_date=signal_date,
        end_date=signal_date,
        holding_period_days=holding_days,
    )

    result = run(request, [signal])
    print_result(result, signal)


if __name__ == "__main__":
    main()
