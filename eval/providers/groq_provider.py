from __future__ import annotations

import os
from groq import Groq

from .base import Provider, GenParams


class GroqProvider(Provider):
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set in environment.")
        self.client = Groq(api_key=api_key)

    def generate(self, *, model: str, prompt: str, params: GenParams) -> str:
        resp = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Return only the answer text."},
                {"role": "user", "content": prompt},
            ],
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            top_p=params.top_p,
        )
        return (resp.choices[0].message.content or "").strip()