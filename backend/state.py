from typing import Annotated, TypedDict, List, Dict, Any, Optional, Literal
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

class MasteryData(BaseModel):
    score: float = 0.0 # 0.0 to 1.0 (Mastery level)
    attempts: int = 0
    last_updated: str = ""
    status: Literal["not_started", "in_progress", "mastered"] = "not_started"
    learning_objectives_met: List[str] = Field(default_factory=list)

class AgentState(TypedDict):
    # Standard LangGraph message management
    messages: Annotated[list, add_messages]
    
    # Student Context
    student_id: str
    session_id: str
    current_topic: Optional[str]
    current_module: Optional[str]
    
    # Progress & Mastery (Mastery Tracking Algorithm data)
    mastery_levels: Dict[str, MasteryData] 
    global_mastery_score: float # Overall progress
    
    # Agent Coordination
    next_agent: str
    last_agent: str
    
    # Emotional/Engagement Context (Priority Matrix Input)
    frustration_level: float # 0.0 to 1.0
    engagement_score: float # 0.0 to 1.0
    sentiment: str # 'positive', 'negative', 'neutral', 'confused'
    
    # Planner Data (Dynamic Syllabus)
    syllabus: List[Dict[str, Any]]
    remaining_objectives: List[str]
    
    # Evaluator Data (Rubric-Based Assessment)
    last_evaluation_result: Optional[Dict[str, Any]]
    gold_standard_answer: Optional[str] # For the Evaluator to compare against
    
    # Conflict Resolution / Priority Matrix
    priority_level: int # 1 (Critical/Coach) to 5 (Standard/Tutor)
    active_intervention: bool 
    intervention_reason: Optional[str]
