"""JUDO Connectivity Module API Client."""

from __future__ import annotations

import json
import logging
from typing import Any

import aiohttp
import async_timeout

from .utils import decode_hex_value

LOGGER = logging.getLogger(__name__)

# API Endpoints
ENDPOINT_DEVICE_TYPE = "FF00"
ENDPOINT_SERIAL_NUMBER = "0600"
ENDPOINT_SOFTWARE_VERSION = "0100"
ENDPOINT_LEAK_PROTECTION_ACTIVATE = "5100"
ENDPOINT_LEAK_PROTECTION_DEACTIVATE = "5200"
ENDPOINT_SLEEP_MODE_START = "5400"
ENDPOINT_SLEEP_MODE_END = "5500"
ENDPOINT_TOTAL_WATER = "2800"
ENDPOINT_RESET_MESSAGE = "6300"
ENDPOINT_DAILY_STATISTICS = "FB"
ENDPOINT_WEEKLY_STATISTICS = "FC"


class JudoConnectivityModuleApiClientError(Exception):
    """Exception to indicate a general API error."""

    MESSAGE = "An error occurred in the JUDO Connectivity Module API Client."


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

    async def async_get_data(self, *, skip_static: bool = False) -> dict[str, Any]:
        """Get data from the API."""
        try:
            async with async_timeout.timeout(10):
                data = {}
                if not skip_static:
                    device_type = await self.async_get_device_type()
                    serial_number = await self.async_get_serial_number()
                    data.update(
                        {
                            "device_type": device_type,
                            "serial_number": serial_number,
                        }
                    )

                software_version = await self.async_get_software_version()
                total_water_consumed = await self.async_get_total_water_consumed()

                data.update(
                    {
                        "software_version": software_version,
                        "total_water_consumed": total_water_consumed,
                    }
                )
                return data
        except Exception as exception:
            raise JudoConnectivityModuleApiClientError(
                JudoConnectivityModuleApiClientError.MESSAGE
            ) from exception

    async def async_get_device_type(self) -> str:
        """Get device type."""
        return await self._async_get_endpoint(ENDPOINT_DEVICE_TYPE)

    async def async_get_serial_number(self) -> dict[str, Any]:
        """Get serial number."""
        try:
            response = await self._async_get_endpoint(ENDPOINT_SERIAL_NUMBER)
            data = response.get("data", "")
            LOGGER.debug("Raw data received for serial number: %s", data)

            value = decode_hex_value(data)
            if value != "unknown":
                return {"serial_number": value}
            return {"serial_number": -1}  # noqa: TRY300
        except (aiohttp.ClientError, ValueError, AttributeError):
            LOGGER.exception("Error getting serial number: %s")
            return {"serial_number": -1}

    async def async_get_software_version(self) -> str:
        """Get software version."""
        return await self._async_get_endpoint(ENDPOINT_SOFTWARE_VERSION)

    async def async_get_total_water_consumed(self) -> dict[str, Any]:
        """Get total water consumed information."""
        try:
            response = await self._async_get_endpoint(ENDPOINT_TOTAL_WATER)
            data = response.get("data", "")
            LOGGER.debug("Raw data received for total water consumed: %s", data)
            value = decode_hex_value(data)
            return {"cubic_meters": value / 1000.0 if value != "unknown" else -1}
        except (aiohttp.ClientError, ValueError, AttributeError):
            LOGGER.exception("Error getting total water consumed")
            return {"cubic_meters": -1}

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

    async def async_reset_message(self) -> None:
        """Reset message."""
        await self._async_get_endpoint(ENDPOINT_RESET_MESSAGE)

    async def async_get_daily_statistics(self, date: str) -> dict:
        """Get daily statistics."""
        return await self._async_get_endpoint(f"{ENDPOINT_DAILY_STATISTICS}{date}")

    async def async_get_weekly_statistics(self, week: str) -> dict:
        """Get weekly statistics."""
        return await self._async_get_endpoint(f"{ENDPOINT_WEEKLY_STATISTICS}{week}")

    async def _async_get_endpoint(self, endpoint: str) -> dict:
        """Make a GET request to an endpoint."""
        url = f"http://{self._hostname}/api/rest/{endpoint}"
        LOGGER.debug("Making GET request to: %s", url)

        async with async_timeout.timeout(10):
            response = await self._session.get(
                url,
                auth=aiohttp.BasicAuth(self._username, self._password),
            )
            LOGGER.debug("Response status: %d", response.status)
            _verify_response_or_raise(response)
            text = await response.text()
            LOGGER.debug("Response text: %s", text)
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"data": text.strip()}

    @property
    def hostname(self) -> str:
        """Return the hostname."""
        return self._hostname

    @property
    def username(self) -> str:
        """Return the username."""
        return self._username

    @property
    def password(self) -> str:
        """Return the password."""
        return self._password


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that response is valid."""
    if response.status in (401, 403):
        raise JudoConnectivityModuleApiClientAuthenticationError(
            JudoConnectivityModuleApiClientAuthenticationError.MESSAGE
        )
    response.raise_for_status()
