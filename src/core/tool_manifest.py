"""
Fingerprint of the tools a version's subagents expose to the LLM.

A tool's name, description and argument schema are what the model sees, so they act
like a prompt: editing a description changes behaviour. This module reduces them to
a stable hash so a version can pin them the way it pins prompts.

Only that interface is hashed, not the implementation. Implementation fixes that
should apply to every version are allowed by policy (see AGENTS.md); ``git_sha`` on
the ``system_versions`` row points at the code.

Duck-typed on purpose (``name``, ``description``, ``args``): imports no agent or
LangChain code, so ``version_registry`` can use it.
"""

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any


def tool_interface(tool: Any) -> dict:
    """What the LLM sees of one tool. Whitespace in the description is ignored."""
    return {
        "name": tool.name,
        "description": " ".join((tool.description or "").split()),
        "args": tool.args,
    }


def tool_names(tools: Sequence[Any]) -> tuple[str, ...]:
    return tuple(sorted(tool.name for tool in tools))


def tool_hash(tools_by_subagent: Mapping[str, Sequence[Any]]) -> str:
    """8-char hash over every tool interface, independent of ordering."""
    interfaces = {
        subagent: sorted(
            (tool_interface(tool) for tool in tools), key=lambda i: i["name"]
        )
        for subagent, tools in tools_by_subagent.items()
    }
    payload = json.dumps(interfaces, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:8]
