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
    repository
      ↓
    CockroachDB
    """

    def __init__(self, chunker, embedding_service, repository):
        self.chunker = chunker
        self.embedding_service = embedding_service
        self.repository = repository


    async def write(
        self,
        company_id,
        text: str,
        memory_type: str = "document",
        metadata: dict | None = None,
        importance: float = 0.5,
    ):
        """
        Convert text into stored memories.

        Parameters:
            company_id:
                Tenant/company identifier.

            text:
                Raw input text.

            memory_type:
                Type of memory being stored.

            metadata:
                Additional structured information.

            importance:
                Memory importance score.
        """

        if metadata is None:
            metadata = {}

        chunks = self.chunker.chunk_text(text)

        saved_memories = []

        for chunk in chunks:

            embedding = await self.embedding_service.generate_embedding(
                chunk
            )

            memory_id = await self.repository.save_memory(
                company_id=company_id,
                memory_type=memory_type,
                content=chunk,
                metadata=metadata,
                importance=importance,
                embedding=embedding,
            )

            saved_memories.append(memory_id)

        return saved_memories