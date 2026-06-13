from pathlib import Path
from typing import Any
import yaml
from dotenv import load_dotenv


class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._env_loaded = False

    def load_yaml(self, filename: str) -> dict[str, Any]:
        path = self.config_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path) as f:
            return yaml.safe_load(f)

    def load_settings(self) -> dict[str, Any]:
        return self.load_yaml("settings.yaml")

    def load_strategies(self) -> dict[str, Any]:
        return self.load_yaml("strategies.yaml")

    def load_env(self, env_file: str = ".env") -> None:
        path = self.config_dir / env_file
        if path.exists():
            load_dotenv(path)
        self._env_loaded = True

    def get_env(self, key: str, default: str | None = None) -> str | None:
        import os
        if not self._env_loaded:
            self.load_env()
        return os.getenv(key, default)
