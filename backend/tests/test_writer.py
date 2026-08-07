from uuid import uuid4

from backend.memory.chunker import TextChunker
from backend.memory.embedding import BedrockEmbeddingService
from backend.tests.mocks.repository import MockMemoryRepository
from backend.memory.writer import MemoryWriter
from backend.tests.mocks.bedrock import MockBedrockClient


async def test_memory_writer_pipeline():
    """
    Verify the complete memory write pipeline:

    Text
      ↓
    Text chunking
      ↓
    Embedding generation (mocked Bedrock)
      ↓
    Memory persistence
      ↓
    CockroachDB

    This test uses a mocked Bedrock client to avoid external AWS calls
    while validating that the memory creation flow works correctly.
    """
    
    chunker = TextChunker()

    bedrock_client = MockBedrockClient()

    bedrock_service = BedrockEmbeddingService(bedrock_client = bedrock_client)

    repository = MockMemoryRepository()

    writer = MemoryWriter(
        chunker = chunker,
        embedding_service = bedrock_service,
        repository = repository
    )

    company_id = uuid4()
    test_memory = """
            A team lead mentioned that she would be away for a personal event this evening
            and asked everyone to share pull requests or important updates in the group chat.

            The GrowthPilot memory system saved the note successfully. The AI assistant wanted
            to create a 47-step productivity plan, schedule five reminder notifications, and
            write an inspirational speech about "the importance of clicking merge," but it
            finally learned that sometimes the best action is simply remembering and waiting.
        """

    result = await writer.write(
        company_id = company_id,
        text = test_memory
    )

    assert len(result) > 0