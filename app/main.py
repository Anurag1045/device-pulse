from flask import Flask, request, jsonify
from app.models import HealthReport
from app.analyzer import analyze

app = Flask(__name__)
app.config["VERSION"] = "1.0.0"

# In-memory store: { device_id: [HealthReport, ...] }
_store: dict[str, list[HealthReport]] = {}


@app.get("/health")
def health_check():
    return jsonify({"status": "ok", "version": app.config["VERSION"]})


@app.post("/devices/<device_id>/report")
def submit_report(device_id: str):
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    required = ["battery_percent", "temperature_celsius", "wifi_signal_dbm", "storage_used_percent"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    report = HealthReport(
        device_id=device_id,
        battery_percent=float(data["battery_percent"]),
        temperature_celsius=float(data["temperature_celsius"]),
        wifi_signal_dbm=float(data["wifi_signal_dbm"]),
        storage_used_percent=float(data["storage_used_percent"]),
    )
    _store.setdefault(device_id, []).append(report)
    alerts = analyze(report)
    return jsonify({"device_id": device_id, "alerts": alerts, "accepted": True}), 201


@app.get("/devices/<device_id>/status")
def get_status(device_id: str):
    if device_id not in _store or not _store[device_id]:
        return jsonify({"error": f"No reports found for device '{device_id}'"}), 404

    latest = _store[device_id][-1]
    alerts = analyze(latest)
    return jsonify({
        "device_id": device_id,
        "latest_report": latest.to_dict(),
        "alerts": alerts,
        "healthy": len(alerts) == 0,
    })


@app.get("/devices/<device_id>/history")
def get_history(device_id: str):
    if device_id not in _store:
        return jsonify({"error": f"No reports found for device '{device_id}'"}), 404
    return jsonify({
        "device_id": device_id,
        "reports": [r.to_dict() for r in _store[device_id]],
    })


@app.get("/devices")
def list_devices():
    return jsonify({"devices": list(_store.keys()), "count": len(_store)})
