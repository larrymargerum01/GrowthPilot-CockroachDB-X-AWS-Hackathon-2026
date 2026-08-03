from __future__ import annotations

from datetime import datetime
from typing import Literal, Protocol, Sequence
from uuid import UUID

from pydantic import BaseModel, Field


MemoryType = Literal[
    "episodic",
    "semantic",
    "user",
    "task",
    "reflection",
]


class MemoryHit(BaseModel):
    """One retrieved memory, with its retrieval score when applicable."""

    id: UUID
    company_id: UUID
    content: str
    memory_type: MemoryType
    metadata: dict[str, object] = Field(default_factory=dict)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    similarity: float | None = None
    created_at: datetime


class MemoryStore(Protocol):
    async def write(
        self,
        *,
        company_id: UUID,
        memory_type: MemoryType,
        content: str,
        metadata: dict[str, object] | None = None,
        importance: float = 0.5,
    ) -> UUID:
        """Persist one memory and return its ID."""
        ...

    async def search(
        self,
        *,
        company_id: UUID,
        query: str,
        k: int = 8,
        types: Sequence[MemoryType] | None = None,
        since: datetime | None = None,
    ) -> list[MemoryHit]:
        """Search memories semantically within one company."""
        ...

    async def recent(
        self,
        *,
        company_id: UUID,
        memory_type: MemoryType,
        limit: int = 20,
    ) -> list[MemoryHit]:
        """Return the most recent memories of one type."""
        ...