from sqlalchemy import func, literal_column
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.evaluation.models import PaperTrade


async def upsert_signal(session: AsyncSession, values: dict) -> bool:
    """Insert a signal, or replace the same ticker/day/version signal.

    Returns True if a new row was inserted, False if an existing one was updated.
    The caller is responsible for committing.
    """
    stmt = insert(PaperTrade).values(**values)
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
    return (await session.execute(stmt)).scalar_one()
