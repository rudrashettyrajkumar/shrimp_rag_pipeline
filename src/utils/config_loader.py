"""
Configuration Loader Module
Loads and manages YAML configuration files
"""

import os
import yaml
from typing import Dict, Any
from pathlib import Path


class ConfigLoader:
    """Loads and manages configuration from YAML files"""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the config loader
        
        Args:
            config_dir: Path to configuration directory
        """
        if config_dir is None:
            config_dir = os.path.join(
                os.path.dirname(__file__), '../../config'
            )
        
        self.config_dir = config_dir
        self.configs = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all YAML files from config directory"""
        config_dir_path = Path(self.config_dir)
        
        if not config_dir_path.exists():
            raise ValueError(f"Config directory not found: {self.config_dir}")
        
        yaml_files = list(config_dir_path.glob("*.yaml")) + list(
            config_dir_path.glob("*.yml")
        )
        
        for yaml_file in yaml_files:
            config_name = yaml_file.stem
            self.configs[config_name] = self._load_yaml(str(yaml_file))
    
    @staticmethod
    def _load_yaml(file_path: str) -> Dict[str, Any]:
        """
        Load a YAML file
        
        Args:
            file_path: Path to YAML file
        
        Returns:
            Dictionary containing the YAML content
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
        return content if content else {}
    
    def get_config(self, config_name: str) -> Dict[str, Any]:
        """
        Get configuration by name
        
        Args:
            config_name: Name of the configuration (without .yaml)
        
        Returns:
            Configuration dictionary
        """
        if config_name not in self.configs:
            raise KeyError(f"Configuration '{config_name}' not found")
        return self.configs[config_name]
    
    def get(self, config_name: str, key: str, default: Any = None) -> Any:
        """
        Get a specific key from a configuration
        
        Args:
            config_name: Name of the configuration file
            key: Key to retrieve (supports dot notation: 'section.subsection.key')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        config = self.get_config(config_name)
        keys = key.split('.')
        
        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def get_settings(self) -> Dict[str, Any]:
        """Get the settings configuration"""
        return self.get_config('settings')
    
    def get_prompts(self) -> Dict[str, Any]:
        """Get the prompts configuration"""
        return self.get_config('prompts')


# Global config instance
_config_instance = None


def get_config_loader(config_dir: str = None) -> ConfigLoader:
    """
    Get or create the global config loader instance
    
    Args:
        config_dir: Path to configuration directory
    
    Returns:
        ConfigLoader instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_dir)
    return _config_instance
