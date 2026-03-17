"""
LangGraph Orchestrator — Production Architecture with Critic Agent.

Flow per student turn:
  START
    ↓
  [meta_agent_node]     ← Updates: sentiment, frustration, topic, next_agent
    ↓ (hybrid routing: rules + sentiment + LLM)
  [tutor | planner | evaluator | coach]   ← Each writes state updates
    ↓
  [critic_node]         ← Reviews & improves response quality (skips coach)
    ↓
  END

Features:
- MetaAgent uses LLM + ML for intent/sentiment analysis
- Hybrid router combines rule-based, sentiment, and LLM decisions
- Critic agent reviews tutor/evaluator/planner responses
- All agents update shared state
- Mastery tracking updates on every evaluation
- Frustration decays after coaching
"""

from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END

from state.agent_state import AgentState
from agents.meta_agent import meta_agent
from agents.tutor import tutor_agent
from agents.planner import planner_agent
from agents.evaluator import evaluator_agent
from agents.coach import coach_agent
from agents.critic_agent import critic_agent
from evaluation.mastery_model import update_mastery
from orchestration.router import hybrid_route


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
    print("[Node] Entering Tutor Node")
    try:
        response_text = tutor_agent.generate_response(state)
        return {
            "messages": [AIMessage(content=response_text)],
            "last_agent": "tutor",
        }
    except Exception as e:
        print(f"[TutorNode] ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise e


# ---------------------------------------------------------------------------
# Node 2: Planner (writes back updated objectives)
# ---------------------------------------------------------------------------

def planner_node(state: AgentState) -> dict:
    print("[Node] Entering Planner Node")
    response_text, new_objectives = planner_agent.generate_response(state)
    updates: dict = {
        "messages": [AIMessage(content=response_text)],
        "last_agent": "planner",
    }
    if new_objectives:
        updates["remaining_objectives"] = new_objectives
        updates["learning_objectives"] = new_objectives
    return updates


# ---------------------------------------------------------------------------
# Node 3: Evaluator (writes back mastery scores using ML algorithm)
# ---------------------------------------------------------------------------

def evaluator_node(state: AgentState) -> dict:
    print("[Node] Entering Evaluator Node")
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

    # Track evaluation history
    eval_history = list(state.get("evaluation_history", []) or [])
    eval_history.append(evaluation_result)
    eval_history = eval_history[-50:]  # Keep last 50

    print(f"[Evaluator] Topic: {topic} | Score: {correctness_score}/10 | "
          f"Mastery: {updated_topic_mastery['score']:.1%} | Global: {new_global_score:.1%}")

    return {
        "messages": [AIMessage(content=response_text)],
        "last_agent": "evaluator",
        "last_evaluation_result": evaluation_result,
        "mastery_levels": new_mastery_levels,
        "global_mastery_score": new_global_score,
        "evaluation_history": eval_history,
    }


# ---------------------------------------------------------------------------
# Node 4: Coach (writes reduced frustration after intervention)
# ---------------------------------------------------------------------------

def coach_node(state: AgentState) -> dict:
    print("[Node] Entering Coach Node")
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
# Node 5: Critic (reviews and improves the last agent's response)
# ---------------------------------------------------------------------------

def critic_node(state: AgentState) -> dict:
    print("[Node] Entering Critic Node")
    """
    Reviews the last agent's response and potentially improves it.
    Modifies the last AI message in the state.
    """
    # Check if we should review
    if not critic_agent.should_review(state):
        return {}  # No changes needed
    
    # Get the last AI message
    messages = state.get("messages", [])
    last_ai_content = ""
    for msg in reversed(messages):
        # LangChain messages use 'type' property but better to check class
        if isinstance(msg, AIMessage):
            last_ai_content = str(msg.content)
            break
    
    if not last_ai_content:
        return {}
    
    # Review the response
    reviewed = critic_agent.review_response(last_ai_content, state)
    
    # Only update if the critic actually changed something
    if reviewed != last_ai_content and reviewed:
        print(f"[Critic] Reviewed and improved {state.get('last_agent', 'unknown')} response")
        # Replace the last message with the reviewed version
        return {
            "messages": [AIMessage(content=reviewed)],
        }
    
    return {}


# ---------------------------------------------------------------------------
# Router: Hybrid routing using rules + sentiment + LLM
# ---------------------------------------------------------------------------

def router(state: AgentState) -> Literal["tutor", "planner", "evaluator", "coach"]:
    """Route using hybrid router that combines rules, sentiment, and LLM decision."""
    return hybrid_route(state)


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
workflow.add_node("critic", critic_node)

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

# Specialized agents → Critic for quality review
workflow.add_edge("tutor", "critic")
workflow.add_edge("planner", "critic")
workflow.add_edge("evaluator", "critic")
workflow.add_edge("coach", "critic")  # Coach goes through critic but critic skips review

# Critic → END
workflow.add_edge("critic", END)

app = workflow.compile()
