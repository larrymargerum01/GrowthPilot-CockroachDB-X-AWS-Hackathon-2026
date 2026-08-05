from pathlib import Path

MIGRATION = Path(__file__).parent.parent / "migrations" / "001_init.sql"


def test_migration_file_exists():
    assert MIGRATION.exists(), "001_init.sql is missing"


def test_all_four_tables_declared():
    sql = MIGRATION.read_text().lower()
    for table in ("companies", "memories", "campaigns", "tasks"):
        assert f"create table if not exists {table}" in sql


def test_vector_index_is_declared_inline():
    """Adding a vector index post-hoc blocks writes during backfill,
    so it must live inside CREATE TABLE."""
    sql = MIGRATION.read_text().lower()
    assert "vector index (company_id, embedding vector_cosine_ops)" in sql
    assert "create vector index" not in sql, (
        "vector index must be inline in CREATE TABLE, not a separate statement"
    )


def test_dedup_index_is_scoped_to_company():
    """A global unique index on content_hash would leak across tenants:
    company B couldn't store a memory company A already had."""
    sql = MIGRATION.read_text().lower()
    assert "unique index idx_dedup (company_id, content_hash)" in sql