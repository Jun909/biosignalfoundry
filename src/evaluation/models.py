from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (Boolean, CheckConstraint, Date, DateTime, Enum, Index,
                        Integer, Numeric, String, Text, UniqueConstraint, func)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base
from src.evaluation.types import DecisionLabel


class PaperTrade(Base):
    __tablename__ = "paper_trades"
    __table_args__ = (
        UniqueConstraint(
            "ticker", "signal_date", "system_version", name="uq_paper_trade_signal"
        ),
        CheckConstraint("holding_days > 0", name="ck_holding_days_positive"),
        CheckConstraint("confidence BETWEEN 0 AND 1", name="ck_confidence_range"),
        Index("ix_paper_trades_exit_date", "exit_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    system_version: Mapped[str] = mapped_column(String(32))
    ticker: Mapped[str] = mapped_column(String(16))
    signal_date: Mapped[date] = mapped_column(Date)
    exit_date: Mapped[date] = mapped_column(Date)
    holding_days: Mapped[int] = mapped_column(Integer)
    decision: Mapped[DecisionLabel] = mapped_column(
        Enum(DecisionLabel, name="decision_label")
    )
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4))
    rationale: Mapped[str] = mapped_column(Text)
    entry_price: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    exit_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    forward_return: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    is_correct: Mapped[bool | None] = mapped_column(Boolean)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
