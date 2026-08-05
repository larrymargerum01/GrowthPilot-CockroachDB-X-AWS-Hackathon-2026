import pytest

from backend.memory.writer import MemoryWriter


class MockChunker:
    """
    Mock text chunking service.
    """

    def chunk_text(
        self,
        text,
    ):
        return [
            text
        ]


class MockEmbeddingService:
    """
    Mock embedding generator.
    """

    async def generate_embedding(
        self,
        text,
    ):
        return [
            0.1,
            0.2,
            0.3,
        ]


class MockRepository:
    """
    Mock memory repository.

    Simulates saving memory into CockroachDB.
    """

    async def save_memory(
        self,
        company_id,
        memory_type,
        content,
        metadata,
        importance,
        embedding,
    ):
        return "test-memory-id"


@pytest.mark.asyncio
async def test_memory_writer_pipeline():
    """
    Verify the complete memory creation pipeline:

    text
      ↓
    chunks
      ↓
    embeddings
      ↓
    repository
      ↓
    memory id
    """

    writer = MemoryWriter(
        chunker=MockChunker(),
        embedding_service=MockEmbeddingService(),
        repository=MockRepository(),
    )

    result = await writer.write(
        company_id="test-company-id",
        text="hello world",
    )

    assert result == [
        "test-memory-id"
    ]