from datetime import datetime, timezone
from uuid import uuid4

import pytest

from backend.database.database import database
from backend.memory.repository import MemoryRepository
from backend.memory.store import MemoryHit



# Save-memory mocks


class MockConnection:
    """
    Fake database connection used by save_memory tests.
    """

    async def fetchval(self, query, *args):
        return 1


class MockAcquire:
    """
    Fake async context manager returned by pool.acquire().
    """

    async def __aenter__(self):
        return MockConnection()

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        return False


class MockPool:
    """
    Fake database connection pool.
    """

    def acquire(self):
        return MockAcquire()


@pytest.mark.asyncio
async def test_save_memory(monkeypatch):
    """
    save_memory should return the ID produced by the database.
    """

    monkeypatch.setattr(
        database,
        "pool",
        MockPool(),
    )

    repository = MemoryRepository()

    result = await repository.save_memory(
        company_id="company-1",
        memory_type="reflection",
        content="GrowthPilot learned something",
        content_hash="test-hash-123",
        metadata={
            "source": "agent",
        },
        importance=0.8,
        embedding=[0.1, 0.2, 0.3],
    )

    assert result == 1


# Search helpers and mocks



def create_test_embedding():
    """
    Return a deterministic 1024-dimensional test embedding.
    """

    embedding = [0.0] * 1024
    embedding[0] = 1.0

    return embedding


class FakeSearchEmbeddingService:
    """
    Fake embedding service that records incoming requests.
    """

    def __init__(self):
        self.calls = []

    async def generate_embedding(
        self,
        text,
    ):
        self.calls.append(text)

        return create_test_embedding()


class MockSearchConnection:
    """
    Fake database connection used by search tests.

    It records the SQL query and arguments so the test can
    inspect how MemoryRepository called CockroachDB.
    """

    def __init__(self, rows):
        self.rows = rows
        self.query = None
        self.args = None

    async def fetch(
        self,
        query,
        *args,
    ):
        self.query = query
        self.args = args

        return self.rows


class MockSearchAcquire:
    """
    Fake async context manager for search connections.
    """

    def __init__(self, connection):
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        return False


class MockSearchPool:
    """
    Fake connection pool that returns MockSearchConnection.
    """

    def __init__(self, connection):
        self.connection = connection

    def acquire(self):
        return MockSearchAcquire(
            self.connection
        )


# Search test


@pytest.mark.asyncio
async def test_search_uses_vector_candidates_and_hybrid_ranking(
    monkeypatch,
):
    """
    GrowthPilot should retrieve a relevant campaign reflection
    and return it as a MemoryHit.

    The SQL should:

    1. Scope retrieval to one company.
    2. Use cosine vector distance for candidates.
    3. Re-rank with similarity, recency, and importance.
    """

    company_id = uuid4()
    memory_id = uuid4()

    created_at = datetime(
        2026,
        8,
        7,
        12,
        0,
        tzinfo=timezone.utc,
    )

    connection = MockSearchConnection(
        rows=[
            {
                "id": memory_id,
                "company_id": company_id,
                "content": (
                    "Posts about engineering workflows "
                    "generated more engagement than "
                    "AI automation posts."
                ),
                "memory_type": "reflection",
                "metadata": {
                    "channel": "linkedin",
                    "source": "analytics-agent",
                },
                "importance": 0.9,
                "similarity": 0.95,
                "created_at": created_at,
            }
        ]
    )

    monkeypatch.setattr(
        database,
        "pool",
        MockSearchPool(connection),
    )

    embedding_service = FakeSearchEmbeddingService()

    repository = MemoryRepository(
        embedding_service=embedding_service
    )

    results = await repository.search(
        company_id=company_id,
        query=(
            "What messaging worked best "
            "in our previous campaign?"
        ),
        k=5,
        types=[
            "reflection",
        ],
    )

    assert len(results) == 1

    assert isinstance(
        results[0],
        MemoryHit,
    )

    assert results[0].id == memory_id
    assert results[0].company_id == company_id

    assert results[0].memory_type == (
        "reflection"
    )

    assert results[0].similarity == 0.95

    assert (
        "engineering workflows"
        in results[0].content
    )

    # The embedding service should receive the original query.
    assert embedding_service.calls == [
        (
            "What messaging worked best "
            "in our previous campaign?"
        )
    ]

    # Candidate stage must preserve the vector-search query shape.
    assert "AS MATERIALIZED" in connection.query

    assert (
        "WHERE company_id = $1"
        in connection.query
    )

    assert (
        "embedding <=> $2::VECTOR(1024)"
        in connection.query
    )

    # Hybrid ranking must contain recency and importance.
    assert "POWER" in connection.query
    assert "GREATEST(importance" in connection.query

    # Verify arguments sent into CockroachDB.
    assert connection.args[0] == company_id

    # max(50, k * 10), where k is 5.
    assert connection.args[2] == 50

    assert connection.args[3] == [
        "reflection",
    ]

    assert connection.args[4] is None
    assert connection.args[5] == 5

