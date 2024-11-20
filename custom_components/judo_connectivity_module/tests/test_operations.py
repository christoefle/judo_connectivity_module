"""Tests for JUDO Connectivity Module API operations."""

from unittest.mock import AsyncMock

import aiohttp
import pytest

from custom_components.judo_connectivity_module.api import (
    JudoConnectivityModuleApiClient,
)


@pytest.mark.asyncio
async def test_get_device_type(
    api_client: JudoConnectivityModuleApiClient, mock_session: AsyncMock
) -> None:
    """Test getting device type."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text.return_value = '{"data": "44"}'

    mock_session.get = AsyncMock(return_value=mock_response)

    result = await api_client.async_get_device_type()

    assert result["data"] == "44"
    mock_session.get.assert_called_once_with(
        "http://192.168.1.100/api/rest/FF00",
        auth=aiohttp.BasicAuth("admin", "password"),
    )


@pytest.mark.asyncio
async def test_dynamic_operation_call(
    api_client: JudoConnectivityModuleApiClient, mock_session: AsyncMock
) -> None:
    """Test dynamic operation calling based on YAML specs."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text.return_value = '{"data": "0774ed0b"}'
    mock_session.get = AsyncMock(return_value=mock_response)

    result = await api_client.async_read_serial_number()

    assert "data" in result
    assert result["data"] == "0774ed0b"
    mock_session.get.assert_called_once_with(
        "http://192.168.1.100/api/rest/0600",
        auth=aiohttp.BasicAuth("admin", "password"),
    )

    with pytest.raises(AttributeError):
        await api_client.async_invalid_operation()


@pytest.mark.asyncio
async def test_operations_with_samples(
    api_client: JudoConnectivityModuleApiClient, mock_session: AsyncMock
) -> None:
    """Test operations using the test samples from operations.yaml."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_session.get = AsyncMock(return_value=mock_response)

    # Test device type
    mock_response.text.return_value = '{"data": "44"}'
    result = await api_client.async_get_device_type()
    assert result["data"] == "44"
    assert result["decoded"] == 68
    mock_session.get.assert_called_with(
        "http://192.168.1.100/api/rest/FF00",
        auth=aiohttp.BasicAuth("admin", "password"),
    )

    # Test serial number
    mock_response.text.return_value = '{"data": "0774ed0b"}'
    result = await api_client.async_read_serial_number()
    assert result["data"] == "0774ed0b"
    assert result["decoded"] == 200111111
    mock_session.get.assert_called_with(
        "http://192.168.1.100/api/rest/0600",
        auth=aiohttp.BasicAuth("admin", "password"),
    )

    # Test start date
    mock_response.text.return_value = '{"data": "6414CB7B"}'
    result = await api_client.async_read_start_date()
    assert result["data"] == "6414CB7B"
    assert result["decoded"].isoformat() == "2023-03-17T21:20:00"
    mock_session.get.assert_called_with(
        "http://192.168.1.100/api/rest/0E00",
        auth=aiohttp.BasicAuth("admin", "password"),
    )

    # Test software version
    mock_response.text.return_value = '{"data": "661301"}'
    result = await api_client.async_read_software_version()
    assert result["data"] == "661301"
    assert result["decoded"] == "1.19f"
    mock_session.get.assert_called_with(
        "http://192.168.1.100/api/rest/0100",
        auth=aiohttp.BasicAuth("admin", "password"),
    )
