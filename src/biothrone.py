from typing import Annotated

from deepagents import create_deep_agent
from langchain.messages import AIMessage, HumanMessage
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
    response_format=BiothroneOutput,
)
