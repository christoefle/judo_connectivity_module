"""Utility functions for JUDO Connectivity Module."""

from datetime import datetime, timezone
from pathlib import Path

import yaml


# Decoding functions for response patterns
def decode_hex_value(value: str) -> int:
    """Decode a hex string to an integer."""
    return int.from_bytes(bytes.fromhex(value), byteorder="little")


def decode_water_volume(value: str) -> float:
    """Decode a hex string to a water volume in cubic meters."""
    liters = int.from_bytes(bytes.fromhex(value), byteorder="little")
    return round(liters / 1000, 3)  # Convert to m³ with 3 decimal places


def decode_timestamp(value: str) -> datetime:
    """Decode a hex string to a UNIX timestamp in UTC."""
    timestamp = int.from_bytes(bytes.fromhex(value), byteorder="big")
    return datetime.fromtimestamp(
        timestamp,
        tz=timezone.utc,  # Use UTC timezone  # noqa: UP017
    )


def decode_version(value: str) -> str:
    """Decode a hex string to a version string."""
    letter = chr(int(value[0:2], 16))
    minor = int(value[2:4], 16)
    major = int(value[4:6], 16)
    return f"{major}.{minor}{letter}"


def decode_datetime_bytes(value: str) -> datetime:
    """Decode a hex string to a datetime object in UTC."""
    day = int(value[0:2], 16)
    month = int(value[2:4], 16)
    year = int(value[4:6], 16) + 2000  # Assuming years are 20xx
    hour = int(value[6:8], 16)
    minute = int(value[8:10], 16)
    second = int(value[10:12], 16)
    return datetime(
        year,
        month,
        day,
        hour,
        minute,
        second,
        tzinfo=timezone.utc,  # Use UTC timezone  # noqa: UP017
    )


def decode_serial_number(value: str) -> str:
    """Decode a hex string to a decimal serial number."""
    return str(decode_hex_value(value)) if value else ""


def get_device_name(device_type: str) -> str:
    """Get device name from device type."""
    api_spec_dir = Path(__file__).parent / "api_spec"
    devices = yaml.safe_load((api_spec_dir / "devices.yaml").open(encoding="utf-8"))[
        "device_types"
    ]
    return devices.get(device_type, {}).get("name", "JUDO Device")


# Encoding functions for parameter patterns
def encode_hex_date(date: datetime) -> str:
    """Encode a datetime object to a hex string representing a date."""
    return f"{date.day:02X}{date.month:02X}{date.year:04X}"


def encode_hex_week(week: int) -> str:
    """Encode a week number to a hex string."""
    return f"{week:02X}"


def encode_hex_month(month: int) -> str:
    """Encode a month number to a hex string."""
    return f"{month:02X}"


def encode_hex_year(year: int) -> str:
    """Encode a year to a hex string."""
    return f"{year:04X}"
