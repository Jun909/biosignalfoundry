from deepagents import create_deep_agent
from langchain.agents.structured_output import AutoStrategy
from pydantic import BaseModel, Field

from llm_provider import llm
from src.agents.financial_health_agent import financial_health_subagent
from src.prompts.biosignalfoundry_prompt import biosignalfoundry_prompt


class BioSignalFoundryOutput(BaseModel):
    ticker: str = Field(..., description="The ticker of the biotech company")
    decision: str = Field(..., description="Decision made - Buy | Hold | Sell | Avoid")
    confidence: int = Field(..., description="A score from 0 to 100")
    reasoning: str = Field(
        ..., description="The reason behind the decision and the score"
    )


biosignalfoundry = create_deep_agent(
    model=llm,
    system_prompt=biosignalfoundry_prompt,
    subagents=[financial_health_subagent],
    response_format=AutoStrategy(BioSignalFoundryOutput),
)
