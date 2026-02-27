"""
LangGraph Orchestrator — Production Architecture

Flow per student turn:
  START
    ↓
  [meta_agent_node]     ← Updates: sentiment, frustration, topic, next_agent
    ↓ (routes by state["next_agent"])
  [tutor | planner | evaluator | coach]   ← Each writes state updates back
    ↓
  END

This makes the system truly agentic:
- MetaAgent uses an LLM to decide routing (not keywords)
- All agents update shared state
- Mastery tracking updates on every evaluation
- Frustration decays after coaching
"""

from datetime import datetime
from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END

from state import AgentState
from agents.meta_agent import meta_agent
from agents.tutor import tutor_agent
from agents.planner import planner_agent
from agents.evaluator import evaluator_agent
from agents.coach import coach_agent
from ml.mastery import update_mastery


# ---------------------------------------------------------------------------
# Node 0: Meta-Agent (runs FIRST on every turn)
# ---------------------------------------------------------------------------

def meta_agent_node(state: AgentState) -> dict:
    """
    The brain of the system. Analyzes the message using ML + LLM,
    then writes routing decision and emotional state to shared state.
    """
    state_updates = meta_agent.analyze(state)
    print(f"[MetaAgent] → next: {state_updates.get('next_agent')} | "
          f"frustration: {state_updates.get('frustration_level', 0):.2f} | "
          f"sentiment: {state_updates.get('sentiment')}")
    return state_updates


# ---------------------------------------------------------------------------
# Node 1: Tutor
# ---------------------------------------------------------------------------

def tutor_node(state: AgentState) -> dict:
    response_text = tutor_agent.generate_response(state)
    return {
        "messages": [AIMessage(content=response_text)],
        "last_agent": "tutor",
    }


# ---------------------------------------------------------------------------
# Node 2: Planner (writes back updated objectives)
# ---------------------------------------------------------------------------

def planner_node(state: AgentState) -> dict:
    response_text, new_objectives = planner_agent.generate_response(state)
    updates = {
        "messages": [AIMessage(content=response_text)],
        "last_agent": "planner",
    }
    if new_objectives:
        updates["remaining_objectives"] = new_objectives
    return updates


# ---------------------------------------------------------------------------
# Node 3: Evaluator (writes back mastery scores using ML algorithm)
# ---------------------------------------------------------------------------

def evaluator_node(state: AgentState) -> dict:
    response_text, evaluation_result = evaluator_agent.generate_response(state)

    # --- Update mastery using ELO + BKT algorithm ---
    topic = state.get("current_topic", "General")
    correctness_score = evaluation_result.get("score", 5)
    current_mastery_levels = state.get("mastery_levels", {}) or {}
    current_topic_mastery = current_mastery_levels.get(topic, {}) or {}

    updated_topic_mastery, new_global_score = update_mastery(
        current_mastery=current_topic_mastery,
        topic=topic,
        correctness_score=correctness_score,
        all_topics_mastery=current_mastery_levels,
    )

    new_mastery_levels = {**current_mastery_levels, topic: updated_topic_mastery}

    print(f"[Evaluator] Topic: {topic} | Score: {correctness_score}/10 | "
          f"Mastery: {updated_topic_mastery['score']:.1%} | Global: {new_global_score:.1%}")

    return {
        "messages": [AIMessage(content=response_text)],
        "last_agent": "evaluator",
        "last_evaluation_result": evaluation_result,
        "mastery_levels": new_mastery_levels,
        "global_mastery_score": new_global_score,
    }


# ---------------------------------------------------------------------------
# Node 4: Coach (writes reduced frustration after intervention)
# ---------------------------------------------------------------------------

def coach_node(state: AgentState) -> dict:
    response_text = coach_agent.generate_response(state)

    # After coaching, reduce frustration significantly
    current_frustration = state.get("frustration_level", 0.0)
    post_coaching_frustration = max(0.0, current_frustration - 0.30)

    print(f"[Coach] Frustration before: {current_frustration:.2f} → after: {post_coaching_frustration:.2f}")

    return {
        "messages": [AIMessage(content=response_text)],
        "last_agent": "coach",
        "active_intervention": True,
        "frustration_level": post_coaching_frustration,
        "sentiment": "neutral",  # coaching resets to neutral
    }


# ---------------------------------------------------------------------------
# Router: reads next_agent from state (set by MetaAgent)
# ---------------------------------------------------------------------------

def router(state: AgentState) -> Literal["tutor", "planner", "evaluator", "coach"]:
    """Route based on MetaAgent's decision stored in state."""
    next_agent = state.get("next_agent", "tutor")
    # Safety: validate it's a known agent
    if next_agent not in ("tutor", "planner", "evaluator", "coach"):
        next_agent = "tutor"
    return next_agent


# ---------------------------------------------------------------------------
# Build the LangGraph
# ---------------------------------------------------------------------------

workflow = StateGraph(AgentState)

# Add all nodes
workflow.add_node("meta_agent", meta_agent_node)
workflow.add_node("tutor", tutor_node)
workflow.add_node("planner", planner_node)
workflow.add_node("evaluator", evaluator_node)
workflow.add_node("coach", coach_node)

# Entry point: always start with MetaAgent
workflow.set_entry_point("meta_agent")

# MetaAgent → conditional routing to specialized agents
workflow.add_conditional_edges(
    "meta_agent",
    router,
    {
        "tutor": "tutor",
        "planner": "planner",
        "evaluator": "evaluator",
        "coach": "coach",
    },
)

# All agents → END after responding
workflow.add_edge("tutor", END)
workflow.add_edge("planner", END)
workflow.add_edge("evaluator", END)
workflow.add_edge("coach", END)

app = workflow.compile()
