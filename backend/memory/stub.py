"""In-memory MemoryStore for development and tests.

Deliberately naive: word-overlap matching instead of embeddings. The point is
that the agent layer can be built and tested today, against the real
interface, without a database or Bedrock credentials.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID, uuid4

from backend.memory.store import MemoryHit, MemoryStore, MemoryType


class InMemoryStore(MemoryStore):
    def __init__(self) -> None:
        self._rows: list[MemoryHit] = []

    async def write(
        self,
        *,
        company_id: UUID,
        memory_type: MemoryType,
        content: str,
        metadata: dict[str, object] | None = None,
        importance: float = 0.5,
    ) -> UUID:
        # Mirror the real dedup behaviour so callers can rely on it.
        for row in self._rows:
            if row.company_id == company_id and row.content == content:
                return row.id

        hit = MemoryHit(
            id=uuid4(),
            company_id=company_id,
            content=content,
            memory_type=memory_type,
            metadata=metadata or {},
            importance=importance,
            similarity=None,
            created_at=datetime.now(timezone.utc),
        )

        self._rows.append(hit)
        return hit.id

    async def search(
        self,
        *,
        company_id: UUID,
        query: str,
        k: int = 8,
        types: Sequence[MemoryType] | None = None,
        since: datetime | None = None,
    ) -> list[MemoryHit]:
        terms = {
            term
            for term in query.lower().split()
            if len(term) > 2
        }

        results: list[MemoryHit] = []

        for row in self._rows:
            if row.company_id != company_id:
                continue

            if types and row.memory_type not in types:
                continue

            if since and row.created_at < since:
                continue

            words = set(row.content.lower().split())

            overlap = (
                len(terms & words) / len(terms)
                if terms
                else 0.0
            )

            if overlap > 0:
                results.append(
                    row.model_copy(
                        update={"similarity": overlap}
                    )
                )

        # `similarity` is Optional on the model (it is None for stored rows that
        # were never retrieved), so fall back to 0.0 to keep the key a float.
        results.sort(
            key=lambda result: result.similarity or 0.0,
            reverse=True,
        )

        return results[:k]

    async def recent(
        self,
        *,
        company_id: UUID,
        memory_type: MemoryType,
        limit: int = 20,
    ) -> list[MemoryHit]:
        rows = [
            row
            for row in self._rows
            if (
                row.company_id == company_id
                and row.memory_type == memory_type
            )
        ]

        rows.sort(
            key=lambda row: row.created_at,
            reverse=True,
        )

        return rows[:limit]