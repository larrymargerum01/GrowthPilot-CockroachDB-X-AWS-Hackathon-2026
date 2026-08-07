from datetime import datetime, timezone
from uuid import UUID
from fastapi import Request, HTTPException, status
from backend.database.database import database


async def get_current_company_id(request: Request) -> UUID:
    """
    Extract and validate the session token, returning the associated company_id.
    """
    token_str = None

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token_str = auth_header[7:]

    if not token_str:
        token_str = request.cookies.get("session_token")

    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing"
        )

    try:
        token_uuid = UUID(token_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token format"
        )

    query = """
    SELECT company_id, expires_at
    FROM sessions
    WHERE token = $1;
    """

    async with database.acquire() as conn:
        row = await conn.fetchrow(query, token_uuid)

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )

    if row["expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired"
        )

    return row["company_id"]
