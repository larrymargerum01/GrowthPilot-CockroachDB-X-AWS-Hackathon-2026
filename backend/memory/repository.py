"""
Memory repository.

Responsible for storing and retrieving memories.
Uses asyncpg directly because CockroachDB VECTOR
operations require custom SQL.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

import asyncpg

from backend.database.database import (
    database,
    run_in_txn,
    to_vector_literal,
)
from backend.memory.hash import create_content_hash
from backend.memory.store import (
    MemoryHit,
    MemoryType,
)

SEARCH_SQL = """
WITH candidates AS MATERIALIZED
(
    SELECT
        id,
        company_id,
        content,
        memory_type,
        metadata,
        importance,
        created_at,
        1.0 - (
            embedding <=> $2::VECTOR(1024)
        ) AS similarity
    FROM memories
    WHERE company_id = $1
    ORDER BY embedding <=> $2::VECTOR(1024)
    LIMIT $3
)
SELECT
    id,
    company_id,
    content,
    memory_type,
    metadata,
    importance,
    similarity,
    created_at
FROM candidates
WHERE
    (
        $4::STRING[] IS NULL
        OR memory_type = ANY($4::STRING[])
    )
    AND
    (
        $5::TIMESTAMPTZ IS NULL
        OR created_at >= $5
    )
ORDER BY
    GREATEST(similarity, 0.0)
    *
    POWER(
        0.5::FLOAT8,
        GREATEST(
            EXTRACT(
                EPOCH FROM (now() - created_at)
            ),
            0.0
        )
        /
        (30.0 * 86400.0)
    )
    *
    GREATEST(importance, 0.01) DESC,
    similarity DESC,
    created_at DESC,
    id ASC
LIMIT $6
"""

INSERT_SQL = """
INSERT INTO memories
(
    company_id,
    memory_type,
    content,
    content_hash,
    metadata,
    importance,
    embedding
)
VALUES (
    $1,
    $2,
    $3,
    $4,
    $5,
    $6,
    $7::VECTOR(1024)
)
ON CONFLICT (company_id, content_hash) DO NOTHING
RETURNING id
"""


SELECT_BY_HASH_SQL = """
SELECT id
FROM memories
WHERE company_id = $1
  AND content_hash = $2
"""


RECENT_SQL = """
SELECT
    id,
    company_id,
    content,
    memory_type,
    metadata,
    importance,
    created_at
FROM memories
WHERE company_id = $1
  AND memory_type = $2
