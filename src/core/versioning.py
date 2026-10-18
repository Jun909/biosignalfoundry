"""
Automatic system version label for paper trades.

Format: ``<git sha>-<prompt hash>[-dirty]``, e.g. ``1b37f93-9f3e1b2c``.

* git sha     — captures code changes (tools, signal extraction, wiring).
* prompt hash — changes only when prompt text changes, so a README edit moves
                the SHA but not the prompt hash.
* ``-dirty``  — uncommitted tracked changes exist, so the SHA does not fully
                describe what ran.

The SHA comes from the ``GIT_SHA`` env var when set (deployments without a
``.git`` directory, e.g. a Docker build), otherwise from git. If neither is
available it is ``nogit``.
"""

import hashlib
import os
import subprocess
from pathlib import Path

from src.prompts.biosignalfoundry_prompt import biosignalfoundry_prompt
from src.prompts.financial_health_agent_prompt import financial_health_agent_prompt

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Add new agent prompts here so they are covered by the hash.
PROMPTS: dict[str, str] = {
    "biosignalfoundry": biosignalfoundry_prompt,
    "financial_health_agent": financial_health_agent_prompt,
}


def _normalize(text: str) -> str:
    """Ignore line-ending and trailing-whitespace churn."""
    return "\n".join(
        line.rstrip() for line in text.replace("\r\n", "\n").split("\n")
    ).strip()


def prompt_hash(prompts: dict[str, str] | None = None) -> str:
    """8-char hash over all prompts, independent of dict ordering."""
    prompts = PROMPTS if prompts is None else prompts
    digest = hashlib.sha256()
    for name in sorted(prompts):
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update(_normalize(prompts[name]).encode())
        digest.update(b"\0")
    return digest.hexdigest()[:8]


def _git(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=_PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip()


def git_sha() -> str:
    env_sha = os.environ.get("GIT_SHA")
    if env_sha:
        return env_sha[:7]
    return _git("rev-parse", "--short", "HEAD") or "nogit"


def is_dirty() -> bool:
    # Untracked files are ignored: they can't change what the committed code does.
    status = _git("status", "--porcelain", "--untracked-files=no")
    return bool(status)


def system_version() -> str:
    version = f"{git_sha()}-{prompt_hash()}"
    return f"{version}-dirty" if is_dirty() else version
