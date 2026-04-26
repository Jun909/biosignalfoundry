from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class DecisionLabel(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    AVOID = "AVOID"


@dataclass(slots=True)
class BacktestRequest:
    ticker: str
    start_date: date
    end_date: date
    holding_period_days: int = 20
    buy_threshold: float = 0.10 #10%
    sell_threshold: float = -0.10 #10%


@dataclass(slots=True)
class Signal:
    ticker: str
    as_of_date: date
    decision: DecisionLabel
    rationale: str | None = None
    confidence: float | None = None


@dataclass(slots=True)
class BacktestObservation:
    ticker: str
    as_of_date: date
    exit_date: date
    decision: DecisionLabel
    entry_price: float
    exit_price: float
    forward_return: float
    is_correct: bool
    rationale: str | None = None
    confidence: float | None = None


@dataclass(slots=True)
class BacktestResult:
    request: BacktestRequest
    observations: list[BacktestObservation] = field(default_factory=list)

    @property
    def total_observations(self) -> int:
        return len(self.observations)

    @property
    def correct_observations(self) -> int:
        return sum(1 for observation in self.observations if observation.is_correct)

    @property
    def accuracy(self) -> float:
        if not self.observations:
            return 0.0
        return self.correct_observations / self.total_observations
