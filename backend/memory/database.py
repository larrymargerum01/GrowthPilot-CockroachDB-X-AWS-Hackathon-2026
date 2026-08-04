class CockroachDBConnection:
    """
    Handles connection and query execution
    for CockroachDB.
    """

    def __init__(self, connection):
        self.connection = connection

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