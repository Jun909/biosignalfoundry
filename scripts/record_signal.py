"""
Record a paper-trading batch: run one or more registered versions over the
watchlist on the same day and store each decision with entry prices for the
stock, XBI and IBB (see README "Evaluation").

Every version in a batch shares one signal date and one set of entry prices, so
versions can be compared stock by stock. Re-running the same batch skips signals
already recorded (so a failed batch can be resumed); --force replaces them and
deletes their evaluations. Run after the US market close so the entry price is
a full day's close.

Usage:
    uv run python scripts/record_signal.py --batch 2026-11-a --versions all
    uv run python scripts/record_signal.py --batch 2026-11-a --versions v1.0,v1.1
    uv run python scripts/record_signal.py --batch test-1 --versions v1.0 --tickers MRNA,GILD
"""

import argparse
import asyncio
import sys
from datetime import date
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from config import settings
from src.core.db import engine
from src.core.logging_config import setup_logging
from src.core.version_registry import VersionError, resolve_labels
from src.evaluation.recorder import BatchError, record_batch
from src.evaluation.watchlist import WATCHLIST


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record a paper-trading batch")
    parser.add_argument(
        "--batch",
        required=True,
        help="Batch name grouping the versions compared together, e.g. 2026-11-a",
    )
    parser.add_argument(
        "--versions",
        required=True,
        help="'all' or comma-separated version labels, e.g. v1.0,v1.1",
    )
    parser.add_argument(
        "--tickers",
        help="Comma-separated tickers (default: the full WATCHLIST)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace signals already recorded in this batch (deletes their evaluations)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Agent runs in parallel (default: 1; mind data-provider rate limits)",
    )
    return parser.parse_args()


async def main() -> int:
    args = _parse_args()
    setup_logging(log_level=settings.log_level, render_json=False)

    tickers = args.tickers.split(",") if args.tickers else WATCHLIST
    signal_date = date.today()

    try:
        labels = resolve_labels(args.versions)
        report = await record_batch(
            batch=args.batch,
            labels=labels,
            tickers=tickers,
            signal_date=signal_date,
            force=args.force,
            concurrency=args.concurrency,
        )
    except (BatchError, VersionError) as exc:
        print(f"\n  [!] {exc}")
        return 2
    finally:
        await engine.dispose()

    print(f"\n{'=' * 55}")
    print(f"  Batch {args.batch}  ({signal_date})  versions: {', '.join(labels)}")
    print(f"  Recorded : {len(report.recorded)}")
    print(f"  Skipped  : {len(report.skipped)}  (already in this batch)")
    print(f"  Failed   : {len(report.failed)}")
    for label, ticker, error in report.failed:
        print(f"    [!] {label} {ticker}: {error}")
    print(f"{'=' * 55}")
    if report.failed:
        print("  Re-run the same command to retry only the failed signals.\n")
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
