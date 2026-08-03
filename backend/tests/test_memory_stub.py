from uuid import uuid4

from backend.memory.stub import InMemoryStore


async def test_write_then_search():
    store = InMemoryStore()
    company = uuid4()

    await store.write(
        company_id=company,
        memory_type="semantic",
        content="Reddit generated the highest engagement for our launch",
    )

    hits = await store.search(company_id=company, query="reddit engagement")

    assert len(hits) == 1
    assert "Reddit" in hits[0].content


async def test_tenant_isolation():
    """The single most important property of the memory layer."""
    store = InMemoryStore()
    mine, theirs = uuid4(), uuid4()

    await store.write(
        company_id=theirs, memory_type="semantic", content="secret competitor data"
    )

    hits = await store.search(company_id=mine, query="secret competitor data")

    assert hits == [], "memories must never leak across companies"


async def test_write_is_idempotent():
    store = InMemoryStore()
    company = uuid4()

    first = await store.write(
        company_id=company, memory_type="user", content="prefers LinkedIn launches"
    )
    second = await store.write(
        company_id=company, memory_type="user", content="prefers LinkedIn launches"
    )

    assert first == second