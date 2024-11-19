"""Tests for JUDO Connectivity Module API."""

from __future__ import annotations

from unittest.mock import AsyncMock

import aiohttp
import pytest

from custom_components.judo_connectivity_module.api import (
    JudoConnectivityModuleApiClient,
)


@pytest.fixture
def mock_session():
    """Fixture for aiohttp client session."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    return session


@pytest.fixture
def api_client(mock_session):
    """Fixture for API client."""
    return JudoConnectivityModuleApiClient(
        hostname="192.168.1.100",
        username="admin",
        password="password",
        session=mock_session,
    )


def test_api_client_initialization(api_client):
    """Test API client initialization."""
    assert api_client._hostname == "192.168.1.100"
    assert api_client._username == "admin"
    assert api_client._password == "password"


@pytest.mark.asyncio
async def test_get_device_type(api_client, mock_session):
    """Test getting device type."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text.return_value = '{"data": "44"}'

    # Ensure the get method is an AsyncMock
    mock_session.get = AsyncMock(return_value=mock_response)

    result = await api_client.async_get_device_type()

    assert result["data"] == "44"
    mock_session.get.assert_called_once_with(
        "http://192.168.1.100/api/rest/FF00",
        auth=aiohttp.BasicAuth("admin", "password"),
    )
