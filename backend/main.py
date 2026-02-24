from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.planner import planner_agent
from agents.tutor import tutor_agent
from agents.evaluator import evaluator_agent
from agents.coach import coach_agent
from agents.animator import animator_agent

app = FastAPI(title="Multi-Agent Educational Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    agent_type: str

class ChatResponse(BaseModel):
    response: str
    agent: str

AGENT_MAP = {
    "planner": planner_agent,
    "tutor": tutor_agent,
    "evaluator": evaluator_agent,
    "coach": coach_agent,
    "animator": animator_agent,
}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Multi-Agent Educational Copilot API"}

@app.get("/health")
def health_check():
    return {"status": "ok", "agents": list(AGENT_MAP.keys())}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    agent = AGENT_MAP.get(request.agent_type)
    if not agent:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent type '{request.agent_type}'. Available: {list(AGENT_MAP.keys())}"
        )
    
    try:
        response = agent.generate_response(request.message)
        return ChatResponse(response=response, agent=request.agent_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
