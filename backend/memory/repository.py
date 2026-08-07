"""
Memory repository.

Responsible for storing and retrieving memories.
Uses asyncpg directly because CockroachDB VECTOR
operations require custom SQL.
"""

from backend.database.database import database
from backend.database.database import run_in_txn
class MemoryRepository:

    async def save_memory(
        self,
        company_id,
        memory_type,
        content,
        content_hash,
        metadata,
        importance,
        embedding
    ):
        """
        Store a memory record.

        Returns:
            inserted memory id
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
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id;
        """

        async with database.pool.acquire() as connection:

            memory_id = await connection.fetchval(
                query,
                company_id,
                memory_type,
                content,
                content_hash,
                metadata,
                importance,
                embedding
            )

        return memory_id


    async def get_memory(self, memory_id):
        """
        Retrieve memory by id.
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

            row = await connection.fetchrow(query, memory_id)

        return row

    async def get_by_content_hash(
        self,
        company_id,
        content_hash
    ):
        """
        Find existing memory by company and content hash.
        """

        query = """
        SELECT id
        FROM memories
        WHERE company_id = $1
        AND content_hash = $2;
        """

        async with database.pool.acquire() as connection:
            memory_id = await connection.fetchval(query, company_id, content_hash)

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
