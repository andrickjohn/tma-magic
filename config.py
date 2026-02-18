# TMA Magic Black Box — Configuration Management
"""
Platform-aware configuration management.
Stores config in user-writable locations (not app directory).
"""

import json
import os
import platform
from pathlib import Path
from typing import Optional, Dict, Any


def get_config_dir() -> Path:
    """Get platform-appropriate config directory."""
    system = platform.system()
    
    if system == "Windows":
        # Use %APPDATA%\TMA Magic
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        config_dir = base / "TMA Magic"
    elif system == "Darwin":  # macOS
        config_dir = Path.home() / ".tma_magic"
    else:  # Linux and others
        config_dir = Path.home() / ".config" / "tma_magic"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_temp_dir() -> Path:
    """Get temp directory for job files."""
    import tempfile
    temp_dir = Path(tempfile.gettempdir()) / "tma_magic"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


class Config:
    """Application configuration."""
    
    _instance: Optional["Config"] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    @property
    def config_file(self) -> Path:
        return get_config_dir() / "config.json"
    
    def _load(self):
        """Load config from disk or Streamlit secrets."""
        # 1. Start with defaults
        self._config = self._defaults()
        
        # 2. Try loading from file
        if self.config_file.exists():
            try:
                local_config = json.loads(self.config_file.read_text())
                self._config.update(local_config)
            except json.JSONDecodeError:
                pass
        
        # 3. OVERRIDE with Streamlit Secrets if available (Cloud Deployment)
        try:
            import streamlit as st
            if "general" in st.secrets:
                if "openai_api_key" in st.secrets["general"]:
                    self._config["openai_api_key"] = st.secrets["general"]["openai_api_key"]
        except:
            # Fallback if st.secrets is not available (local run)
            pass
    
    def _defaults(self) -> Dict[str, Any]:
        """Default configuration values."""
        return {
            "openai_api_key": "",
            "extraction_mode": "hybrid",  # regex_only, ai_only, hybrid
            "confidence_threshold": 85,
            "theme": "dark",
            "last_directory": str(Path.home()),
        }
    
    def _save(self):
        """Save config to disk."""
        self.config_file.write_text(json.dumps(self._config, indent=2))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a config value and save."""
        self._config[key] = value
        self._save()
    
    @property
    def openai_api_key(self) -> str:
        return self.get("openai_api_key", "")
    
    @openai_api_key.setter
    def openai_api_key(self, value: str):
        self.set("openai_api_key", value)
    
    @property
    def has_api_key(self) -> bool:
        return bool(self.openai_api_key)
    
    @property
    def confidence_threshold(self) -> int:
        return self.get("confidence_threshold", 85)
    
    @property
    def extraction_mode(self) -> str:
        return self.get("extraction_mode", "hybrid")


# Convenience functions
def get_config() -> Config:
    """Get the singleton config instance."""
    return Config()
