from __future__ import annotations

from .base import Provider
from .groq_provider import GroqProvider


def get_provider(name: str) -> Provider:
    name = name.lower().strip()
    if name == "groq":
        return GroqProvider()
    raise ValueError(f"Unknown provider: {name}")