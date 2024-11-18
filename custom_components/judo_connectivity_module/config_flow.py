"""Adds config flow for Judo Connectivity Module."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    JudoConnectivityModuleApiClient,
    JudoConnectivityModuleApiClientAuthenticationError,
    JudoConnectivityModuleApiClientCommunicationError,
    JudoConnectivityModuleApiClientError,
)
from .const import DOMAIN, LOGGER


class JudoConnectivityModuleFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Judo Connectivity Module."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> data_entry_flow.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    host=user_input[CONF_HOST],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except JudoConnectivityModuleApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except JudoConnectivityModuleApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except JudoConnectivityModuleApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                            placeholder="192.168.1.100",
                        ),
                    ),
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_credentials(self, host: str, username: str, password: str) -> None:
        """Validate credentials."""
        client = JudoConnectivityModuleApiClient(
            host=host,
            username=username,
            password=password,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_device_info()
