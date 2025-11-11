"""API specification loader for JUDO Connectivity Module."""

import asyncio
from pathlib import Path
from typing import Any

import aiofiles
import yaml

# Path to the api_spec directory
API_SPEC_DIR = Path(__file__).parent

# Global variables to store loaded specifications (will be populated on import)
BASE_SPEC: dict[str, Any] = {}
DEVICE_SPEC: dict[str, Any] = {}
OPERATIONS_SPEC: dict[str, Any] = {}


async def load_yaml_file(file_path: Path) -> dict[str, Any]:
    """Load a single YAML file asynchronously.

    Args:
        file_path: Path to the YAML file.

    Returns:
        Parsed YAML content as a dictionary.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        yaml.YAMLError: If the YAML is invalid.
    """
    async with aiofiles.open(file_path, encoding="utf-8") as file:
        content = await file.read()
        return yaml.safe_load(content) or {}


def _load_yaml_file_sync(file_path: Path) -> dict[str, Any]:
    """Load a single YAML file synchronously.

    Args:
        file_path: Path to the YAML file.

    Returns:
        Parsed YAML content as a dictionary.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        yaml.YAMLError: If the YAML is invalid.
    """
    with file_path.open(encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


async def load_all_specs() -> None:
    """Load all API specification files asynchronously.

    This function loads base.yaml, devices.yaml, and operations.yaml
    and stores them in global variables for use throughout the module.

    Raises:
        FileNotFoundError: If any specification file is missing.
        yaml.YAMLError: If any YAML file is invalid.
    """
    global BASE_SPEC, DEVICE_SPEC, OPERATIONS_SPEC  # pylint: disable=global-statement

    try:
        # Load all YAML files concurrently
        results = await asyncio.gather(
            load_yaml_file(API_SPEC_DIR / "base.yaml"),
            load_yaml_file(API_SPEC_DIR / "devices.yaml"),
            load_yaml_file(API_SPEC_DIR / "operations.yaml"),
        )

        BASE_SPEC, DEVICE_SPEC, OPERATIONS_SPEC = results

    except FileNotFoundError as err:
        raise FileNotFoundError(f"API specification file not found: {err}") from err
    except yaml.YAMLError as err:
        raise yaml.YAMLError(f"Invalid YAML in API specification: {err}") from err


def _load_all_specs_sync() -> None:
    """Load all API specification files synchronously (used on import).

    Raises:
        FileNotFoundError: If any specification file is missing.
        yaml.YAMLError: If any YAML file is invalid.
    """
    global BASE_SPEC, DEVICE_SPEC, OPERATIONS_SPEC  # pylint: disable=global-statement

    try:
        BASE_SPEC = _load_yaml_file_sync(API_SPEC_DIR / "base.yaml")
        DEVICE_SPEC = _load_yaml_file_sync(API_SPEC_DIR / "devices.yaml")
        OPERATIONS_SPEC = _load_yaml_file_sync(API_SPEC_DIR / "operations.yaml")

    except FileNotFoundError as err:
        raise FileNotFoundError(f"API specification file not found: {err}") from err
    except yaml.YAMLError as err:
        raise yaml.YAMLError(f"Invalid YAML in API specification: {err}") from err


def get_base_spec() -> dict[str, Any]:
    """Get the loaded base specification.

    Returns:
        Base specification dictionary.
    """
    return BASE_SPEC


def get_device_spec() -> dict[str, Any]:
    """Get the loaded device specification.

    Returns:
        Device specification dictionary.
    """
    return DEVICE_SPEC


def get_operations_spec() -> dict[str, Any]:
    """Get the loaded operations specification.

    Returns:
        Operations specification dictionary.
    """
    return OPERATIONS_SPEC


__all__ = [
    "BASE_SPEC",
    "DEVICE_SPEC",
    "OPERATIONS_SPEC",
    "get_base_spec",
    "get_device_spec",
    "get_operations_spec",
    "load_all_specs",
    "load_yaml_file",
]


# Load specifications synchronously on import
try:
    _load_all_specs_sync()
except (FileNotFoundError, yaml.YAMLError) as err:
    import warnings

    warnings.warn(
        f"Failed to load API specifications on import: {err}",
        stacklevel=2,
    )
