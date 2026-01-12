import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_skills():
    print("\nTesting skills endpoint returns items")
    response = client.get("/resume/skills")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)