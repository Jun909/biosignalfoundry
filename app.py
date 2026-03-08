from typing import Annotated

from deepagents import create_deep_agent
from langchain.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field

from llm_provider import llm
from src.agents.financial_health_agent import financial_health_subagent
from src.prompts.biothrone_prompt import biothrone_prompt


class BiothroneOutput(BaseModel):
    ticker: str = Field(..., description="The ticker of the biotech company")
    decision: str = Field(..., description="Decision made - Buy | Hold | Sell | Avoid")
    confidence: int = Field(..., description="A score from 0 to 100")
    reasoning: str = Field(
        ..., description="The reason behind the decision and the score"
    )


biothrone = create_deep_agent(
    model=llm,
    system_prompt=biothrone_prompt,
    subagents=[financial_health_subagent],
    # response_format=BiothroneOutput,
)


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

    # Only AI-generated text tokens, skip tool calls and tool results
    if not isinstance(token, AIMessage):
        continue
    if token.tool_call_chunks:
        continue

    # Stream the final response token by token
    if token.content:
        print(token.content, end="", flush=True)
