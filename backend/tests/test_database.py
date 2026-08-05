import pytest

from backend.database.database import database


@pytest.mark.integration
@pytest.mark.asyncio
async def test_memories_table_exists():

    await database.connect()

    async with database.pool.acquire() as connection:

        result = await connection.fetchval(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'memories'
            """
        )

    assert result == 1

    await database.disconnect()