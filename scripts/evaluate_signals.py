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

BUY_THRESHOLD = 0.05  # +5% to be a correct BUY
SELL_THRESHOLD = -0.05  # -5% to be a correct SELL or AVOID


def _is_correct(decision: str, forward_return: float) -> bool:
    if decision == "BUY":
        return forward_return >= BUY_THRESHOLD
    if decision in ("SELL", "AVOID"):
        return forward_return <= SELL_THRESHOLD
    if decision == "HOLD":
        return SELL_THRESHOLD < forward_return < BUY_THRESHOLD
    return False


def _direction_correct(decision: str, forward_return: float) -> bool:
    """Looser correctness: did we get the direction right, ignoring magnitude?"""
    if decision == "BUY":
        return forward_return > 0
    if decision in ("SELL", "AVOID"):
        return forward_return < 0
    if decision == "HOLD":
        return SELL_THRESHOLD < forward_return < BUY_THRESHOLD
    return False


def _simulated_pnl(decision: str, confidence: float, forward_return: float) -> float:
    """Confidence-weighted directional return for one signal.

    Positive = the signal made money if you sized by confidence and shorted SELL/AVOID.
    """
    if decision == "BUY":
        return confidence * forward_return
    if decision in ("SELL", "AVOID"):
        return confidence * -forward_return
    return 0.0


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
        r
        for r in records
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

    updated = False
    w_header = 57

    print(f"\n{'=' * w_header}")
    print(f"  Evaluating {len(to_evaluate)} signal(s)  (as of {today})")
    print(f"{'=' * w_header}")

    for r in to_evaluate:
        ticker = r["ticker"]
        signal_date = date.fromisoformat(r["signal_date"])
        exit_date = date.fromisoformat(r["exit_date"])

        entry_price: float = r["entry_price"]  # already captured at record time

        prices = load_prices(ticker, exit_date, exit_date + timedelta(days=5))
        exit_price = nearest_price(prices, exit_date)

        if exit_price is None:
            print(
                f"\n  [{r['id']}] {ticker} — could not fetch exit price for {exit_date}, skipping."
            )
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
        print(
            f"  Decision : {r['decision']}  (confidence: {r['confidence'] * 100:.0f}%)"
        )
        print(f"  Entry    : ${entry_price:.2f}  →  Exit: ${exit_price:.2f}")
        print(f"  Return   : {fwd * 100:+.1f}%")
        print(f"  Correct  : {'✓' if correct else '✗'}")

    # ── Summary ──────────────────────────────────────────────────────
    all_evaluated = [r for r in records if r["outcome"] is not None]
    if all_evaluated:
        w = 66

        def _row(label: str, rs: list[dict]) -> str:
            n = len(rs)
            thresh = sum(1 for r in rs if r["outcome"]["is_correct"])
            direc = sum(
                1 for r in rs
                if _direction_correct(r["decision"], r["outcome"]["forward_return"])
            )
            avg_ret = sum(r["outcome"]["forward_return"] for r in rs) / n
            sim = (
                sum(
                    _simulated_pnl(
                        r["decision"], r["confidence"], r["outcome"]["forward_return"]
                    )
                    for r in rs
                )
                / n
            )
            return (
                f"  {label:<12} {n:>4}"
                f"  {thresh:>3} {thresh / n:>5.0%}"
                f"  {direc:>3} {direc / n:>5.0%}"
                f"  {avg_ret:>+7.1%}"
                f"  {sim:>+7.1%}"
            )

        HDR = (
            f"  {'':12} {'N':>4}"
            f"  {'Threshold':>9}"
            f"  {'Direction':>9}"
            f"  {'Avg Ret':>8}"
            f"  {'Sim P&L':>8}"
        )
        SEP = f"  {'-' * (w - 4)}"

        # ── By version ────────────────────────────────────────────────
        versions: dict[str, list[dict]] = {}
        for r in all_evaluated:
            v = r.get("system_version", "unknown")
            versions.setdefault(v, []).append(r)

        print(f"\n{'=' * w}")
        print(f"  Performance by system version")
        print(HDR)
        print(SEP)
        for v, rs in sorted(versions.items()):
            print(_row(v, rs))
        print(SEP)
        print(_row("Overall", all_evaluated))

        # ── By decision type ──────────────────────────────────────────
        by_decision: dict[str, list[dict]] = {}
        for r in all_evaluated:
            by_decision.setdefault(r["decision"], []).append(r)

        print(f"\n  By decision type")
        print(HDR)
        print(SEP)
        for d in ["BUY", "SELL", "AVOID", "HOLD"]:
            if d in by_decision:
                print(_row(d, by_decision[d]))

        # ── Confidence calibration ────────────────────────────────────
        CONF_BUCKETS = [
            ("<60%",   lambda c: c < 0.60),
            ("60–70%", lambda c: 0.60 <= c < 0.70),
            ("70–80%", lambda c: 0.70 <= c < 0.80),
            ("≥80%",   lambda c: c >= 0.80),
        ]

        print(f"\n  Confidence calibration")
        print(
            f"  {'':12} {'N':>4}"
            f"  {'Threshold':>9}"
            f"  {'Direction':>9}"
        )
        print(SEP)
        for label, pred in CONF_BUCKETS:
            rs = [r for r in all_evaluated if pred(r["confidence"])]
            if not rs:
                continue
            n = len(rs)
            thresh = sum(1 for r in rs if r["outcome"]["is_correct"])
            direc = sum(
                1 for r in rs
                if _direction_correct(r["decision"], r["outcome"]["forward_return"])
            )
            print(
                f"  {label:<12} {n:>4}"
                f"  {thresh:>3} {thresh / n:>5.0%}"
                f"  {direc:>3} {direc / n:>5.0%}"
            )

        print(f"{'=' * w}\n")

    if updated:
        LOG_PATH.write_text(json.dumps(records, indent=2, default=str))
        print(f"  Log updated: {LOG_PATH}\n")


if __name__ == "__main__":
    main()
