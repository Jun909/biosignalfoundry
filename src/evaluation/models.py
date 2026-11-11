from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (CheckConstraint, Date, DateTime, Enum, ForeignKey,
                        Index, Integer, Numeric, String, Text,
                        UniqueConstraint, func)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base
from src.evaluation.types import DecisionLabel

# Only observations are stored (prices, decisions, raw agent output). Verdicts such as
# forward return, excess return, "correct" or spread are derived at report time, so
# their definitions can change without re-running anything.


class SystemVersion(Base):
    """A named, registered configuration of the system (v1.0, v1.1, ...).

    Treat a row as immutable once signals reference it: change the config by
    registering a new version instead.
    """

    __tablename__ = "system_versions"

    label: Mapped[str] = mapped_column(String(32), primary_key=True)
    description: Mapped[str] = mapped_column(Text)
    # enabled subagents/tools, LLM provider + model, prompt names
    config: Mapped[dict] = mapped_column(JSONB)
    # metadata only: the label is the identifier
    git_sha: Mapped[str | None] = mapped_column(String(40))
    prompt_hash: Mapped[str | None] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class PaperTrade(Base):
    """One decision by one version on one ticker in one batch."""

    __tablename__ = "paper_trades"
    __table_args__ = (
        UniqueConstraint(
            "batch", "version_label", "ticker", name="uq_paper_trade_signal"
        ),
        CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_confidence_range"),
        Index("ix_paper_trades_signal_date", "signal_date"),
        Index("ix_paper_trades_version_label", "version_label"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Groups the versions compared on the same watchlist and date, e.g. "2026-11-a".
    batch: Mapped[str] = mapped_column(String(64))
    version_label: Mapped[str] = mapped_column(
        String(32), ForeignKey("system_versions.label")
    )
    ticker: Mapped[str] = mapped_column(String(16))
    signal_date: Mapped[date] = mapped_column(Date)

    decision: Mapped[DecisionLabel] = mapped_column(
        Enum(DecisionLabel, name="decision_label")
    )
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4))
    rationale: Mapped[str] = mapped_column(Text)
    # Full structured output, including each subagent's output.
    agent_output: Mapped[dict] = mapped_column(JSONB)

    # Entry prices share one date (the last trading day on or before signal_date).
    entry_price_date: Mapped[date] = mapped_column(Date)
    entry_price: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    xbi_entry_price: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    ibb_entry_price: Mapped[Decimal] = mapped_column(Numeric(12, 4))

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class PaperTradeEvaluation(Base):
    """A paper trade priced at one horizon (7, 30, 90 days after the signal)."""

    __tablename__ = "paper_trade_evaluations"
    __table_args__ = (
        UniqueConstraint(
            "paper_trade_id", "horizon_days", name="uq_evaluation_horizon"
        ),
        CheckConstraint("horizon_days > 0", name="ck_horizon_days_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    paper_trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("paper_trades.id", ondelete="CASCADE")
    )
    horizon_days: Mapped[int] = mapped_column(Integer)
    # signal_date + horizon_days, which may fall on a non-trading day...
    target_date: Mapped[date] = mapped_column(Date)
    # ...so this is the trading day actually priced (all three prices share it).
    price_date: Mapped[date] = mapped_column(Date)
    exit_price: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    xbi_exit_price: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    ibb_exit_price: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    # Entry prices re-fetched in the same download as the exit prices. The entry
    # prices on paper_trades were adjusted for splits/dividends as of the signal
    # day, so a split in between would make them incomparable with exit prices.
    # Returns must use these, not the paper_trades entry prices.
    entry_price_adj: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    xbi_entry_price_adj: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    ibb_entry_price_adj: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
