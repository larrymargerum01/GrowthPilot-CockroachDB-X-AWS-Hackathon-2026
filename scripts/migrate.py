"""
Database migration runner.

Applies SQL migration files from backend/migrations
using the existing asyncpg database manager.
"""

import asyncio
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.database.database import database


MIGRATIONS_DIR = (
    ROOT_DIR
    / "backend"
    / "migrations"
)


async def run_migrations():
    """
    Apply all database migrations in order.
    """

    await database.connect()

    try:
        async with database.acquire() as conn:

            migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

            if not migration_files:
                raise RuntimeError("No migration files found")

            print(f"Found {len(migration_files)} migration file(s)")

            for migration_file in migration_files:
                print(f"Applying {migration_file.name}...")

                sql = migration_file.read_text(encoding="utf-8")

                try: 
                    # CockroachDB cluster setting must run outside transaction
                    if "SET CLUSTER SETTING" in sql:
                        setting = (
                            "SET CLUSTER SETTING "
                            "feature.vector_index.enabled = true;"
                        )

                        print("Applying cluster setting...")

                        await conn.execute(setting)

                        sql = sql.replace(setting, "")

                    # Execute schema statements
                    if sql.strip():
                        async with conn.transaction():
                            await conn.execute(sql)
                except Exception as e:
                    raise RuntimeError(f"Migration failed: {migration_file.name}") from e

                print(f"✓ {migration_file.name} completed")

        print("All migrations completed successfully.")

    finally:
        await database.disconnect()


if __name__ == "__main__":
    asyncio.run(run_migrations())