ORDER BY created_at DESC
LIMIT $3
"""


class MemoryRepository:
    def __init__(
        self,
        embedding_service=None,
    ):
        self.embedding_service = embedding_service

    async def write(
        self,
        *,
        company_id,
        memory_type: MemoryType,
        content: str,
        metadata: dict | None = None,
        importance: float = 0.5,
    ):
        """
        Persist one memory and return its ID.

        Idempotent: writing identical content for the same company returns
        the existing row's ID rather than creating a duplicate. Dedup is
        enforced by the database's unique index rather than a prior lookup,
        so two agents writing the same content concurrently can't both pass
        a check and both insert.
        """

        if self.embedding_service is None:
            raise RuntimeError("An embedding service is required to write memories")

        content_hash = create_content_hash(content)

        # Computed OUTSIDE the transaction. run_in_txn re-runs the whole
        # transaction on a 40001 conflict, and re-running a Bedrock call
        # costs money and latency.
        embedding = await self.embedding_service.generate_embedding(content)
        embedding_vector = to_vector_literal(embedding)

        async def _insert(connection: asyncpg.Connection):
            memory_id = await connection.fetchval(
                INSERT_SQL,
                company_id,
                memory_type,
                content,
                content_hash,
                metadata or {},
                importance,
                embedding_vector,
            )

            if memory_id is not None:
                return memory_id

            # ON CONFLICT DO NOTHING returns no row, so fetch the id of the
            # memory that was already there.
            return await connection.fetchval(
                SELECT_BY_HASH_SQL,
                company_id,
                content_hash,
            )

        return await run_in_txn(_insert)

    async def save_memory(
        self,
        company_id,
        memory_type,
        content,
        content_hash,
        metadata,
        importance,
        embedding,
    ):
        """
        Store a memory record.

        Returns:
            Inserted memory ID.
        """

        query = """
        INSERT INTO memories
        (
            company_id,
            memory_type,
            content,
            content_hash,
            metadata,
            importance,
            embedding
        )
        VALUES (
            $1,
            $2,
            $3,
            $4,
            $5,
            $6,
            $7::VECTOR(1024)
        )
        RETURNING id;
        """

        embedding_vector = to_vector_literal(embedding)

        async with database.pool.acquire() as connection:
            memory_id = await connection.fetchval(
                query,
                company_id,
                memory_type,
                content,
                content_hash,
                metadata,
                importance,
                embedding_vector,
            )

        return memory_id

    async def save_memories_batch(
        self,
        memories: list[dict]
    ):
        """
        Insert multiple memories in one transaction.

        CockroachDB transactions may fail with
        serialization errors, therefore run through
        retry wrapper.
        """

        async def transaction(conn):

            ids = []

            query = """
            INSERT INTO memories
            (
                company_id,
                memory_type,
                content,
                content_hash,
                metadata,
                importance,
                embedding
            )
            VALUES
            (
                $1,
                $2,
                $3,
                $4,
                $5,
                $6,
                $7::VECTOR(1024)
            )
            RETURNING id;
            """

            for memory in memories:

                memory_id = await conn.fetchval(
                    query,
                    memory["company_id"],
                    memory["memory_type"],
                    memory["content"],
                    memory["content_hash"],
                    memory["metadata"],
                    memory["importance"],
                    memory["embedding"],
                )

                ids.append(memory_id)

            return ids

        return await run_in_txn(transaction)

    async def get_memory(self, memory_id):
        """
        Retrieve a memory by ID.
        """

        query = """
        SELECT
            id,
            company_id,
            memory_type,
            content,
            metadata,
            importance,
            embedding
        FROM memories
        WHERE id = $1;
        """

        async with database.pool.acquire() as connection:
            row = await connection.fetchrow(
                query,
                memory_id,
            )

        return row

    async def get_by_content_hash(
        self,
        company_id,
        content_hash,
    ):
        """
        Find an existing memory by company and content hash.
        """

        query = """
        SELECT id
        FROM memories
        WHERE company_id = $1
          AND content_hash = $2;
        """

        async with database.pool.acquire() as connection:
            memory_id = await connection.fetchval(
                query,
                company_id,
                content_hash,
            )

        return memory_id

    async def search(
        self,
        *,
        company_id,
        query: str,
        k: int = 8,
        types: Sequence[MemoryType] | None = None,
        since: datetime | None = None,
    ) -> list[MemoryHit]:
        """
        Search company memories using two-stage retrieval.

        Stage one:
            Use CockroachDB vector search to retrieve candidates.

        Stage two:
            Re-rank candidates using:

            similarity × recency × importance
        """

        if self.embedding_service is None:
            raise RuntimeError("An embedding service is required for memory search")

        if not query.strip():
            raise ValueError("Search query must not be empty")

        if k <= 0:
            raise ValueError("Search result count must be positive")

        query_embedding = await self.embedding_service.generate_embedding(query)

        if len(query_embedding) != 1024:
            raise ValueError(
                f"Expected a 1024-dimensional query embedding, received {len(query_embedding)}"
            )

        query_vector = to_vector_literal(query_embedding)

        # Retrieve more candidates than the caller needs.
        # Hybrid ranking is applied only to this candidate set.
        candidate_limit = max(
            50,
            k * 10,
        )

        normalized_types = list(types) if types else None

        async with database.pool.acquire() as connection:
            rows = await connection.fetch(
                SEARCH_SQL,
                company_id,
                query_vector,
                candidate_limit,
                normalized_types,
                since,
                k,
            )

        return [self._to_memory_hit(row) for row in rows]

    async def recent(
        self,
        *,
        company_id,
        memory_type: MemoryType,
        limit: int = 20,
    ) -> list[MemoryHit]:
        """
        Return the most recent memories of one type.

        Backed by idx_company_type_time (company_id, memory_type,
        created_at DESC) — no vector work involved, so this stays cheap
        even as the table grows.
        """

        if limit <= 0:
            raise ValueError("Result limit must be positive")

        async def _query(connection: asyncpg.Connection):
            return await connection.fetch(
                RECENT_SQL,
                company_id,
                memory_type,
                limit,
            )

        rows = await run_in_txn(_query)

        return [self._to_memory_hit(row) for row in rows]

    @staticmethod
    def _to_memory_hit(
        row,
    ) -> MemoryHit:
        """
        Convert an asyncpg row into the shared MemoryHit model.
        """

        data = dict(row)

        return MemoryHit(
            id=data["id"],
            company_id=data["company_id"],
            content=data["content"],
            memory_type=data["memory_type"],
            metadata=data.get("metadata") or {},
            importance=data["importance"],
            similarity=data.get("similarity"),
            created_at=data["created_at"],
        )
