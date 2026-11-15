import pytest
from fastapi.testclient import TestClient

from app.main import app, readings

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_readings():
    """Start every test with an empty readings list."""
    readings.clear()
    yield
    readings.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_valid_reading():
    payload = {"sensor_id": "motor1", "temperature": 72.5}
    response = client.post("/readings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["sensor_id"] == "motor1"
    assert data["temperature"] == 72.5
    assert "timestamp" in data


def test_reject_temperature_out_of_range():
    payload = {"sensor_id": "motor1", "temperature": 999}
    response = client.post("/readings", json=payload)
    assert response.status_code == 422


def test_reject_missing_sensor_id():
    response = client.post("/readings", json={"temperature": 50})
    assert response.status_code == 422


def test_list_returns_posted_readings():
    client.post("/readings", json={"sensor_id": "motor1", "temperature": 60})
    client.post("/readings", json={"sensor_id": "pump1", "temperature": 55})
    response = client.get("/readings")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_limit_parameter():
    for i in range(5):
        client.post("/readings", json={"sensor_id": "motor1", "temperature": 60 + i})
    response = client.get("/readings", params={"limit": 3})
    assert len(response.json()) == 3