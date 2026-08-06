from uuid import uuid4
from unittest.mock import MagicMock
import pytest
from backend.agents import Agent, AgentContext, AgentResult


class ConcreteAgent(Agent):
    def __init__(self, context: AgentContext):
        super().__init__(context)
        self.retrieved = False
        self.persisted = False

    @property
    def name(self) -> str:
        return "test-agent"

    async def retrieve_memories(self, *args, **kwargs):
        self.retrieved = True
        return "mock-memories"

    async def process(self, retrieved_memories: str, *args, **kwargs) -> str:
        assert retrieved_memories == "mock-memories"
        return "run-success"

    async def persist_memories(self, result_data: str) -> None:
        assert result_data == "run-success"
        self.persisted = True


def test_agent_context_creation():
    company_id = uuid4()
    mock_bedrock = MagicMock()
    mock_repo = MagicMock()

    context = AgentContext(
        company_id=company_id,
        bedrock_client=mock_bedrock,
        memory_repository=mock_repo,
    )

    assert context.company_id == company_id
    assert context.bedrock_client == mock_bedrock
    assert context.memory_repository == mock_repo


def test_agent_abc_prevent_instantiation():
    mock_context = MagicMock()
    with pytest.raises(TypeError):
        Agent(mock_context)


@pytest.mark.asyncio
async def test_concrete_agent_lifecycle_execution():
    company_id = uuid4()
    mock_bedrock = MagicMock()
    mock_repo = MagicMock()

    context = AgentContext(
        company_id=company_id,
        bedrock_client=mock_bedrock,
        memory_repository=mock_repo,
    )

    agent = ConcreteAgent(context)
    assert agent.name == "test-agent"
    assert agent.context == context
    assert agent.retrieved is False
    assert agent.persisted is False

    result = await agent.run()
    assert isinstance(result, AgentResult)
    assert result.agent_name == "test-agent"
    assert result.success is True
    assert result.output == "run-success"

    assert agent.retrieved is True
    assert agent.persisted is True
