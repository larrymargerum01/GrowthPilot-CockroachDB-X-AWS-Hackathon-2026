import asyncio
import json
import os
import boto3


class BedrockClient:
    """
    Asynchronous client wrapper for AWS Bedrock services.
    """

    def __init__(
        self,
        region_name: str | None = None,
        embedding_model: str | None = None,
    ):
        """
        Initialize the Bedrock client runtime using environment settings.
        """
        self.region_name = region_name or os.getenv("AWS_REGION", "eu-west-2")
        self.embedding_model = embedding_model or os.getenv(
            "BEDROCK_EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0"
        )
        self.client = boto3.client("bedrock-runtime", region_name=self.region_name)

    async def get_embedding(self, text: str) -> list[float]:
        """
        Generate a vector embedding for the given text using Amazon Titan.
        """
        body = json.dumps({
            "inputText": text,
            "dimensions": 1024,
            "normalize": True
        })

        response = await asyncio.to_thread(
            self.client.invoke_model,
            modelId=self.embedding_model,
            contentType="application/json",
            accept="application/json",
            body=body
        )

        response_body = json.loads(response["body"].read())
        return response_body["embedding"]

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0",
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate text response/completion using Claude on AWS Bedrock.
        """
        messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
        }

        if system_prompt:
            payload["system"] = system_prompt

        body = json.dumps(payload)

        response = await asyncio.to_thread(
            self.client.invoke_model,
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body
        )

        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]
