"""Common test fixtures for JUDO Connectivity Module."""

from asyncio import AbstractEventLoop
from pathlib import Path
from unittest.mock import AsyncMock

import aiohttp
import pytest
from homeassistant.core import HomeAssistant

from custom_components.judo_connectivity_module.api import (
    JudoConnectivityModuleApiClient,
)


@pytest.fixture(name="mock_session")
def setup_mock_session() -> AsyncMock:
    """Fixture for aiohttp client session."""
    return AsyncMock(spec=aiohttp.ClientSession)


@pytest.fixture(name="api_client")
def setup_api_client(mock_session: AsyncMock) -> JudoConnectivityModuleApiClient:
    """Fixture for API client."""
    return JudoConnectivityModuleApiClient(
        hostname="192.168.1.100",
        username="admin",
        password="password",  # noqa: S106
        session=mock_session,
    )


@pytest.fixture
def hass(event_loop: AbstractEventLoop, tmp_path: Path) -> HomeAssistant:
    """Fixture for Home Assistant instance."""
    return HomeAssistant(config_dir=str(tmp_path))
