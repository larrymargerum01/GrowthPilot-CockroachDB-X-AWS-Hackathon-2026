"""
Memory repository.

Responsible for storing and retrieving memories.
Uses asyncpg directly because CockroachDB VECTOR
operations require custom SQL.
"""

from backend.database.database import database


class MemoryRepository:

    async def save_memory(
        self,
        company_id,
        memory_type,
        content,
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
            metadata,
            importance,
            embedding
        )
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id;
        """

        async with database.pool.acquire() as connection:

            memory_id = await connection.fetchval(
                query,
                company_id,
                memory_type,
                content,
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