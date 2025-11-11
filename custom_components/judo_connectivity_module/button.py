"""Button platform for judo_connectivity_module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from .entity import JudoConnectivityModuleEntity
from .helpers import load_entity_configs
from .api_spec import DEVICE_SPEC, OPERATIONS_SPEC

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
    entity_configs = load_entity_configs()  # FIXME: Do it async
    device_type_id = entry.runtime_data.coordinator.data.get(
        "read_device_type", {}
    ).get("decoded", "0")
    device_spec = DEVICE_SPEC.get("device_types", {}).get(str(device_type_id))

    # Filter for button entities. Only add compatible button entities.
    button_entities = [
        (key, config)
        for key, config in entity_configs.items()
        if config.get("type") == "button" and key in device_spec.get("capabilities", {})
    ]

    async_add_entities(
        JudoConnectivityModuleButton(
            coordinator=entry.runtime_data.coordinator,
            client=entry.runtime_data.client,
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
        client,
        entity_description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button class."""
        super().__init__(coordinator)
        self._client = client
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    def press(self) -> None:
        """Handle the button press synchronously."""
        self.hass.add_job(self.async_press())

    async def async_press(self) -> None:
        """Handle the button press asynchronously."""
        operation = self._client.get_operation(self.entity_description.key)
        await self._client._async_call_operation(operation)
