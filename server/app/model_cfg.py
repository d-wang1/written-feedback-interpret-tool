import os
from pathlib import Path
import yaml

DEFAULT_MODEL_FILE = Path(__file__).parent / "model_config.yaml"


class ModelConfigStore:
    def __init__(self):
        self._cache = None
        self._cache_mtime = None

    def load(self):
        path = Path(os.getenv("MODEL_CONFIG_FILE", str(DEFAULT_MODEL_FILE)))

        if not path.exists():
            raise RuntimeError(f"Model config file not found: {path}")

        mtime = path.stat().st_mtime
        if self._cache is None or self._cache_mtime != mtime:
            with path.open("r", encoding="utf-8") as f:
                self._cache = yaml.safe_load(f) or {}
            self._cache_mtime = mtime

        return self._cache


model_config_store = ModelConfigStore()
