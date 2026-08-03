class BedrockEmbeddingService:
    """
    Service responsible for generating text embeddings
    using AWS Bedrock.
    """

    def __init__(self, client, model_id: str):
        self.client = client
        self.model_id = model_id

    def generate_embedding(self, text: str):
        """
        Generate an embedding vector for the given text.
        """

        response = self.client.invoke_model(body = text)

        return response