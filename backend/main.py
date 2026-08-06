from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.database.database import database
from backend.api.health import router as health_router
from backend.api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to the database on startup (initializes the connection pool)
    await database.connect()
    yield
    # Disconnect from the database on shutdown (closes the pool)
    await database.disconnect()

# Initialize the core FastAPI application with the lifespan manager
app = FastAPI(title="GTM Agent API", lifespan=lifespan)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
