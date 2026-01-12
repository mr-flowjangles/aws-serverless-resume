import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_work_experience():
    print("\nTesting work experience endpoint returns items")
    response = client.get("/resume/work-experience")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)