class MemoryRepository:
    """
    Repository responsible for storing memory chunks
    and their embeddings in CockroachDB.
    """

    def __init__(self, connection):
        self.connection = connection