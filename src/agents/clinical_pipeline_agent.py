from deepagents import CompiledSubAgent
from langchain.agents import create_agent
from pydantic import BaseModel, Field

from src.middleware import LoggingMiddleware


class ClinicalPipelineAgentOutput(BaseModel):
    pipeline_stage: str = Field(
        ...,
        description="Most advanced development stage - Preclinical | Phase 1 | "
        "Phase 2 | Phase 3 | Filed | Approved | Unknown",
    )
    upcoming_catalysts: str = Field(
        ..., description="Upcoming regulatory or clinical catalysts, if any"
    )
    regulatory_history: str = Field(
        ..., description="Past FDA approvals, rejections, recalls or safety actions"
    )
    regulatory_risk_level: str = Field(
        ..., description="Regulatory risk level - Low | Medium | High | Unknown"
    )
    summary: str = Field(..., description="The summary of your findings")
    score: int = Field(..., description="Score from 1 - 10")


# Single source of truth for this subagent's tools: the builder uses it and the version
# registry fingerprints it (see SUBAGENT_TOOLS in src/biosignalfoundry.py).
# Intentionally empty for now: tools are added one at a time after their responses
# are verified. Adding tools later is a new version (see AGENTS.md).
CLINICAL_PIPELINE_TOOLS: list = []


def build_clinical_pipeline_subagent(llm, system_prompt: str) -> CompiledSubAgent:
    agent = create_agent(
        model=llm,
        tools=CLINICAL_PIPELINE_TOOLS,
        system_prompt=system_prompt,
        response_format=ClinicalPipelineAgentOutput,
        middleware=[LoggingMiddleware(agent_name="clinical_pipeline")],
    )
    return CompiledSubAgent(
        name="clinical_pipeline_agent",
        description="An agent that specializes in the clinical and regulatory pipeline of biotech companies (FDA approvals, catalysts, safety signals).",
        runnable=agent,
    )
