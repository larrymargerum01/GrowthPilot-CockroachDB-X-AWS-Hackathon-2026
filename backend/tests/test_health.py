from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check_success():
    """Test the health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    # It will be either 'ok' or 'degraded' depending on if the DB is actually running during tests
    assert data["status"] in ["ok", "degraded"]
