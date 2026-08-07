from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, status, Response
from pydantic import BaseModel, EmailStr, Field
from backend.database.database import database

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)
    website: str | None = None
    industry: str | None = None
    description: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SessionResponse(BaseModel):
    session_token: UUID
    company_id: UUID


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2 with a secure random salt.
    """
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000
    )
    return f"{salt.hex()}${pwd_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against a stored PBKDF2 hash.
    """
    try:
        salt_hex, hash_hex = stored_hash.split("$")
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            100000
        )
        return hmac.compare_digest(actual_hash, expected_hash)
    except (ValueError, TypeError):
        return False


async def create_session_token(company_id: UUID, response: Response) -> UUID:
    """
    Create a session token in database and set it as a secure cookie.
    """
    token = uuid4()
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    query = """
    INSERT INTO sessions (token, company_id, expires_at)
    VALUES ($1, $2, $3);
    """
    async with database.acquire() as conn:
        await conn.execute(query, token, company_id, expires_at)

    response.set_cookie(
        key="session_token",
        value=str(token),
        httponly=True,
        secure=True,
        samesite="lax",
        expires=expires_at,
    )
    return token


@router.post("/signup", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, response: Response):
    """
    Create a new company account and start a session.
    """
    email_check_query = "SELECT id FROM companies WHERE email = $1;"
    async with database.acquire() as conn:
        existing = await conn.fetchval(email_check_query, request.email)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    pwd_hash = hash_password(request.password)

    insert_query = """
    INSERT INTO companies (name, email, password_hash, website, industry, description)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING id;
    """
    async with database.acquire() as conn:
        company_id = await conn.fetchval(
            insert_query,
            request.name,
            request.email,
            pwd_hash,
            request.website,
            request.industry,
            request.description
        )

    token = await create_session_token(company_id, response)
    return SessionResponse(session_token=token, company_id=company_id)


@router.post("/login", response_model=SessionResponse)
async def login(request: LoginRequest, response: Response):
    """
    Authenticate credentials and start a session.
    """
    query = "SELECT id, password_hash FROM companies WHERE email = $1;"
    async with database.acquire() as conn:
        row = await conn.fetchrow(query, request.email)

    if not row or not verify_password(request.password, row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    company_id = row["id"]
    token = await create_session_token(company_id, response)
    return SessionResponse(session_token=token, company_id=company_id)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    """
    Invalidate session token and clear the session cookie.
    """
    response.delete_cookie(key="session_token")
