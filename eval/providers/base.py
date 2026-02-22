from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class GenParams:
    temperature: float = 0.2
    max_tokens: int = 512
    top_p: float | None = None


class Provider:
    """Model provider interface (Groq, Gemini, OpenAI, etc.)."""

    def generate(self, *, model: str, prompt: str, params: GenParams) -> str:
        raise NotImplementedError