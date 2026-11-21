"""Tests for JUDO Connectivity Module API client."""

from unittest.mock import AsyncMock

import aiohttp
import pytest

from custom_components.judo_connectivity_module.api import (
    JudoConnectivityModuleApiClient,
    JudoConnectivityModuleApiClientAuthenticationError,
    JudoConnectivityModuleApiClientCommunicationError,
    JudoConnectivityModuleApiClientRateLimitError,
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "error"),
    [
        (429, JudoConnectivityModuleApiClientRateLimitError),
        (401, JudoConnectivityModuleApiClientAuthenticationError),
        (500, JudoConnectivityModuleApiClientCommunicationError),
    ],
)
async def test_http_errors_are_mapped(
    api_client: JudoConnectivityModuleApiClient,
    mock_session: AsyncMock,
    status: int,
    error: type[Exception],
) -> None:
    """HTTP errors become integration errors (429 is retried by the coordinator)."""
    mock_response = AsyncMock()
    mock_response.status = status
    mock_session.get = AsyncMock(return_value=mock_response)

    with pytest.raises(error):
        await api_client.async_get_device_type()


@pytest.mark.asyncio
async def test_network_error_is_mapped(
    api_client: JudoConnectivityModuleApiClient, mock_session: AsyncMock
) -> None:
    """Connection problems become a communication error, not a raw aiohttp error."""
    mock_session.get = AsyncMock(side_effect=aiohttp.ClientConnectionError("down"))

    with pytest.raises(JudoConnectivityModuleApiClientCommunicationError):
        await api_client.async_get_device_type()
