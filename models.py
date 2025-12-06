from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class Transport(str, Enum):
    TCP = "tcp"
    UDP = "udp"

class EventType(str, Enum):
    HEARTBEAT = "heartbeat"
    LOCATION = "location"
    TEMPERATURE = "temperature"
    ALERT = "alert"
    STATUS = "status"

class AlertType(str, Enum):
    SOS = "sos"
    FALL = "fall"
    HYPOTHERMIA = "hypothermia"
    WATER = "water"

@dataclass
class Device:
    device_id: str
    name: str
    scenario: str
    status: str = "online"   # online/offline
    last_seen: Optional[datetime] = None

@dataclass
class Alert:
    alert_id: str
    device_id: str
    alert_type: AlertType
    message: str
    severity: int
    ts: datetime
    resolved: bool = False
