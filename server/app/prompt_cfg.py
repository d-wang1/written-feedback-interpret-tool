import os
from pathlib import Path
import yaml

DEFAULT_PROMPT_FILE = Path(__file__).parent / "prompts.yaml"
print("Default prompt file path:", DEFAULT_PROMPT_FILE)
DEFAULT_PROFILE = "default"


class PromptStore:
    def __init__(self):
        self._cache = None
        self._cache_mtime = None

    def load(self):
        # Allow override by env var
        prompt_path = Path(os.getenv("PROMPT_FILE", str(DEFAULT_PROMPT_FILE)))
        profile = os.getenv("PROMPT_PROFILE", DEFAULT_PROFILE)

        if not prompt_path.exists():
            raise RuntimeError(
                f"Prompt file not found: {prompt_path}\n"
                f"Contents of directory: {list(prompt_path.parent.glob('*'))}"
            )
        # Hot-reload when file changes (nice for dev)
        mtime = prompt_path.stat().st_mtime
        if self._cache is None or self._cache_mtime != mtime:
            with prompt_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            self._cache = data
            self._cache_mtime = mtime

        if profile not in self._cache:
            raise RuntimeError(
                f"Prompt profile '{profile}' not found in {prompt_path}. "
                f"Available: {', '.join(self._cache.keys())}"
            )

        return self._cache[profile]


prompt_store = PromptStore()


def build_system_prompt(profile_cfg: dict) -> str:
    return (profile_cfg.get("system") or "").strip()


def build_user_prompt(text: str, options: dict, profile_cfg: dict) -> str:
    instr_cfg = profile_cfg.get("instructions") or {}

    parts = []
    base = (instr_cfg.get("base") or "").strip()
    if base:
        parts.append(base)

    # Add goals only if selected
    if options.get("simplify"):
        parts.append((instr_cfg.get("simplify") or "").strip())
    if options.get("soften"):
        parts.append((instr_cfg.get("soften") or "").strip())
    if options.get("caseSupport"):
        parts.append((instr_cfg.get("caseSupport") or "").strip())

    # If no options selected, still do something deterministic
    if len(parts) == 0 or (len(parts) == 1 and parts[0] == base):
        parts.append("If no goals are selected, return the feedback unchanged.")

    instruction_block = "\n\n".join([p for p in parts if p])

    # If caseSupport, tell it the bullet character we want (configurable)
    fmt = profile_cfg.get("format") or {}
    bullet_prefix = (fmt.get("bullet_prefix") or "• ").strip()

    if options.get("caseSupport"):
        instruction_block += f"\n\nUse '{bullet_prefix}' to start each bullet."

    return f"{instruction_block}\n\nFEEDBACK:\n{text}".strip()
