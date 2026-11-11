import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import version_registry as vr
from src.core.versioning import PROMPTS
from src.evaluation.models import SystemVersion


def make_config(**overrides) -> vr.VersionConfig:
    values = dict(
        description="test version",
        supervisor_prompt="biosignalfoundry",
        subagents={"financial_health": "financial_health_agent"},
        llm=vr.LLMConfig(provider="deepseek", model="deepseek-chat", temperature=0.1),
        prompt_hash=vr.current_prompt_hash("v1.0"),
    )
    values.update(overrides)
    return vr.VersionConfig(**values)


@pytest.fixture
def fake_session():
    session = MagicMock(name="session")
    session.get = AsyncMock(return_value=None)
    session.flush = AsyncMock()
    return session


# ---------------------------------------------------------------------------
# Registry contents
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("label", list(vr.VERSIONS))
def test_every_registered_version_has_its_pinned_prompt_hash(label):
    """Fails if a prompt used by a registered version was edited in place."""
    vr.verify_prompts(label)


def test_default_version_is_registered():
    assert vr.DEFAULT_VERSION in vr.VERSIONS


def test_baseline_version_is_financial_health_only():
    config = vr.get_version("v1.0")
    assert list(config.subagents) == ["financial_health"]
    assert config.llm.provider == "deepseek"


def test_validate_registry_rejects_unknown_prompt(monkeypatch):
    bad = make_config(supervisor_prompt="does_not_exist")
    monkeypatch.setitem(vr.VERSIONS, "v9.0", bad)
    with pytest.raises(vr.VersionError, match="does_not_exist"):
        vr._validate_registry()


def test_validate_registry_rejects_unregistered_default(monkeypatch):
    monkeypatch.setattr(vr, "DEFAULT_VERSION", "v9.9")
    with pytest.raises(vr.VersionError, match="DEFAULT_VERSION"):
        vr._validate_registry()


# ---------------------------------------------------------------------------
# VersionConfig
# ---------------------------------------------------------------------------
def test_prompt_names_are_sorted_and_deduplicated():
    config = make_config(
        supervisor_prompt="biosignalfoundry",
        subagents={"a": "financial_health_agent", "b": "financial_health_agent"},
    )
    assert config.prompt_names == ("biosignalfoundry", "financial_health_agent")


def test_snapshot_is_json_serialisable_and_excludes_description():
    snapshot = make_config().snapshot()
    assert "description" not in snapshot
    assert snapshot["subagents"] == {"financial_health": "financial_health_agent"}
    assert snapshot["llm"]["temperature"] == 0.1
    json.dumps(snapshot)


def test_config_is_frozen():
    with pytest.raises(Exception):
        make_config().description = "changed"


def test_prompt_hash_must_be_eight_characters():
    with pytest.raises(ValueError):
        make_config(prompt_hash="abc")


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------
def test_get_version_unknown_lists_available_versions():
    with pytest.raises(vr.UnknownVersion, match="v9.9.*Available: v1.0"):
        vr.get_version("v9.9")


def test_resolve_labels_all_returns_every_version():
    assert vr.resolve_labels("all") == list(vr.VERSIONS)
    assert vr.resolve_labels(" ALL ") == list(vr.VERSIONS)


def test_resolve_labels_splits_strips_and_dedupes(monkeypatch):
    monkeypatch.setitem(vr.VERSIONS, "v1.1", make_config())
    assert vr.resolve_labels("v1.1, v1.0 ,v1.1") == ["v1.1", "v1.0"]


@pytest.mark.parametrize("spec", ["", " , ", ","])
def test_resolve_labels_rejects_empty(spec):
    with pytest.raises(vr.UnknownVersion, match="No versions"):
        vr.resolve_labels(spec)


def test_resolve_labels_rejects_unknown_label():
    with pytest.raises(vr.UnknownVersion, match="v7"):
        vr.resolve_labels("v1.0,v7")


