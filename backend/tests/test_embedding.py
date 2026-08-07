import pytest

from backend.memory.embedding import BedrockEmbeddingService
from backend.tests.mocks.bedrock import MockBedrockClient


@pytest.mark.asyncio
async def test_generate_embedding():

    bedrock_client = MockBedrockClient()

    service = BedrockEmbeddingService(
        bedrock_client=bedrock_client
    )

    embedding = await service.generate_embedding(
        "hello world"
    )

    assert len(embedding) == 1024
    assert embedding[0] == 0.1