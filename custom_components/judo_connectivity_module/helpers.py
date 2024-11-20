"""Helper functions for entity configuration."""

from pathlib import Path

import yaml


def load_entity_configs() -> dict:
    """Load entity configurations from YAML."""
    config_dir = Path(__file__).parent / "config"
    with (config_dir / "entities.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)["entities"]
