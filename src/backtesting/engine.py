from __future__ import annotations

from datetime import timedelta

from src.backtesting.price_loader import load_prices, nearest_price
from src.backtesting.types import (BacktestObservation, BacktestRequest,
                                   BacktestResult, DecisionLabel, Signal)


def _is_correct(
    decision: DecisionLabel, forward_return: float, request: BacktestRequest
) -> bool:
    if decision == DecisionLabel.BUY:
        return forward_return >= request.buy_threshold
    if decision in (DecisionLabel.SELL, DecisionLabel.AVOID):
        return forward_return <= request.sell_threshold
    if decision == DecisionLabel.HOLD:
        return request.sell_threshold < forward_return < request.buy_threshold
    return False


def run(request: BacktestRequest, signals: list[Signal]) -> BacktestResult:
    price_end = request.end_date + timedelta(days=request.holding_period_days + 7)
    prices = load_prices(request.ticker, request.start_date, price_end)

    result = BacktestResult(request=request)

    for signal in signals:
        if signal.ticker != request.ticker:
            continue
        if not (request.start_date <= signal.as_of_date <= request.end_date):
            continue

        exit_date = signal.as_of_date + timedelta(days=request.holding_period_days)

        entry_price = nearest_price(prices, signal.as_of_date)
        exit_price = nearest_price(prices, exit_date)

        if entry_price is None or exit_price is None:
            continue

        forward_return = (exit_price - entry_price) / entry_price

        result.observations.append(
            BacktestObservation(
                ticker=signal.ticker,
                as_of_date=signal.as_of_date,
                exit_date=exit_date,
                decision=signal.decision,
                entry_price=entry_price,
                exit_price=exit_price,
                forward_return=forward_return,
                is_correct=_is_correct(signal.decision, forward_return, request),
                rationale=signal.rationale,
                confidence=signal.confidence,
            )
        )

    return result
