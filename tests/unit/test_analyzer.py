from app.models import HealthReport
from app.analyzer import analyze


def _make_report(**kwargs):
    defaults = dict(
        device_id="test-device",
        battery_percent=80.0,
        temperature_celsius=35.0,
        wifi_signal_dbm=-60.0,
        storage_used_percent=50.0,
    )
    defaults.update(kwargs)
    return HealthReport(**defaults)


def test_healthy_device_has_no_alerts():
    report = _make_report()
    assert analyze(report) == []


def test_low_battery_triggers_alert():
    report = _make_report(battery_percent=10.0)
    alerts = analyze(report)
    assert any("LOW_BATTERY" in a for a in alerts)


def test_battery_exactly_at_threshold_is_safe():
    report = _make_report(battery_percent=15.0)
    alerts = analyze(report)
    assert not any("LOW_BATTERY" in a for a in alerts)


def test_high_temperature_triggers_alert():
    report = _make_report(temperature_celsius=50.0)
    alerts = analyze(report)
    assert any("HIGH_TEMP" in a for a in alerts)


def test_weak_wifi_triggers_alert():
    report = _make_report(wifi_signal_dbm=-85.0)
    alerts = analyze(report)
    assert any("WEAK_WIFI" in a for a in alerts)


def test_full_storage_triggers_alert():
    report = _make_report(storage_used_percent=95.0)
    alerts = analyze(report)
    assert any("STORAGE_CRITICAL" in a for a in alerts)


def test_multiple_issues_generate_multiple_alerts():
    report = _make_report(battery_percent=5.0, temperature_celsius=55.0)
    alerts = analyze(report)
    assert len(alerts) == 2
