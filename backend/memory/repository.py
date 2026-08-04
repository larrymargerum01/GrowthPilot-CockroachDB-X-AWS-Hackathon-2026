from backend.database.connection import CockroachDBConnection

class MemoryRepository:
    """
    Repository responsible for storing memory chunks
    and their embeddings in CockroachDB.
    """

    def __init__(self, connection):
        self.connection = connection

    def save_memory(self, content: str, embedding: list):
        """
        Save a memory chunk and its embedding vector.
        """

        query = """
        INSERT INTO memories (content, embedding)
        VALUES (%s, %s)
        """

        result = self.connection.execute(query, (content, embedding))

        return result