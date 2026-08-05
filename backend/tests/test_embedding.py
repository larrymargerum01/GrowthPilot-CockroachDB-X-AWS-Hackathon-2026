import pytest

from backend.memory.embedding import BedrockEmbeddingService


class MockBody:
    """
    Mock AWS Bedrock response body.
    """

    def read(self):
        return b'{"embedding": [0.1, 0.2, 0.3]}'


class MockBedrockClient:
    """
    Mock Bedrock client.

    Tests should not call AWS directly.
    """

    def invoke_model(
        self,
        modelId,
        body,
    ):
        return {
            "body": MockBody()
        }


@pytest.mark.asyncio
async def test_generate_embedding():
    """
    Verify that the embedding service correctly
    parses the embedding vector returned by Bedrock.
    """

    client = MockBedrockClient()

    service = BedrockEmbeddingService(
        client=client,
        model_id="test-model",
    )

    embedding = await service.generate_embedding(
        "hello world"
    )

    assert embedding == [
        0.1,
        0.2,
        0.3,
    ]