import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_contact_endpoint_requires_data():
    print("\nTesting contact endpoint rejects empty requests")
    response = client.post("/contact")
    assert response.status_code == 422  # Validation error for missing required fields