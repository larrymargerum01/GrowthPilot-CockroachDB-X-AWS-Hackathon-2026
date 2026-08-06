from backend.memory.hash import create_content_hash
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
        company_id,
        text: str,
    ):
        """
        Convert text into stored memories.
        """

        chunks = self.chunker.chunk_text(text)

        saved_memories = []

        for chunk in chunks:

            content_hash = create_content_hash(chunk)

            # Check if this memory already exists before generating embeddings.
            # This avoids duplicate records and unnecessary Bedrock embedding calls.
            existing_memory = await (
                self.repository.get_by_content_hash(
                    company_id,
                    content_hash
                )
            )

            if existing_memory:
                # Reuse existing memory instead of creating a duplicate.
                saved_memories.append(existing_memory)
                continue

            embedding = await (
                self.embedding_service
                .generate_embedding(chunk)
            )

            memory_id = await (
                self.repository
                .save_memory(
                    company_id = company_id,
                    memory_type = 'semantic',
                    content = chunk,
                    content_hash = content_hash,
                    metadata = {},
                    importance = 0.5,
                    embedding = embedding
                )
            )

            saved_memories.append(memory_id)

        return saved_memories