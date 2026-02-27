import os
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


def _get_conversation_history(state, max_turns: int = 6) -> str:
    """Build a short conversation history string for context continuity."""
    messages = state.get("messages", [])
    history_lines = []
    for msg in messages[-max_turns:]:
        msg_type = getattr(msg, "type", None)
        msg_content = getattr(msg, "content", None)
        if msg_type is not None and msg_content is not None:
            role = "Student" if msg_type == "human" else "Tutor"
            history_lines.append(f"{role}: {str(msg_content)[:300]}")
        elif isinstance(msg, (list, tuple)) and len(msg) >= 2:
            # Use local variables to help narrow down types for the checker
            m_list = list(msg)
            role = "Student" if str(m_list[0]) == "human" else "Tutor"
            history_lines.append(f"{role}: {str(m_list[1])[:300]}")
    return "\n".join(history_lines)


class TutorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7,
        )

    def generate_response(self, state: dict) -> str:
        human_input = _get_last_human_text(state)
        history = _get_conversation_history(state, max_turns=8)

        mastery_score = state.get("global_mastery_score", 0.0)
        frustration = state.get("frustration_level", 0.0)
        topic = state.get("current_topic", "General")
        module = state.get("current_module", "Introduction")
        sentiment = state.get("sentiment", "neutral")

        # Adapt explanation depth based on mastery
        if mastery_score < 0.30:
            depth_instruction = (
                "The student is a BEGINNER. Use very simple language, real-world analogies, "
                "and everyday examples. Break every concept into the smallest possible steps. "
                "Avoid jargon unless absolutely necessary, and always define it if used."
            )
        elif mastery_score < 0.60:
            depth_instruction = (
                "The student has INTERMEDIATE knowledge. Use proper technical terminology "
                "but always pair it with intuitive explanations. Connect new ideas to what they already know."
            )
        else:
            depth_instruction = (
                "The student is ADVANCED. Use precise technical language. Introduce edge cases, "
                "complexity analysis, and nuanced distinctions. Challenge them with follow-up thinking questions."
            )

        # Soften Socratic mode if frustrated
        if frustration > 0.4:
            socratic_mode = (
                "The student is SOMEWHAT FRUSTRATED. Tone down the Socratic questioning. "
                "Provide a bit more direct guidance and reassurance before asking questions. "
                "Start with a validating statement."
            )
        else:
            socratic_mode = (
                "Use the full Socratic method. NEVER give the direct answer. "
                "Ask probing questions, give hints, break the problem into smaller pieces."
            )

        system_text = (
            f"You are the Tutor Agent — a world-class educational AI with deep expertise in CS and Sciences.\n\n"
            f"PEDAGOGICAL APPROACH:\n"
            f"{socratic_mode}\n\n"
            f"EXPLANATION DEPTH:\n"
            f"{depth_instruction}\n\n"
            f"STUDENT CONTEXT:\n"
            f"• Topic: {topic} | Module: {module}\n"
            f"• Mastery Score: {mastery_score:.1%} | Sentiment: {sentiment}\n"
            f"• Frustration Level: {frustration:.2f}/1.0\n\n"
            f"CONVERSATION HISTORY (last few turns):\n{history}\n\n"
            f"FORMATTING RULES:\n"
            f"• Use markdown: **bold** for key terms, `code` for syntax, numbered lists for steps\n"
            f"• Keep response focused and under 350 words unless a detailed explanation is essential\n"
            f"• Always end with ONE follow-up question to check understanding\n\n"
            f"STRICT SCOPE: DSA, OOP, Computer Networks, DBMS, Physics, Mathematics, Chemistry ONLY. "
            f"Politely decline anything else."
        )

        response = self.llm.invoke([
            SystemMessage(content=system_text),
            HumanMessage(content=human_input),
        ])
        return response.content


tutor_agent = TutorAgent()
