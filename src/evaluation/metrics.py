"""Evaluation metrics: pure functions over rows of the ``paper_trade_returns`` view.

Nothing here touches the database or the network. Callers load ``ReturnRow``s
(see ``repository.load_return_rows``), usually grouped by version and horizon,
and pass them in. Definitions and thresholds live in this file, not in stored
data, so changing one never requires re-running or re-pricing anything.

Conventions
* Returns are fractions (0.05 = +5%).
* ``excess`` is the stock's return minus the chosen benchmark's return (XBI or
  IBB) over the same window.
* Decisions fall into three sides: BUY, SELL_AVOID (SELL and AVOID together) and
  HOLD. HOLD is left out of the headline metrics (spread, hit rate, calibration,
  loss profile), because it is rewarded simply for the stock not moving.
* Every aggregate carries its N. Intervals are ~95% (normal approximation, Wilson
  for proportions) and are crude with the small samples of an early batch.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Callable, Iterable, Literal, Sequence

from src.evaluation.types import DecisionLabel

Benchmark = Literal["xbi", "ibb"]
Side = Literal["BUY", "SELL_AVOID", "HOLD"]
Outcome = Literal["up", "flat", "down"]

Z95 = 1.96
# An excess return within +/- this band counts as "flat" in the confusion matrix.
FLAT_BAND = 0.02
# Confidence buckets (lower inclusive, upper exclusive) for calibration.
CONFIDENCE_BUCKETS: tuple[tuple[float, float], ...] = (
    (0.0, 0.6),
    (0.6, 0.7),
    (0.7, 0.8),
    (0.8, 1.01),
)


@dataclass(frozen=True, slots=True)
class ReturnRow:
    """One signal priced at one horizon (a row of ``paper_trade_returns``)."""

    version_label: str
    ticker: str
    batch: str
    decision: DecisionLabel
    confidence: float
    horizon_days: int
    forward_return: float
    xbi_return: float
    ibb_return: float


def side(decision: DecisionLabel) -> Side:
    if decision is DecisionLabel.BUY:
        return "BUY"
    if decision is DecisionLabel.HOLD:
        return "HOLD"
    return "SELL_AVOID"


def benchmark_return(row: ReturnRow, benchmark: Benchmark) -> float:
    return row.xbi_return if benchmark == "xbi" else row.ibb_return


def excess_return(row: ReturnRow, benchmark: Benchmark) -> float:
    return row.forward_return - benchmark_return(row, benchmark)


def signed_return(row: ReturnRow) -> float | None:
    """What acting on the call earned: the return for BUY, minus it for SELL/AVOID.
    ``None`` for HOLD."""
    s = side(row.decision)
    if s == "BUY":
        return row.forward_return
    if s == "SELL_AVOID":
        return -row.forward_return
    return None


def signed_excess(row: ReturnRow, benchmark: Benchmark) -> float | None:
    """Excess return in the direction of the call (``None`` for HOLD)."""
    s = side(row.decision)
    if s == "BUY":
        return excess_return(row, benchmark)
    if s == "SELL_AVOID":
        return -excess_return(row, benchmark)
    return None


def is_hit(row: ReturnRow, benchmark: Benchmark) -> bool | None:
    """BUY beat the benchmark / SELL-AVOID trailed it. A tie is not a hit.
    ``None`` for HOLD."""
    value = signed_excess(row, benchmark)
    return None if value is None else value > 0


def directional(rows: Iterable[ReturnRow]) -> list[ReturnRow]:
    """BUY and SELL/AVOID rows only."""
    return [r for r in rows if side(r.decision) != "HOLD"]


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class MeanStat:
    n: int
    mean: float | None
    ci_low: float | None = None
    ci_high: float | None = None


@dataclass(frozen=True, slots=True)
class Proportion:
    n: int
    successes: int
    rate: float | None
    ci_low: float | None = None
    ci_high: float | None = None


def _variance(values: Sequence[float]) -> float:
    m = sum(values) / len(values)
    return sum((v - m) ** 2 for v in values) / (len(values) - 1)


def mean_stat(values: Sequence[float]) -> MeanStat:
    n = len(values)
    if n == 0:
        return MeanStat(0, None)
    mean = sum(values) / n
    if n < 2:
        return MeanStat(n, mean)
    half = Z95 * sqrt(_variance(values) / n)
    return MeanStat(n, mean, mean - half, mean + half)


def proportion(successes: int, n: int) -> Proportion:
    """Rate with a Wilson 95% interval."""
    if n == 0:
        return Proportion(0, 0, None)
    p = successes / n
    denom = 1 + Z95**2 / n
    centre = (p + Z95**2 / (2 * n)) / denom
    half = Z95 * sqrt(p * (1 - p) / n + Z95**2 / (4 * n**2)) / denom
    return Proportion(n, successes, p, max(0.0, centre - half), min(1.0, centre + half))


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def mean_excess_return(rows: Sequence[ReturnRow], benchmark: Benchmark) -> MeanStat:
    return mean_stat([excess_return(r, benchmark) for r in rows])


@dataclass(frozen=True, slots=True)
class Spread:
    """Mean forward return of BUY calls minus that of SELL/AVOID calls."""

    n_buy: int
    n_sell_avoid: int
    buy_mean: float | None
    sell_avoid_mean: float | None
    spread: float | None
    ci_low: float | None = None
    ci_high: float | None = None


def spread(rows: Sequence[ReturnRow]) -> Spread:
    """The headline metric: a system with skill favours stocks that do better than
    the ones it dislikes, whichever way the market moves. Needs both sides; the
    interval (Welch) needs at least two calls on each."""
    buys = [r.forward_return for r in rows if side(r.decision) == "BUY"]
    sells = [r.forward_return for r in rows if side(r.decision) == "SELL_AVOID"]
    buy_mean = sum(buys) / len(buys) if buys else None
    sell_mean = sum(sells) / len(sells) if sells else None
    if buy_mean is None or sell_mean is None:
        return Spread(len(buys), len(sells), buy_mean, sell_mean, None)
    value = buy_mean - sell_mean
    if len(buys) < 2 or len(sells) < 2:
        return Spread(len(buys), len(sells), buy_mean, sell_mean, value)
    se = sqrt(_variance(buys) / len(buys) + _variance(sells) / len(sells))
    return Spread(
        len(buys),
        len(sells),
        buy_mean,
        sell_mean,
        value,
        value - Z95 * se,
        value + Z95 * se,
    )


@dataclass(frozen=True, slots=True)
class HitRate:
    overall: Proportion  # BUY + SELL/AVOID
    by_side: dict[str, Proportion]  # "BUY", "SELL_AVOID"


def hit_rate(rows: Sequence[ReturnRow], benchmark: Benchmark) -> HitRate:
    counts: dict[str, list[int]] = {"BUY": [0, 0], "SELL_AVOID": [0, 0]}
    for r in directional(rows):
        bucket = counts[side(r.decision)]
        bucket[1] += 1
        bucket[0] += bool(is_hit(r, benchmark))
    by_side = {k: proportion(*v) for k, v in counts.items()}
    total = [sum(v[0] for v in counts.values()), sum(v[1] for v in counts.values())]
    return HitRate(proportion(*total), by_side)


@dataclass(frozen=True, slots=True)
class Baselines:
    """What simple strategies score on the same rows, to read results against."""

    n: int
    # Treat every signal as BUY: mean forward / excess return, share beating the benchmark.
    always_buy_mean_return: float | None
    always_buy_mean_excess: float | None
    always_buy_hit_rate: float | None
    # Hold cash: earns 0, so it trails the benchmark by the benchmark's return.
    always_hold_mean_excess: float | None
    # Expected hit rate of a coin flip between BUY and SELL/AVOID on every signal.
    random_hit_rate: float | None
    benchmark_mean_return: float | None


def baselines(rows: Sequence[ReturnRow], benchmark: Benchmark) -> Baselines:
    n = len(rows)
    if n == 0:
        return Baselines(0, None, None, None, None, None, None)
    excess = [excess_return(r, benchmark) for r in rows]
    bench = [benchmark_return(r, benchmark) for r in rows]
    up = sum(e > 0 for e in excess) / n
    down = sum(e < 0 for e in excess) / n
    return Baselines(
        n=n,
        always_buy_mean_return=sum(r.forward_return for r in rows) / n,
        always_buy_mean_excess=sum(excess) / n,
        always_buy_hit_rate=up,
        always_hold_mean_excess=-sum(bench) / n,
        random_hit_rate=(up + down) / 2,
        benchmark_mean_return=sum(bench) / n,
    )


SIDES: tuple[Side, ...] = ("BUY", "HOLD", "SELL_AVOID")
OUTCOMES: tuple[Outcome, ...] = ("up", "flat", "down")


def outcome(
    row: ReturnRow, benchmark: Benchmark, flat_band: float = FLAT_BAND
) -> Outcome:
    e = excess_return(row, benchmark)
    if e > flat_band:
        return "up"
    if e < -flat_band:
        return "down"
    return "flat"


def confusion_matrix(
    rows: Sequence[ReturnRow], benchmark: Benchmark, flat_band: float = FLAT_BAND
) -> dict[Side, dict[Outcome, int]]:
    """Decision side (BUY / HOLD / SELL+AVOID) vs realised outcome relative to the
    benchmark. A diagnostic for systematic habits (e.g. never SELL), not a score."""
    matrix: dict[Side, dict[Outcome, int]] = {
        s: {o: 0 for o in OUTCOMES} for s in SIDES
    }
    for r in rows:
        matrix[side(r.decision)][outcome(r, benchmark, flat_band)] += 1
    return matrix


@dataclass(frozen=True, slots=True)
class CalibrationBucket:
    low: float
    high: float
    hits: Proportion
    mean_signed_excess: MeanStat


def calibration(
    rows: Sequence[ReturnRow],
    benchmark: Benchmark,
    buckets: Sequence[tuple[float, float]] = CONFIDENCE_BUCKETS,
) -> list[CalibrationBucket]:
    """Do high-confidence calls do better than low-confidence ones? Directional
    calls only. Empty buckets are returned with N = 0."""
    result = []
    for low, high in buckets:
        in_bucket = [r for r in directional(rows) if low <= r.confidence < high]
        hits = sum(bool(is_hit(r, benchmark)) for r in in_bucket)
        result.append(
            CalibrationBucket(
                low,
                high,
                proportion(hits, len(in_bucket)),
                mean_stat([signed_excess(r, benchmark) for r in in_bucket]),
            )
        )
    return result


@dataclass(frozen=True, slots=True)
class LossProfile:
    """Per-call outcome of acting on each directional call (signed forward return)."""

    n: int
    n_wins: int
    n_losses: int
    average_win: float | None
    average_loss: float | None  # negative
    worst_loss: float | None  # negative
    best_win: float | None


def loss_profile(rows: Sequence[ReturnRow]) -> LossProfile:
    """Worst single-call loss and average win vs average loss. Maximum drawdown
    needs a simulated basket over time, so it is not a per-signal metric here."""
    values = [v for r in rows if (v := signed_return(r)) is not None]
    wins = [v for v in values if v > 0]
    losses = [v for v in values if v < 0]
    return LossProfile(
        n=len(values),
        n_wins=len(wins),
        n_losses=len(losses),
        average_win=sum(wins) / len(wins) if wins else None,
        average_loss=sum(losses) / len(losses) if losses else None,
        worst_loss=min(losses) if losses else None,
        best_win=max(wins) if wins else None,
    )


# ---------------------------------------------------------------------------
# Bundling
# ---------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class MetricsSummary:
    n: int
    benchmark: Benchmark
    mean_excess_return: MeanStat
    spread: Spread
    hit_rate: HitRate
    baselines: Baselines
    confusion: dict[Side, dict[Outcome, int]]
    calibration: list[CalibrationBucket]
    loss_profile: LossProfile


def summarize(
    rows: Sequence[ReturnRow], benchmark: Benchmark = "xbi"
) -> MetricsSummary:
    """All metrics for one set of rows. Pass rows of a single version and horizon;
    mixing horizons or versions would blur what the numbers mean."""
    return MetricsSummary(
        n=len(rows),
        benchmark=benchmark,
        mean_excess_return=mean_excess_return(rows, benchmark),
        spread=spread(rows),
        hit_rate=hit_rate(rows, benchmark),
        baselines=baselines(rows, benchmark),
        confusion=confusion_matrix(rows, benchmark),
        calibration=calibration(rows, benchmark),
        loss_profile=loss_profile(rows),
    )


def group_rows(
    rows: Iterable[ReturnRow], key: Callable[[ReturnRow], object]
) -> dict[object, list[ReturnRow]]:
    groups: dict[object, list[ReturnRow]] = {}
    for r in rows:
        groups.setdefault(key(r), []).append(r)
    return groups
