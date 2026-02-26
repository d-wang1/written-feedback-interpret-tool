from __future__ import annotations

from typing import Dict
import math
import re

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .shared import length_ratio


_POLITE_MARKERS = [
    "please",
    "could you",
    "would you",
    "consider",
    "i suggest",
    "it might help",
    "i recommend",
    "thanks",
    "thank you",
    "appreciate",
]
_PROFANITY = [
    "stupid",
    "idiot",
    "dumb",
    "ridiculous",
    "unacceptable",
    "lazy",
    "sloppy",
]

_analyzer = SentimentIntensityAnalyzer()


def _count_markers(text: str, markers: list[str]) -> int:
    t = (text or "").lower()
    return sum(1 for m in markers if m in t)


def _count_words_from_list(text: str, words: list[str]) -> int:
    t = (text or "").lower()
    return sum(len(re.findall(rf"\b{re.escape(w)}\b", t)) for w in words)


def toxicity_score(text: str) -> float:
    """
    Optional: returns toxicity in [0,1]. If Detoxify isn't installed, returns NaN.
    """
    try:
        from detoxify import Detoxify  # type: ignore
    except Exception:
        return float("nan")

    # instantiate lazily (Detoxify loads a model)
    if not hasattr(toxicity_score, "_model"):
        toxicity_score._model = Detoxify("original")  # type: ignore[attr-defined]

    preds = toxicity_score._model.predict(text or "")  # type: ignore[attr-defined]
    # 'toxicity' key exists for Detoxify("original")
    return float(preds.get("toxicity", float("nan")))


def soften_metrics(inp: str, out: str) -> Dict[str, float]:
    lr = length_ratio(inp, out)

    in_sent = _analyzer.polarity_scores(inp or "")
    out_sent = _analyzer.polarity_scores(out or "")

    in_tox = toxicity_score(inp)
    out_tox = toxicity_score(out)

    polite_in = _count_markers(inp, _POLITE_MARKERS)
    polite_out = _count_markers(out, _POLITE_MARKERS)

    prof_in = _count_words_from_list(inp, _PROFANITY)
    prof_out = _count_words_from_list(out, _PROFANITY)

    return {
        "length_ratio": lr,
        "in_vader_compound": float(in_sent["compound"]),
        "out_vader_compound": float(out_sent["compound"]),
        "vader_compound_gain": float(out_sent["compound"] - in_sent["compound"]),  # higher = less negative
        "in_toxicity": float(in_tox),
        "out_toxicity": float(out_tox),
        "toxicity_drop": float(in_tox - out_tox) if (not math.isnan(in_tox) and not math.isnan(out_tox)) else float("nan"),
        "polite_markers_in": float(polite_in),
        "polite_markers_out": float(polite_out),
        "polite_marker_gain": float(polite_out - polite_in),
        "profanity_in": float(prof_in),
        "profanity_out": float(prof_out),
        "profanity_drop": float(prof_in - prof_out),
    }


def soften_composite(m: Dict[str, float]) -> float:
    """
    Simple composite: reward toxicity drop + sentiment improvement + polite markers.
    Penalize large length changes slightly.
    """
    tox_drop = m.get("toxicity_drop", 0.0)
    sent_gain = m.get("vader_compound_gain", 0.0)
    polite_gain = m.get("polite_marker_gain", 0.0)
    prof_drop = m.get("profanity_drop", 0.0)
    lr = m.get("length_ratio", 1.0)

    penalty = 0.0
    if lr < 0.6:
        penalty += (0.6 - lr) * 4.0
    if lr > 1.5:
        penalty += (lr - 1.5) * 2.0

    score = (2.0 * tox_drop) + (1.2 * sent_gain) + (0.2 * polite_gain) + (0.3 * prof_drop) - penalty
    return float(score)