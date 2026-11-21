"""JUDO Connectivity Module API Client."""

from __future__ import annotations

import asyncio
import importlib
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiohttp
import async_timeout
import yaml

if TYPE_CHECKING:
    from collections.abc import Callable

LOGGER = logging.getLogger(__name__)

# Load API specifications
API_SPEC_DIR = Path(__file__).parent / "api_spec"
OPERATIONS = yaml.safe_load((API_SPEC_DIR / "operations.yaml").open(encoding="utf-8"))[
    "operations"
]
BASE_SPEC = yaml.safe_load((API_SPEC_DIR / "base.yaml").open(encoding="utf-8"))

# HTTP Status Codes
HTTP_SUCCESS_STATUS = 200
HTTP_UNAUTHORIZED = 401
HTTP_TOO_MANY_REQUESTS = 429

# The module answers HTTP 429 when requests come in too fast (seen in the field after a burst
# of sequential reads). All requests go through one lock with a minimum gap between them.
MIN_REQUEST_INTERVAL = 2.0  # seconds


class JudoConnectivityModuleApiClientError(Exception):
    """Exception raised for general JUDO Connectivity Module API errors."""

    def __init__(self, message: str = "API error occurred") -> None:
        """Initialize the exception."""
        self.message = message
        super().__init__(self.message)


class JudoConnectivityModuleApiClientAuthenticationError(Exception):
    """Exception raised for authentication errors with the JUDO Connectivity Module."""

    def __init__(self, message: str = "Authentication failed") -> None:
        """Initialize the exception."""
        self.message = message
        super().__init__(self.message)


class JudoConnectivityModuleApiClientCommunicationError(
    JudoConnectivityModuleApiClientError
):
    """Exception raised for communication errors with the JUDO Connectivity Module."""

    def __init__(self, message: str = "Communication failed") -> None:
        """Initialize the exception."""
        self.message = message
        super().__init__(self.message)


class JudoConnectivityModuleApiClientRateLimitError(
    JudoConnectivityModuleApiClientCommunicationError
):
    """Exception raised when the module answers HTTP 429 (too many requests)."""

    def __init__(self, message: str = "Rate limited by the device (HTTP 429)") -> None:
        """Initialize the exception."""
        self.message = message
        super().__init__(self.message)


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
        self._lock = asyncio.Lock()
        self._last_request = 0.0

        # Dynamically load decoder functions from utils module
        self._decoders = self._load_decoders()

    def _load_decoders(self) -> dict[str, Callable]:
        """Dynamically load decoder functions from patterns in base.yaml."""
        utils = importlib.import_module(".utils", package=__package__)
        patterns = BASE_SPEC.get("response_patterns", {})

        decoders = {}
        for pattern_name, pattern_spec in patterns.items():
            decoder_name = pattern_spec.get("decode_method")
            if decoder_name and hasattr(utils, decoder_name):
                decoders[pattern_name] = getattr(utils, decoder_name)

        return decoders

    def _verify_response_or_raise(self, response: aiohttp.ClientResponse) -> None:
        """Verify that the response is valid or raise an exception."""
        if response.status == HTTP_UNAUTHORIZED:
            raise JudoConnectivityModuleApiClientAuthenticationError
        if response.status == HTTP_TOO_MANY_REQUESTS:
            raise JudoConnectivityModuleApiClientRateLimitError
        if response.status != HTTP_SUCCESS_STATUS:
            msg = f"HTTP {response.status}"
            raise JudoConnectivityModuleApiClientCommunicationError(msg)

    def __getattr__(self, name: str) -> Callable:
        """Dynamically handle API operation calls."""
        if name.startswith("async_"):
            operation_name = name[6:]  # Remove async_ prefix
            operation = next(
                (op for op in OPERATIONS if op["name"] == operation_name),
                None,
            )
            if operation:
                return lambda **kwargs: self._async_call_operation(operation, **kwargs)

        error_message = f"No attribute {name}"
        raise AttributeError(error_message)

    async def _async_call_operation(
        self, operation: dict[str, Any], **params: Any
    ) -> dict[str, Any]:
        """Execute an API operation based on its specification."""
        # Format command with parameters if needed
        command = operation["command"]
        if params and "{" in command:
            command = command.format(**params)

        # Make API call
        response = await self._async_get_endpoint(command)

        # Process response according to pattern
        if "response" in operation:
            pattern_name = operation["response"]["pattern"]
            if pattern_name in self._decoders:
                decoder = self._decoders[pattern_name]
                data = response.get("data", "")
                try:
                    decoded_value = decoder(data)
                    return {  # noqa: TRY300
                        "data": data,  # Original hex string
                        "decoded": decoded_value,  # Decoded value
                    }
                except (ValueError, TypeError):
                    LOGGER.exception("Error decoding response: %s")
                    return {"data": data, "decoded": "unknown"}

        return response

    async def _async_get_endpoint(self, endpoint: str) -> dict:
        """Make a GET request to an endpoint."""
        url = f"http://{self._hostname}/api/rest/{endpoint}"

        async with self._lock:
            loop = asyncio.get_running_loop()
            wait = self._last_request + MIN_REQUEST_INTERVAL - loop.time()
            if wait > 0:
                await asyncio.sleep(wait)
            try:
                async with async_timeout.timeout(10):
                    response = await self._session.get(
                        url,
                        auth=aiohttp.BasicAuth(self._username, self._password),
                    )
                    self._verify_response_or_raise(response)
                    text = await response.text()
            except (aiohttp.ClientError, TimeoutError) as exception:
                msg = f"Error talking to {self._hostname}: {exception}"
                raise JudoConnectivityModuleApiClientCommunicationError(
                    msg
                ) from exception
            finally:
                self._last_request = loop.time()

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"data": text.strip()}

    @property
    def hostname(self) -> str:
        """Get the hostname."""
        return self._hostname

    @property
    def username(self) -> str:
        """Get the username."""
        return self._username

    @property
    def password(self) -> str:
        """Get the password."""
        return self._password
