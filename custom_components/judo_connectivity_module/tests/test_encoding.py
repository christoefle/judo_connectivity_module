"""Tests for JUDO Connectivity Module parameter encoding."""

from datetime import datetime

from custom_components.judo_connectivity_module.utils import (
    encode_hex_date,
    encode_hex_month,
    encode_hex_week,
    encode_hex_year,
)


def test_encode_date() -> None:
    """Test daily statistics date parameter encoding."""
    date = datetime.strptime("13 August 2023", "%d %B %Y")
    encoded_date = encode_hex_date(date)
    assert encoded_date == "0D0807E7"


def test_encode_week() -> None:
    """Test weekly statistics parameter encoding."""
    week = 32  # From "Week 32 2023"
    encoded_week = encode_hex_week(week)
    assert encoded_week == "20"


def test_encode_month() -> None:
    """Test monthly statistics parameter encoding."""
    month_date = datetime.strptime("August 2023", "%B %Y")
    encoded_month = encode_hex_month(month_date.month)
    assert encoded_month == "08"


def test_encode_year() -> None:
    """Test yearly statistics parameter encoding."""
    year = 2023
    encoded_year = encode_hex_year(year)
    assert encoded_year == "07E7"
