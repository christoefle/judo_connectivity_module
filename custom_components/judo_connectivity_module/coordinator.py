"""DataUpdateCoordinator for judo_connectivity_module."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    JudoConnectivityModuleApiClientAuthenticationError,
    JudoConnectivityModuleApiClientError,
)
from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import JudoConnectivityModuleConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class JudoConnectivityModuleDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: JudoConnectivityModuleConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except JudoConnectivityModuleApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except JudoConnectivityModuleApiClientError as exception:
            raise UpdateFailed(exception) from exception
