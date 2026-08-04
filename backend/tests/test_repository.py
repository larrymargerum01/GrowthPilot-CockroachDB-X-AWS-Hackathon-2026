from backend.memory.repository import MemoryRepository

class MockDatabaseConnection:
    """
    Fake database connection used for testing.

    It records SQL queries instead of executing them.
    """

    def __init__(self):
        self.executed_query = None
        self.executed_values = None

    def execute(self, query, values):
        """
        Simulate database execution.
        """

        self.executed_query = query
        self.executed_values = values

def test_save_memory():
    """
    Verify that memory content and embeddings
    are sent correctly to the database.
    """

    connection = MockDatabaseConnection()

    repository = MemoryRepository(connection)

    content = "Customer prefers sustainable products"

    embedding = [0.123, 0.456, 0.789]

    repository.save_memory(content, embedding)

    assert "INSERT INTO memories" in (
        connection.executed_query
    )

    assert connection.executed_values == (
        content,
        embedding
    )
