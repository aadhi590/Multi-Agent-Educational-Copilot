import os
import json
import re
from typing import Tuple, List, Dict, Any
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


class PlannerAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.5,
        )

    def generate_response(self, state: dict) -> Tuple[str, List[str]]:
        """
        Returns: (response_text, updated_objectives_list)
        """
        human_input = _get_last_human_text(state)
        syllabus = state.get("syllabus", [])
        remaining = state.get("remaining_objectives", [])
        mastery = state.get("mastery_levels", {})
        topic = state.get("current_topic", "General")
        global_mastery = state.get("global_mastery_score", 0.0)

        # Format mastery summary
        mastery_summary = []
        for t, data in mastery.items():
            if isinstance(data, dict):
                score = data.get("score", 0.0)
                status = data.get("status", "unknown")
                mastery_summary.append(f"  • {t}: {score:.0%} ({status})")
        mastery_text = "\n".join(mastery_summary) if mastery_summary else "  • No topics assessed yet"

        system_text = (
            f"You are the Planner Agent — a master curriculum architect and learning strategist.\n\n"
            f"STUDENT PROFILE:\n"
            f"• Current Topic Focus: {topic}\n"
            f"• Global Mastery: {global_mastery:.1%}\n"
            f"• Mastery Breakdown:\n{mastery_text}\n"
            f"• Current Syllabus: {syllabus if syllabus else 'Not yet defined'}\n"
            f"• Remaining Objectives: {remaining if remaining else 'Not yet defined'}\n\n"
            f"YOUR RESPONSIBILITIES:\n"
            f"1. If the student states a goal → create a structured learning roadmap\n"
            f"2. If a topic is mastered → recommend the next logical topic\n"
            f"3. Break goals into 3-5 clear, actionable milestones\n"
            f"4. Always include:\n"
            f"   - **Recommended Path** (ordered list of topics)\n"
            f"   - **Current Priority** (what to focus on RIGHT NOW)\n"
            f"   - **Next Steps** (specific actions for today)\n"
            f"   - **Estimated Timeline** (realistic time estimates)\n\n"
            f"AFTER YOUR RESPONSE, add a JSON block (do NOT render as markdown) with this EXACT format:\n"
            f"OBJECTIVES_JSON: {{\"objectives\": [\"objective1\", \"objective2\", \"objective3\"]}}\n\n"
            f"SCOPE: DSA, OOP, Computer Networks, DBMS, Physics, Mathematics, Chemistry ONLY.\n"
            f"Use markdown formatting. Be encouraging, concrete, and strategic."
        )

        response = self.llm.invoke([
            SystemMessage(content=system_text),
            HumanMessage(content=human_input),
        ])

        response_text = response.content

        # Extract updated objectives from JSON block
        new_objectives = remaining[:]  # default: keep existing
        match = re.search(r"OBJECTIVES_JSON:\s*(\{.*?\})", response_text, re.DOTALL)
        if match:
            try:
                obj_data = json.loads(match.group(1))
                new_objectives = obj_data.get("objectives", remaining)
                # Clean the JSON from the displayed response
                response_text = response_text[:match.start()].strip()
            except json.JSONDecodeError:
                pass

        return response_text, new_objectives


planner_agent = PlannerAgent()
