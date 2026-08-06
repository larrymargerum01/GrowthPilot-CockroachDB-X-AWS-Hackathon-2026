"""
Database connection manager using asyncpg connection pool.

This module owns database lifecycle:
- create pool
- provide connections
- close pool
"""
from __future__ import annotations

import asyncio
import json
import random
import ssl
from typing import Awaitable, Callable, TypeVar

import asyncpg

from backend.database.config import get_settings


T = TypeVar("T")

SERIALIZATION_FAILURE = "40001"

async def _init_connection(conn: asyncpg.Connection) -> None:
    """Register type codecs asyncpg doesn't know about.

    Runs once per new pooled connection, so every query gets them without
    callers having to serialise by hand.
    """
    # asyncpg hands JSONB back as a raw string by default. Registering
    # json.dumps/loads lets callers pass and receive plain dicts.
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


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

            settings = get_settings()
            ssl_context = ssl.create_default_context()

            self.pool = await asyncpg.create_pool(
                settings.database_url,
                ssl=ssl_context,
                min_size=settings.db_pool_min_size,
                max_size=settings.db_pool_max_size,
                command_timeout=settings.db_command_timeout,
                max_inactive_connection_lifetime=(
                    settings.db_max_inactive_connection_lifetime
                ),
                init=_init_connection,
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

async def with_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 5,
    base_delay: float = 0.05,
) -> T:
    for attempt in range(1, max_attempts + 1):
        try:
            return await operation()
        except asyncpg.PostgresError as exc:
            retryable = getattr(exc, "sqlstate", None) == SERIALIZATION_FAILURE

            if not retryable or attempt == max_attempts:
                raise

            # Full jitter: without it, two conflicting transactions back off
            # by the same amount and collide again on the retry.
            delay = random.uniform(0, base_delay * (2 ** (attempt - 1)))
            await asyncio.sleep(delay)

    raise AssertionError("unreachable")

async def run_in_txn(
        fn: Callable[[asyncpg.Connection],Awaitable[T]],
        *,
        max_attempts: int = 5,
        base_delay: float = 0.05,
) -> T:
    """Run `fn` inside a transaction, retrying the whole transaction on 40001.

This is what the rest of the codebase should use for writes. Compute
embeddings *before* calling it — retrying a transaction that calls
Bedrock costs money and latency.
    """
    pool = database.pool

    if pool is None: 
            raise RuntimeError("Database Pool is not initialized")

    async def _attempt() -> T:
    # Acquire inside the retry so a connection that just carried an
    # aborted transaction isn't reused.
        async with pool.acquire() as conn:
            async with conn.transaction():
                return await fn(conn)

    return await with_retry(
        _attempt,
        max_attempts=max_attempts,
        base_delay=base_delay,
    )

def to_vector_literal(embedding: list[float]) ->str:
    """Format an embedding for a VECTOR column.

    asyncpg doesn't know CockroachDB's VECTOR type, so a Python list won't
    bind directly. Pass the result with an explicit cast:

        INSERT INTO memories (embedding) VALUES ($1::VECTOR(1024))
    """
    return "[" + ",".join(repr(float(x)) for x in embedding) + "]"