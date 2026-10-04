from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama

from config import settings

if settings.llm_provider == "ollama":
    llm = ChatOllama(
        model="mistral:latest",
        temperature=0.1,
    )
elif settings.llm_provider == "deepseek":
    llm = ChatDeepSeek(
        model="deepseek-chat",  # or "deepseek-reasoner"
        temperature=0.1,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=settings.deepseek_api_key,  # type: ignore
        base_url="https://api.deepseek.com",
    )
