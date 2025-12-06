# Enables forward references for type hints (allows you to refer to classes
# that are defined later in the file
from __future__ import annotations
# Imports the @dataclass decorator, which automatically generates 
# class boilerplate (constructor, repr, etc.).
from dataclasses import dataclass
# Imports Python’s datetime object so you can store timestamps.
from datetime import datetime
# Imports the Enum class for creating enumerations (fixed sets of constants).
from enum import Enum
# Allows using Optional[...] to specify a value that may also be None.
from typing import Optional

# ---------------------------------------------------------------
# ENUM DEFINITIONS
#-------------------------------------------------------------------
'''
Creates an enum named Transport.
Each member inherits from str and Enum (so they behave like strings).
Defines two possible transport protocols: "tcp" and "udp".
'''
class Transport(str, Enum):
    TCP = "tcp"
    UDP = "udp"

'''
Event types your IoT devices may generate.
Using Enum ensures values are restricted to these known types.
Values are strings: "heartbeat", "location", etc.
'''
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

# ----------------------
# DATA CLASSES
# ----------------------
# 📌 Device Class
'''
@dataclass automatically generates __init__, __repr__, and comparison methods.
device_id: str → unique device identifier.
name: str → human-readable device name.
scenario: str → scenario or use-case (e.g., "elderly-care", "outdoor", etc.).
status: str = "online" or "offline" .Default status is "online" unless set otherwise.
last_seen: Optional[datetime] = None
Tracks when device was last active.
Optional means it can be None initially.
'''
@dataclass
class Device:
    device_id: str
    name: str
    scenario: str
    status: str = "online"   # online/offline
    last_seen: Optional[datetime] = None

'''
Represents an alert raised by a device.
alert_id: str (Unique identifier for the alert)
device_id: str(Links alert to its device)
alert_type: AlertType (Must be one of the enum values (SOS, fall, hypothermia, water).
message: str (Human-readable explanation of the alert)
severity: int (Numeric severity scale (e.g., 1–10).
ts: datetime (Timestamp when alert occurred).
resolved: bool = False (Default: the alert is unresolved)
'''
@dataclass
class Alert:
    alert_id: str
    device_id: str
    alert_type: AlertType
    message: str
    severity: int
    ts: datetime
    resolved: bool = False
