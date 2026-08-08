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

    async def generate_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple chunks.

        Keeps batching logic here so Bedrock changes stay isolated.
        """

        embeddings = []

        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)

        return embeddings