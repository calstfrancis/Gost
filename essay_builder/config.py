"""
config.py — Settings persistence for Gost.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("gost")


class Config:

    DEFAULT_CONFIG = {
        "citation_style": "SBL",
        "engine": "xelatex",
        "font_size": "11pt",
        "paper": "letterpaper",
        "window_width": 960,
        "window_height": 720,
    }
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "gost"
        self.config_file = self.config_dir / "config.json"
        self._config: Dict[str, Any] = {}
        self._load()
    
    def _load(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
            else:
                self._config = self.DEFAULT_CONFIG.copy()
                self._save()
                logger.info("Created default configuration")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._config = self.DEFAULT_CONFIG.copy()
    
    def _save(self) -> None:
        """Save configuration to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.debug(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save."""
        self._config[key] = value
        self._save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()
    
    def set_window_size(self, width: int, height: int) -> None:
        """Save window size."""
        self.set("window_width", width)
        self.set("window_height", height)
    
    def get_window_size(self) -> tuple[int, int]:
        """Get saved window size."""
        return (
            self.get("window_width", 960),
            self.get("window_height", 720)
        )

    # ------------------------------------------------------------------
    # Profiles
    # ------------------------------------------------------------------

    @property
    def _profiles_file(self) -> Path:
        return self.config_dir / "profiles.json"

    def get_profiles(self) -> Dict[str, Any]:
        if not self._profiles_file.exists():
            return {}
        try:
            with open(self._profiles_file) as f:
                return json.load(f)
        except Exception:
            return {}

    def save_profile(self, name: str, state: Dict[str, Any]) -> None:
        profiles = self.get_profiles()
        profiles[name] = state
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self._profiles_file, "w") as f:
                json.dump(profiles, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save profile '{name}': {e}")

    def delete_profile(self, name: str) -> None:
        profiles = self.get_profiles()
        profiles.pop(name, None)
        try:
            with open(self._profiles_file, "w") as f:
                json.dump(profiles, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to delete profile '{name}': {e}")
