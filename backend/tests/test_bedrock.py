import io
import json
from unittest.mock import MagicMock, patch
import pytest
from backend.llm.client import BedrockClient


@pytest.fixture
def mock_boto3_client():
    with patch("boto3.client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client_factory.return_value = mock_client
        yield mock_client


@pytest.mark.asyncio
async def test_get_embedding(mock_boto3_client):
    mock_response = {
        "body": io.BytesIO(
            json.dumps({"embedding": [0.1] * 1024}).encode("utf-8")
        )
    }
    mock_boto3_client.invoke_model.return_value = mock_response

    client = BedrockClient(region_name="eu-west-2")
    embedding = await client.get_embedding("hello world")

    assert len(embedding) == 1024
    assert embedding[0] == 0.1
    mock_boto3_client.invoke_model.assert_called_once()

    call_args = mock_boto3_client.invoke_model.call_args[1]
    assert call_args["modelId"] == "amazon.titan-embed-text-v2:0"
    assert call_args["contentType"] == "application/json"
    body = json.loads(call_args["body"])
    assert body["inputText"] == "hello world"
    assert body["dimensions"] == 1024


@pytest.mark.asyncio
async def test_generate_text(mock_boto3_client):
    mock_response = {
        "body": io.BytesIO(
            json.dumps({
                "content": [{"type": "text", "text": "Generated text response"}]
            }).encode("utf-8")
        )
    }
    mock_boto3_client.invoke_model.return_value = mock_response

    client = BedrockClient(region_name="eu-west-2")
    text = await client.generate_text("generate a marketing slogan", system_prompt="be helpful")

    assert text == "Generated text response"
    mock_boto3_client.invoke_model.assert_called_once()

    call_args = mock_boto3_client.invoke_model.call_args[1]
    assert call_args["modelId"] == "anthropic.claude-3-5-sonnet-20241022-v2:0"
    body = json.loads(call_args["body"])
    assert body["system"] == "be helpful"
    assert body["messages"][0]["content"][0]["text"] == "generate a marketing slogan"
