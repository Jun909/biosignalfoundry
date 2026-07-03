"""
Mock-based test to verify backtesting engine logic without hitting any API.
Patches load_prices so the engine uses hardcoded prices.
"""

import sys
from pathlib import Path

# Make sure the project root is on the path when running this file directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datetime import date
from types import ModuleType
from unittest.mock import patch

# Stub out heavy dependencies before any src imports
_config_stub = ModuleType("config")
_config_stub.MARKETSTACK_API_KEY = "mock-key"  # type: ignore[attr-defined]
sys.modules.setdefault("config", _config_stub)

for _mod in (
    "src.data_providers",
    "src.data_providers.alphavintage",
    "src.data_providers.finnhub",
    "src.data_providers.fred",
    "src.data_providers.massive",
    "src.data_providers.openfda",
    "src.data_providers.sec_edgar",
    "src.data_providers.base",
):
    sys.modules.setdefault(_mod, ModuleType(_mod))

# MarketStackAPIClient must exist on the stub so price_loader can import it
_marketstack_stub = ModuleType("src.data_providers.marketstack")
_marketstack_stub.MarketStackAPIClient = object  # type: ignore[attr-defined]
sys.modules["src.data_providers.marketstack"] = _marketstack_stub

from src.backtesting.engine import run
from src.backtesting.types import BacktestRequest, DecisionLabel, Signal

# ---------------------------------------------------------------------------
# Fake price map: every weekday from 2024-01-01 to 2024-03-31
# We define prices manually for the dates we care about.
# ---------------------------------------------------------------------------
MOCK_PRICES = {
    date(2024, 1, 2): 100.0,  # signal entry (BUY — stock will rise)
    date(2024, 1, 22): 115.0,  # exit after 20 days → +15% → correct BUY
    date(2024, 1, 5): 200.0,  # signal entry (SELL — stock will fall)
    date(2024, 1, 25): 170.0,  # exit after 20 days → -15% → correct SELL
    date(2024, 1, 8): 50.0,  # signal entry (BUY — stock barely moves)
    date(2024, 1, 28): 52.0,  # exit after 20 days → +4% → incorrect BUY (below 10%)
    date(2024, 1, 10): 80.0,  # signal entry (HOLD — stock stays flat)
    date(2024, 1, 30): 83.0,  # exit after 20 days → +3.75% → correct HOLD (within band)
    date(2024, 1, 12): 60.0,  # signal entry (AVOID — stock drops)
    date(2024, 2, 1): 52.0,  # exit after 20 days → -13.3% → correct AVOID
}

SIGNALS = [
    Signal(
        ticker="AAPL",
        as_of_date=date(2024, 1, 2),
        decision=DecisionLabel.BUY,
        rationale="Strong momentum",
        confidence=0.9,
    ),
    Signal(
        ticker="AAPL",
        as_of_date=date(2024, 1, 5),
        decision=DecisionLabel.SELL,
        rationale="Bearish pattern",
        confidence=0.8,
    ),
    Signal(
        ticker="AAPL",
        as_of_date=date(2024, 1, 8),
        decision=DecisionLabel.BUY,
        rationale="Weak signal",
        confidence=0.4,
    ),
    Signal(
        ticker="AAPL",
        as_of_date=date(2024, 1, 10),
        decision=DecisionLabel.HOLD,
        rationale="Neutral outlook",
        confidence=0.6,
    ),
    Signal(
        ticker="AAPL",
        as_of_date=date(2024, 1, 12),
        decision=DecisionLabel.AVOID,
        rationale="Risk off",
        confidence=0.7,
    ),
]

REQUEST = BacktestRequest(
    ticker="AAPL",
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31),
    holding_period_days=20,
    buy_threshold=0.10,
    sell_threshold=-0.10,
)


def test_backtest_engine():
    with patch("src.backtesting.engine.load_prices", return_value=MOCK_PRICES):
        result = run(REQUEST, SIGNALS)

    print(f"\n{'='*55}")
    print(f"  Ticker : {REQUEST.ticker}")
    print(f"  Period : {REQUEST.start_date} → {REQUEST.end_date}")
    print(f"  Hold   : {REQUEST.holding_period_days} days")
    print(
        f"  Thresh : buy≥{REQUEST.buy_threshold*100:.0f}%  sell≤{REQUEST.sell_threshold*100:.0f}%"
    )
    print(f"{'='*55}")
    print(
        f"{'Date':<12} {'Decision':<8} {'Entry':>8} {'Exit':>8} {'Return':>8} {'Correct'}"
    )
    print(f"{'-'*55}")

    for obs in result.observations:
        ret_pct = obs.forward_return * 100
        print(
            f"{obs.as_of_date!s:<12} {obs.decision:<8} "
            f"{obs.entry_price:>8.2f} {obs.exit_price:>8.2f} "
            f"{ret_pct:>+7.1f}%  {'✓' if obs.is_correct else '✗'}"
        )

    print(f"{'='*55}")
    print(f"  Total      : {result.total_observations}")
    print(f"  Correct    : {result.correct_observations}")
    print(f"  Accuracy   : {result.accuracy:.0%}")
    print(f"{'='*55}\n")

    # Assertions
    assert result.total_observations == 5

    by_date = {obs.as_of_date: obs for obs in result.observations}

    assert by_date[date(2024, 1, 2)].is_correct is True, "BUY +15% should be correct"
    assert by_date[date(2024, 1, 5)].is_correct is True, "SELL -15% should be correct"
    assert (
        by_date[date(2024, 1, 8)].is_correct is False
    ), "BUY +4% should be incorrect (below threshold)"
    assert (
        by_date[date(2024, 1, 10)].is_correct is True
    ), "HOLD +3.75% should be correct (within band)"
    assert (
        by_date[date(2024, 1, 12)].is_correct is True
    ), "AVOID -13.3% should be correct"

    print("All assertions passed.")


if __name__ == "__main__":
    test_backtest_engine()
