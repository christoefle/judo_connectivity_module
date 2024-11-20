"""Button platform for judo_connectivity_module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from .entity import JudoConnectivityModuleEntity
from .helpers import load_entity_configs

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import (
        JudoConnectivityModuleConfigEntry,
        JudoConnectivityModuleDataUpdateCoordinator,
    )


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: JudoConnectivityModuleConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    entity_configs = load_entity_configs()

    # Filter for button entities
    button_entities = [
        (key, config)
        for key, config in entity_configs.items()
        if config.get("type") == "button"
    ]

    async_add_entities(
        JudoConnectivityModuleButton(
            coordinator=entry.runtime_data.coordinator,
            entity_description=ButtonEntityDescription(
                key=key,
                name=config["name"],
                icon=config.get("icon"),
            ),
        )
        for key, config in button_entities
    )


class JudoConnectivityModuleButton(JudoConnectivityModuleEntity, ButtonEntity):
    """Judo Connectivity Module button class."""

    def __init__(
        self,
        coordinator: JudoConnectivityModuleDataUpdateCoordinator,
        entity_description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    def press(self) -> None:
        """Handle the button press synchronously."""
        self.hass.async_create_task(self.async_press())
