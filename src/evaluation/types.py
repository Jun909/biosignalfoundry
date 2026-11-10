from __future__ import annotations

from enum import StrEnum


class DecisionLabel(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    AVOID = "AVOID"
