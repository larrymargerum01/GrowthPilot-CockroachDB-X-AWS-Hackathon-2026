from abc import ABC, abstractmethod
from backend.agents.context import AgentContext


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
    async def run(self, *args, **kwargs):
        """
        Execute the main business logic of the agent.
        """
        pass
