import json

from backend.memory.embedding import BedrockEmbeddingService

class MockBedrockClient:
    """
    Fake AWS Bedrock client used for testing.

    This avoids making real AWS API calls during tests.
    """

    def __init__(self):
        """
        Store the request arguments so the test can verify that the service
        sends the correct data to Bedrock.
        """
        self.called_with = None

    def invoke_model(self, modelId, body):
        """
        Simulate the Bedrock invoke_model API call.
        """

        self.called_with = {
            "modelId": modelId,
            "body": body
        }

        return {
            "body": MockBody()
        }
    

class MockBody:
    """
    Simulates the response body returned by AWS Bedrock.

    In production, Bedrock returns a streaming response object.
    This mock provides the same interface needed by our service.
    """

    def read(self):
        """
        Return a fake Bedrock JSON response containing
        an embedding vector.
        """

        return json.dumps({
            "embedding": [0.123, 0.456, 0.789]
        })
    

def test_generate_embedding():
    """
    Verify that the embedding service:

    1. Sends the correct model ID.
    2. Sends the correct input text payload.
    3. Correctly parses the embedding response.
    """

    client = MockBedrockClient()

    service = BedrockEmbeddingService(client, "amazon.titan-embed-text-v2:0")

    text =  "Customer prefers sustainable products"
    
    embedding = service.generate_embedding(text)

    request_body = json.loads(client.called_with["body"])

    # Verify the request sent to Bedrock.
    assert client.called_with["modelId"] == (
        "amazon.titan-embed-text-v2:0"
    )

    assert request_body["inputText"] == text

    # Verify that the returned value is the embedding vector.
    assert embedding == [0.123, 0.456, 0.789]


