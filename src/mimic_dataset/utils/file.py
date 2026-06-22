"""
Configuration File Management

Provides utilities for loading and managing YAML configuration files
for different environments (dev, prod, etc.).
"""

import yaml
import json
import logging
from typing import Tuple, Dict, Any
from importlib import resources

logger = logging.getLogger(__name__)


def load_config(env: str = "dev") -> Tuple[Dict[str, Any], str]:
    """
    Load configuration from YAML file for the specified environment.

    Configuration files are located at:
    resources/configs/{env}/config.yaml

    Args:
        env (str): Environment name (default: "dev")
                   Options: "dev", "prod", etc.

    Returns:
        Tuple[Dict[str, Any], str]:
            - Dictionary containing configuration key-value pairs
            - JSON string representation of the configuration

    Raises:
        FileNotFoundError: If config file doesn't exist for the environment
        yaml.YAMLError: If YAML parsing fails
        Exception: For other configuration loading errors

    Example:
        >>> config, config_json = load_config("dev")
        >>> schema_name = config["schema_name"]
        >>> print(config_json)
    """
    config_path = f"resources/configs/{env}/config.yaml"

    try:
        logger.info(f"Loading configuration for environment: {env}")

        # Read file using importlib (works inside .whl)
        with resources.files("mimic_dataset").joinpath(config_path).open("r") as f:
            data = yaml.safe_load(f)

        if data is None:
            logger.warning(f"Configuration file {config_path} is empty")
            data = {}

        # Convert to JSON string
        json_data = json.dumps(data, indent=4)

        logger.info(f"✓ Configuration loaded successfully from {config_path}")
        logger.debug(f"Config keys: {list(data.keys())}")

        return data, json_data

    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise

    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in {config_path}: {e}")
        raise

    except Exception as e:
        logger.error(f"Failed to load configuration: {type(e).__name__}: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config_dict, config_json = load_config()

    print("DICT:", config_dict)
    print("\nJSON:\n", config_json)
