
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)

def test_create_reading():
    response = client.post("/readings", json={
        "patient_id": 5,
        "sleep_duration_hours": 7.5,
        "heart_rate": 62,
        "is_deep_sleep": True,
        "recorded_at": "2026-08-17"
    })
    assert response.status_code == 200
    assert response.json()["patient_id"] == 5

def test_get_readings_not_found():
    response = client.get("/readings/999999")
    assert response.status_code == 404