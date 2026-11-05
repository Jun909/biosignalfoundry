from typing import Callable

from deepagents import CompiledSubAgent, create_deep_agent
from langchain.agents.structured_output import AutoStrategy
from pydantic import BaseModel, Field

from llm_provider import llm, make_llm
from src.agents.financial_health_agent import build_financial_health_subagent
from src.core.version_registry import (DEFAULT_VERSION, VersionError,
                                       get_version, verify_prompts)
from src.core.versioning import PROMPTS
from src.middleware.logging_middleware import LoggingMiddleware


class BioSignalFoundryOutput(BaseModel):
    ticker: str = Field(..., description="The ticker of the biotech company")
    decision: str = Field(..., description="Decision made - Buy | Hold | Sell | Avoid")
    confidence: int = Field(..., description="A score from 0 to 100")
    reasoning: str = Field(
        ..., description="The reason behind the decision and the score"
    )


# Subagent name (as used in version configs) -> builder(llm, system_prompt).
# The only list of subagents: register a new one here.
SUBAGENT_BUILDERS: dict[str, Callable[..., CompiledSubAgent]] = {
    "financial_health": build_financial_health_subagent,
}


def build_agent(label: str, model=None):
    """Build the supervisor agent for a registered version.

    The prompts are checked against the version's pinned hash first, so an
    in-place prompt edit raises ``VersionDrift`` instead of silently changing the
    version. ``model`` overrides the version's LLM; paper trading never passes it,
    so a recorded signal always comes from the LLM the version pins.
    """
    config = get_version(label)
    unknown = config.subagents.keys() - SUBAGENT_BUILDERS.keys()
    if unknown:
        raise VersionError(
            f"{label} enables subagents with no builder: {sorted(unknown)}. "
            "Register them in SUBAGENT_BUILDERS."
        )
    verify_prompts(label)

    if model is None:
        model = make_llm(config.llm.provider, config.llm.model, config.llm.temperature)

    subagents = [
        SUBAGENT_BUILDERS[name](model, PROMPTS[prompt_name])
        for name, prompt_name in config.subagents.items()
    ]
    return create_deep_agent(
        model=model,
        system_prompt=PROMPTS[config.supervisor_prompt],
        subagents=subagents,
        response_format=AutoStrategy(BioSignalFoundryOutput),
        middleware=[LoggingMiddleware(agent_name="biosignalfoundry")],
    )


# The API serves the default version with the LLM chosen by LLM_PROVIDER, so local
# development can run on Ollama without a DeepSeek key.
biosignalfoundry = build_agent(DEFAULT_VERSION, model=llm)