# ---------------------------------------------------------------------------
# Prompt drift
# ---------------------------------------------------------------------------
def test_verify_prompts_detects_in_place_edit(monkeypatch):
    monkeypatch.setitem(PROMPTS, "biosignalfoundry", PROMPTS["biosignalfoundry"] + "!")
    with pytest.raises(vr.VersionDrift, match="v1.0 changed|Prompts for v1.0"):
        vr.verify_prompts("v1.0")


def test_verify_prompts_ignores_whitespace_churn(monkeypatch):
    monkeypatch.setitem(
        PROMPTS, "biosignalfoundry", PROMPTS["biosignalfoundry"] + "   \n\n"
    )
    vr.verify_prompts("v1.0")


def test_verify_prompts_ignores_prompts_the_version_does_not_use(monkeypatch):
    monkeypatch.setitem(PROMPTS, "some_future_prompt", "anything")
    vr.verify_prompts("v1.0")


# ---------------------------------------------------------------------------
# register_version
# ---------------------------------------------------------------------------
async def test_register_inserts_new_version(fake_session):
    row = await vr.register_version(fake_session, "v1.0")

    config = vr.get_version("v1.0")
    fake_session.add.assert_called_once_with(row)
    fake_session.flush.assert_awaited_once()
    assert isinstance(row, SystemVersion)
    assert row.label == "v1.0"
    assert row.description == config.description
    assert row.config == config.snapshot()
    assert row.prompt_hash == config.prompt_hash
    assert row.git_sha


async def test_register_existing_identical_version_is_a_no_op(fake_session):
    config = vr.get_version("v1.0")
    existing = SystemVersion(
        label="v1.0",
        description="an older wording",
        config=config.snapshot(),
        git_sha="abc1234",
        prompt_hash=config.prompt_hash,
    )
    fake_session.get.return_value = existing

    row = await vr.register_version(fake_session, "v1.0")

    assert row is existing
    fake_session.add.assert_not_called()
    assert row.git_sha == "abc1234"  # first-registration metadata is kept
    assert row.description == "an older wording"


async def test_register_rejects_changed_config(fake_session):
    config = vr.get_version("v1.0")
    fake_session.get.return_value = SystemVersion(
        label="v1.0",
        description="x",
        config={**config.snapshot(), "subagents": {}},
        prompt_hash=config.prompt_hash,
    )
    with pytest.raises(vr.VersionDrift, match="different configuration"):
        await vr.register_version(fake_session, "v1.0")


async def test_register_rejects_changed_llm(fake_session):
    config = vr.get_version("v1.0")
    stored = config.snapshot()
    stored["llm"] = {**stored["llm"], "temperature": 0.9}
    fake_session.get.return_value = SystemVersion(
        label="v1.0", description="x", config=stored, prompt_hash=config.prompt_hash
    )
    with pytest.raises(vr.VersionDrift):
        await vr.register_version(fake_session, "v1.0")


async def test_register_rejects_changed_stored_prompt_hash(fake_session):
    config = vr.get_version("v1.0")
    fake_session.get.return_value = SystemVersion(
        label="v1.0",
        description="x",
        config=config.snapshot(),
        prompt_hash="00000000",
    )
    with pytest.raises(vr.VersionDrift):
        await vr.register_version(fake_session, "v1.0")


async def test_register_checks_prompts_before_touching_the_database(
    fake_session, monkeypatch
):
    monkeypatch.setitem(PROMPTS, "biosignalfoundry", "edited")
    with pytest.raises(vr.VersionDrift):
        await vr.register_version(fake_session, "v1.0")
    fake_session.get.assert_not_awaited()
    fake_session.add.assert_not_called()


async def test_register_unknown_version(fake_session):
    with pytest.raises(vr.UnknownVersion):
        await vr.register_version(fake_session, "v9.9")
    fake_session.get.assert_not_awaited()
