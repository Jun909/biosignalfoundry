"""
Registry of named system versions (v1.0, v1.1, ...) used by paper trading.

A version is a *configuration*: which subagents are enabled, which prompts they
use, and which LLM runs them. The label is the identifier; the git SHA recorded
at registration is metadata only. Versions are defined here, in code, so adding
one is an ordinary reviewed commit.

Once a version has paper trades it must not change. Two checks enforce that:

* ``verify_prompts``   — the hash of the prompts a version names must equal the
                         ``prompt_hash`` pinned in its config, so editing a prompt
                         file in place fails loudly. To change a prompt, copy it
                         under a new name in ``versioning.PROMPTS`` and register a
                         new version.
* ``register_version`` — writes the config to ``system_versions`` on first use and
                         refuses to continue if the stored config later differs.

A version captures configuration and prompts, not tool code: a bug fix in a shared
tool applies to every version run afterwards. ``git_sha`` on the row records which
commit first registered it.

This module deliberately imports no agent or LLM code. Turning a config into a
running agent is the job of the agent factory.
"""

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.versioning import PROMPTS, git_sha, prompt_hash
from src.evaluation.models import SystemVersion

# Subagent names a version may enable. The agent factory maps each name to its
# CompiledSubAgent; add the name here when wiring a new subagent.
KNOWN_SUBAGENTS: frozenset[str] = frozenset({"financial_health"})


class VersionError(Exception):
    """Base class for version registry errors."""


class UnknownVersion(VersionError):
    pass


class VersionDrift(VersionError):
    """A registered version's prompts or config no longer match what was recorded."""


class LLMConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider: str
    model: str
    temperature: float


class VersionConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    description: str
    subagents: tuple[str, ...]
    # Names in ``versioning.PROMPTS`` that this version uses (supervisor + subagents).
    prompts: tuple[str, ...]
    llm: LLMConfig
    # Hash of the prompts above, pinned so an in-place prompt edit is detected.
    prompt_hash: str = Field(min_length=8, max_length=8)

    def snapshot(self) -> dict:
        """The JSON stored in ``system_versions.config``. Excludes the description,
        which is documentation and may be reworded without changing behaviour."""
        return self.model_dump(mode="json", exclude={"description"})


VERSIONS: dict[str, VersionConfig] = {
    "v1.0": VersionConfig(
        description="Baseline: supervisor + financial health subagent only",
        subagents=("financial_health",),
        prompts=("biosignalfoundry", "financial_health_agent"),
        llm=LLMConfig(provider="deepseek", model="deepseek-chat", temperature=0.1),
        prompt_hash="aa847f50",
    ),
}

# Version the API serves. Include the label in the /analyze cache key so changing
# this cannot return a decision made by the previous default.
DEFAULT_VERSION = "v1.0"


def _validate_registry() -> None:
    for label, config in VERSIONS.items():
        unknown_subagents = set(config.subagents) - KNOWN_SUBAGENTS
        if unknown_subagents:
            raise VersionError(
                f"{label}: unknown subagents {sorted(unknown_subagents)}"
            )
        missing_prompts = set(config.prompts) - PROMPTS.keys()
        if missing_prompts:
            raise VersionError(
                f"{label}: prompts {sorted(missing_prompts)} are not in "
                "versioning.PROMPTS"
            )
    if DEFAULT_VERSION not in VERSIONS:
        raise VersionError(f"DEFAULT_VERSION {DEFAULT_VERSION!r} is not registered")


_validate_registry()


def get_version(label: str) -> VersionConfig:
    try:
        return VERSIONS[label]
    except KeyError:
        raise UnknownVersion(
            f"Unknown version {label!r}. Available: {', '.join(VERSIONS)}"
        ) from None


def resolve_labels(spec: str) -> list[str]:
    """Parse a CLI value: ``all`` or comma-separated labels (``v1.0,v1.1``)."""
    if spec.strip().lower() == "all":
        return list(VERSIONS)
    labels = [part.strip() for part in spec.split(",") if part.strip()]
    if not labels:
        raise UnknownVersion("No versions given")
    for label in labels:
        get_version(label)
    return list(dict.fromkeys(labels))


def current_prompt_hash(label: str) -> str:
    config = get_version(label)
    return prompt_hash({name: PROMPTS[name] for name in config.prompts})


def verify_prompts(label: str) -> None:
    """Raise ``VersionDrift`` if the prompts a version uses were edited in place."""
    expected = get_version(label).prompt_hash
    actual = current_prompt_hash(label)
    if actual != expected:
        raise VersionDrift(
            f"Prompts for {label} changed (hash {actual}, pinned {expected}). "
            "Copy the edited prompt under a new name in versioning.PROMPTS and "
            "register a new version instead of changing this one."
        )


async def register_version(session: AsyncSession, label: str) -> SystemVersion:
    """Ensure ``label`` exists in ``system_versions`` and still matches its config.

    Inserts the row on first use. If it already exists with a different config or
    prompt hash, raises ``VersionDrift``. The caller is responsible for committing.
    """
    config = get_version(label)
    verify_prompts(label)

    row = await session.get(SystemVersion, label)
    if row is None:
        row = SystemVersion(
            label=label,
            description=config.description,
            config=config.snapshot(),
            git_sha=git_sha(),
            prompt_hash=config.prompt_hash,
        )
        session.add(row)
        await session.flush()
        return row

    if row.config != config.snapshot() or row.prompt_hash != config.prompt_hash:
        raise VersionDrift(
            f"{label} is already registered with a different configuration. "
            "Register a new version label instead of changing an existing one."
        )
    return row
