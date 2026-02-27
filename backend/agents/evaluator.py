import os
import json
import re
from typing import Tuple, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()


def _get_last_human_text(state) -> str:
    messages = state.get("messages", [])
    for msg in reversed(messages):
        content = getattr(msg, "content", None)
        if content is not None:
            return str(content)
        if isinstance(msg, (list, tuple)) and len(msg) == 2:
            return str(msg[1])
    return ""


def _extract_score(text: str) -> int:
    """Extract numerical score from evaluator LLM response. Returns 0-10."""
    match = re.search(r"(?:score|correctness)[:\s]*(\d+)\s*/\s*10", text, re.IGNORECASE)
    if match:
        return min(10, max(0, int(match.group(1))))
    match = re.search(r"\b([0-9]|10)\s*/\s*10\b", text)
    if match:
        return int(match.group(1))
    # Keyword fallback
    lower = text.lower()
    if "perfect" in lower or "excellent" in lower or "mastered" in lower:
        return 9
    if "good" in lower or "mostly correct" in lower:
        return 7
    if "partial" in lower or "partially" in lower:
        return 5
    if "incorrect" in lower or "wrong" in lower or "failed" in lower:
        return 3
    return 5  # neutral fallback


class EvaluatorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3,  # lower temp for consistent grading
        )

    def generate_response(self, state: dict) -> Tuple[str, Dict[str, Any]]:
        """
        Returns: (response_text, evaluation_result_dict)
        The dict contains: score, passed, topic, feedback_summary
        """
        human_input = _get_last_human_text(state)
        topic = state.get("current_topic", "General")
        objectives = state.get("remaining_objectives", [])
        gold_standard = state.get("gold_standard_answer") or "No reference provided. Use your expert knowledge."
        mastery_score = state.get("global_mastery_score", 0.0)

        system_text = (
            f"You are the Evaluator Agent — a precise, fair, and structured academic assessor.\n\n"
            f"EVALUATION CONTEXT:\n"
            f"• Current Topic: {topic}\n"
            f"• Student's Global Mastery: {mastery_score:.1%}\n"
            f"• Learning Objectives to Check: {objectives if objectives else 'General understanding of ' + topic}\n"
            f"• Gold Standard Reference: {gold_standard}\n\n"
            f"EVALUATION PROTOCOL:\n"
            f"1. Analyze the student's response for correctness and conceptual depth.\n"
            f"2. Compare against the Gold Standard and learning objectives.\n"
            f"3. Output a structured evaluation with this EXACT format:\n\n"
            f"   **Correctness Score: X/10**\n"
            f"   **Verdict:** [Mastered ✅ / Needs Improvement ⚠️ / Incorrect ❌]\n"
            f"   **Objectives Met:** [list them]\n"
            f"   **Key Misconceptions:** [list them, or 'None' if none]\n"
            f"   **Feedback:** [2-4 sentences of specific, constructive feedback]\n\n"
            f"CRITICAL RULES:\n"
            f"• Passing threshold: 6/10 or above\n"
            f"• If they pass → congratulate and hint at what to learn next\n"
            f"• If they fail → give precise feedback but DO NOT teach (the Tutor handles teaching)\n"
            f"• Adjust grading standards to the student's mastery level\n"
            f"• SCOPE: Evaluate ONLY DSA, OOP, Networks, DBMS, Physics, Math, Chemistry"
        )

        response = self.llm.invoke([
            SystemMessage(content=system_text),
            HumanMessage(content=human_input),
        ])

        response_text = response.content
        score = _extract_score(response_text)
        passed = score >= 6

        evaluation_result = {
            "score": score,
            "passed": passed,
            "topic": topic,
            "feedback_summary": response_text[:200],
        }

        return response_text, evaluation_result


evaluator_agent = EvaluatorAgent()
