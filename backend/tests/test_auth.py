from datetime import datetime, timezone, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import FastAPI, Depends, status
from fastapi.testclient import TestClient
from backend.api.auth import hash_password, verify_password, router as auth_router
from backend.api.deps import get_current_company_id

app = FastAPI()
app.include_router(auth_router)


@app.get("/test-protected")
async def protected_route(company_id=Depends(get_current_company_id)):
    return {"company_id": str(company_id)}


client = TestClient(app)


def test_password_hashing_and_verification():
    raw_password = "secure_password_123"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert "$" in hashed
    assert verify_password(raw_password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


@patch("backend.api.deps.database")
def test_dependency_token_valid(mock_db):
    company_uuid = uuid4()
    session_uuid = uuid4()

    mock_conn = AsyncMock()
    mock_db.acquire.return_value.__aenter__.return_value = mock_conn

    mock_conn.fetchrow.return_value = {
        "company_id": company_uuid,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=1)
    }

    headers = {"Authorization": f"Bearer {session_uuid}"}
    response = client.get("/test-protected", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"company_id": str(company_uuid)}
    mock_conn.fetchrow.assert_called_once()


@patch("backend.api.deps.database")
def test_dependency_token_expired(mock_db):
    company_uuid = uuid4()
    session_uuid = uuid4()

    mock_conn = AsyncMock()
    mock_db.acquire.return_value.__aenter__.return_value = mock_conn
    mock_conn.fetchrow.return_value = {
        "company_id": company_uuid,
        "expires_at": datetime.now(timezone.utc) - timedelta(days=1)
    }

    headers = {"Authorization": f"Bearer {session_uuid}"}
    response = client.get("/test-protected", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "expired" in response.json()["detail"].lower()


@patch("backend.api.deps.database")
def test_dependency_token_missing(mock_db):
    response = client.get("/test-protected")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "missing" in response.json()["detail"].lower()


@patch("backend.api.auth.database")
def test_signup_endpoint_success(mock_db):
    mock_conn = AsyncMock()
    mock_db.acquire.return_value.__aenter__.return_value = mock_conn

    mock_conn.fetchval.side_effect = [None, uuid4()]

    payload = {
        "name": "Acme Inc",
        "email": "info@acme.com",
        "password": "supersecurepassword"
    }

    response = client.post("/api/auth/signup", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert "session_token" in response.json()
    assert "company_id" in response.json()
    assert "session_token" in response.cookies


@patch("backend.api.auth.database")
def test_login_endpoint_success(mock_db):
    company_uuid = uuid4()
    mock_conn = AsyncMock()
    mock_db.acquire.return_value.__aenter__.return_value = mock_conn

    password = "securepassword"
    pwd_hash = hash_password(password)

    mock_conn.fetchrow.return_value = {
        "id": company_uuid,
        "password_hash": pwd_hash
    }

    payload = {
        "email": "user@acme.com",
        "password": password
    }

    response = client.post("/api/auth/login", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert "session_token" in response.json()
    assert response.json()["company_id"] == str(company_uuid)
