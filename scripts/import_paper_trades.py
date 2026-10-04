"""
One-time import of data/paper_trades.json into the paper_trades table.

Safe to re-run: rows that already exist (same ticker, signal_date,
system_version) are skipped, not duplicated.

Usage:
    uv run python scripts/import_paper_trades.py            # import
    uv run python scripts/import_paper_trades.py --dry-run  # parse and report only
"""

import argparse
import asyncio
import json
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from src.core.db import SessionLocal, engine
from src.evaluation.models import PaperTrade
from src.evaluation.types import DecisionLabel

LOG_PATH = Path(__file__).resolve().parents[1] / "data" / "paper_trades.json"


def _price(value: float) -> Decimal:
    return Decimal(str(round(value, 4)))


def to_row(r: dict) -> dict:
    outcome = r.get("outcome")
    row = {
        "system_version": r["system_version"],
        "ticker": r["ticker"],
        "signal_date": date.fromisoformat(r["signal_date"]),
        "exit_date": date.fromisoformat(r["exit_date"]),
        "holding_days": r["holding_days"],
        "decision": DecisionLabel(r["decision"]),
        "confidence": Decimal(str(r["confidence"])),
        "rationale": r["rationale"],
        "entry_price": _price(r["entry_price"]),
        "recorded_at": datetime.fromisoformat(r["recorded_at"]),
        "exit_price": None,
        "forward_return": None,
        "is_correct": None,
        "evaluated_at": None,
    }
    if outcome:
        row.update(
            exit_price=_price(outcome["exit_price"]),
            forward_return=Decimal(str(outcome["forward_return"])),
            is_correct=outcome["is_correct"],
            evaluated_at=datetime.fromisoformat(outcome["evaluated_at"]),
        )
    return row


async def main(dry_run: bool) -> None:
    records = json.loads(LOG_PATH.read_text())
    rows = [to_row(r) for r in records]

    keys = [(r["ticker"], r["signal_date"], r["system_version"]) for r in rows]
    dupes = len(keys) - len(set(keys))
    print(f"Parsed {len(rows)} record(s) from {LOG_PATH.name}.")
    if dupes:
        print(
            f"  {dupes} share a (ticker, signal_date, system_version) key; only the first of each is kept."
        )

    if dry_run:
        print("Dry run — nothing written.")
        return

    async with SessionLocal() as session:
        before = await session.scalar(select(func.count()).select_from(PaperTrade))
        await session.execute(
            insert(PaperTrade)
            .values(rows)
            .on_conflict_do_nothing(constraint="uq_paper_trade_signal")
        )
        await session.commit()
        after = await session.scalar(select(func.count()).select_from(PaperTrade))

    inserted = after - before
    print(f"Inserted {inserted}, skipped {len(rows) - inserted} already present.")
    print(f"paper_trades now has {after} row(s).")
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import paper_trades.json into Postgres"
    )
    parser.add_argument("--dry-run", action="store_true")
    asyncio.run(main(parser.parse_args().dry_run))
