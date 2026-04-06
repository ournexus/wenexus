"""
config - Application settings loaded from environment variables.

Depends: pydantic-settings
Consumers: main, repository.db, facade, service modules
"""

import os

from pydantic_settings import BaseSettings

_APP_ENV = os.getenv("APP_ENV", "development")


class Settings(BaseSettings):
    app_env: str = "development"
    app_port: int = 8000
    database_url: str = ""
    redis_url: str = "redis://localhost:6379/0"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    frontend_urls: str = "http://localhost:3000"
    agent_model: str = "openai/gpt-4o-mini"
    tavily_api_key: str = ""
    langsmith_tracing: str = ""
    langsmith_endpoint: str = ""
    langsmith_api_key: str = ""
    langsmith_project: str = ""
    log_level: str = "INFO"
    log_file_backend: str = ""
    log_file_backend_error: str = ""

    @property
    def allowed_origins(self) -> list[str]:
        return [u.strip() for u in self.frontend_urls.split(",") if u.strip()]

    class Config:
        env_file = f".env.{_APP_ENV}"
        env_file_encoding = "utf-8"


settings = Settings()
