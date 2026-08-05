from uuid import UUID
from backend.llm.client import BedrockClient
from backend.memory.repository import MemoryRepository


class AgentContext:
    """
    Shared execution context for agents.

    Provides common resources like Bedrock LLM client, Memory Repository, and
    company configuration parameters required for agent execution.
    """

    def __init__(
        self,
        company_id: UUID,
        bedrock_client: BedrockClient,
        memory_repository: MemoryRepository,
    ):
        self.company_id = company_id
        self.bedrock_client = bedrock_client
        self.memory_repository = memory_repository
