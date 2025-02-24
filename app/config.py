"""
Configuration management using Pydantic v2 settings.
"""

import logging
import secrets
from typing import Any

from pydantic import (
    AmqpDsn,
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
)
from pydantic_settings import BaseSettings
from sqlalchemy import URL

logging.basicConfig(level=logging.INFO)


class DatabaseSettings(BaseModel):
    """Database configuration settings."""

    host: str = Field("localhost")
    port: int = Field(5432)
    user: str = Field("postgres")
    password: str = Field("postgres")
    name: str = Field("postgres")

    @property
    def url(self) -> str:
        """Construct the full database connection URL."""
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        ).render_as_string(False)


class Settings(BaseSettings):
    """Main application settings."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="_",
    )

    bot_token: str = Field("")
    openai_api_key: str = Field("")

    database: DatabaseSettings = DatabaseSettings()


# Create a singleton settings instance
settings = Settings()
