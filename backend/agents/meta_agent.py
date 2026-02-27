"""
Meta-Agent: The master orchestrator that coordinates all other agents.

Responsibilities:
1. Analyzes every student message with an LLM → returns structured JSON
2. Updates state: sentiment, frustration_level, engagement_score, current_topic, next_agent
3. The LangGraph router reads state["next_agent"] set by this agent
4. Suppresses Socratic mode if frustration is high (Conflict Resolution)
"""

import os
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from ml.sentiment import analyze_sentiment, update_frustration_with_decay

load_dotenv()


META_SYSTEM_PROMPT = """You are the Master Orchestrator of a multi-agent educational AI system.
Your ONLY job is to analyze the student's message and return a JSON decision object.

AGENTS AVAILABLE:
- "tutor"     → Socratic teaching via questions and scaffolding
- "planner"   → Curriculum roadmap, syllabus, next steps
- "evaluator" → Grading, rubric-based assessment, mastery check
- "coach"     → Emotional support, motivation, frustration intervention

OUTPUT FORMAT (JSON only, no markdown, no extra text):
{
  "intent": <"learn" | "evaluate" | "plan" | "frustrated" | "confused" | "greeting">,
  "detected_topic": <string or null>,
  "frustration_signal": <float 0.0-1.0>,
  "next_agent": <"tutor" | "planner" | "evaluator" | "coach">,
  "reasoning": <one short sentence explaining your decision>,
  "suggested_objective": <string or null>
}

ROUTING RULES (apply in priority order):
1. frustration_signal > 0.6 → ALWAYS route to "coach" (override everything)
2. intent == "plan"  → "planner"
3. intent == "evaluate" → "evaluator"
4. intent == "frustrated" or intent == "confused" → "coach"
5. Default → "tutor"

TOPIC DETECTION: Detect if the message is about DSA, OOP, CN, DBMS, Physics, Math, or Chemistry.
If the topic is outside these, set detected_topic to "out_of_scope".
"""


def _extract_json(text: str) -> dict:
    """Robustly extract JSON from LLM response that might have extra text."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON block from markdown
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Fallback defaults
    return {
        "intent": "learn",
        "detected_topic": None,
        "frustration_signal": 0.0,
        "next_agent": "tutor",
        "reasoning": "Fallback: could not parse meta-agent response",
        "suggested_objective": None,
    }


class MetaAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",   # fast, cheap model for routing
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1,            # low temp for consistent JSON
        )

    def analyze(self, state: dict) -> dict:
        """
        Runs on every student message.
        Returns a state-update dict with routing decision and updated ML fields.
        """
        # --- Get last human message ---
        messages = state.get("messages", [])
        last_text = ""
        for msg in reversed(messages):
            if hasattr(msg, "content"):
                last_text = msg.content
                break
            if isinstance(msg, (list, tuple)) and len(msg) == 2:
                last_text = str(msg[1])
                break

        # --- ML Sentiment Analysis (fast, no LLM call) ---
        ml_frustration, ml_sentiment, ml_engagement = analyze_sentiment(last_text)

        # --- LLM-based Intent & Route Classification ---
        conversation_summary = f"Student message: {last_text}\nCurrent topic: {state.get('current_topic', 'Unknown')}\nGlobal mastery: {state.get('global_mastery_score', 0.0):.1%}"

        try:
            llm_response = self.llm.invoke([
                SystemMessage(content=META_SYSTEM_PROMPT),
                HumanMessage(content=conversation_summary),
            ])
            analysis = _extract_json(llm_response.content)
        except Exception as e:
            print(f"[MetaAgent] LLM error: {e}, using ML-only fallback")
            analysis = {
                "intent": "learn",
                "detected_topic": None,
                "frustration_signal": ml_frustration,
                "next_agent": "coach" if ml_frustration > 0.6 else "tutor",
                "reasoning": "LLM fallback — using sentiment only",
                "suggested_objective": None,
            }

        # --- Blend ML frustration with LLM frustration signal ---
        llm_frustration_raw = analysis.get("frustration_signal", 0.0)
        try:
            llm_frustration = float(llm_frustration_raw)
        except (ValueError, TypeError):
            llm_frustration = 0.0
        
        blended_frustration = round((ml_frustration * 0.5) + (llm_frustration * 0.5), 3)

        # Apply decay from current state (frustration resolves over time)
        current_frustration = state.get("frustration_level", 0.0)
        final_frustration = update_frustration_with_decay(current_frustration, blended_frustration)

        # --- Override next_agent if frustration is critical ---
        next_agent = analysis.get("next_agent", "tutor")
        if final_frustration > 0.65:
            next_agent = "coach"

        # --- Build state updates ---
        state_update = {
            "next_agent": next_agent,
            "sentiment": ml_sentiment,
            "frustration_level": final_frustration,
            "engagement_score": ml_engagement,
            "active_intervention": final_frustration > 0.65,
            "intervention_reason": analysis.get("reasoning") if final_frustration > 0.65 else None,
        }

        # Update topic if detected
        detected_topic = analysis.get("detected_topic")
        if detected_topic and detected_topic != "out_of_scope" and detected_topic is not None:
            state_update["current_topic"] = detected_topic

        # Update objectives if suggested
        suggested_obj = analysis.get("suggested_objective")
        if suggested_obj:
            existing_objs = list(state.get("remaining_objectives", []))
            if suggested_obj not in existing_objs:
                existing_objs.append(suggested_obj)
                state_update["remaining_objectives"] = existing_objs

        return state_update


meta_agent = MetaAgent()
