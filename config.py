from typing import Literal
from urllib.parse import quote_plus

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # Postgres
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str

    # Provider API keys
    alphavantage_api_key: str
    finnhub_api_key: str
    marketstack_api_key: str | None = None
    # other providers (in the future when we wire them up)

    # LLM provider
    llm_provider: Literal["ollama", "deepseek"]
    deepseek_api_key: str | None = None

    # App
    log_level: str = "INFO"
    env: str = "development"
    allowed_origins: str = "http://localhost:5173"

    # Abuse / cost control on /analyze
    rate_limit_per_minute: int = 5
    rate_limit_per_day: int = 50
    daily_analysis_budget_cap: int = 500

    @model_validator(mode="after")
    def _check_deepseek_key(self) -> "Settings":
        if self.llm_provider == "deepseek" and not self.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is required when LLM_PROVIDER=deepseek")
        return self

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{quote_plus(self.postgres_user)}:"
            f"{quote_plus(self.postgres_password)}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()

# Backward-compatible module-level constants — existing `from config import X`
# call sites are unaffected by the move to pydantic-settings.
REDIS_HOST = settings.redis_host
REDIS_PORT = settings.redis_port
REDIS_DB = settings.redis_db

REDIS_CACHE_TTL_SECONDS_MARKETSTACK = 604800
REDIS_CACHE_TTL_SECONDS_ALPHAVANTAGE = 86400
REDIS_CACHE_TTL_SECONDS_ALPHAVANTAGE_ERROR = (
    300  # 5 min — lets quota reset before retrying
)
REDIS_CACHE_TTL_SECONDS_FINNHUB = 86400
REDIS_CACHE_TTL_SECONDS_BIOSIGNALFOUNDRY = 120

ALPHAVANTAGE_API_KEY = settings.alphavantage_api_key
FINNHUB_API_KEY = settings.finnhub_api_key
MARKETSTACK_API_KEY = settings.marketstack_api_key
