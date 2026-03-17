"""
Multi-Agent Educational Copilot — FastAPI Server

Enhanced API with endpoints for:
- Chat interaction (LangGraph orchestrator)
- Study plan retrieval
- Mastery/analytics data
- Knowledge base management
"""

import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage

from orchestration.orchestrator import app as graph_app
from database import db_manager

app = FastAPI(title="Multi-Agent Educational Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# In-memory session store (for when Firebase is unavailable)
# ---------------------------------------------------------------------------
_sessions: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    student_id: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    agent: str
    session_id: str
    state: Optional[dict] = None


class StudyPlanResponse(BaseModel):
    syllabus: List[Dict[str, Any]]
    objectives: List[str]
    current_topic: str
    global_mastery: float


class AnalyticsResponse(BaseModel):
    mastery_levels: Dict[str, Any]
    global_mastery_score: float
    evaluation_history: List[Dict[str, Any]]
    total_messages: int
    topics_studied: List[str]


class KnowledgeAddRequest(BaseModel):
    content: str
    title: str = ""
    topic: str = ""


# ---------------------------------------------------------------------------
# Helper: build initial state for a brand-new session
# ---------------------------------------------------------------------------

def _build_initial_state(student_id: str, session_id: str, first_message: str) -> dict:
    return {
        "messages": [HumanMessage(content=first_message)],
        "student_id": student_id,
        "session_id": session_id,
        "current_topic": "General",
        "current_module": "Intro",
        "mastery_levels": {},
        "global_mastery_score": 0.0,
        "frustration_level": 0.0,
        "engagement_score": 1.0,
        "sentiment": "neutral",
        "syllabus": [],
        "remaining_objectives": [],
        "learning_objectives": [],
        "next_agent": "tutor",
        "last_agent": "system",
        "active_intervention": False,
        "intervention_reason": None,
        "priority_level": 4,
        "last_evaluation_result": None,
        "gold_standard_answer": None,
        "evaluation_history": [],
        "conversation_history": [],
    }


def _restore_messages(raw_messages: list) -> list:
    """Convert stored message dicts back to LangChain message objects."""
    restored = []
    for m in raw_messages:
        if isinstance(m, dict):
            role = m.get("role", "unknown")
            content = m.get("content", "")
            if role in ("human", "user"):
                restored.append(HumanMessage(content=content))
            else:
                restored.append(AIMessage(content=content))
        elif hasattr(m, "content"):
            restored.append(m)
    return restored


def _save_session(student_id: str, session_id: str, state: dict):
    """Save session state to both in-memory store and Firebase."""
    key = f"{student_id}:{session_id}"
    _sessions[key] = state
    db_manager.save_student_session_state(student_id, session_id, state)


def _load_session(student_id: str, session_id: str) -> dict:
    """Load session state from in-memory store or Firebase."""
    key = f"{student_id}:{session_id}"
    if key in _sessions:
        return _sessions[key]
    return db_manager.get_student_session_state(student_id, session_id)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def read_root():
    return {
        "message": "Multi-Agent Educational Copilot API",
        "status": "running",
        "agents": ["meta", "tutor", "planner", "evaluator", "coach", "critic"],
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "agents": ["meta", "tutor", "planner", "evaluator", "coach", "critic"],
        "features": ["rag", "tools", "mastery_tracking", "sentiment_analysis"],
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    # 1. Load existing session state
    existing_state = _load_session(request.student_id, session_id)

    # 2. Build or restore state
    if not existing_state:
        state = _build_initial_state(request.student_id, session_id, request.message)
    else:
        # Restore message objects from stored dicts
        if "messages" in existing_state:
            existing_state["messages"] = _restore_messages(existing_state["messages"])
        # Append the new user message
        existing_state["messages"].append(HumanMessage(content=request.message))
        
        # Ensure new state fields exist
        existing_state.setdefault("learning_objectives", [])
        existing_state.setdefault("evaluation_history", [])
        existing_state.setdefault("conversation_history", [])
        
        state = existing_state

    # 3. Run the LangGraph orchestrator
    try:
        final_state = await graph_app.ainvoke(state)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[Orchestrator] Critical Error:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Orchestrator error: {str(e)}")

    # 4. Update conversation history
    conv_history: List[Dict[str, str]] = list(final_state.get("conversation_history", []) or [])
    conv_history.append({"role": "human", "content": request.message})

    # 5. Persist updated state
    _save_session(request.student_id, session_id, final_state)

    # 6. Return the last AI message
    last_ai_message = ""
    messages_list: List[Any] = final_state.get("messages", [])
    for msg in reversed(messages_list):
        if isinstance(msg, AIMessage):
            if isinstance(msg.content, list):
                text_blocks = []
                for block in msg.content:
                    if isinstance(block, dict) and "text" in block:
                        text_blocks.append(block["text"])
                    elif isinstance(block, str):
                        text_blocks.append(block)
                last_ai_message = "".join(text_blocks)
            else:
                last_ai_message = str(msg.content)
            break

    if not last_ai_message:
        last_ai_message = "I'm sorry, I couldn't generate a response. Please try again."

    # Prepare evaluation history for response with safe slicing
    eval_hist: List[Any] = list(final_state.get("evaluation_history", []) or [])
    safe_eval_hist = eval_hist[-10:] if len(eval_hist) > 10 else eval_hist

    return ChatResponse(**{
        "response": last_ai_message,
        "agent": str(final_state.get("last_agent", "unknown")),
        "session_id": session_id,
        "state": {
            "frustration_level": float(final_state.get("frustration_level", 0.0)),
            "engagement_score": float(final_state.get("engagement_score", 0.8)),
            "sentiment": str(final_state.get("sentiment", "neutral")),
            "global_mastery_score": float(final_state.get("global_mastery_score", 0.0)),
            "mastery_levels": dict(final_state.get("mastery_levels", {}) or {}),
            "current_topic": str(final_state.get("current_topic", "—")),
            "session_id": session_id,
            "remaining_objectives": list(final_state.get("remaining_objectives", []) or []),
            "learning_objectives": list(final_state.get("learning_objectives", []) or []),
            "syllabus": list(final_state.get("syllabus", []) or []),
            "evaluation_history": safe_eval_hist,
            "last_evaluation_result": final_state.get("last_evaluation_result"),
        },
    })


@app.get("/study-plan/{student_id}/{session_id}")
def get_study_plan(student_id: str, session_id: str):
    """Get the current study plan for a student session."""
    state = _load_session(student_id, session_id)
    if not state:
        return {
            "syllabus": [],
            "objectives": [],
            "current_topic": "General",
            "global_mastery": 0.0,
        }
    
    return {
        "syllabus": state.get("syllabus", []),
        "objectives": state.get("remaining_objectives", []),
        "current_topic": state.get("current_topic", "General"),
        "global_mastery": state.get("global_mastery_score", 0.0),
    }


@app.get("/analytics/{student_id}/{session_id}")
def get_analytics(student_id: str, session_id: str):
    """Get performance analytics for a student session."""
    state = _load_session(student_id, session_id)
    if not state:
        return {
            "mastery_levels": {},
            "global_mastery_score": 0.0,
            "evaluation_history": [],
            "total_messages": 0,
            "topics_studied": [],
        }
    
    mastery_levels = state.get("mastery_levels", {})
    topics = list(mastery_levels.keys()) if mastery_levels else []
    
    messages = state.get("messages", [])
    total_messages = len(messages) if isinstance(messages, list) else 0
    
    return {
        "mastery_levels": {
            k: (v if isinstance(v, dict) else {})
            for k, v in (mastery_levels or {}).items()
        },
        "global_mastery_score": state.get("global_mastery_score", 0.0),
        "evaluation_history": (state.get("evaluation_history") or [])[-20:],
        "total_messages": total_messages,
        "topics_studied": topics,
    }


@app.get("/mastery/{student_id}")
def get_mastery(student_id: str):
    """Mastery dashboard endpoint for the frontend."""
    data = db_manager.get_mastery(student_id)
    return {"student_id": student_id, "mastery": data}


@app.post("/knowledge/add")
async def add_knowledge(request: KnowledgeAddRequest):
    """Add a document to the knowledge base for RAG."""
    try:
        from retrieval.vector_store import get_vector_store
        store = get_vector_store()
        store.add_documents([{
            "content": request.content,
            "title": request.title,
            "topic": request.topic,
        }])
        return {"status": "ok", "total_documents": store.size}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add knowledge: {str(e)}")


@app.get("/knowledge/stats")
def knowledge_stats():
    """Get knowledge base statistics."""
    try:
        from retrieval.vector_store import get_vector_store
        store = get_vector_store()
        return {"total_documents": store.size}
    except Exception as e:
        return {"total_documents": 0, "error": str(e)}
