from typing import Annotated

from deepagents import create_deep_agent
from langchain.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field

from llm_provider import llm
from src.agents.financial_health_agent import financial_health_subagent
from src.biothrone import biothrone
from src.prompts.biothrone_prompt import biothrone_prompt

current_source = ""

for namespace, chunk in biothrone.stream(
    {"messages": [HumanMessage("Should I invest in Astrazeneca?")]},
    stream_mode="messages",
    subgraphs=True,
):
    token, metadata = chunk

    # Only main agent (empty namespace), ignore all subagent traffic
    if namespace:
        continue

    # if we use response_format
    # for node_name, data in chunk.items():
    #     messages = data.get("messages", [])
    #     if not messages:
    #         continue

    #     last_msg = messages[-1]

    #     # The final structured response is an AIMessage with no tool calls
    #     if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
    #         output = last_msg.additional_kwargs.get("parsed")
    #         if output and isinstance(output, BiothroneOutput):
    #             print(f"Ticker:     {output.ticker}")
    #             print(f"Decision:   {output.decision}")
    #             print(f"Confidence: {output.confidence}")
    #             print(f"Reasoning:  {output.reasoning}")

    # Only AI-generated text tokens, skip tool calls and tool results
    if not isinstance(token, AIMessage):
        continue
    if token.tool_call_chunks:
        continue

    # Stream the final response token by token
    if token.content:
        print(token.content, end="", flush=True)
