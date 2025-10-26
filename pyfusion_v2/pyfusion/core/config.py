"""
Configuration management system
"""
import os
import json
from typing import Any, Dict
from .exceptions import ConfigurationError

class Config:
    """Configuration manager with environment variable support"""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._load_environment()
        self._load_defaults()
    
    def _load_environment(self):
        """Load configuration from environment variables"""
        env_mapping = {
            'PYFUSION_DB_PATH': 'database.path',
            'PYFUSION_DB_TYPE': 'database.type',
            'PYFUSION_SECRET_KEY': 'security.secret_key',
            'PYFUSION_DEBUG': 'debug',
            'PYFUSION_HOST': 'server.host',
            'PYFUSION_PORT': 'server.port',
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested(config_key, self._cast_value(value))
    
    def _load_defaults(self):
        """Load default configuration"""
        defaults = {
            'database': {
                'type': 'sqlite',
                'path': 'pyfusion_db.sqlite',
                'pool_size': 5,
                'timeout': 30
            },
            'server': {
                'host': 'localhost',
                'port': 5000,
                'debug': False
            },
            'security': {
                'secret_key': 'pyfusion-default-secret-key-change-in-production',
                'cors_enabled': True,
                'rate_limit': 100
            },
            'logging': {
                'level': 'INFO',
                'file': 'pyfusion.log',
                'max_size': 10485760  # 10MB
            },
            'cache': {
                'enabled': True,
                'ttl': 3600,
                'type': 'memory'
            }
        }
        
        # Merge defaults with existing config
        for key, value in defaults.items():
            if key not in self._config:
                self._config[key] = value
            elif isinstance(value, dict):
                self._config[key].update(value)
    
    def _set_nested(self, key_path: str, value: Any):
        """Set nested configuration value"""
        keys = key_path.split('.')
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def _cast_value(self, value: str) -> Any:
        """Cast string value to appropriate type"""
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        elif value.isdigit():
            return int(value)
        elif value.replace('.', '').isdigit():
            return float(value)
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        config = self._config
        
        for key in keys:
            if isinstance(config, dict) and key in config:
                config = config[key]
            else:
                return default
        
        return config
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._set_nested(key, value)
    
    def load_from_file(self, file_path: str):
        """Load configuration from JSON file"""
        try:
            with open(file_path, 'r') as f:
                file_config = json.load(f)
                self._config.update(file_config)
        except Exception as e:
            raise ConfigurationError(f"Failed to load config file: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return self._config.copy()