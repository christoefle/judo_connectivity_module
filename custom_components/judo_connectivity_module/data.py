"""Custom types for judo_connectivity_module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import JudoConnectivityModuleApiClient
    from .coordinator import JudoConnectivityModuleDataUpdateCoordinator


type JudoConnectivityModuleConfigEntry = ConfigEntry[JudoConnectivityModuleData]


@dataclass
class JudoConnectivityModuleData:
    """Data for the Blueprint integration."""

    client: JudoConnectivityModuleApiClient
    coordinator: JudoConnectivityModuleDataUpdateCoordinator
    integration: Integration
