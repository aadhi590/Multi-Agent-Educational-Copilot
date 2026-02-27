import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage

from orchestrator import app as graph_app
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
    state: Optional[dict] = None  # Live state for frontend dashboard


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
        "next_agent": "tutor",
        "last_agent": "system",
        "active_intervention": False,
        "intervention_reason": None,
        "priority_level": 4,
        "last_evaluation_result": None,
        "gold_standard_answer": None,
    }


def _restore_messages(raw_messages: list) -> list:
    """Convert Firestore-stored message dicts back to LangChain message objects."""
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
            restored.append(m)  # already a message object
    return restored


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def read_root():
    return {"message": "Multi-Agent Educational Copilot API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "ok", "agents": ["tutor", "planner", "evaluator", "coach"]}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    # 1. Load existing session state from Firebase (returns {} if unavailable)
    existing_state = db_manager.get_student_session_state(request.student_id, session_id)

    # 2. Build or restore state
    if not existing_state:
        state = _build_initial_state(request.student_id, session_id, request.message)
    else:
        # Restore message objects from stored dicts
        if "messages" in existing_state:
            existing_state["messages"] = _restore_messages(existing_state["messages"])
        # Append the new user message
        existing_state["messages"].append(HumanMessage(content=request.message))
        state = existing_state

    # 3. Run the LangGraph orchestrator
    try:
        final_state = await graph_app.ainvoke(state)
    except Exception as e:
        print(f"[Orchestrator] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Orchestrator error: {str(e)}")

    # 4. Persist updated state to Firebase (fire-and-forget; errors are logged, not raised)
    db_manager.save_student_session_state(request.student_id, session_id, final_state)

    # 5. Return the last AI message
    last_ai_message = ""
    for msg in reversed(final_state.get("messages", [])):
        if isinstance(msg, AIMessage):
            last_ai_message = msg.content
            break

    if not last_ai_message:
        last_ai_message = "I'm sorry, I couldn't generate a response. Please try again."

    return ChatResponse(**{
        "response": last_ai_message,
        "agent": final_state.get("last_agent", "unknown"),
        "session_id": session_id,
        "state": {
            "frustration_level": final_state.get("frustration_level", 0.0),
            "engagement_score":  final_state.get("engagement_score", 0.8),
            "sentiment":         final_state.get("sentiment", "neutral"),
            "global_mastery_score": final_state.get("global_mastery_score", 0.0),
            "mastery_levels":    {
                k: (v if isinstance(v, dict) else {})
                for k, v in (final_state.get("mastery_levels") or {}).items()
            },
            "current_topic":     final_state.get("current_topic", "—"),
            "session_id":        session_id,
        },
    })


@app.get("/mastery/{student_id}")
def get_mastery(student_id: str):
    """Mastery dashboard endpoint for the frontend."""
    data = db_manager.get_mastery(student_id)
    return {"student_id": student_id, "mastery": data}
