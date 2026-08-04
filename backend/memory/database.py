import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv() # Load secret variable from .env file.

DATABASE_URL = os.getenv("DATABASE_URL") # Grab that url.and
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "cockroachdb+asyncpg://", 1)
    # Remove query string parameters like ?sslmode=verify-full since asyncpg doesn't support them 
    # and we provide ssl configuration in connect_args.
    if "?" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.split("?")[0]

# Initialize the CockroachDB engine.
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"ssl": "require"}
)

# Create the session factory for establishing session on every transaction.
AsyncSessionLocal = sessionmaker(
    engine , class_=AsyncSession , expire_on_commit=False
)

# Define the database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session