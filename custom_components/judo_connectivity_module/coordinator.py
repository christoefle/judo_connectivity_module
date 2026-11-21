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
        # values that never change while HA runs (serial, type, ...) are read only once
        self._static: dict[str, Any] = {}

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            data = dict(self._static)
            # Get data for all sensor entities (static ones only on the first run)
            for entity_id, config in self._entity_configs.items():
                if config["type"] != "sensor" or entity_id in self._static:
                    continue
                method_name = f"async_{entity_id}"
                if hasattr(self._client, method_name):
                    data[entity_id] = await getattr(self._client, method_name)()
                    if config.get("static"):
                        self._static[entity_id] = data[entity_id]
            return data  # noqa: TRY300
        except JudoConnectivityModuleApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except JudoConnectivityModuleApiClientError as exception:
            raise UpdateFailed(exception) from exception
