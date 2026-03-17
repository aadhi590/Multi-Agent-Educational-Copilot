"""
Agent State — Shared state definition for all agents in the system.

This is the single source of truth passed through the LangGraph workflow.
Every agent reads from and writes to this shared state.
"""

from typing import Annotated, TypedDict, List, Dict, Any, Optional, Literal
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class MasteryData(BaseModel):
    score: float = 0.0  # 0.0 to 1.0 (Mastery level)
    elo_score: float = 0.3
    bkt_score: float = 0.3
    attempts: int = 0
    last_updated: str = ""
    last_correctness: int = 0
    status: Literal["not_started", "in_progress", "mastered"] = "not_started"
    learning_objectives_met: List[str] = Field(default_factory=list)
    score_history: List[Dict[str, Any]] = Field(default_factory=list)
    learning_velocity: float = 0.0
    passed: bool = False


class AgentState(TypedDict):
    # ── Standard LangGraph message management ──
    messages: Annotated[list, add_messages]

    # ── Student Context ──
    student_id: str
    session_id: str
    current_topic: Optional[str]
    current_module: Optional[str]

    # ── Learning Objectives ──
    learning_objectives: List[str]

    # ── Progress & Mastery ──
    mastery_levels: Dict[str, Any]
    global_mastery_score: float

    # ── Agent Coordination ──
    next_agent: str
    last_agent: str

    # ── Emotional/Engagement Context ──
    frustration_level: float        # 0.0 to 1.0
    engagement_score: float         # 0.0 to 1.0
    sentiment: str                  # 'positive', 'negative', 'neutral', 'confused'

    # ── Planner Data ──
    syllabus: List[Dict[str, Any]]
    remaining_objectives: List[str]

    # ── Evaluator Data ──
    last_evaluation_result: Optional[Dict[str, Any]]
    gold_standard_answer: Optional[str]
    evaluation_history: List[Dict[str, Any]]

    # ── Conversation History tracking ──
    conversation_history: List[Dict[str, str]]

    # ── Priority / Conflict Resolution ──
    priority_level: int             # 1 (Critical/Coach) to 5 (Standard/Tutor)
    active_intervention: bool
    intervention_reason: Optional[str]
