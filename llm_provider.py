from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama

from config import settings


def make_llm(provider: str, model: str, temperature: float):
    """Build a chat model. Used by the agent factory to honour a version's LLM config."""
    if provider == "ollama":
        return ChatOllama(model=model, temperature=temperature)
    if provider == "deepseek":
        if not settings.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is required for the deepseek provider")
        return ChatDeepSeek(
            model=model,  # "deepseek-chat" or "deepseek-reasoner"
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=settings.deepseek_api_key,  # type: ignore
            base_url="https://api.deepseek.com",
        )
    raise ValueError(f"Unknown LLM provider: {provider!r}")


# Default model for the API, chosen by LLM_PROVIDER. Paper-trading versions pin
# their own provider/model in src/core/version_registry.py instead.
_DEFAULT_MODELS = {"ollama": "mistral:latest", "deepseek": "deepseek-chat"}

llm = make_llm(
    settings.llm_provider, _DEFAULT_MODELS[settings.llm_provider], temperature=0.1
)
