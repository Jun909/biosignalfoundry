import pytest
from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel

from src.core.subagent_capture import (capture_structured_output,
                                       capture_subagent_outputs)


class Out(BaseModel):
    score: int


def inner(response=Out(score=7)):
    state_out = {"messages": ["last"], "structured_response": response}
    return RunnableLambda(lambda s: state_out)


STATE = {"messages": [HumanMessage("analyse MRNA")]}


async def test_captures_typed_output_and_returns_result_unchanged():
    wrapped = capture_structured_output("financial_health_agent", inner())
    with capture_subagent_outputs() as captured:
        result = await wrapped.ainvoke(STATE)
    assert result["messages"] == ["last"]
    assert captured == [
        {
            "subagent": "financial_health_agent",
            "task": "analyse MRNA",
            "output": {"score": 7},
        }
    ]


def test_sync_invoke_is_captured_too():
    wrapped = capture_structured_output("a", inner())
    with capture_subagent_outputs() as captured:
        wrapped.invoke(STATE)
    assert captured[0]["output"] == {"score": 7}


async def test_does_nothing_outside_a_capture_block():
    wrapped = capture_structured_output("a", inner())
    assert (await wrapped.ainvoke(STATE))["structured_response"] == Out(score=7)


async def test_result_without_structured_response_is_not_recorded():
    wrapped = capture_structured_output("a", RunnableLambda(lambda s: {"messages": []}))
    with capture_subagent_outputs() as captured:
        await wrapped.ainvoke(STATE)
    assert captured == []


async def test_collectors_do_not_leak_between_blocks():
    wrapped = capture_structured_output("a", inner())
    with capture_subagent_outputs() as first:
        await wrapped.ainvoke(STATE)
    with capture_subagent_outputs() as second:
        pass
    assert len(first) == 1 and second == []
