"""make_llm lives in the real llm_provider module, which conftest stubs; load the
real file under another name so it can be tested without a network or API keys."""

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import config

_PATH = Path(__file__).resolve().parents[2] / "llm_provider.py"


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setattr(config.settings, "llm_provider", "ollama")
    spec = importlib.util.spec_from_file_location("real_llm_provider", _PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ollama_uses_the_given_model_and_temperature(provider, monkeypatch):
    chat = MagicMock(name="ChatOllama")
    monkeypatch.setattr(provider, "ChatOllama", chat)

    result = provider.make_llm("ollama", "llama3:8b", 0.3)

    chat.assert_called_once_with(model="llama3:8b", temperature=0.3)
    assert result is chat.return_value


def test_deepseek_uses_the_given_model_and_configured_key(provider, monkeypatch):
    chat = MagicMock(name="ChatDeepSeek")
    monkeypatch.setattr(provider, "ChatDeepSeek", chat)
    monkeypatch.setattr(provider.settings, "deepseek_api_key", "sk-test")

    provider.make_llm("deepseek", "deepseek-reasoner", 0.0)

    kwargs = chat.call_args.kwargs
    assert kwargs["model"] == "deepseek-reasoner"
    assert kwargs["temperature"] == 0.0
    assert kwargs["api_key"] == "sk-test"


def test_deepseek_without_a_key_fails_clearly(provider, monkeypatch):
    monkeypatch.setattr(provider.settings, "deepseek_api_key", None)
    with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
        provider.make_llm("deepseek", "deepseek-chat", 0.1)


def test_unknown_provider_is_rejected(provider):
    with pytest.raises(ValueError, match="openai"):
        provider.make_llm("openai", "gpt", 0.1)
