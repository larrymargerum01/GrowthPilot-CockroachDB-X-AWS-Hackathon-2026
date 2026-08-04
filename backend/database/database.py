import psycopg2

from backend.database.config import DatabaseConfig

class CockroachDBConnection:
    """
    Handles connection and query execution
    for CockroachDB.
    """

    def __init__(self):
        config = DatabaseConfig()
        
        self.connection = psycopg2.connect(config.database_url)

    def execute(self, query, values = None):
        """
        Execute a SQL query against CockroachDB.
        """

        cursor = self.connection.cursor()

        cursor.execute(
            query,
            values
        )

        self.connection.commit()