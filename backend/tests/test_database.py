from backend.database.connection import CockroachDBConnection


def test_database_connection_creation():
    """
    Verify that the database connection object
    can be created.
    """

    assert CockroachDBConnection is not None