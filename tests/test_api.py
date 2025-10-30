import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert "item" in response.json()
