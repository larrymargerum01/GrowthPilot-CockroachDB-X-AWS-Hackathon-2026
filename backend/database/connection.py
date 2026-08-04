import psycopg2

from backend.database.config import DatabaseConfig


class CockroachDBConnection:
    """
    Handles connection and SQL execution
    for CockroachDB.
    """

    def __init__(self):
        """
        Create a CockroachDB connection
        using DATABASE_URL from configuration.
        """

        config = DatabaseConfig()

        if not config.database_url:
            raise ValueError(
                "DATABASE_URL is not configured"
            )

        self.connection = psycopg2.connect(
            config.database_url
        )


    def execute(self, query: str, values=None):
        """
        Execute SQL query and return result
        when available.

        Used by repositories.
        """

        cursor = self.connection.cursor()

        try:
            cursor.execute(query, values)

            result = None

            # For queries like INSERT ... RETURNING id
            if cursor.description:
                result = cursor.fetchone()

            self.connection.commit()

            return result

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()


    def execute_schema(self, schema_path: str):
        """
        Execute SQL schema file.

        Used for creating database tables.
        """

        with open(schema_path, "r", encoding="utf-8") as file:
            schema_sql = file.read()


        cursor = self.connection.cursor()

        try:
            cursor.execute(schema_sql)

            self.connection.commit()

        except Exception:
            self.connection.rollback()
            raise

        finally:
            cursor.close()


    def close(self):
        """
        Close database connection.
        """

        if self.connection:
            self.connection.close()