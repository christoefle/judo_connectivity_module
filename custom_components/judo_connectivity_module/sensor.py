"""Sensor platform for judo_connectivity_module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)

from .entity import JudoConnectivityModuleEntity
from .helpers import load_entity_configs

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import JudoConnectivityModuleDataUpdateCoordinator
    from .data import JudoConnectivityModuleConfigEntry


class JudoConnectivityModuleSensor(JudoConnectivityModuleEntity, SensorEntity):
    """Judo Connectivity Module sensor class."""

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

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key, {}).get("decoded")


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: JudoConnectivityModuleConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    entity_configs = load_entity_configs()

    # Filter for sensor entities
    sensor_entities = [
        (key, config)
        for key, config in entity_configs.items()
        if config.get("type") == "sensor"
    ]

    async_add_entities(
        JudoConnectivityModuleSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=SensorEntityDescription(
                key=key,
                name=config["name"],
                icon=config.get("icon"),
                device_class=config.get("device_class"),
                native_unit_of_measurement=config.get("unit"),
                state_class=config.get("state_class"),
            ),
        )
        for key, config in sensor_entities
    )
