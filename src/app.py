from deepagents import create_deep_agent
from llm_provider import llm
from src.agents.financial_health_agent import financial_health_subagent
from src.prompts.biothrone_prompt import biothrone_prompt
from langchain.messages import HumanMessage

biothrone = create_deep_agent(
    model=llm,
    system_prompt=biothrone_prompt,
    subagents=[financial_health_subagent]
)

result = biothrone.invoke(
    {"messages": [HumanMessage("Should I invest in Eli Lilly and Co?")]},
)

print(result)