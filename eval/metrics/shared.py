from __future__ import annotations

import re
from typing import Dict, Any

import numpy as np
from bert_score import score as bert_score


_WORD_RE = re.compile(r"[A-Za-z']+")


def safe_len(s: str) -> int:
    return len(s or "")


def word_stats(text: str) -> Dict[str, float]:
    words = _WORD_RE.findall(text or "")
    if not words:
        return {"num_words": 0, "avg_word_len": float("nan")}
    lens = [len(w) for w in words]
    return {"num_words": float(len(words)), "avg_word_len": float(np.mean(lens))}


def length_ratio(inp: str, out: str) -> float:
    li = max(1, len(inp))
    return len(out) / li


def bertscore_f1(inp: str, out: str, *, lang: str = "en") -> float:
    """
    Reference-free semantic preservation proxy:
    compare output to input. Higher ~= better meaning preservation.
    """
    # bert_score expects lists
    P, R, F1 = bert_score([out], [inp], lang=lang, verbose=False)
    return float(F1[0].item())