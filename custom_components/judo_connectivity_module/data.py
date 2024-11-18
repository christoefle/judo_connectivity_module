"""Custom types for judo_connectivity_module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:
    from homeassistant.loader import Integration

    from .api import JudoConnectivityModuleApiClient
    from .coordinator import JudoConnectivityModuleDataUpdateCoordinator


@dataclass
class JudoConnectivityModuleData:
    """Data for the JUDO Connectivity Module integration."""

    client: JudoConnectivityModuleApiClient
    coordinator: JudoConnectivityModuleDataUpdateCoordinator
    integration: Integration


T = TypeVar("T")
JudoConnectivityModuleConfigEntry = ConfigEntry[JudoConnectivityModuleData]
