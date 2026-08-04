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

    def execute_schema(self, schema_path: str):
        """
        Execute a SQL query against CockroachDB.
        """

        with open(schema_path, "r", encoding="utf-8") as file:
            schema_sql = file.read()

        cursor = self.connection.cursor()

        cursor.execute(schema_sql)

        self.connection.commit()