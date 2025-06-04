"""
Configuration Manager
Handles app settings and user preferences
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.default_config_path = self.config_dir / "settings.json"
        self.user_config_path = self.config_dir / "user_settings.json"
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from files"""
        # Load default config
        default_config = {}
        if self.default_config_path.exists():
            try:
                with open(self.default_config_path, 'r') as f:
                    default_config = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load default config: {e}")
        
        # Load user config
        user_config = {}
        if self.user_config_path.exists():
            try:
                with open(self.user_config_path, 'r') as f:
                    user_config = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load user config: {e}")
        
        # Merge configs (user overrides default)
        config = default_config.copy()
        config.update(user_config)
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save to user config
        self._save_user_config()
    
    def _save_user_config(self):
        """Save user configuration to file"""
        try:
            with open(self.user_config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("User configuration saved")
        except Exception as e:
            logger.error(f"Failed to save user config: {e}")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        if self.user_config_path.exists():
            os.remove(self.user_config_path)
        self.config = self._load_config()
        logger.info("Configuration reset to defaults")