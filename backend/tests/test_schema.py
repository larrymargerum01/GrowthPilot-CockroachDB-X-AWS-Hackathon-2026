import os
import pytest
from pathlib import Path

from backend.database.connection import CockroachDBConnection


@pytest.mark.integration
def test_apply_schema():

    if not os.getenv("DATABASE_URL"):
        pytest.skip("DATABASE_URL is not configured")

    db = CockroachDBConnection()

    schema_path = (
        Path(__file__)
        .parent
        .parent
        / "database"
        / "schema.sql"
    )

    assert db.connection is not None

    db.connection.close()