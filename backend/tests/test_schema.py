import pytest

from backend.database.database import database


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_pool_connection():
    """
    Verify that the application can connect
    to CockroachDB through asyncpg pool.
    """

    await database.connect()

    assert database.pool is not None


    async with database.pool.acquire() as connection:

        result = await connection.fetchval(
            "SELECT 1"
        )


    assert result == 1


    await database.disconnect()

    assert database.pool is None