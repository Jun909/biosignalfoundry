import pytest

from src.evaluation import metrics as m
from src.evaluation.types import DecisionLabel as D


def row(decision, ret, xbi=0.0, conf=0.8, ibb=0.0, ticker="T", version="v1.0", h=30):
    return m.ReturnRow(version, ticker, "b", decision, conf, h, ret, xbi, ibb)


def test_excess_and_sides():
    r = row(D.AVOID, -0.10, xbi=0.02)
    assert m.excess_return(r, "xbi") == pytest.approx(-0.12)
    assert m.side(D.SELL) == m.side(D.AVOID) == "SELL_AVOID"
    assert m.signed_return(r) == pytest.approx(0.10)
    assert m.signed_excess(r, "xbi") == pytest.approx(0.12)
    assert m.signed_return(row(D.HOLD, 0.01)) is None


def test_hit_rate_ignores_hold_and_ties():
    rows = [
        row(D.BUY, 0.10),  # hit
        row(D.BUY, -0.05),  # miss
        row(D.SELL, -0.08),  # hit
        row(D.AVOID, 0.0),  # tie -> not a hit
        row(D.HOLD, 0.0),  # excluded
    ]
    h = m.hit_rate(rows, "xbi")
    assert (h.overall.successes, h.overall.n) == (2, 4)
    assert h.by_side["BUY"].rate == 0.5
    assert h.by_side["SELL_AVOID"].rate == 0.5


def test_spread_buy_minus_sell_avoid_uses_forward_return():
    rows = [
        row(D.BUY, 0.10),
        row(D.BUY, 0.20),
        row(D.SELL, -0.10),
        row(D.AVOID, 0.00),
        row(D.HOLD, 0.50),
    ]
    s = m.spread(rows)
    assert (s.n_buy, s.n_sell_avoid) == (2, 2)
    assert s.buy_mean == pytest.approx(0.15)
    assert s.sell_avoid_mean == pytest.approx(-0.05)
    assert s.spread == pytest.approx(0.20)
    assert s.ci_low < s.spread < s.ci_high


def test_spread_needs_both_sides():
    s = m.spread([row(D.BUY, 0.1), row(D.HOLD, 0.0)])
    assert s.spread is None and s.n_buy == 1 and s.n_sell_avoid == 0
    assert m.spread([]).spread is None


def test_spread_has_no_interval_with_single_calls():
    s = m.spread([row(D.BUY, 0.1), row(D.SELL, -0.1)])
    assert s.spread == pytest.approx(0.2) and s.ci_low is None


def test_mean_stat_and_proportion_edge_cases():
    assert m.mean_stat([]).mean is None
    one = m.mean_stat([0.1])
    assert one.mean == 0.1 and one.ci_low is None
    two = m.mean_stat([0.0, 0.2])
    assert two.mean == pytest.approx(0.1) and two.ci_low < 0.1 < two.ci_high
    assert m.proportion(0, 0).rate is None
    p = m.proportion(5, 10)
    assert p.rate == 0.5 and 0 < p.ci_low < 0.5 < p.ci_high < 1


def test_baselines():
    rows = [
        row(D.SELL, 0.10, xbi=0.02),
        row(D.SELL, -0.10, xbi=0.02),
        row(D.HOLD, 0.02, xbi=0.02),
    ]
    b = m.baselines(rows, "xbi")
    assert b.n == 3
    assert b.always_buy_mean_return == pytest.approx(0.02 / 3)
    assert b.always_buy_hit_rate == pytest.approx(1 / 3)  # only the +8% excess
    assert b.random_hit_rate == pytest.approx((1 / 3 + 1 / 3) / 2)
    assert b.always_hold_mean_excess == pytest.approx(-0.02)
    assert b.benchmark_mean_return == pytest.approx(0.02)
    assert m.baselines([], "xbi").n == 0


def test_confusion_matrix_uses_flat_band():
    rows = [
        row(D.BUY, 0.10),  # up
        row(D.BUY, 0.01),  # flat
        row(D.SELL, 0.10),  # up (a SELL on a riser)
        row(D.AVOID, -0.10),  # down
        row(D.HOLD, -0.03),  # down
    ]
    c = m.confusion_matrix(rows, "xbi")
    assert c["BUY"] == {"up": 1, "flat": 1, "down": 0}
    assert c["SELL_AVOID"] == {"up": 1, "flat": 0, "down": 1}
    assert c["HOLD"] == {"up": 0, "flat": 0, "down": 1}


def test_calibration_buckets_directional_calls_only():
    rows = [
        row(D.BUY, 0.10, conf=0.9),
        row(D.BUY, -0.10, conf=0.9),
        row(D.SELL, -0.10, conf=0.5),
        row(D.HOLD, 0.0, conf=0.9),
    ]
    buckets = {(b.low, b.high): b for b in m.calibration(rows, "xbi")}
    assert buckets[(0.8, 1.01)].hits.n == 2 and buckets[(0.8, 1.01)].hits.rate == 0.5
    assert buckets[(0.0, 0.6)].hits.rate == 1.0
    assert buckets[(0.6, 0.7)].hits.n == 0


def test_loss_profile():
    rows = [
        row(D.BUY, 0.20),
        row(D.BUY, -0.30),
        row(D.SELL, 0.10),  # stock rose: a loss
        row(D.AVOID, -0.10),  # win
        row(D.HOLD, 0.9),
    ]
    lp = m.loss_profile(rows)
    assert (lp.n, lp.n_wins, lp.n_losses) == (4, 2, 2)
    assert lp.average_win == pytest.approx(0.15)
    assert lp.average_loss == pytest.approx(-0.20)
    assert lp.worst_loss == pytest.approx(-0.30)
    assert m.loss_profile([row(D.HOLD, 0.1)]).worst_loss is None


def test_benchmark_choice_changes_excess():
    r = row(D.BUY, 0.05, xbi=0.0, ibb=0.10)
    assert m.is_hit(r, "xbi") is True
    assert m.is_hit(r, "ibb") is False


def test_summarize_and_group_rows():
    rows = [row(D.BUY, 0.1, h=7), row(D.SELL, -0.1, h=30)]
    groups = m.group_rows(rows, lambda r: r.horizon_days)
    assert set(groups) == {7, 30}
    s = m.summarize(groups[30], "ibb")
    assert s.n == 1 and s.benchmark == "ibb" and s.spread.n_sell_avoid == 1
    assert m.summarize([]).n == 0
