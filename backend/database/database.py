"""
Database connection manager using asyncpg connection pool.

This module owns database lifecycle:
- create pool
- provide connections
- close pool
"""

import asyncpg
import ssl
from backend.database.config import DATABASE_URL


class Database:
    """
    Global database manager.
    """

    def __init__(self):
        self.pool: asyncpg.Pool | None = None


    async def connect(self):
        """
        Create asyncpg connection pool.
        """

        if self.pool is None:

            ssl_context = ssl.create_default_context()

            self.pool = await asyncpg.create_pool(
                DATABASE_URL,
                ssl=ssl_context,
                min_size=2,
                max_size=10,
            )


    async def disconnect(self):
        """
        Close all database connections.
        """

        if self.pool:
            await self.pool.close()
            self.pool = None


    def acquire(self):
        """
        Acquire one connection from pool.
        """

        if self.pool is None:
            raise RuntimeError(
                "Database pool is not initialized"
            )

        return self.pool.acquire()


database = Database()