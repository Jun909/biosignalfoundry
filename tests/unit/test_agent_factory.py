"""
Tests for build_agent in src/biosignalfoundry.py.

conftest stubs `deepagents` and `llm_provider`, so create_deep_agent and make_llm
are mocks here; we assert on what the factory passes to them rather than on a
real agent.
"""

from unittest.mock import MagicMock

import pytest

import src.biosignalfoundry as bsf
from src.core import version_registry as vr
from src.core.versioning import PROMPTS, prompt_hash


@pytest.fixture
def create_deep_agent(monkeypatch):
    mock = MagicMock(name="create_deep_agent")
    monkeypatch.setattr(bsf, "create_deep_agent", mock)
    return mock


@pytest.fixture
def make_llm(monkeypatch):
    mock = MagicMock(name="make_llm")
    monkeypatch.setattr(bsf, "make_llm", mock)
    return mock


@pytest.fixture
def builders(monkeypatch):
    """Replace the real subagent builders with recording mocks."""
    mocks = {name: MagicMock(name=f"build_{name}") for name in bsf.SUBAGENT_BUILDERS}
    monkeypatch.setattr(bsf, "SUBAGENT_BUILDERS", mocks)
    return mocks


@pytest.mark.parametrize("label", list(vr.VERSIONS))
def test_every_registered_version_only_uses_subagents_with_builders(label):
    """Fails in CI if a version names a subagent nobody registered a builder for."""
    assert vr.get_version(label).subagents.keys() <= bsf.SUBAGENT_BUILDERS.keys()


def test_module_level_agent_is_the_default_version_on_the_env_llm():
    # conftest's create_deep_agent returns a shared mock; what matters is that it
    # was built at import time without raising VersionDrift.
    assert bsf.biosignalfoundry is not None


def test_build_agent_passes_version_prompts_and_subagents(
    create_deep_agent, make_llm, builders
):
    config = vr.get_version("v1.0")

    agent = bsf.build_agent("v1.0")

    assert agent is create_deep_agent.return_value
    kwargs = create_deep_agent.call_args.kwargs
    assert kwargs["system_prompt"] == PROMPTS[config.supervisor_prompt]
    assert kwargs["model"] is make_llm.return_value
    builders["financial_health"].assert_called_once_with(
        make_llm.return_value, PROMPTS["financial_health_agent"]
    )
    assert kwargs["subagents"] == [builders["financial_health"].return_value]


def test_build_agent_uses_the_llm_pinned_by_the_version(
    create_deep_agent, make_llm, builders
):
    llm_config = vr.get_version("v1.0").llm

    bsf.build_agent("v1.0")

    make_llm.assert_called_once_with(
        llm_config.provider, llm_config.model, llm_config.temperature
    )


def test_build_agent_model_override_skips_make_llm(
    create_deep_agent, make_llm, builders
):
    override = MagicMock(name="override_llm")

    bsf.build_agent("v1.0", model=override)

    make_llm.assert_not_called()
    assert create_deep_agent.call_args.kwargs["model"] is override
    builders["financial_health"].assert_called_once_with(
        override, PROMPTS["financial_health_agent"]
    )


def test_build_agent_enables_only_the_versions_subagents(
    create_deep_agent, make_llm, builders, monkeypatch
):
    none_enabled = vr.VersionConfig(
        description="supervisor only",
        supervisor_prompt="biosignalfoundry",
        subagents={},
        llm=vr.get_version("v1.0").llm,
        prompt_hash=prompt_hash({"biosignalfoundry": PROMPTS["biosignalfoundry"]}),
    )
    monkeypatch.setitem(vr.VERSIONS, "v0.1", none_enabled)

    bsf.build_agent("v0.1")

    assert create_deep_agent.call_args.kwargs["subagents"] == []
    for builder in builders.values():
        builder.assert_not_called()


def test_build_agent_rejects_a_subagent_without_a_builder(
    create_deep_agent, make_llm, builders, monkeypatch
):
    config = vr.get_version("v1.0")
    bad = config.model_copy(
        update={"subagents": {"astrology": "financial_health_agent"}}
    )
    monkeypatch.setitem(vr.VERSIONS, "v9.0", bad)

    with pytest.raises(vr.VersionError, match="astrology"):
        bsf.build_agent("v9.0")

    make_llm.assert_not_called()
    create_deep_agent.assert_not_called()


def test_build_agent_rejects_unknown_version(create_deep_agent, make_llm):
    with pytest.raises(vr.UnknownVersion):
        bsf.build_agent("v9.9")
    create_deep_agent.assert_not_called()
    make_llm.assert_not_called()


def test_build_agent_refuses_to_build_after_a_prompt_edit(
    create_deep_agent, make_llm, builders, monkeypatch
):
    monkeypatch.setitem(PROMPTS, "financial_health_agent", "edited in place")

    with pytest.raises(vr.VersionDrift):
        bsf.build_agent("v1.0")

    # nothing expensive happens before the drift check
    make_llm.assert_not_called()
    create_deep_agent.assert_not_called()
