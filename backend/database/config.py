"""
Database configuration.

Loads environment variables and exposes
DATABASE_URL for asyncpg connection pool.
"""

import os

from dotenv import load_dotenv


# Load variables from .env
load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured"
    )