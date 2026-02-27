"""
Lexical + weighted sentiment analysis.
Computes frustration_level (0-1), sentiment label, and engagement_score (0-1).
No external ML library needed — pure Python, fast.
"""

import re
from typing import Dict, Tuple

# ---------------------------------------------------------------------------
# Lexicons — (pattern, frustration_weight, engagement_delta)
# ---------------------------------------------------------------------------

FRUSTRATION_LEXICON: Dict[str, float] = {
    "i give up": 0.95,
    "i quit": 0.90,
    "i hate this": 0.88,
    "this is useless": 0.85,
    "can't do this": 0.80,
    "i can't": 0.75,
    "i cant": 0.75,
    "frustrated": 0.80,
    "frustrating": 0.75,
    "i'm lost": 0.70,
    "im lost": 0.70,
    "so confused": 0.70,
    "don't understand": 0.65,
    "dont understand": 0.65,
    "i don't get it": 0.65,
    "i dont get it": 0.65,
    "stuck": 0.55,
    "confused": 0.50,
    "hard": 0.25,
    "difficult": 0.25,
    "struggling": 0.45,
    "help me": 0.30,
    "this is hard": 0.40,
    "makes no sense": 0.60,
    "boring": 0.40,
    "pointless": 0.55,
    "waste of time": 0.70,
    "terrible": 0.70,
    "awful": 0.70,
    "angry": 0.75,
}

POSITIVE_LEXICON: Dict[str, float] = {
    "got it": 0.40,
    "i understand": 0.50,
    "makes sense": 0.45,
    "that helps": 0.40,
    "thank you": 0.35,
    "thanks": 0.25,
    "great": 0.30,
    "excellent": 0.40,
    "perfect": 0.40,
    "clear": 0.30,
    "love this": 0.45,
    "i learned": 0.50,
    "i know": 0.30,
    "easy": 0.30,
    "awesome": 0.40,
    "nice": 0.25,
    "cool": 0.20,
    "fascinating": 0.45,
}

# Confusion signals (moderate frustration, low engagement)
CONFUSION_LEXICON: Dict[str, float] = {
    "what does": 0.15,
    "what is": 0.10,
    "how does": 0.10,
    "i'm not sure": 0.20,
    "im not sure": 0.20,
    "not sure": 0.15,
    "what do you mean": 0.25,
    "can you explain": 0.10,
    "i think": 0.05,
    "maybe": 0.05,
}


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def analyze_sentiment(text: str) -> Tuple[float, str, float]:
    """
    Returns: (frustration_level: float, sentiment: str, engagement_score: float)
    - frustration_level: 0.0 (calm) → 1.0 (very frustrated)
    - sentiment: 'positive' | 'neutral' | 'confused' | 'negative'
    - engagement_score: 0.0 (disengaged) → 1.0 (highly engaged)
    """
    normalized = _normalize(text)

    frustration_score = 0.0
    positive_score = 0.0
    confusion_score = 0.0

    # Score frustration phrases
    for phrase, weight in FRUSTRATION_LEXICON.items():
        if phrase in normalized:
            frustration_score = max(frustration_score, weight)

    # Score positive phrases
    for phrase, weight in POSITIVE_LEXICON.items():
        if phrase in normalized:
            positive_score = max(positive_score, weight)

    # Score confusion phrases
    for phrase, weight in CONFUSION_LEXICON.items():
        if phrase in normalized:
            confusion_score = max(confusion_score, weight)

    # Compute net frustration (positive phrases reduce frustration)
    net_frustration = max(0.0, min(1.0, frustration_score - positive_score * 0.5))

    # Compute engagement: high message length + positive signals = engaged
    word_count = len(text.split())
    length_boost = min(0.3, word_count / 100)  # longer messages = more engaged
    engagement = max(0.0, min(1.0, (positive_score * 0.6) + length_boost + 0.4 - (net_frustration * 0.4)))

    # Determine label
    if net_frustration >= 0.6:
        sentiment = "negative"
    elif net_frustration >= 0.3 or confusion_score >= 0.2:
        sentiment = "confused"
    elif positive_score >= 0.25:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    return (
        float(int(net_frustration * 1000 + 0.5) / 1000.0),
        sentiment,
        float(int(engagement * 1000 + 0.5) / 1000.0)
    )


def update_frustration_with_decay(
    current_level: float, new_signal: float, decay: float = 0.15
) -> float:
    """
    Blends current frustration with new signal using exponential decay.
    Called after every message so frustration slowly resolves after coaching.
    decay: how quickly old frustration fades when new signal is lower.
    """
    if new_signal < current_level:
        # Coach calmed them down — decay toward new signal
        return float(int(max(0.0, current_level - decay) * 1000 + 0.5) / 1000.0)
    else:
        # Frustration is rising — update immediately
        return float(int(min(1.0, (current_level * 0.4) + (new_signal * 0.6)) * 1000 + 0.5) / 1000.0)
