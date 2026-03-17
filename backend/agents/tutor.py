"""
Tutor Agent — Enhanced with Tool Usage and RAG.

Uses the Socratic method to teach concepts, with the ability to:
1. Retrieve relevant knowledge from the vector store (RAG)
2. Use math tools for equation solving and differentiation
3. Execute Python code for coding problems
4. Adapt explanation depth based on student mastery
"""

import os
import re
from typing import List, Dict, Any, Optional
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


def _get_conversation_history(state, max_turns: int = 6) -> str:
    """Build a short conversation history string for context continuity."""
    messages: List[Any] = state.get("messages", [])
    history_lines: List[str] = []
    for msg in messages[-max_turns:]:
        msg_type = getattr(msg, "type", None)
        msg_content = getattr(msg, "content", None)
        if msg_type is not None and msg_content is not None:
            role = "Student" if msg_type == "human" else "Tutor"
            content_str = str(msg_content)
            # Use explicit slicing to avoid type checker confusion
            history_lines.append(f"{role}: {content_str[0:300]}")
        elif isinstance(msg, (list, tuple)) and len(msg) >= 2:
            m_list = list(msg)
            role = "Student" if str(m_list[0]) == "human" else "Tutor"
            content_str = str(m_list[1])
            history_lines.append(f"{role}: {content_str[0:300]}")
    return "\n".join(history_lines)


def _detect_math_request(text: str) -> Dict[str, Any]:
    """Detect if the student is asking a math/computation question."""
    text_lower = text.lower()
    
    result: Dict[str, Any] = {"type": None, "expression": None}
    
    # Detect equation solving requests
    equation_patterns = [
        r'solve\s+(.+?\s*=\s*.+)',
        r'find\s+x\s+(?:in|for|when)\s+(.+)',
        r'what\s+is\s+x\s+(?:in|if|when)\s+(.+)',
    ]
    for pattern in equation_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["type"] = "solve"
            result["expression"] = match.group(1).strip()
            return result
    
    # Detect differentiation requests
    diff_patterns = [
        r'(?:differentiate|derivative\s+of|d/dx)\s+(.+)',
        r'find\s+(?:the\s+)?derivative\s+(?:of\s+)?(.+)',
    ]
    for pattern in diff_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["type"] = "differentiate"
            result["expression"] = match.group(1).strip()
            return result
    
    # Detect calculation requests
    calc_patterns = [
        r'(?:calculate|compute|evaluate|what\s+is)\s+([\d\s\+\-\*\/\(\)\.\^]+)',
    ]
    for pattern in calc_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result["type"] = "calculate"
            result["expression"] = match.group(1).strip()
            return result
    
    return result


def _use_tools(human_input: str) -> str:
    """Use appropriate tools based on the input and return formatted results."""
    math_request = _detect_math_request(human_input)
    
    if not math_request["type"]:
        return ""
    
    tool_output = ""
    
    try:
        if math_request["type"] == "solve":
            from tools.math_tools import solve_equation
            result = solve_equation(math_request["expression"])
            if result["success"]:
                steps = "\n".join(f"  {s}" for s in result["steps"])
                tool_output = f"\n📐 **Tool: Equation Solver**\n{steps}\n"
        
        elif math_request["type"] == "differentiate":
            from tools.math_tools import differentiate
            result = differentiate(math_request["expression"])
            if result["success"]:
                steps = "\n".join(f"  {s}" for s in result["steps"])
                tool_output = f"\n📐 **Tool: Differentiation**\n{steps}\n"
        
        elif math_request["type"] == "calculate":
            from tools.calculator import calculate
            result = calculate(math_request["expression"])
            if result["success"]:
                tool_output = f"\n🔢 **Calculator**: {math_request['expression']} = {result['result']}\n"
    
    except Exception as e:
        print(f"[TutorAgent] Tool error: {e}")
    
    return tool_output


def _get_rag_context(human_input: str, topic: str) -> str:
    """Retrieve relevant knowledge from the vector store."""
    try:
        from retrieval.retriever import retrieve_context, format_context_for_prompt
        results = retrieve_context(human_input, topic=topic, top_k=2)
        if results:
            return format_context_for_prompt(results)
    except Exception as e:
        print(f"[TutorAgent] RAG error: {e}")
    
    return ""


class TutorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro-latest",
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

        # ── Tool Augmentation ──
        tool_output = _use_tools(human_input)
        
        # ── RAG Context ──
        rag_context = _get_rag_context(human_input, topic)

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

        # Build tool context section
        tool_section = ""
        if tool_output:
            tool_section = (
                f"\n\nTOOL RESULTS (incorporate these into your explanation):\n{tool_output}"
            )
        
        # Build RAG context section
        rag_section = ""
        if rag_context:
            rag_section = f"\n\n{rag_context}"

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
            f"CONVERSATION HISTORY (last few turns):\n{history}\n"
            f"{tool_section}"
            f"{rag_section}\n\n"
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
        return extract_text(response.content)


tutor_agent = TutorAgent()
