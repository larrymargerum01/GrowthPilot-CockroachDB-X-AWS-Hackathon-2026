class MemoryWriter:

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
        company_id: str,
        content: str,
        memory_type: str = "episodic",
        metadata: dict | None = None,
        importance: float = 0.5,
    ):

        metadata = metadata or {}

        chunks = self.chunker.chunk_text(content)

        saved_memories = []

        for chunk in chunks:

            embedding = await (
                self.embedding_service
                .generate_embedding(chunk)
            )

            memory_id = await (
                self.repository
                .save_memory(
                    company_id=company_id,
                    memory_type=memory_type,
                    content=chunk,
                    metadata=metadata,
                    importance=importance,
                    embedding=embedding,
                )
            )

            saved_memories.append(memory_id)

        return saved_memories