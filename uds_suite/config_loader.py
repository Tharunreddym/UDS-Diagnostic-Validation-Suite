"""
config_loader.py

Loads ECU simulation configuration from YAML.
"""

from pathlib import Path

import yaml


class ConfigLoader:
    """
    Loads YAML configuration for the simulated ECU.
    """

    def __init__(self, config_path: str = "config/ecu_config.yaml"):
        self.config_path = Path(config_path)

    def load(self) -> dict:
        """
        Load YAML config and return it as a dictionary.
        """

        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with self.config_path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file)