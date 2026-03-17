"""
Critic Agent — Response Quality Reviewer.

Reviews responses from other agents (especially the Tutor) and improves them
before sending to the student. Acts as a quality gate for LLM output.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from .utils import extract_text

load_dotenv()


CRITIC_SYSTEM_PROMPT = """You are the Critic Agent — a meticulous educational quality reviewer.

Your job is to review a response from another AI agent (the Tutor, Planner, or Evaluator)
and IMPROVE it before it reaches the student.

REVIEW CRITERIA:
1. **Accuracy**: Is the information factually correct?
2. **Clarity**: Is the explanation clear and well-structured?
3. **Pedagogical Quality**: Does it follow good teaching practices?
4. **Completeness**: Does it address the student's question fully?
5. **Tone**: Is it encouraging and appropriate?
6. **Format**: Is it well-formatted with markdown?

RULES:
- If the response is already excellent, return it AS-IS with minimal changes.
- If it needs improvement, rewrite ONLY the problematic parts.
- NEVER change the fundamental teaching approach or contradict the original agent.
- Keep the same length or shorter — do not bloat responses.
- Preserve any code blocks, formulas, and examples exactly.
- If you make changes, make them seamlessly — the student should not know a review happened.

OUTPUT: Return ONLY the improved response text. No meta-commentary about your review.
"""


class CriticAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.2,  # Low temp for precise review
        )

    def review_response(self, original_response: str, state: dict) -> str:
        """
        Review and potentially improve an agent's response.
        
        Args:
            original_response: The response from the original agent.
            state: Current agent state for context.
        
        Returns:
            The reviewed (and potentially improved) response.
        """
        topic = state.get("current_topic", "General")
        mastery = state.get("global_mastery_score", 0.0)
        frustration = state.get("frustration_level", 0.0)
        last_agent = state.get("last_agent", "unknown")

        review_prompt = (
            f"ORIGINAL AGENT: {last_agent}\n"
            f"STUDENT CONTEXT: Topic={topic}, Mastery={mastery:.1%}, Frustration={frustration:.2f}\n\n"
            f"RESPONSE TO REVIEW:\n{original_response}\n\n"
            f"Review this response and return an improved version. "
            f"If it's already good, return it with minimal or no changes."
        )

        try:
            response = self.llm.invoke([
                SystemMessage(content=CRITIC_SYSTEM_PROMPT),
                HumanMessage(content=review_prompt),
            ])
            reviewed = extract_text(response.content)

            # Safety: if critic returns empty or very short, keep original
            if not reviewed or len(reviewed) < len(original_response) * 0.3:
                return original_response

            return reviewed

        except Exception as e:
            print(f"[CriticAgent] Review failed: {e}, using original response")
            return original_response

    def should_review(self, state: dict) -> bool:
        """
        Decide whether this response needs critic review.
        Not every response needs review — skip for simple/coaching responses.
        """
        last_agent = state.get("last_agent", "")
        
        # Always review tutor and evaluator responses (accuracy matters)
        if last_agent in ("tutor", "evaluator"):
            return True
        
        # Review planner responses for completeness
        if last_agent == "planner":
            return True
        
        # Skip coach responses (empathy doesn't need factual review)
        return False


critic_agent = CriticAgent()
