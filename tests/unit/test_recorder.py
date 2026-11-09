from datetime import date
from decimal import Decimal

import pytest
from langchain.messages import AIMessage, ToolMessage

from src.evaluation import recorder
from src.evaluation.price_loader import latest_common_date
from src.evaluation.types import DecisionLabel
from src.evaluation.watchlist import BENCHMARKS, WATCHLIST

# ---------------------------------------------------------------------------
# Watchlist
# ---------------------------------------------------------------------------


def test_watchlist_has_thirty_unique_valid_tickers():
    assert len(WATCHLIST) == 30
    assert len(set(WATCHLIST)) == 30
    assert all(recorder.TICKER_RE.match(t) for t in WATCHLIST)


def test_watchlist_does_not_contain_the_benchmarks():
    assert set(WATCHLIST).isdisjoint(BENCHMARKS)
    assert BENCHMARKS == ("XBI", "IBB")


# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", ["2026-11-a", "test_1", "v1.0.run", "A" * 64])
def test_valid_batch_names(name):
    assert recorder.validate_batch_name(name) == name


@pytest.mark.parametrize("name", ["", "has space", "slash/name", "A" * 65, "naïve"])
def test_invalid_batch_names(name):
    with pytest.raises(recorder.BatchError, match="Invalid batch name"):
        recorder.validate_batch_name(name)


def test_normalize_tickers_uppercases_strips_and_dedupes():
    assert recorder.normalize_tickers([" mrna", "GILD", "mrna", ""]) == [
        "MRNA",
        "GILD",
    ]


def test_normalize_tickers_accepts_class_share_symbols():
    assert recorder.normalize_tickers(["brk.b"]) == ["BRK.B"]


@pytest.mark.parametrize(
    "bad", [["MR NA"], ["1ABC"], ["TOOLONGTICKERSYMBOLS"], ["A;B"]]
)
def test_normalize_tickers_rejects_malformed(bad):
    with pytest.raises(recorder.BatchError, match="Invalid ticker"):
        recorder.normalize_tickers(bad)


@pytest.mark.parametrize("empty", [[], [" "], [""]])
def test_normalize_tickers_rejects_empty(empty):
    with pytest.raises(recorder.BatchError, match="No tickers"):
        recorder.normalize_tickers(empty)


# ---------------------------------------------------------------------------
# Agent output parsing
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Buy", DecisionLabel.BUY),
        (" SELL ", DecisionLabel.SELL),
        ("hold", DecisionLabel.HOLD),
        ("Avoid", DecisionLabel.AVOID),
    ],
)
def test_parse_decision(raw, expected):
    assert recorder.parse_decision(raw) is expected


def test_parse_decision_rejects_unknown_label():
    with pytest.raises(ValueError, match="Unknown decision"):
        recorder.parse_decision("strong buy")


@pytest.mark.parametrize(
    "raw, expected", [(75, "0.75"), (0, "0.00"), (100, "1.00"), (5, "0.05")]
)
def test_parse_confidence_scales_to_zero_one(raw, expected):
    assert recorder.parse_confidence(raw) == Decimal(expected)


@pytest.mark.parametrize("raw", [-1, 101])
def test_parse_confidence_rejects_out_of_range(raw):
    with pytest.raises(ValueError, match="out of range"):
        recorder.parse_confidence(raw)


# ---------------------------------------------------------------------------
# Subagent output extraction
# ---------------------------------------------------------------------------
def _task_call(call_id: str, subagent: str = "financial_health_agent") -> dict:
    return {
        "name": "task",
        "id": call_id,
        "args": {"subagent_type": subagent, "description": "analyse MRNA"},
    }


def test_extract_matches_task_calls_to_their_results_and_parses_json():
    messages = [
        AIMessage(content="", tool_calls=[_task_call("c1")]),
        ToolMessage(content='{"score": 4, "summary": "weak"}', tool_call_id="c1"),
    ]

    assert recorder.extract_subagent_outputs(messages) == [
        {
            "subagent": "financial_health_agent",
            "task": "analyse MRNA",
            "output": {"score": 4, "summary": "weak"},
        }
    ]


def test_extract_keeps_non_json_content_as_text():
    messages = [
        AIMessage(content="", tool_calls=[_task_call("c1")]),
        ToolMessage(content="Score: 4/10, weak", tool_call_id="c1"),
    ]
    assert recorder.extract_subagent_outputs(messages)[0]["output"] == (
        "Score: 4/10, weak"
    )


