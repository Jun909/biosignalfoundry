"""
Evaluate matured paper trading signals from the signal log.
A signal is mature when today >= its exit_date.

Evaluations are written back into the log so they only run once.

Usage:
    python3 scripts/evaluate_signals.py               # evaluate all matured signals
    python3 scripts/evaluate_signals.py --ticker MRNA # filter by ticker
    python3 scripts/evaluate_signals.py --all         # re-evaluate already evaluated signals
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from src.backtesting.price_loader import load_prices, nearest_price

LOG_PATH = Path(__file__).resolve().parents[1] / "data" / "paper_trades.json"

BUY_THRESHOLD = 0.05   # +5% to be a correct BUY
SELL_THRESHOLD = -0.05  # -5% to be a correct SELL or AVOID


def _is_correct(decision: str, forward_return: float) -> bool:
    if decision == "BUY":
        return forward_return >= BUY_THRESHOLD
    if decision in ("SELL", "AVOID"):
        return forward_return <= SELL_THRESHOLD
    if decision == "HOLD":
        return SELL_THRESHOLD < forward_return < BUY_THRESHOLD
    return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate matured paper trading signals"
    )
    parser.add_argument("--ticker", type=str, help="Filter by ticker")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Re-evaluate signals that have already been evaluated",
    )
    args = parser.parse_args()

    if not LOG_PATH.exists():
        print("No signal log found. Run record_signal.py first.")
        return

    records: list[dict] = json.loads(LOG_PATH.read_text())
    today = date.today()

    to_evaluate = [
        r for r in records
        if date.fromisoformat(r["exit_date"]) <= today
        and (args.all or r["outcome"] is None)
        and (args.ticker is None or r["ticker"] == args.ticker.upper())
    ]

    if not to_evaluate:
        pending = [r for r in records if r["outcome"] is None]
        print("No matured signals to evaluate.")
        if pending:
            earliest = min(r["exit_date"] for r in pending)
            print(
                f"  {len(pending)} signal(s) pending. "
                f"Earliest matures on {earliest}."
            )
        return

    width = 57
    updated = False

    print(f"\n{'=' * width}")
    print(f"  Evaluating {len(to_evaluate)} signal(s)  (as of {today})")
    print(f"{'=' * width}")

    for r in to_evaluate:
        ticker = r["ticker"]
        signal_date = date.fromisoformat(r["signal_date"])
        exit_date = date.fromisoformat(r["exit_date"])

        prices = load_prices(ticker, signal_date, exit_date + timedelta(days=5))
        entry_price = nearest_price(prices, signal_date)
        exit_price = nearest_price(prices, exit_date)

        if entry_price is None or exit_price is None:
            print(f"\n  [{r['id']}] {ticker} — could not fetch prices, skipping.")
            continue

        fwd = (exit_price - entry_price) / entry_price
        correct = _is_correct(r["decision"], fwd)

        # Write outcome back into the record
        for rec in records:
            if rec["id"] == r["id"]:
                rec["outcome"] = {
                    "exit_price": exit_price,
                    "forward_return": round(fwd, 6),
                    "is_correct": correct,
                    "evaluated_at": datetime.now(timezone.utc).isoformat(),
                }
                updated = True

        print(f"\n  [{r['id']}] {ticker}")
        print(f"  Signal   : {signal_date}  →  Exit: {exit_date}")
        print(f"  Decision : {r['decision']}  (confidence: {r['confidence'] * 100:.0f}%)")
        print(f"  Entry    : ${entry_price:.2f}  →  Exit: ${exit_price:.2f}")
        print(f"  Return   : {fwd * 100:+.1f}%")
        print(f"  Correct  : {'✓' if correct else '✗'}")

    # Accuracy summary grouped by system version
    all_evaluated = [r for r in records if r["outcome"] is not None]
    if all_evaluated:
        versions: dict[str, list[dict]] = {}
        for r in all_evaluated:
            v = r.get("system_version", "unknown")
            versions.setdefault(v, []).append(r)

        print(f"\n{'=' * width}")
        print(f"  Performance by system version")
        print(f"  {'Version':<12} {'Signals':>8} {'Correct':>8} {'Accuracy':>9}")
        print(f"  {'-' * 41}")
        for v, rs in sorted(versions.items()):
            correct = sum(1 for r in rs if r["outcome"]["is_correct"])
            print(f"  {v:<12} {len(rs):>8} {correct:>8} {correct / len(rs):>8.0%}")
        total_correct = sum(1 for r in all_evaluated if r["outcome"]["is_correct"])
        print(f"  {'-' * 41}")
        print(f"  {'Overall':<12} {len(all_evaluated):>8} {total_correct:>8} {total_correct / len(all_evaluated):>8.0%}")
        print(f"{'=' * width}\n")

    if updated:
        LOG_PATH.write_text(json.dumps(records, indent=2, default=str))
        print(f"  Log updated: {LOG_PATH}\n")


if __name__ == "__main__":
    main()
