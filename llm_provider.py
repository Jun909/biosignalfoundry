from os import getenv

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama

load_dotenv()

LLM_PROVIDER = getenv("LLM_PROVIDER")

if LLM_PROVIDER == "ollama":
    llm = ChatOllama(
        model="mistral:latest",
        temperature=0.1,
    )
elif LLM_PROVIDER == "deepseek":
    llm = ChatDeepSeek(
        model="deepseek-chat",  # or "deepseek-reasoner"
        temperature=0.1,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=getenv("DEEPSEEK_API_KEY"),  # type: ignore
        base_url="https://api.deepseek.com",
    )
