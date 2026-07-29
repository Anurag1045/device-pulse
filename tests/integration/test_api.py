import pytest
from app.main import app, _store


@pytest.fixture(autouse=True)
def clear_store():
    _store.clear()
    yield
    _store.clear()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_submit_report_returns_201(client):
    payload = {
        "battery_percent": 75.0,
        "temperature_celsius": 32.0,
        "wifi_signal_dbm": -55.0,
        "storage_used_percent": 40.0,
    }
    response = client.post("/devices/spectacles-001/report", json=payload)
    assert response.status_code == 201
    assert response.get_json()["accepted"] is True


def test_submit_unhealthy_report_returns_alerts(client):
    payload = {
        "battery_percent": 5.0,
        "temperature_celsius": 55.0,
        "wifi_signal_dbm": -55.0,
        "storage_used_percent": 40.0,
    }
    response = client.post("/devices/spectacles-002/report", json=payload)
    data = response.get_json()
    assert len(data["alerts"]) == 2


def test_get_status_for_known_device(client):
    client.post("/devices/spectacles-003/report", json={
        "battery_percent": 90.0,
        "temperature_celsius": 30.0,
        "wifi_signal_dbm": -50.0,
        "storage_used_percent": 20.0,
    })
    response = client.get("/devices/spectacles-003/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["healthy"] is True
    assert data["device_id"] == "spectacles-003"


def test_get_status_for_unknown_device_returns_404(client):
    response = client.get("/devices/ghost-device/status")
    assert response.status_code == 404


def test_list_devices_shows_submitted_devices(client):
    for i in range(3):
        client.post(f"/devices/device-{i}/report", json={
            "battery_percent": 80.0,
            "temperature_celsius": 30.0,
            "wifi_signal_dbm": -60.0,
            "storage_used_percent": 50.0,
        })
    response = client.get("/devices")
    assert response.get_json()["count"] == 3


def test_history_returns_all_reports(client):
    for _ in range(3):
        client.post("/devices/spectacles-004/report", json={
            "battery_percent": 80.0,
            "temperature_celsius": 30.0,
            "wifi_signal_dbm": -60.0,
            "storage_used_percent": 50.0,
        })
    response = client.get("/devices/spectacles-004/history")
    assert len(response.get_json()["reports"]) == 3


def test_submit_report_missing_fields_returns_400(client):
    response = client.post("/devices/spectacles-005/report", json={"battery_percent": 80.0})
    assert response.status_code == 400


def test_stats_returns_summary(client):
    client.post("/devices/spectacles-006/report", json={
        "battery_percent": 5.0,   # triggers LOW_BATTERY alert
        "temperature_celsius": 30.0,
        "wifi_signal_dbm": -60.0,
        "storage_used_percent": 50.0,
    })
    client.post("/devices/spectacles-007/report", json={
        "battery_percent": 80.0,
        "temperature_celsius": 30.0,
        "wifi_signal_dbm": -60.0,
        "storage_used_percent": 50.0,
    })
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total_devices"] == 2
    assert data["total_reports"] == 2
    assert data["unhealthy_count"] == 1
    assert "spectacles-006" in data["unhealthy_devices"]
