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

    async def run(self, *args, **kwargs) -> AgentResult:
        """
        Orchestrate the standard agent lifecycle:
        1. Retrieve memories/context
        2. Execute reasoning/actions (process)
        3. Persist new memories or reflections
        """
        try:
            memories = await self.retrieve_memories(*args, **kwargs)
            output = await self.process(memories, *args, **kwargs)
            await self.persist_memories(output)
            return AgentResult(
                agent_name=self.name,
                success=True,
                output=output
            )
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                success=False,
                output=str(e)
            )

    async def retrieve_memories(self, *args, **kwargs) -> Any:
        """
        Hook to retrieve relevant memories/context prior to execution.
        """
        return None

    @abstractmethod
    async def process(self, retrieved_memories: Any, *args, **kwargs) -> Any:
        """
        Execute core reasoning and actions. Must be implemented by sub-classes.
        """
        pass

    async def persist_memories(self, result_data: Any) -> None:
        """
        Hook to persist new memories or reflections back to storage.
        """
        pass
