from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class HealthReport:
    device_id: str
    battery_percent: float
    temperature_celsius: float
    wifi_signal_dbm: float
    storage_used_percent: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "battery_percent": self.battery_percent,
            "temperature_celsius": self.temperature_celsius,
            "wifi_signal_dbm": self.wifi_signal_dbm,
            "storage_used_percent": self.storage_used_percent,
            "timestamp": self.timestamp,
        }
