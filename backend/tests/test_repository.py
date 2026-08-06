import pytest

from backend.memory.repository import MemoryRepository
from backend.database.database import database


class MockConnection:

    async def fetchval(self, query, *args):
        return 1



class MockAcquire:

    async def __aenter__(self):
        return MockConnection()


    async def __aexit__(self, exc_type, exc, tb):
        pass



class MockPool:

    def acquire(self):
        return MockAcquire()



@pytest.mark.asyncio
async def test_save_memory():

    original_pool = database.pool

    database.pool = MockPool()


    repository = MemoryRepository()


    result = await repository.save_memory(
        company_id="company-1",
        memory_type="reflection",
        content="GrowthPilot learned something",
        content_hash = "test-hash-123",
        metadata={
            "source": "agent"
        },
        importance=0.8,
        embedding=[0.1, 0.2, 0.3],
    )


    assert result == 1


    database.pool = original_pool