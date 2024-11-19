"""Button platform for judo_connectivity_module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from .entity import JudoConnectivityModuleEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import (
        JudoConnectivityModuleConfigEntry,
        JudoConnectivityModuleDataUpdateCoordinator,
    )

ENTITY_DESCRIPTIONS = (
    ButtonEntityDescription(
        key="leak_protection_activate",
        name="Activate Leak Protection",
        icon="mdi:water-alert",
    ),
    ButtonEntityDescription(
        key="leak_protection_deactivate",
        name="Deactivate Leak Protection",
        icon="mdi:water-off",
    ),
    ButtonEntityDescription(
        key="sleep_mode_start",
        name="Start Sleep Mode",
        icon="mdi:sleep",
    ),
    ButtonEntityDescription(
        key="sleep_mode_end",
        name="Stop Sleep Mode",
        icon="mdi:sleep-off",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 # pylint: disable=unused-argument
    entry: JudoConnectivityModuleConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities(
        JudoConnectivityModuleButton(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
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

    async def async_press(self) -> None:
        """Handle the button press."""
        client = self.coordinator.config_entry.runtime_data.client

        if self.entity_description.key == "leak_protection_activate":
            await client.async_activate_leak_protection()
        elif self.entity_description.key == "leak_protection_deactivate":
            await client.async_deactivate_leak_protection()
        elif self.entity_description.key == "sleep_mode_start":
            await client.async_start_sleep_mode()
        elif self.entity_description.key == "sleep_mode_end":
            await client.async_end_sleep_mode()