def test_extract_returns_one_entry_per_subagent_call():
    messages = [
        AIMessage(
            content="",
            tool_calls=[_task_call("c1"), _task_call("c2", "sentiment_agent")],
        ),
        ToolMessage(content='{"a": 1}', tool_call_id="c1"),
        ToolMessage(content='{"b": 2}', tool_call_id="c2"),
    ]
    result = recorder.extract_subagent_outputs(messages)
    assert [r["subagent"] for r in result] == [
        "financial_health_agent",
        "sentiment_agent",
    ]


def test_extract_ignores_other_tools_and_unmatched_results():
    other_call = {"name": "write_todos", "id": "c9", "args": {}}
    messages = [
        AIMessage(content="", tool_calls=[other_call]),
        ToolMessage(content="ok", tool_call_id="c9"),
        ToolMessage(content="orphan", tool_call_id="nope"),
    ]
    assert recorder.extract_subagent_outputs(messages) == []


def test_extract_handles_no_messages():
    assert recorder.extract_subagent_outputs([]) == []


# ---------------------------------------------------------------------------
# latest_common_date / entry prices
# ---------------------------------------------------------------------------
D = date  # brevity


def test_latest_common_date_prefers_the_signal_date_when_all_have_it():
    maps = [{D(2026, 11, 6): 1.0}, {D(2026, 11, 6): 2.0}]
    assert latest_common_date(maps, D(2026, 11, 6)) == D(2026, 11, 6)


def test_latest_common_date_falls_back_to_the_latest_shared_day():
    stock = {D(2026, 11, 4): 1.0, D(2026, 11, 5): 1.1}
    etf = {D(2026, 11, 4): 9.0, D(2026, 11, 5): 9.1, D(2026, 11, 6): 9.2}
    assert latest_common_date([stock, etf], D(2026, 11, 6)) == D(2026, 11, 5)


def test_latest_common_date_none_when_nothing_is_shared():
    assert (
        latest_common_date(
            [{D(2026, 11, 1): 1.0}, {D(2026, 11, 2): 1.0}], D(2026, 11, 6)
        )
        is None
    )


def test_latest_common_date_respects_the_lookback_limit():
    maps = [{D(2026, 10, 20): 1.0}]
    assert latest_common_date(maps, D(2026, 11, 6), max_lookback=7) is None
    assert latest_common_date(maps, D(2026, 11, 6), max_lookback=20) == D(2026, 10, 20)


def test_latest_common_date_ignores_future_days():
    maps = [{D(2026, 11, 9): 1.0}]
    assert latest_common_date(maps, D(2026, 11, 6)) is None


def _bench():
    return {
        "XBI": {D(2026, 11, 5): 100.0, D(2026, 11, 6): 101.0},
        "IBB": {D(2026, 11, 5): 140.0, D(2026, 11, 6): 141.0},
    }


def test_fetch_entry_prices_uses_one_shared_day_for_stock_and_benchmarks():
    stock = {D(2026, 11, 5): 46.88123, D(2026, 11, 6): 47.5}
    entry = recorder.fetch_entry_prices(
        "MRNA", D(2026, 11, 6), _bench(), price_fn=lambda *a: stock
    )
    assert entry.price_date == D(2026, 11, 6)
    assert (entry.stock, entry.xbi, entry.ibb) == (
        Decimal("47.5"),
        Decimal("101.0"),
        Decimal("141.0"),
    )


def test_fetch_entry_prices_steps_back_together_when_the_stock_lacks_the_latest_day():
    stock = {D(2026, 11, 5): 46.88123}  # e.g. halted on the 6th
    entry = recorder.fetch_entry_prices(
        "MRNA", D(2026, 11, 6), _bench(), price_fn=lambda *a: stock
    )
    assert entry.price_date == D(2026, 11, 5)
    assert entry.stock == Decimal("46.8812")
    assert entry.xbi == Decimal("100.0")  # the benchmark's price on the same day
    assert entry.ibb == Decimal("140.0")


def test_fetch_entry_prices_fails_without_stock_data():
    with pytest.raises(RuntimeError, match="No price data for XYZ"):
        recorder.fetch_entry_prices(
            "XYZ", D(2026, 11, 6), _bench(), price_fn=lambda *a: {}
        )


def test_fetch_entry_prices_fails_without_a_shared_trading_day():
    stock = {D(2026, 10, 1): 5.0}
    with pytest.raises(RuntimeError, match="No trading day"):
        recorder.fetch_entry_prices(
            "XYZ", D(2026, 11, 6), _bench(), price_fn=lambda *a: stock
        )
