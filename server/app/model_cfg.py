import os
from pathlib import Path
import yaml

DEFAULT_MODEL_FILE = Path(__file__).parent / "model_config.yaml"
DEFAULT_PROFILE = "default"


class ModelConfigStore:
    def __init__(self):
        self._cache = None
        self._cache_mtime = None

    def load(self):
        path = Path(os.getenv("MODEL_CONFIG_FILE", str(DEFAULT_MODEL_FILE)))
        profile = os.getenv("MODEL_PROFILE", DEFAULT_PROFILE)

        if not path.exists():
            raise RuntimeError(f"Model config file not found: {path}")

        mtime = path.stat().st_mtime
        if self._cache is None or self._cache_mtime != mtime:
            with path.open("r", encoding="utf-8") as f:
                self._cache = yaml.safe_load(f) or {}
            self._cache_mtime = mtime

        if profile not in self._cache:
            raise RuntimeError(
                f"Model profile '{profile}' not found. "
                f"Available: {', '.join(self._cache.keys())}"
            )

        return self._cache[profile]


model_config_store = ModelConfigStore()
