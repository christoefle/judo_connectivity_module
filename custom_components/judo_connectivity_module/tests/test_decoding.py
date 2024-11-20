"""Tests for JUDO Connectivity Module response decoding."""

from datetime import datetime, timezone

from custom_components.judo_connectivity_module.utils import (
    decode_datetime_bytes,
    decode_hex_value,
    decode_serial_number,
    decode_timestamp,
    decode_version,
    decode_water_volume,
    get_device_name,
)


def test_decode_hex_value() -> None:
    """Test hex value decoding."""
    assert decode_hex_value("44") == 68  # Device type
    assert decode_hex_value("0774ed0b") == 200111111  # Serial number


def test_decode_water_volume() -> None:
    """Test water volume decoding."""
    # Test various water volumes
    assert decode_water_volume("40420F00") == 1000.0  # 1,000,000 liters = 1000 m³
    assert decode_water_volume("10270000") == 10.0  # 10,000 liters = 10 m³
    assert decode_water_volume("A0860100") == 100.0  # 100,000 liters = 100 m³
    assert decode_water_volume("80969800") == 10000.0  # 10,000,000 liters = 10000 m³


def test_decode_timestamp() -> None:
    """Test timestamp decoding."""
    # Test the sample timestamp from operations.yaml
    decoded = decode_timestamp("6414CB7B")
    assert isinstance(decoded, datetime)
    assert decoded.year == 2023
    assert decoded.month == 3
    assert decoded.day == 17


def test_decode_version() -> None:
    """Test version string decoding."""
    assert decode_version("661301") == "1.19f"  # Major.Minorf
    assert decode_version("651A02") == "2.26e"  # Major.Minore


def test_decode_datetime_bytes() -> None:
    """Test datetime bytes decoding."""
    # Test sample from operations.yaml
    decoded = decode_datetime_bytes("1c04170e041e")
    assert isinstance(decoded, datetime)
    assert decoded == datetime(2023, 4, 28, 14, 4, 30, tzinfo=timezone.utc)

    # Test edge case - January 1, 2023, 00:00:00
    assert decode_datetime_bytes("010117000000") == datetime(
        2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc
    )


def test_decode_serial_number() -> None:
    """Test serial number decoding."""
    assert decode_serial_number("0774ed0b") == "200111111"
    assert decode_serial_number("") == ""


def test_get_device_name() -> None:
    """Test device name lookup."""
    assert get_device_name("68") == "PROM-i-SAFE"
