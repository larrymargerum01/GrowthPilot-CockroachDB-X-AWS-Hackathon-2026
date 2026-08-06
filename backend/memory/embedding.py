class BedrockEmbeddingService:
    """
    Memory-layer embedding service.

    This keeps memory logic independent from AWS.
    It delegates Bedrock communication to BedrockClient.
    """

    def __init__(self, bedrock_client):
        self.bedrock_client = bedrock_client

    async def generate_embedding(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate embedding for memory storage.
        """

        return await (
            self.bedrock_client
            .get_embedding(text)
        )