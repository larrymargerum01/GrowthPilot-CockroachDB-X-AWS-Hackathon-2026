class MemoryWriter:
    """
    Coordinates the memory creation pipeline.

    Flow:
    text
      ↓
    chunks
      ↓
    embeddings
      ↓
    database
    """

    def __init__(self, chunker, embedding_service, repository):
        self.chunker = chunker
        self.embedding_service = embedding_service
        self.repository = repository

    def write(self, text: str):
        """
        Convert text into stored memories.
        """

        chunks = self.chunker.chunk_text(text)

        saved_memories = []

        for chunk in chunks:
            embedding = (self.embedding_service.generate_embedding(chunk))

            memory_id = (self.repository.save_memory(chunk, embedding))

            saved_memories.append(memory_id)

        return saved_memories