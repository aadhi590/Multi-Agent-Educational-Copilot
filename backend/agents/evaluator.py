"""
Evaluator Agent — Enhanced with tool-augmented grading.

Evaluates student answers with:
1. LLM-based rubric assessment
2. Math tool verification for computation answers
3. Misconception detection
4. Mastery score updates using ELO+BKT
"""

import os
import json
import re
from typing import Tuple, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from .utils import extract_text

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


def _extract_misconceptions(text: str) -> list:
    """Extract misconceptions identified in evaluation."""
    misconceptions = []
    
    # Look for misconception sections
    patterns = [
        r"Misconceptions?[:\s]*(.+?)(?:\n\n|\n\*\*|$)",
        r"Key Misconceptions?[:\s]*(.+?)(?:\n\n|\n\*\*|$)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            if content.lower() != "none" and content.lower() != "none detected":
                # Split by bullet points or newlines
                items = re.split(r'\n[-•*]\s*', content)
                misconceptions.extend([item.strip() for item in items if item.strip()])
    
    return misconceptions


def _verify_with_tools(student_answer: str, topic: str) -> str:
    """Use math tools to verify student's computational answers."""
    tool_verification = ""
    
    try:
        # Check if answer contains equations
        if re.search(r'[=\+\-\*/\^].*\d', student_answer):
            from tools.math_tools import simplify_expression
            # Try to find and verify math expressions in the answer
            math_exprs = re.findall(r'[\d\w\+\-\*/\^\(\)\s\.]+[=][\d\w\+\-\*/\^\(\)\s\.]+', student_answer)
            for expr in math_exprs[:2]:  # Verify first 2 expressions
                parts = expr.split("=")
                if len(parts) == 2:
                    try:
                        result = simplify_expression(f"({parts[0].strip()}) - ({parts[1].strip()})")
                        if result["success"]:
                            if result["result"] == "0":
                                tool_verification += f"\n✅ Verified: {expr.strip()} is correct"
                            else:
                                tool_verification += f"\n⚠️ Check: {expr.strip()} may be incorrect (difference: {result['result']})"
                    except Exception:
                        pass
    except Exception as e:
        print(f"[EvaluatorAgent] Tool verification error: {e}")
    
    return tool_verification


class EvaluatorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3,  # lower temp for consistent grading
        )

    def generate_response(self, state: dict) -> Tuple[str, Dict[str, Any]]:
        """
        Returns: (response_text, evaluation_result_dict)
        The dict contains: score, passed, topic, feedback_summary, misconceptions
        """
        human_input = _get_last_human_text(state)
        topic = state.get("current_topic", "General")
        objectives = state.get("remaining_objectives", [])
        gold_standard = state.get("gold_standard_answer") or "No reference provided. Use your expert knowledge."
        mastery_score = state.get("global_mastery_score", 0.0)

        # ── Tool-Augmented Verification ──
        tool_verification = _verify_with_tools(human_input, topic)
        tool_section = ""
        if tool_verification:
            tool_section = f"\n\nAUTOMATED VERIFICATION RESULTS:\n{tool_verification}\n"

        system_text = (
            f"You are the Evaluator Agent — a precise, fair, and structured academic assessor.\n\n"
            f"EVALUATION CONTEXT:\n"
            f"• Current Topic: {topic}\n"
            f"• Student's Global Mastery: {mastery_score:.1%}\n"
            f"• Learning Objectives to Check: {objectives if objectives else 'General understanding of ' + topic}\n"
            f"• Gold Standard Reference: {gold_standard}\n"
            f"{tool_section}\n"
            f"EVALUATION PROTOCOL:\n"
            f"1. Analyze the student's response for correctness and conceptual depth.\n"
            f"2. Compare against the Gold Standard and learning objectives.\n"
            f"3. Identify specific conceptual mistakes or misconceptions.\n"
            f"4. Output a structured evaluation with this EXACT format:\n\n"
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

        response_text = extract_text(response.content)
        score = _extract_score(response_text)
        passed = score >= 6
        misconceptions = _extract_misconceptions(response_text)

        evaluation_result = {
            "score": score,
            "passed": passed,
            "topic": topic,
            "feedback_summary": response_text[:200],
            "misconceptions": misconceptions,
            "tool_verified": bool(tool_verification),
        }

        return response_text, evaluation_result


evaluator_agent = EvaluatorAgent()
