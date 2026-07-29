from app.models import HealthReport


THRESHOLDS = {
    "battery_low": 15.0,
    "temp_high": 45.0,
    "wifi_weak": -80.0,
    "storage_critical": 90.0,
}


def analyze(report: HealthReport) -> list[str]:
    alerts = []

    if report.battery_percent < THRESHOLDS["battery_low"]:
        alerts.append(f"LOW_BATTERY: {report.battery_percent}% (threshold: {THRESHOLDS['battery_low']}%)")

    if report.temperature_celsius > THRESHOLDS["temp_high"]:
        alerts.append(f"HIGH_TEMP: {report.temperature_celsius}°C (threshold: {THRESHOLDS['temp_high']}°C)")

    if report.wifi_signal_dbm < THRESHOLDS["wifi_weak"]:
        alerts.append(f"WEAK_WIFI: {report.wifi_signal_dbm} dBm (threshold: {THRESHOLDS['wifi_weak']} dBm)")

    if report.storage_used_percent > THRESHOLDS["storage_critical"]:
        alerts.append(f"STORAGE_CRITICAL: {report.storage_used_percent}% used (threshold: {THRESHOLDS['storage_critical']}%)")

    return alerts
