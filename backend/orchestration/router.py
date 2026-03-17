"""
Hybrid Router — Combines rule-based, sentiment-based, and LLM reasoning.

The routing decision pipeline:
1. Rule-based override: High frustration → Coach (always)
2. Sentiment detection: Negative sentiment patterns → Coach
3. LLM reasoning: Meta-agent's intent classification → appropriate agent
"""

from typing import Literal


AgentRoute = Literal["tutor", "planner", "evaluator", "coach"]


def hybrid_route(state: dict) -> AgentRoute:
    """
    Determine which agent should handle the current message.
    
    Priority order:
    1. Frustration override (rule-based)
    2. Sentiment-based routing (rule-based)
    3. Meta-agent's LLM-based decision
    4. Default fallback
    
    Args:
        state: Current AgentState dict
    
    Returns:
        Agent name to route to.
    """
    frustration = state.get("frustration_level", 0.0)
    sentiment = state.get("sentiment", "neutral")
    next_agent = state.get("next_agent", "tutor")
    
    # ── Rule 1: Frustration Override ──
    # High frustration ALWAYS routes to coach regardless of other signals
    if frustration > 0.65:
        return "coach"
    
    # ── Rule 2: Moderate frustration with negative sentiment ──
    if frustration > 0.4 and sentiment in ("negative", "confused"):
        return "coach"
    
    # ── Rule 3: Active intervention from previous turn ──
    if state.get("active_intervention", False) and frustration > 0.3:
        return "coach"
    
    # ── Rule 4: Validate LLM-chosen agent ──
    valid_agents = ("tutor", "planner", "evaluator", "coach")
    if next_agent in valid_agents:
        return next_agent  # type: ignore
    
    # ── Fallback ──
    return "tutor"


def get_routing_explanation(state: dict) -> str:
    """Generate a human-readable explanation of the routing decision."""
    frustration = state.get("frustration_level", 0.0)
    sentiment = state.get("sentiment", "neutral")
    next_agent = state.get("next_agent", "tutor")
    
    if frustration > 0.65:
        return f"Frustration ({frustration:.0%}) exceeded critical threshold → Coach"
    if frustration > 0.4 and sentiment in ("negative", "confused"):
        return f"Moderate frustration ({frustration:.0%}) + {sentiment} sentiment → Coach"
    if state.get("active_intervention", False) and frustration > 0.3:
        return f"Active coaching intervention with frustration ({frustration:.0%}) → Coach"
    
    return f"LLM intent analysis → {next_agent} (sentiment: {sentiment})"
