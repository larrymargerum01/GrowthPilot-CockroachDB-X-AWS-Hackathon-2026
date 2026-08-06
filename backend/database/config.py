"""
Database configuration.

Uses pydantic-settings so a missing DATABASE_URL fails at startup with a
clear message naming the field, rather than surfacing as a confusing error
on the first query. Also reads .env natively, so python-dotenv is no
longer needed.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


    database_url: str

    # CockroachDB Serverless caps concurrent connections and every agent
    # shares this pool, so keep max_size conservative.
    db_pool_min_size: int = 2
    db_pool_max_size: int = 10

    # Fail a query rather than hang if the cluster is unreachable.
    db_command_timeout: float = 10.0

    # CockroachDB Cloud drops idle connections; recycle before it does.
    db_max_inactive_connection_lifetime: float = 300.0


@lru_cache
def get_settings() -> Settings:
    """Cached so .env is parsed once per process."""
    return Settings()
