from __future__ import annotations

import re
from typing import Any

_HEDGE_PATTERN = re.compile(
    r"\b(?:perhaps|maybe|might|could|seems?|appears?|likely|somewhat|relatively|"
    r"it is important to note that|kindly|as discussed)\b",
    re.IGNORECASE,
)
_CONTRACTION_PATTERN = re.compile(
    r"\b(?:don't|won't|can't|isn't|aren't|wasn't|weren't|hasn't|haven't|hadn't|"
    r"wouldn't|shouldn't|couldn't|mustn't|it's|that's|there's|we're|you're|I'm|"
    r"they're|we've|you've|I've|they've|we'll|you'll|I'll|they'll)\b",
    re.IGNORECASE,
)
_YOU_PATTERN = re.compile(r"\byou\b", re.IGNORECASE)
_WE_PATTERN = re.compile(r"\bwe\b", re.IGNORECASE)
_I_PATTERN = re.compile(r"\bI\b")


def _rate(count: int, words: int) -> float:
    if words == 0:
        return 0.0
    return count / words


def suggest_register_text(text: str) -> dict[str, Any]:
    words = len(text.split())
    you_count = len(_YOU_PATTERN.findall(text))
    we_count = len(_WE_PATTERN.findall(text))
    i_count = len(_I_PATTERN.findall(text))
    hedge_count = len(_HEDGE_PATTERN.findall(text))
    contraction_count = len(_CONTRACTION_PATTERN.findall(text))

    you_rate = _rate(you_count, words)
    we_rate = _rate(we_count, words)
    i_rate = _rate(i_count, words)
    hedge_rate = _rate(hedge_count, words)
    contraction_rate = _rate(contraction_count, words)

    # Voice
    if you_rate >= 0.02 and you_rate >= max(we_rate, i_rate):
        voice = "you"
        voice_confidence = min(0.95, 0.6 + you_rate * 10)
    elif we_rate >= 0.02 and we_rate > i_rate:
        voice = "keep"
        voice_confidence = 0.75
    else:
        voice = "active"
        voice_confidence = 0.65 if you_rate < 0.005 and we_rate < 0.005 else 0.55

    # Tone
    if hedge_rate >= 0.03:
        tone = "plain"
        tone_confidence = 0.6
    elif hedge_rate <= 0.008 and contraction_rate < 0.01:
        tone = "firm"
        tone_confidence = min(0.9, 0.7 + (0.01 - hedge_rate) * 20)
    elif contraction_rate >= 0.015:
        tone = "warm"
        tone_confidence = min(0.9, 0.65 + contraction_rate * 8)
    else:
        tone = "plain"
        tone_confidence = 0.7

    confidence = round(min(voice_confidence, tone_confidence), 2)

    return {
        "voice": voice,
        "tone": tone,
        "confidence": confidence,
        "signals": {
            "you_rate": round(you_rate, 4),
            "we_rate": round(we_rate, 4),
            "i_rate": round(i_rate, 4),
            "hedge_rate": round(hedge_rate, 4),
            "contraction_rate": round(contraction_rate, 4),
            "word_count": words,
        },
    }
