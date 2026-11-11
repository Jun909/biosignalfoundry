from typing import Sequence

from sqlalchemy import func, literal_column, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.evaluation.metrics import ReturnRow
from src.evaluation.models import PaperTrade, PaperTradeEvaluation
from src.evaluation.types import DecisionLabel


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


async def load_return_rows(
    session: AsyncSession,
    batch: str | None = None,
    labels: Sequence[str] | None = None,
    horizons: Sequence[int] | None = None,
) -> list[ReturnRow]:
    """Rows of the ``paper_trade_returns`` view as ``ReturnRow``s (read only)."""
    clauses, params = [], {}
    if batch:
        clauses.append("batch = :batch")
        params["batch"] = batch
    if labels:
        clauses.append("version_label = ANY(:labels)")
        params["labels"] = list(labels)
    if horizons:
        clauses.append("horizon_days = ANY(:horizons)")
        params["horizons"] = list(horizons)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    result = await session.execute(
        text(
            "SELECT version_label, ticker, batch, decision, confidence, horizon_days, "
            "forward_return, xbi_return, ibb_return "
            f"FROM paper_trade_returns {where} "
            "ORDER BY version_label, horizon_days, ticker"
        ),
        params,
    )
    return [
        ReturnRow(
            version_label=r.version_label,
            ticker=r.ticker,
            batch=r.batch,
            decision=DecisionLabel(r.decision),
            confidence=float(r.confidence),
            horizon_days=r.horizon_days,
            forward_return=float(r.forward_return),
            xbi_return=float(r.xbi_return),
            ibb_return=float(r.ibb_return),
        )
        for r in result.all()
    ]


async def count_trades(
    session: AsyncSession,
    batch: str | None = None,
    labels: Sequence[str] | None = None,
) -> dict[str, int]:
    """Signals recorded per version label, evaluated or not."""
    stmt = select(PaperTrade.version_label, func.count()).group_by(
        PaperTrade.version_label
    )
    if batch:
        stmt = stmt.where(PaperTrade.batch == batch)
    if labels:
        stmt = stmt.where(PaperTrade.version_label.in_(labels))
    return {label: n for label, n in (await session.execute(stmt)).all()}
