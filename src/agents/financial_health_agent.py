from langchain.agents import create_agent
from deepagents import CompiledSubAgent
from llm_provider import llm
from src.agent_tools.financial_health_agent_tools import get_income_statement_annual, get_company_profile
from src.prompts.financial_health_agent_prompt import financial_health_agent_prompt

financial_health_agent = create_agent(
    model=llm,
    tools=[get_income_statement_annual, get_company_profile],
    system_prompt=financial_health_agent_prompt
)

financial_health_subagent = CompiledSubAgent(
    name="financial_health_agent",
    description="An agent that specializes in checking financial health of biotech companies.",
    runnable=financial_health_agent
)
