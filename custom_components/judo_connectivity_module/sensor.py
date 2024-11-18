"""Sensor platform for judo_connectivity_module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
)
from homeassistant.const import UnitOfVolume

from .entity import JudoConnectivityModuleEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import JudoConnectivityModuleDataUpdateCoordinator
    from .data import JudoConnectivityModuleConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="device_type",
        name="Device Type",
        icon="mdi:water-pump",
    ),
    SensorEntityDescription(
        key="serial_number",
        name="Serial Number",
        icon="mdi:identifier",
    ),
    SensorEntityDescription(
        key="software_version",
        name="Software Version",
        icon="mdi:package-variant",
    ),
    SensorEntityDescription(
        key="remaining_water",
        name="Remaining Water",
        icon="mdi:water-percent",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        device_class=SensorDeviceClass.WATER,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: JudoConnectivityModuleConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        JudoConnectivityModuleSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class JudoConnectivityModuleSensor(JudoConnectivityModuleEntity, SensorEntity):
    """judo_connectivity_module Sensor class."""

    def __init__(
        self,
        coordinator: JudoConnectivityModuleDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    def _convert_hex_to_version(self, hex_value: str) -> str:
        """Convert hex string to version format (e.g., 6b1502 -> 2.21k)."""
        if not hex_value or len(hex_value) != 6:
            return "unknown"

        # Example: "6b1502"
        letter_code = int(hex_value[0:2], 16)  # 6b -> 107 -> 'k'
        minor = int(hex_value[2:4], 16)  # 15 -> 21
        major = int(hex_value[4:6], 16)  # 02 -> 2

        # Convert directly to letter (107 -> 'k')
        patch = chr(letter_code)

        return f"{major}.{minor}{patch}"

    def _convert_hex_to_serial(self, hex_value: str) -> str:
        """Convert hex string to serial number format (e.g., 0774ed0b -> 200111111)."""
        if not hex_value or len(hex_value) != 8:
            return "unknown"
        # Convert hex to decimal
        return str(int(hex_value, 16))

    @property
    def native_value(self) -> str | int | None:
        """Return the sensor value."""
        if self.entity_description.key == "device_type":
            device_type = self.coordinator.data.get("device_type", {}).get("data")
            return "PROM-i-SAFE" if device_type == "44" else "JUDO Device"
        elif self.entity_description.key == "software_version":
            raw_value = self.coordinator.data.get("software_version", {}).get("data")
            return self._convert_hex_to_version(raw_value)
        elif self.entity_description.key == "serial_number":
            raw_value = self.coordinator.data.get("serial_number", {}).get("data")
            return self._convert_hex_to_serial(raw_value)
        elif self.entity_description.key == "remaining_water":
            return self.coordinator.data.get("remaining_water", {}).get("liters", 0)

        return None
