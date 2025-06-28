import yaml
import os
from pathlib import Path

# Try to import dotenv, but don't fail if it's not available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


def load_config():
    """Load configuration from config.yaml file and environment variables."""
    # Load .env file if available
    if DOTENV_AVAILABLE:
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        else:
            # Try to load .env.example as fallback
            env_example_path = Path(__file__).parent.parent / ".env.example"
            if env_example_path.exists():
                load_dotenv(env_example_path)
    
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Override config with environment variables
        config = _override_with_env_vars(config)
        
        return config
    except FileNotFoundError:
        print(f"Configuration file not found at {config_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing configuration file: {e}")
        return None


def _override_with_env_vars(config):
    """Override configuration values with environment variables."""
    if not config:
        return config
    
    # Override login credentials with environment variables
    if 'snelstart' not in config:
        config['snelstart'] = {}
    
    if 'login' not in config['snelstart']:
        config['snelstart']['login'] = {}
    
    # Load credentials from environment variables
    email = os.getenv('SNELSTART_EMAIL')
    password = os.getenv('SNELSTART_PASSWORD')
    timeout = os.getenv('SNELSTART_TIMEOUT')
    retry_attempts = os.getenv('SNELSTART_RETRY_ATTEMPTS')
    
    if email:
        config['snelstart']['login']['email'] = email
    
    if password:
        config['snelstart']['login']['password'] = password
    
    if timeout:
        try:
            config['snelstart']['login']['timeout'] = int(timeout)
        except ValueError:
            print(f"Warning: Invalid SNELSTART_TIMEOUT value: {timeout}")
    
    if retry_attempts:
        try:
            config['snelstart']['login']['retry_attempts'] = int(retry_attempts)
        except ValueError:
            print(f"Warning: Invalid SNELSTART_RETRY_ATTEMPTS value: {retry_attempts}")
    
    return config


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