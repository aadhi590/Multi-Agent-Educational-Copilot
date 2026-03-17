"""
Mastery Tracking using ELO-inspired algorithm + BKT-style parameters.

ELO logic:
- Student starts at score = 0.3 (30% mastery per topic)
- Correct evaluations push score toward 1.0
- Incorrect evaluations pull score toward 0.0
- K-factor controls update speed

BKT parameters (Bayesian Knowledge Tracing):
- pL: probability of knowing (= mastery_score)
- pT: probability of learning on each attempt (= 0.1)
- pG: probability of guessing correctly (= 0.25)
- pS: probability of slipping (= 0.1)
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
        # P(obs | know) = 1 - pS; P(obs | ~know) = pG
        p_obs_given_know = 1 - pS
        p_obs_given_not_know = pG
    else:
        # P(obs | know) = pS; P(obs | ~know) = 1 - pG
        p_obs_given_know = pS
        p_obs_given_not_know = 1 - pG

    # Bayes update
    numerator = p_obs_given_know * pL
    denominator = numerator + p_obs_given_not_know * (1 - pL)
    pL_given_obs = numerator / denominator if denominator > 0 else pL

    # Apply learning (transition probability)
    pL_new = pL_given_obs + (1 - pL_given_obs) * pT

    return float(int(min(1.0, pL_new) * 10000 + 0.5) / 10000.0)


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

    updated = {
        "score": blended,
        "elo_score": new_elo,
        "bkt_score": new_bkt,
        "attempts": attempts + 1,
        "last_correctness": correctness_score,
        "status": status,
        "last_updated": datetime.now().isoformat(),
        "learning_objectives_met": objectives_met,
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
