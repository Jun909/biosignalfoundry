from sqlalchemy import func, literal_column
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.evaluation.models import PaperTrade, PaperTradeEvaluation


async def upsert_signal(session: AsyncSession, values: dict) -> bool:
    """Insert a signal, or replace the same batch/version/ticker signal.

    Returns True if a new row was inserted, False if an existing one was updated.
    Replacing a signal deletes its evaluations, since they priced the old entry.
    The caller is responsible for committing.
    """
    stmt = insert(PaperTrade).values(**values)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_paper_trade_signal",
        set_={
            "signal_date": stmt.excluded.signal_date,
            "decision": stmt.excluded.decision,
            "confidence": stmt.excluded.confidence,
            "rationale": stmt.excluded.rationale,
            "agent_output": stmt.excluded.agent_output,
            "entry_price_date": stmt.excluded.entry_price_date,
            "entry_price": stmt.excluded.entry_price,
            "xbi_entry_price": stmt.excluded.xbi_entry_price,
            "ibb_entry_price": stmt.excluded.ibb_entry_price,
            "recorded_at": func.now(),
        },
    ).returning(PaperTrade.id, literal_column("(xmax = 0)").label("inserted"))
    trade_id, inserted = (await session.execute(stmt)).one()
    if not inserted:
        await session.execute(
            PaperTradeEvaluation.__table__.delete().where(
                PaperTradeEvaluation.paper_trade_id == trade_id
            )
        )
    return inserted
