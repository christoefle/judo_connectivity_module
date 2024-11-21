"""Integration tests for JUDO Connectivity Module."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.judo_connectivity_module.api import (
    JudoConnectivityModuleApiClient,
)
from custom_components.judo_connectivity_module.coordinator import (
    JudoConnectivityModuleDataUpdateCoordinator,
)


@pytest.mark.skip(reason="Integration tests need to be fixed")
@pytest.mark.asyncio
async def test_coordinator_update(hass: HomeAssistant) -> None:
    """Test coordinator data update."""
    mock_client = AsyncMock(spec=JudoConnectivityModuleApiClient)

    # Mock client responses
    mock_client.async_get_device_type.return_value = {"data": "44", "decoded": 68}
    mock_client.async_read_serial_number.return_value = {
        "data": "0774ed0b",
        "decoded": 200111111,
    }
    mock_client.async_read_total_water.return_value = {
        "data": "40420F00",
        "decoded": 1000.0,
    }
    mock_client.async_read_datetime.return_value = {
        "data": "170807E71520",
        "decoded": datetime(2023, 8, 23, 21, 32, 0, tzinfo=UTC),
    }

    coordinator = JudoConnectivityModuleDataUpdateCoordinator(
        hass=hass,
        client=mock_client,
    )

    # Test initial data fetch
    await coordinator.async_config_entry_first_refresh()
    assert coordinator.data is not None
    assert coordinator.data["device_type"]["decoded"] == 68
    assert coordinator.data["serial_number"]["decoded"] == 200111111
    assert coordinator.data["total_water"]["decoded"] == 1000.0

    # Test data update
    mock_client.async_read_total_water.return_value = {
        "data": "80840F00",
        "decoded": 1001.0,
    }
    await coordinator.async_refresh()
    assert coordinator.data["total_water"]["decoded"] == 1001.0


@pytest.mark.skip(reason="Integration tests need to be fixed")
@pytest.mark.asyncio
async def test_error_handling(hass: HomeAssistant) -> None:
    """Test coordinator error handling."""
    mock_client = AsyncMock(spec=JudoConnectivityModuleApiClient)
    mock_client.async_get_device_type.side_effect = Exception("Test error")

    coordinator = JudoConnectivityModuleDataUpdateCoordinator(
        hass=hass,
        client=mock_client,
    )

    # Test error handling during update
    with pytest.raises(Exception, match="Test error"):
        await coordinator.async_config_entry_first_refresh()
