from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from memory.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # We send a tiny, raw SQL query ("SELECT 1") to test the connection.
        # If CockroachDB replies, we know the bridge is working!
        await db.execute(text("SELECT 1"))
        return {"status": "ok" , "dbconnection": "healthy"} 
    
    except Exception as e: # If the database fails to respond, we return a 503 Service Unavailable error.

        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")


@router.get("/company/{id}")

async def get_company(id: int):
    # For this early skeleton phase, we just return mock JSON data.
    # Later, your team will connect this to real data.
    return {
        "company_id": id,
        "name": f"Mock Company {id}",
        "status": "active"
    }