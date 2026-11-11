from deepagents import CompiledSubAgent
from langchain.agents import create_agent
from pydantic import BaseModel, Field

from src.agent_tools.financial_health_agent_tools import (
    get_company_profile, get_income_statement_annual)
from src.middleware import LoggingMiddleware


class FinancialHealthAgentOutput(BaseModel):
    revenue_trend: str = Field(..., description="The revenue trend of the company")
    net_income_trend: str = Field(
        ..., description="The net income trend of the company"
    )
    profitability_status: str = Field(
        ..., description="The profitability status of the company"
    )
    business_stage: str = Field(..., description="The business stage of the company")
    financial_risk_level: str = Field(
        ..., description="Financial risk level - Low | Medium | High"
    )
    summary: str = Field(..., description="The summary of your findings")
    score: int = Field(..., description="Score from 1 - 10")


def build_financial_health_subagent(llm, system_prompt: str) -> CompiledSubAgent:
    agent = create_agent(
        model=llm,
        tools=[get_income_statement_annual, get_company_profile],
        system_prompt=system_prompt,
        response_format=FinancialHealthAgentOutput,
        middleware=[LoggingMiddleware(agent_name="financial_health")],
    )
    return CompiledSubAgent(
        name="financial_health_agent",
        description="An agent that specializes in checking financial health of biotech companies.",
        runnable=agent,
    )
