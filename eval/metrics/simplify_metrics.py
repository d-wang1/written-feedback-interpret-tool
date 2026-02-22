from __future__ import annotations

from typing import Dict
import math

import textstat

from .shared import word_stats, length_ratio


def readability(inp: str, out: str) -> Dict[str, float]:
    in_ease = float(textstat.flesch_reading_ease(inp))
    out_ease = float(textstat.flesch_reading_ease(out))
    in_grade = float(textstat.flesch_kincaid_grade(inp))
    out_grade = float(textstat.flesch_kincaid_grade(out))

    return {
        "in_flesch_ease": in_ease,
        "out_flesch_ease": out_ease,
        "ease_gain": out_ease - in_ease,          # higher is better
        "in_fk_grade": in_grade,
        "out_fk_grade": out_grade,
        "grade_drop": in_grade - out_grade,       # higher is better
    }


def simplify_metrics(inp: str, out: str) -> Dict[str, float]:
    ws_in = word_stats(inp)
    ws_out = word_stats(out)

    lr = length_ratio(inp, out)

    m = {
        **{f"in_{k}": v for k, v in ws_in.items()},
        **{f"out_{k}": v for k, v in ws_out.items()},
        "avg_word_len_drop": (ws_in["avg_word_len"] - ws_out["avg_word_len"])
        if (not math.isnan(ws_in["avg_word_len"]) and not math.isnan(ws_out["avg_word_len"]))
        else float("nan"),
        "length_ratio": lr,
    }
    m.update(readability(inp, out))
    return m


def simplify_composite(m: Dict[str, float]) -> float:
    """
    Lightweight composite for leaderboard comparisons.
    Guardrails handled elsewhere (e.g., semantic similarity threshold).
    """
    ease_gain = m.get("ease_gain", 0.0)
    grade_drop = m.get("grade_drop", 0.0)
    word_len_drop = m.get("avg_word_len_drop", 0.0)
    lr = m.get("length_ratio", 1.0)

    # penalize if output is wildly shorter/longer
    penalty = 0.0
    if lr < 0.55:
        penalty += (0.55 - lr) * 10.0
    if lr > 1.35:
        penalty += (lr - 1.35) * 5.0

    # small weights; readability is the core
    score = (0.08 * ease_gain) + (0.6 * grade_drop) + (0.4 * word_len_drop) - penalty
    return float(score)