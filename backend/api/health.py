from fastapi import APIRouter, HTTPException
from backend.database.database import database

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Check the health of the application and the database connection.
    """
    try:
        # Check if pool is initialized. If not, it means lifespan hasn't run or failed.
        if database.pool is None:
            raise Exception("Database pool is not initialized")
            
        # Acquire a connection and run a simple query to verify it's working
        async with database.acquire() as conn:
            await conn.execute("SELECT 1")
            
        return {"status": "ok", "db_connection": "healthy"}
    except Exception as e:
        # Return 200 so load balancers don't kill the instance, but mark as degraded
        return {"status": "degraded", "db_connection": "unreachable", "details": str(e)}
