class BedrockEmbeddingService:
    """
    Service responsible for generating text embeddings
    using AWS Bedrock.
    """

    def __init__(self, client):
        self.client = client

    def generate_embedding(self, text: str):
        """
        Generate an embedding vector for the given text.
        """

        response = self.client.invoke_model(body = text)

        return response