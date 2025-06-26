import yaml
import os
from pathlib import Path


def load_config():
    """Load configuration from config.yaml file."""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"Configuration file not found at {config_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing configuration file: {e}")
        return None


def get_config_value(config, key_path, default=None):
    """Get a configuration value using dot notation (e.g., 'snelstart.username')."""
    if not config:
        return default
    
    keys = key_path.split('.')
    value = config
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default