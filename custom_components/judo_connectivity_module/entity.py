"""JudoConnectivityModule entity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import JudoConnectivityModuleDataUpdateCoordinator


class JudoConnectivityModuleEntity(
    CoordinatorEntity[JudoConnectivityModuleDataUpdateCoordinator]
):
    """JudoConnectivityModule base entity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    VERSION_HEX_LENGTH = 6

    def _convert_hex_to_version(self, hex_value: str) -> str:
        """Convert hex string to version format."""
        if not hex_value or len(hex_value) != self.VERSION_HEX_LENGTH:
            return "unknown"
        letter_code = int(hex_value[0:2], 16)
        minor = int(hex_value[2:4], 16)
        major = int(hex_value[4:6], 16)
        patch = chr(letter_code)
        return f"{major}.{minor}{patch}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        device_type = self.coordinator.data.get("device_type", {}).get("data")
        device_name = "PROM-i-SAFE" if device_type == "44" else "JUDO Device"

        # Get raw version and convert it
        sw_version_raw = self.coordinator.data.get("software_version", {}).get(
            "data", ""
        )
        sw_version = self._convert_hex_to_version(sw_version_raw)

        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    str(self.coordinator.data.get("serial_number", {}).get("data", "")),
                )
            },
            name=device_name,
            manufacturer="JUDO",
            model=device_name,
            sw_version=sw_version,
        )
