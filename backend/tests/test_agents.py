from uuid import uuid4
from unittest.mock import MagicMock
import pytest
from backend.agents import Agent, AgentContext, AgentResult


class ConcreteAgent(Agent):
    @property
    def name(self) -> str:
        return "test-agent"

    async def run(self, *args, **kwargs) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            success=True,
            output="run-success"
        )


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
async def test_concrete_agent_execution():
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

    result = await agent.run()
    assert isinstance(result, AgentResult)
    assert result.agent_name == "test-agent"
    assert result.success is True
    assert result.output == "run-success"
