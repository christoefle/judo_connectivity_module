"""DataUpdateCoordinator for judo_connectivity_module."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any, ClassVar

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
    _static_data: ClassVar[dict[str, Any]] = {}

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
        self._static_data = {}

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            # Get static data only once
            if not self._static_data:
                # Use initial data if available
                config_data = self.config_entry.data
                if (
                    "initial_device_type" in config_data
                    and "initial_serial_number" in config_data
                ):
                    LOGGER.debug("Using cached device information from config entry")
                    self._static_data = {
                        "device_type": config_data["initial_device_type"],
                        "serial_number": config_data["initial_serial_number"],
                    }
                else:
                    # Fall back to fetching from API
                    LOGGER.debug("Fetching device information from API")
                    client = self.config_entry.runtime_data.client
                    self._static_data = {
                        "device_type": await client.async_get_device_type(),
                        "serial_number": await client.async_get_serial_number(),
                    }

            # Get dynamic data
            dynamic_data = await self.config_entry.runtime_data.client.async_get_data(
                skip_static=True
            )

            # Combine static and dynamic data
            combined_data = {**self._static_data, **dynamic_data}

        except JudoConnectivityModuleApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except JudoConnectivityModuleApiClientError as exception:
            raise UpdateFailed(exception) from exception
        else:
            return combined_data
