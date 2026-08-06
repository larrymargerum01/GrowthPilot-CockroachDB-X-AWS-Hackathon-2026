class MemoryWriter:
    """
    Coordinates the memory creation pipeline.

    Flow:

    Text
      ↓
    Chunker
      ↓
    Embedding Service
      ↓
    Repository
      ↓
    CockroachDB
    """

    def __init__(
        self,
        chunker,
        embedding_service,
        repository,
    ):
        self.chunker = chunker
        self.embedding_service = embedding_service
        self.repository = repository

    async def write(
        self,
        text: str,
    ):
        """
        Convert text into stored memories.
        """

        chunks = self.chunker.chunk_text(text)

        saved_memories = []

        for chunk in chunks:

            embedding = await (
                self.embedding_service
                .generate_embedding(chunk)
            )

            memory_id = await (
                self.repository
                .save_memory(
                    content=chunk,
                    embedding=embedding,
                )
            )

            saved_memories.append(memory_id)

        return saved_memories