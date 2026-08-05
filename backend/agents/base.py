from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel, Field
from backend.agents.context import AgentContext


class AgentResult(BaseModel):
    """
    Standard schema for agent execution results.
    """
    agent_name: str
    success: bool
    output: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Agent(ABC):
    """
    Abstract base class for all GrowthPilot GTM agents.

    All custom agents inherit from this class and utilize the provided
    AgentContext to access shared resources (LLM client, DB repository).
    """

    def __init__(self, context: AgentContext):
        self.context = context

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the unique name identifier of the agent.
        """
        pass

    @abstractmethod
    async def run(self, *args, **kwargs) -> AgentResult:
        """
        Execute the main business logic of the agent.
        """
        pass
