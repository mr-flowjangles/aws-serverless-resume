import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_profile():
    print("\nTesting profile endpoint for all expected fields")
    response = client.get("/resume/profile")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "title" in data
    assert "email" in data
    assert "location" in data
    assert "summary" in data
    assert "github" in data
    assert "linkedin" in data