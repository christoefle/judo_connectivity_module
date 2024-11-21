"""JudoConnectivityModule entity class."""

from __future__ import annotations

from pathlib import Path

import yaml
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import JudoConnectivityModuleDataUpdateCoordinator

# Load device specifications
API_SPEC_DIR = Path(__file__).parent / "api_spec"
DEVICES = yaml.safe_load((API_SPEC_DIR / "devices.yaml").open(encoding="utf-8"))[
    "device_types"
]


class JudoConnectivityModuleEntity(
    CoordinatorEntity[JudoConnectivityModuleDataUpdateCoordinator]
):
    """JudoConnectivityModule base entity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        device_type = self.coordinator.data.get("get_device_type", {}).get("decoded")
        device_name = DEVICES.get(str(device_type), {}).get("name", "JUDO Device")

        sw_version_raw = self.coordinator.data.get("read_software_version", {}).get(
            "decoded", ""
        )
        sw_version = sw_version_raw if sw_version_raw else "unknown"

        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    str(
                        self.coordinator.data.get("read_serial_number", {}).get(
                            "decoded", ""
                        )
                    ),
                )
            },
            name=device_name,
            manufacturer="JUDO",
            model=device_name,
            sw_version=sw_version,
        )
