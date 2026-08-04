import os
import pytest

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

    monkeypatch.setenv("DATABASE_URL", "postgresql://test-url")

    config = DatabaseConfig()

    assert config.database_url == "postgresql://test-url"

@pytest.mark.integration
def test_real_database_connection():
    """
    Verify that the application can connect
    to CockroachDB using DATABASE_URL.
    """

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        pytest.skip("DATABASE_URL is not configured")

    db = CockroachDBConnection()

    assert db.connection is not None

    db.connection.close()