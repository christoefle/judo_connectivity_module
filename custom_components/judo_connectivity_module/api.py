"""JUDO Connectivity Module API Client."""

from __future__ import annotations

import json
import logging
from typing import Any

import aiohttp
import async_timeout

LOGGER = logging.getLogger(__name__)

# API Endpoints
ENDPOINT_DEVICE_TYPE = "FF00"
ENDPOINT_SERIAL_NUMBER = "0600"
ENDPOINT_SOFTWARE_VERSION = "0100"
ENDPOINT_LEAK_PROTECTION_ACTIVATE = "5100"
ENDPOINT_LEAK_PROTECTION_DEACTIVATE = "5200"
ENDPOINT_SLEEP_MODE_START = "5400"
ENDPOINT_SLEEP_MODE_END = "5500"
ENDPOINT_REMAINING_WATER = "6400"


class JudoConnectivityModuleApiClientError(Exception):
    """Exception to indicate a general API error."""


class JudoConnectivityModuleApiClientCommunicationError(
    JudoConnectivityModuleApiClientError
):
    """Exception to indicate a communication error."""


class JudoConnectivityModuleApiClientAuthenticationError(
    JudoConnectivityModuleApiClientError
):
    """Exception to indicate an authentication error."""


class JudoConnectivityModuleApiClient:
    """JUDO Connectivity Module API Client."""

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize."""
        self._hostname = hostname
        self._username = username
        self._password = password
        self._session = session

    async def async_get_data(self) -> dict[str, Any]:
        """Get data from the API."""
        try:
            async with async_timeout.timeout(10):
                device_type = await self.async_get_device_type()
                serial_number = await self.async_get_serial_number()
                software_version = await self.async_get_software_version()
                remaining_water = await self.async_get_remaining_water()

                return {
                    "device_type": device_type,
                    "serial_number": serial_number,
                    "software_version": software_version,
                    "remaining_water": remaining_water,
                }
        except Exception as exception:
            raise JudoConnectivityModuleApiClientError(
                "Error getting data from API"
            ) from exception

    async def async_get_device_type(self) -> str:
        """Get device type."""
        return await self._async_get_endpoint(ENDPOINT_DEVICE_TYPE)

    async def async_get_serial_number(self) -> str:
        """Get serial number."""
        return await self._async_get_endpoint(ENDPOINT_SERIAL_NUMBER)

    async def async_get_software_version(self) -> str:
        """Get software version."""
        return await self._async_get_endpoint(ENDPOINT_SOFTWARE_VERSION)

    async def async_get_remaining_water(self) -> dict[str, Any]:
        """Get remaining water information."""
        response = await self._async_get_endpoint(ENDPOINT_REMAINING_WATER)
        data = response.get("data", "")
        if len(data) >= 8:  # Ensure we have enough data (8 hex characters)
            # Convert hex to decimal
            value_decimal = int(data, 16)
            # Convert to cubic meters (divide by 1000) then to liters (multiply by 1000)
            liters = value_decimal
            return {
                "liters": liters,
            }
        return {"liters": 0}

    async def async_activate_leak_protection(self) -> None:
        """Activate leak protection."""
        await self._async_get_endpoint(ENDPOINT_LEAK_PROTECTION_ACTIVATE)

    async def async_deactivate_leak_protection(self) -> None:
        """Deactivate leak protection."""
        await self._async_get_endpoint(ENDPOINT_LEAK_PROTECTION_DEACTIVATE)

    async def async_start_sleep_mode(self) -> None:
        """Start sleep mode."""
        await self._async_get_endpoint(ENDPOINT_SLEEP_MODE_START)

    async def async_end_sleep_mode(self) -> None:
        """End sleep mode."""
        await self._async_get_endpoint(ENDPOINT_SLEEP_MODE_END)

    async def _async_get_endpoint(self, endpoint: str) -> dict:
        """Make a GET request to an endpoint."""
        url = f"http://{self._hostname}/api/rest/{endpoint}"
        LOGGER.debug("Making GET request to: %s", url)

        async with async_timeout.timeout(10):
            response = await self._session.get(
                url,
                auth=aiohttp.BasicAuth(self._username, self._password),
            )
            _verify_response_or_raise(response)
            text = await response.text()
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"data": text.strip()}


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that response is valid."""
    if response.status in (401, 403):
        raise JudoConnectivityModuleApiClientAuthenticationError("Invalid credentials")
    response.raise_for_status()
