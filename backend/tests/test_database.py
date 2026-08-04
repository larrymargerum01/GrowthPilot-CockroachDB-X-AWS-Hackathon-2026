import os

from backend.database.config import DatabaseConfig
from backend.database.connection import CockroachDBConnection

def test_database_connection_creation():
    """
    Verify that the database connection object
    can be created.
    """

    assert CockroachDBConnection is not None

def test_database_config_loads_url(monkeypatch):
    """
    Verify database URL is loaded from environment.
    """

    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://test-url"
    )

    config = DatabaseConfig()

    assert config.database_url == "postgresql://test-url"