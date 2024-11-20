"""Adds config flow for Judo Connectivity Module."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import voluptuous as vol
from dotenv import load_dotenv
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    JudoConnectivityModuleApiClient,
    JudoConnectivityModuleApiClientAuthenticationError,
    JudoConnectivityModuleApiClientCommunicationError,
)
from .const import DOMAIN, LOGGER

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Get default values from environment variables or fall back to defaults
DEFAULT_HOST = os.getenv("JUDO_DEFAULT_HOST", "192.168.1.1")
DEFAULT_USERNAME = os.getenv("JUDO_DEFAULT_USERNAME", "admin")
DEFAULT_PASSWORD = os.getenv("JUDO_DEFAULT_PASSWORD", "Connectivity")

# Define a constant for the expected serial number length
EXPECTED_SERIAL_LENGTH = 8


class JudoConnectivityModuleFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Judo Connectivity Module."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            try:
                client = JudoConnectivityModuleApiClient(
                    hostname=user_input[CONF_HOST],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    session=async_create_clientsession(self.hass),
                )

                # Get device information for the title
                device_type = await client.async_get_device_type()
                serial_number = await client.async_get_serial_number()

                # Store the initial data
                initial_data = {
                    **user_input,
                    "initial_device_type": device_type,
                    "initial_serial_number": serial_number,
                }

                # Determine device name based on type
                device_name = (
                    "PROM-i-SAFE" if device_type.get("data") == "44" else "JUDO Device"
                )

                # Convert serial number from hex to decimal using little-endian
                serial_hex = serial_number.get("data", "")
                serial_decoded = (
                    str(int.from_bytes(bytes.fromhex(serial_hex), byteorder="little"))
                    if serial_hex and len(serial_hex) == EXPECTED_SERIAL_LENGTH
                    else ""
                )

                # Create title with device name and decoded serial number
                title = f"{device_name} ({serial_decoded})"

                return self.async_create_entry(
                    title=title,
                    data=initial_data,
                )
            except JudoConnectivityModuleApiClientAuthenticationError:
                errors["base"] = "auth"
            except JudoConnectivityModuleApiClientCommunicationError:
                errors["base"] = "connection"
            except Exception:  # pylint: disable=broad-except  # noqa: BLE001
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                    vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return JudoConnectivityModuleOptionsFlow(config_entry)


class JudoConnectivityModuleOptionsFlow(config_entries.OptionsFlow):
    """Judo Connectivity Module config flow options handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            try:
                client = JudoConnectivityModuleApiClient(
                    hostname=user_input[CONF_HOST],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    session=async_create_clientsession(self.hass),
                )
                await client.async_get_device_type()

                return self.async_create_entry(title="", data=user_input)
            except JudoConnectivityModuleApiClientAuthenticationError:
                errors["base"] = "auth"
            except JudoConnectivityModuleApiClientCommunicationError:
                errors["base"] = "connection"
            except Exception:  # pylint: disable=broad-except  # noqa: BLE001
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=self.config_entry.data.get(CONF_HOST),
                    ): str,
                    vol.Required(
                        CONF_USERNAME,
                        default=self.config_entry.data.get(CONF_USERNAME),
                    ): str,
                    vol.Required(
                        CONF_PASSWORD,
                        default=self.config_entry.data.get(CONF_PASSWORD),
                    ): str,
                }
            ),
            errors=errors,
        )
