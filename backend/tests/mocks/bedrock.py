class MockBedrockClient:
    """
    Mock Bedrock client for tests.
    Returns a fixed-size embedding without calling AWS.
    """

    async def get_embedding(self, text: str) -> list[float]:
        return [0.1] * 1024