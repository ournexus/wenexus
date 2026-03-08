"""
config - Application settings loaded from environment variables.

Depends: pydantic-settings
Consumers: main, repository.db, facade, service modules
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    app_port: int = 8000
    database_url: str = ""
    redis_url: str = "redis://localhost:6379/0"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env.development"
        env_file_encoding = "utf-8"


settings = Settings()
