import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()


def _get_last_human_text(state) -> str:
    messages = state.get("messages", [])
    for msg in reversed(messages):
        # Use getattr to satisfy type checker and handle diverse message objects
        content = getattr(msg, "content", None)
        if content is not None:
            return str(content)
        if isinstance(msg, (list, tuple)) and len(msg) == 2:
            return str(msg[1])
    return ""


class CoachAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.8,  # more creative/warm for coaching
        )

    def generate_response(self, state: dict) -> str:
        human_input = _get_last_human_text(state)
        frustration = state.get("frustration_level", 0.0)
        sentiment = state.get("sentiment", "neutral")
        mastery = state.get("global_mastery_score", 0.0)
        topic = state.get("current_topic", "your topic")
        attempts_summary = _build_attempt_summary(state)

        # Choose coaching style based on frustration severity
        if frustration >= 0.80:
            coaching_mode = (
                "CRISIS MODE: The student is extremely frustrated and on the verge of giving up. "
                "Your ONLY job right now is to make them feel heard and supported. "
                "DO NOT mention any academic content. DO NOT ask them to try again. "
                "Simply validate their feelings deeply, normalize the struggle profoundly, "
                "and remind them that frustration means they're pushing their limits — that's growth. "
                "Be genuinely human, warm, and empathetic. Use personal, encouraging language."
            )
        elif frustration >= 0.55:
            coaching_mode = (
                "HIGH FRUSTRATION: The student is visibly struggling. Lead with strong empathy. "
                "Validate first, then gently offer 1-2 study strategies (like the Pomodoro technique, "
                "taking a break, or trying a different approach). Only briefly mention academic content at the end."
            )
        elif frustration >= 0.30:
            coaching_mode = (
                "MODERATE CHALLENGE: The student is finding things hard but not overwhelmed. "
                "Acknowledge their effort, provide motivation, and suggest a concrete study tip. "
                "Help them reframe the difficulty as a normal part of learning."
            )
        else:
            coaching_mode = (
                "MAINTENANCE MODE: The student is doing okay but could use encouragement. "
                "Celebrate their progress, highlight what they've learned, and give them energy "
                "to keep going. Be enthusiastic and positive."
            )

        system_text = (
            f"You are the Coach Agent — an empathetic mentor, growth mindset advocate, and learning psychologist.\n\n"
            f"COACHING MODE: {coaching_mode}\n\n"
            f"STUDENT DATA:\n"
            f"• Current Topic: {topic}\n"
            f"• Sentiment: {sentiment} | Frustration: {frustration:.0%}\n"
            f"• Global Mastery Progress: {mastery:.1%}\n"
            f"• Recent Attempts: {attempts_summary}\n\n"
            f"COACHING TOOLKIT (use as appropriate):\n"
            f"• Validate feelings explicitly ('It's completely normal to feel...')\n"
            f"• Growth mindset reframes ('Every mistake is data, not failure')\n"
            f"• Study techniques: Pomodoro, spaced repetition, rubber duck debugging, active recall\n"
            f"• Progress celebration: highlight what they HAVE mastered\n"
            f"• Motivational stories or analogies from famous scientists/engineers who struggled\n\n"
            f"FORMAT: Use warm, conversational language. 3-4 short paragraphs max. "
            f"End with a specific, actionable next step (not academic content — something they can do RIGHT NOW "
            f"to reset mentally, like 'Take a 5-minute walk' or 'Write down what you DO know').\n\n"
            f"SCOPE: Keep coaching relevant to learning {topic}."
        )

        response = self.llm.invoke([
            SystemMessage(content=system_text),
            HumanMessage(content=human_input),
        ])
        return response.content


def _build_attempt_summary(state: dict) -> str:
    mastery_levels = state.get("mastery_levels", {})
    if not mastery_levels:
        return "No assessments yet"
    summaries = []
    # Use manual count to avoid slice indexing issues with some type checkers
    count = 0
    for topic, data in mastery_levels.items():
        if count >= 3:
            break
        if isinstance(data, dict):
            attempts = data.get("attempts", 0)
            score = data.get("score", 0.0)
            summaries.append(f"{topic}: {attempts} attempts, {score:.0%} mastery")
        count += 1
    return "; ".join(summaries) if summaries else "No data"


coach_agent = CoachAgent()
