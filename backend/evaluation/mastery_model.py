"""
Mastery Model — Enhanced ELO + BKT scoring system.

Provides mastery tracking using a blended ELO-inspired and Bayesian Knowledge
Tracing algorithm, with additional analytics for learning velocity and
misconception detection.
"""

from datetime import datetime
from typing import Dict, Any, Tuple, List


# ---------------------------------------------------------------------------
# ELO-Inspired Update
# ---------------------------------------------------------------------------

def elo_update(current_score: float, passed: bool, k: float = 0.12) -> float:
    """
    ELO-inspired mastery score update.
    - k: learning rate (higher = faster updates)
    - passed=True  → score += k * (1 - score)   [diminishing returns near 1]
    - passed=False → score -= k * score           [diminishing loss near 0]
    """
    if passed:
        new_score = current_score + k * (1.0 - current_score)
    else:
        new_score = current_score - k * current_score

    return float(int(max(0.0, min(1.0, new_score)) * 10000 + 0.5) / 10000.0)


# ---------------------------------------------------------------------------
# Bayesian Knowledge Tracing Update
# ---------------------------------------------------------------------------

def bkt_update(pL: float, correct: bool) -> float:
    """
    One-step BKT update: P(know | observation) → new pL.
    pL: current mastery probability
    correct: did the student get it right?
    """
    pT = 0.10   # learning rate per attempt
    pG = 0.25   # guess probability
    pS = 0.10   # slip probability

    if correct:
        p_obs_given_know = 1 - pS
        p_obs_given_not_know = pG
    else:
        p_obs_given_know = pS
        p_obs_given_not_know = 1 - pG

    # Bayes update
    numerator = p_obs_given_know * pL
    denominator = numerator + p_obs_given_not_know * (1 - pL)
    pL_given_obs = numerator / denominator if denominator > 0 else pL

    # Apply learning transition
    pL_new = pL_given_obs + (1 - pL_given_obs) * pT

    return float(int(min(1.0, pL_new) * 10000 + 0.5) / 10000.0)


# ---------------------------------------------------------------------------
# Misconception Detection
# ---------------------------------------------------------------------------

def detect_misconceptions(
    evaluation_history: List[Dict[str, Any]],
    topic: str,
) -> List[str]:
    """
    Detect recurring misconceptions from evaluation history.
    
    Returns list of identified misconception patterns.
    """
    misconceptions = []
    
    if not evaluation_history:
        return misconceptions
    
    # Count consecutive failures
    consecutive_fails = 0
    for eval_result in reversed(evaluation_history):
        if eval_result.get("topic") == topic and not eval_result.get("passed", True):
            consecutive_fails += 1
        else:
            break
    
    if consecutive_fails >= 3:
        misconceptions.append(
            f"Persistent difficulty with {topic} ({consecutive_fails} consecutive incorrect answers)"
        )
    
    # Check for low scores on specific sub-topics
    low_score_topics = {}
    for eval_result in evaluation_history:
        t = eval_result.get("topic", "")
        score = eval_result.get("score", 5)
        if score < 4:
            low_score_topics[t] = low_score_topics.get(t, 0) + 1
    
    for t, count in low_score_topics.items():
        if count >= 2:
            misconceptions.append(f"Recurring errors in {t} ({count} low-scoring attempts)")
    
    return misconceptions


# ---------------------------------------------------------------------------
# Learning Velocity
# ---------------------------------------------------------------------------

def compute_learning_velocity(
    mastery_history: List[Dict[str, Any]],
) -> float:
    """
    Compute learning velocity (rate of mastery improvement over recent attempts).
    
    Returns a float between -1 and 1:
    - Positive = improving
    - Negative = declining
    - Near 0 = plateau
    """
    if len(mastery_history) < 2:
        return 0.0
    
    # Take last 5 entries
    recent = mastery_history[-5:]
    scores = [entry.get("score", 0.0) for entry in recent]
    
    if len(scores) < 2:
        return 0.0
    
    # Simple linear regression slope
    n = len(scores)
    x_mean = (n - 1) / 2.0
    y_mean = sum(scores) / n
    
    numerator = sum((i - x_mean) * (s - y_mean) for i, s in enumerate(scores))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    
    slope = numerator / denominator if denominator > 0 else 0.0
    
    # Normalize to [-1, 1]
    return max(-1.0, min(1.0, slope * 5))


# ---------------------------------------------------------------------------
# Combined Update (blend ELO + BKT)
# ---------------------------------------------------------------------------

def update_mastery(
    current_mastery: Dict[str, Any],
    topic: str,
    correctness_score: int,          # 0–10 from evaluator
    all_topics_mastery: Dict[str, Any],
) -> Tuple[Dict[str, Any], float]:
    """
    Updates the mastery data for a specific topic.
    Returns the updated mastery dict for that topic and the global score.
    """
    passed = correctness_score >= 6  # 6/10 threshold for passing

    # Get existing values
    existing = current_mastery if isinstance(current_mastery, dict) else {}
    old_elo = float(existing.get("score", 0.3))
    old_bkt = float(existing.get("bkt_score", 0.3))
    attempts = int(existing.get("attempts", 0))
    objectives_met = existing.get("learning_objectives_met", [])
    history = existing.get("score_history", [])

    # Run both algorithms
    new_elo = elo_update(old_elo, passed)
    new_bkt = bkt_update(old_bkt, passed)

    # Blend: 60% ELO + 40% BKT
    blended_val = 0.6 * new_elo + 0.4 * new_bkt
    blended = float(int(blended_val * 10000 + 0.5) / 10000.0)

    # Determine status
    if blended >= 0.80:
        status = "mastered"
    elif blended > 0.3:
        status = "in_progress"
    else:
        status = "not_started"

    # Track history for velocity calculation
    history_entry = {
        "score": blended,
        "correctness": correctness_score,
        "timestamp": datetime.now().isoformat(),
    }
    
    # Cast history to List[Any] to help type checker with slicing
    current_history: List[Any] = list(history)
    current_history.append(history_entry)
    
    # Negative slicing is a standard Python feature, but if the type checker fails,
    # we can be more explicit about it.
    history_len = len(current_history)
    start_idx = max(0, history_len - 20)
    history = current_history[start_idx:history_len]

    # Compute learning velocity
    velocity = compute_learning_velocity(history)

    updated = {
        "score": blended,
        "elo_score": new_elo,
        "bkt_score": new_bkt,
        "attempts": attempts + 1,
        "last_correctness": correctness_score,
        "status": status,
        "last_updated": datetime.now().isoformat(),
        "learning_objectives_met": objectives_met,
        "score_history": history,
        "learning_velocity": velocity,
        "passed": passed,
    }

    # Compute global mastery: average of all topic scores
    all_updated = {**all_topics_mastery, topic: updated}
    all_scores = [
        float(v.get("score", 0.0)) if isinstance(v, dict) else 0.0
        for v in all_updated.values()
    ]
    global_score = float(int((sum(all_scores) / max(len(all_scores), 1)) * 10000 + 0.5) / 10000.0)

    return updated, global_score


def get_mastery_label(score: float) -> str:
    if score >= 0.80:
        return "Mastered 🏆"
    elif score >= 0.60:
        return "Proficient ✅"
    elif score >= 0.40:
        return "Learning 📚"
    elif score >= 0.20:
        return "Beginner 🌱"
    else:
        return "Not Started"
