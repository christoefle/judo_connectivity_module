"""JUDO Connectivity Module API Client."""

from __future__ import annotations

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
        if response.status != HTTP_SUCCESS_STATUS:
            raise aiohttp.ClientResponseError(
                response.request_info,
                response.history,
                status=response.status,
                message=f"HTTP {response.status}",
            )

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

        async with async_timeout.timeout(10):
            response = await self._session.get(
                url,
                auth=aiohttp.BasicAuth(self._username, self._password),
            )
            self._verify_response_or_raise(response)
            text = await response.text()

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
