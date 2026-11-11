"""
Evaluate matured paper-trading signals at 7, 30 and 90 days.

For every signal and horizon that has matured and has no evaluation yet, fetch the
exit prices (stock, XBI, IBB) plus entry prices re-fetched on the same adjusted
basis, and store them in paper_trade_evaluations. Horizons count from the trade's
entry_price_date. Safe to run late or repeatedly: existing evaluations are kept,
and horizons without a closing price yet stay pending. Returns and verdicts are
not stored; see report_metrics.py.

Usage:
    uv run python scripts/evaluate_signals.py
    uv run python scripts/evaluate_signals.py --batch 2026-11-a
    uv run python scripts/evaluate_signals.py --versions v1.0 --horizons 7,30
"""

import argparse
import asyncio
import sys
from collections import Counter
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from config import settings
from src.core.db import engine
from src.core.logging_config import setup_logging
from src.core.version_registry import VersionError, resolve_labels
from src.evaluation.evaluator import HORIZONS, evaluate_matured


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate matured paper trades")
    parser.add_argument("--batch", help="Only this batch (default: all batches)")
    parser.add_argument(
        "--versions", help="'all' or comma-separated labels (default: all)"
    )
    parser.add_argument(
        "--horizons",
        default=",".join(map(str, HORIZONS)),
        help="Comma-separated horizons in days (default: 7,30,90)",
    )
    return parser.parse_args()


def _by_horizon(items) -> str:
    counts = Counter(item[2] for item in items)
    return ", ".join(f"{h}d: {counts[h]}" for h in sorted(counts)) or "-"


async def main() -> int:
    args = _parse_args()
    setup_logging(log_level=settings.log_level, render_json=False)
    try:
        horizons = [int(h) for h in args.horizons.split(",") if h.strip()]
        if not horizons or any(h <= 0 for h in horizons):
            raise ValueError("horizons must be positive integers")
        labels = resolve_labels(args.versions) if args.versions else None
        report = await evaluate_matured(
            horizons=horizons, batch=args.batch, labels=labels
        )
    except (ValueError, VersionError) as exc:
        print(f"\n  [!] {exc}")
        return 2
    finally:
        await engine.dispose()

    print(f"\n{'=' * 55}")
    print(f"  Evaluated : {len(report.created)}  ({_by_horizon(report.created)})")
    print(f"  Pending   : {len(report.pending)}  ({_by_horizon(report.pending)})")
    print(f"  Failed    : {len(report.failed)}")
    for label, ticker, horizon, error in report.failed:
        print(f"    [!] {label} {ticker} {horizon}d: {error}")
    print(f"{'=' * 55}")
    if report.failed:
        print("  Re-run to retry the failed horizons.\n")
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
