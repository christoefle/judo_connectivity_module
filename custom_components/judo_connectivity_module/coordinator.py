"""DataUpdateCoordinator for judo_connectivity_module."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    JudoConnectivityModuleApiClient,
    JudoConnectivityModuleApiClientAuthenticationError,
    JudoConnectivityModuleApiClientError,
)
from .const import DOMAIN, LOGGER
from .helpers import load_entity_configs

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


class JudoConnectivityModuleDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: JudoConnectivityModuleApiClient,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )
        self._entity_configs = load_entity_configs()
        self._client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            data = {}
            # Get data for all sensor entities
            for entity_id, config in self._entity_configs.items():
                if config["type"] == "sensor":
                    method_name = f"async_{entity_id}"
                    if hasattr(self._client, method_name):
                        data[entity_id] = await getattr(self._client, method_name)()
            return data  # noqa: TRY300
        except JudoConnectivityModuleApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except JudoConnectivityModuleApiClientError as exception:
            raise UpdateFailed(exception) from exception
