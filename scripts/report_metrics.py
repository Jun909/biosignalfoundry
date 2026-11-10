"""
Report evaluation metrics from the paper_trade_returns view. Read only: writes
nothing to the database.

Rows are grouped by version and horizon. Each table shows how many signals have
been evaluated against how many were recorded, so a partial 90-day result is not
read as final. See src/evaluation/metrics.py for every definition.

Usage:
    uv run python scripts/report_metrics.py
    uv run python scripts/report_metrics.py --batch 2026-11-a --horizons 30
    uv run python scripts/report_metrics.py --versions v1.0,v1.1 --benchmark ibb --detail
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from src.core.db import SessionLocal, engine
from src.core.version_registry import VersionError, resolve_labels
from src.evaluation.evaluator import HORIZONS
from src.evaluation.metrics import (OUTCOMES, SIDES, MetricsSummary,
                                    group_rows, summarize)
from src.evaluation.repository import count_trades, load_return_rows


def _pct(value, signed: bool = False) -> str:
    if value is None:
        return "-"
    return f"{value * 100:+.1f}%" if signed else f"{value * 100:.1f}%"


def _ci(low, high) -> str:
    return "" if low is None else f" [{_pct(low, True)}, {_pct(high, True)}]"


def _rate(p) -> str:
    if p.rate is None:
        return "-"
    return f"{_pct(p.rate)} ({p.successes}/{p.n})"


def _print_summary_table(label: str, horizon: int, total: int, s: MetricsSummary):
    print(f"\n  {label}  {horizon}d   evaluated {s.n} of {total} signals")
    sp = s.spread
    print(
        f"    Mean excess vs {s.benchmark.upper()} : "
        f"{_pct(s.mean_excess_return.mean, True)}"
        f"{_ci(s.mean_excess_return.ci_low, s.mean_excess_return.ci_high)}"
    )
    print(
        f"    Spread BUY - SELL/AVOID : {_pct(sp.spread, True)}"
        f"{_ci(sp.ci_low, sp.ci_high)}   "
        f"(BUY n={sp.n_buy} {_pct(sp.buy_mean, True)}, "
        f"SELL/AVOID n={sp.n_sell_avoid} {_pct(sp.sell_avoid_mean, True)})"
    )
    h = s.hit_rate
    print(
        f"    Hit rate                : {_rate(h.overall)}   "
        f"BUY {_rate(h.by_side['BUY'])}, SELL/AVOID {_rate(h.by_side['SELL_AVOID'])}"
    )
    b = s.baselines
    print(
        f"    Baselines               : always-BUY {_pct(b.always_buy_mean_excess, True)} "
        f"excess, hit {_pct(b.always_buy_hit_rate)}; "
        f"random hit {_pct(b.random_hit_rate)}; "
        f"{s.benchmark.upper()} {_pct(b.benchmark_mean_return, True)}"
    )


def _print_detail(s: MetricsSummary):
    print("    Confusion (decision vs outcome relative to benchmark)")
    print(f"      {'':12}" + "".join(f"{o:>7}" for o in OUTCOMES))
    for side in SIDES:
        print(
            f"      {side:<12}"
            + "".join(f"{s.confusion[side][o]:>7}" for o in OUTCOMES)
        )
    print("    Calibration (directional calls)")
    for c in s.calibration:
        if c.hits.n:
            print(
                f"      conf {c.low:.0%}-{min(c.high, 1.0):.0%}: n={c.hits.n:<3} "
                f"hit {_rate(c.hits)}  signed excess {_pct(c.mean_signed_excess.mean, True)}"
            )
    lp = s.loss_profile
    print(
        f"    Loss profile            : {lp.n_wins} wins avg {_pct(lp.average_win, True)}, "
        f"{lp.n_losses} losses avg {_pct(lp.average_loss, True)}, "
        f"worst {_pct(lp.worst_loss, True)}"
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report paper-trading metrics")
    parser.add_argument("--batch", help="Only this batch (default: all batches)")
    parser.add_argument("--versions", help="'all' or comma-separated labels")
    parser.add_argument(
        "--horizons",
        default=",".join(map(str, HORIZONS)),
        help="Comma-separated horizons in days (default: 7,30,90)",
    )
    parser.add_argument("--benchmark", choices=("xbi", "ibb"), default="xbi")
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Add confusion matrix, calibration, losses",
    )
    return parser.parse_args()


async def main() -> int:
    args = _parse_args()
    try:
        horizons = [int(h) for h in args.horizons.split(",") if h.strip()]
        labels = resolve_labels(args.versions) if args.versions else None
    except (ValueError, VersionError) as exc:
        print(f"\n  [!] {exc}")
        return 2

    try:
        async with SessionLocal() as session:
            rows = await load_return_rows(session, args.batch, labels, horizons)
            totals = await count_trades(session, args.batch, labels)
    finally:
        await engine.dispose()

    if not totals:
        print("\n  No signals recorded yet.")
        return 0

    scope = f"batch {args.batch}" if args.batch else "all batches"
    print(
        f"\n{'=' * 70}\n  Metrics - {scope}, benchmark {args.benchmark.upper()}\n{'=' * 70}"
    )
    grouped = group_rows(rows, lambda r: (r.version_label, r.horizon_days))
    for label in sorted(totals):
        for horizon in horizons:
            group = grouped.get((label, horizon), [])
            if not group:
                print(
                    f"\n  {label}  {horizon}d   evaluated 0 of {totals[label]} signals"
                )
                continue
            summary = summarize(group, args.benchmark)
            _print_summary_table(label, horizon, totals[label], summary)
            if args.detail:
                _print_detail(summary)
    print(f"\n{'=' * 70}")
    print("  Small samples: intervals are rough; compare versions on the same batch.\n")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
