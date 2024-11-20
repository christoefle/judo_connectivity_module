"""Tests for JUDO Connectivity Module API client."""

from unittest.mock import AsyncMock

import aiohttp
import pytest

from custom_components.judo_connectivity_module.api import (
    JudoConnectivityModuleApiClient,
)


def test_api_client_initialization(api_client: JudoConnectivityModuleApiClient) -> None:
    """Test API client initialization."""
    assert api_client.hostname == "192.168.1.100"
    assert api_client.username == "admin"
    assert api_client.password == "password"  # noqa: S105


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
