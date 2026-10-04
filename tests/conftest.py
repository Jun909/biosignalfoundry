"""
Shared test fixtures and module-level stubs.

Why stubs here instead of in each test file:
  conftest.py is loaded by pytest before any test collection begins,
  so sys.modules entries set here are in place before any 'import app'
  or 'import src.*' in test files.  If we stubbed inside a test file,
  a parallel import triggered by another test could beat us to it.
"""

import os
import sys
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock

# ---------------------------------------------------------------------------
# config env var fallbacks
#
# config.py's Settings requires ALPHAVANTAGE_API_KEY, FINNHUB_API_KEY, and
# LLM_PROVIDER at import time (fail-fast validation — see config.py). Unit
# tests must not depend on real secrets being present, so safe dummy values
# are filled in before anything imports config. setdefault() so a real .env
# (e.g. in local dev) still wins over these.
# ---------------------------------------------------------------------------
os.environ.setdefault("ALPHAVANTAGE_API_KEY", "test-alphavantage-key")
os.environ.setdefault("FINNHUB_API_KEY", "test-finnhub-key")
os.environ.setdefault("LLM_PROVIDER", "ollama")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")

# ---------------------------------------------------------------------------
# llm_provider stub
#
# llm_provider.py reads LLM_PROVIDER from the environment and conditionally
# assigns `llm`.  In a test environment that variable is absent, so `llm`
# would be undefined and every module that does `from llm_provider import llm`
# would raise NameError.  We replace the whole module with a safe stub.
# ---------------------------------------------------------------------------
if "llm_provider" not in sys.modules:
    _llm_stub = ModuleType("llm_provider")
    _llm_stub.llm = MagicMock(name="mock_llm")  # type: ignore[attr-defined]
    sys.modules["llm_provider"] = _llm_stub

# ---------------------------------------------------------------------------
# deepagents stub
#
# create_deep_agent() validates that `model` is a string, so passing our
# mock LLM raises TypeError at import time.  We replace the entire module
# so biosignalfoundry.py gets a controlled mock agent instead.
#
# The mock agent is stored on the stub so tests can reach it via:
#   import app as app_module
#   app_module.biosignalfoundry  →  the same mock object
# ---------------------------------------------------------------------------
if "deepagents" not in sys.modules:
    _mock_agent = MagicMock(name="mock_biosignalfoundry_agent")
    _mock_agent.ainvoke = AsyncMock(name="mock_ainvoke")

    _deepagents_stub = ModuleType("deepagents")
    _deepagents_stub.create_deep_agent = MagicMock(  # type: ignore[attr-defined]
        name="create_deep_agent", return_value=_mock_agent
    )
    _deepagents_stub.CompiledSubAgent = MagicMock(name="CompiledSubAgent")  # type: ignore[attr-defined]
    sys.modules["deepagents"] = _deepagents_stub
