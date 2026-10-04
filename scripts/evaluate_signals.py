"""
Evaluate matured paper trading signals from the paper_trades table.
A signal is mature when today >= its exit_date.

Evaluations are written back to the same row so they only run once.

Usage:
    python3 scripts/evaluate_signals.py               # evaluate all matured signals
    python3 scripts/evaluate_signals.py --ticker MRNA # filter by ticker
    python3 scripts/evaluate_signals.py --all         # re-evaluate already evaluated signals
"""

import argparse
import asyncio
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import func, select

from src.core.db import SessionLocal, engine
from src.evaluation.models import PaperTrade
from src.evaluation.price_loader import load_prices, nearest_price

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


def _as_record(t: PaperTrade) -> dict:
    return {
        "id": str(t.id)[:8],
        "ticker": t.ticker,
        "decision": t.decision.value,
        "confidence": float(t.confidence),
        "system_version": t.system_version,
        "outcome": {
            "forward_return": float(t.forward_return),
            "is_correct": t.is_correct,
        },
    }


async def main() -> None:
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

    today = date.today()

    try:
        async with SessionLocal() as session:
            stmt = select(PaperTrade).where(PaperTrade.exit_date <= today)
            if not args.all:
                stmt = stmt.where(PaperTrade.evaluated_at.is_(None))
            if args.ticker:
                stmt = stmt.where(PaperTrade.ticker == args.ticker.upper())
            to_evaluate = (
                await session.scalars(
                    stmt.order_by(PaperTrade.exit_date, PaperTrade.ticker)
                )
            ).all()

            if not to_evaluate:
                print("No matured signals to evaluate.")
                n_pending, earliest = (
                    await session.execute(
                        select(func.count(), func.min(PaperTrade.exit_date)).where(
                            PaperTrade.evaluated_at.is_(None)
                        )
                    )
                ).one()
                if n_pending:
                    print(
                        f"  {n_pending} signal(s) pending. "
                        f"Earliest matures on {earliest}."
                    )
                return

            w_header = 57
            print(f"\n{'=' * w_header}")
            print(f"  Evaluating {len(to_evaluate)} signal(s)  (as of {today})")
            print(f"{'=' * w_header}")

            for t in to_evaluate:
                prices = load_prices(
                    t.ticker, t.exit_date, t.exit_date + timedelta(days=5)
                )
                exit_float = nearest_price(prices, t.exit_date)

                if exit_float is None:
                    print(
                        f"\n  [{str(t.id)[:8]}] {t.ticker} — could not fetch exit price for {t.exit_date}, skipping."
                    )
                    continue

                exit_price = Decimal(str(round(exit_float, 4)))
                fwd = ((exit_price - t.entry_price) / t.entry_price).quantize(
                    Decimal("0.000001")
                )
                correct = _is_correct(t.decision.value, float(fwd))

                t.exit_price = exit_price
                t.forward_return = fwd
                t.is_correct = correct
                t.evaluated_at = datetime.now(timezone.utc)

                print(f"\n  [{str(t.id)[:8]}] {t.ticker}")
                print(f"  Signal   : {t.signal_date}  →  Exit: {t.exit_date}")
                print(
                    f"  Decision : {t.decision.value}  (confidence: {float(t.confidence) * 100:.0f}%)"
                )
                print(f"  Entry    : ${t.entry_price:.2f}  →  Exit: ${exit_price:.2f}")
                print(f"  Return   : {float(fwd) * 100:+.1f}%")
                print(f"  Correct  : {'✓' if correct else '✗'}")

            await session.commit()

            evaluated = (
                await session.scalars(
                    select(PaperTrade).where(PaperTrade.evaluated_at.is_not(None))
                )
            ).all()

        all_evaluated = [_as_record(t) for t in evaluated]
        if all_evaluated:
            w = 66

            def _row(label: str, rs: list[dict]) -> str:
                n = len(rs)
                thresh = sum(1 for r in rs if r["outcome"]["is_correct"])
                direc = sum(
                    1
                    for r in rs
                    if _direction_correct(r["decision"], r["outcome"]["forward_return"])
                )
                avg_ret = sum(r["outcome"]["forward_return"] for r in rs) / n
                sim = (
                    sum(
                        _simulated_pnl(
                            r["decision"],
                            r["confidence"],
                            r["outcome"]["forward_return"],
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
                ("<60%", lambda c: c < 0.60),
                ("60–70%", lambda c: 0.60 <= c < 0.70),
                ("70–80%", lambda c: 0.70 <= c < 0.80),
                ("≥80%", lambda c: c >= 0.80),
            ]

            print(f"\n  Confidence calibration")
            print(f"  {'':12} {'N':>4}" f"  {'Threshold':>9}" f"  {'Direction':>9}")
            print(SEP)
            for label, pred in CONF_BUCKETS:
                rs = [r for r in all_evaluated if pred(r["confidence"])]
                if not rs:
                    continue
                n = len(rs)
                thresh = sum(1 for r in rs if r["outcome"]["is_correct"])
                direc = sum(
                    1
                    for r in rs
                    if _direction_correct(r["decision"], r["outcome"]["forward_return"])
                )
                print(
                    f"  {label:<12} {n:>4}"
                    f"  {thresh:>3} {thresh / n:>5.0%}"
                    f"  {direc:>3} {direc / n:>5.0%}"
                )

            print(f"{'=' * w}\n")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
