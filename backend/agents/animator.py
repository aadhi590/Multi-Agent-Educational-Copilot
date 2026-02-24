import os
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class AnimatorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
        self.system_prompt = """You are the Animator Agent. Your specific role is to write code that generates educational animations.
When a user asks for an animation or video of a concept (strictly bounded to DSA, OOPS, CN, DBMS, Physics, Mathematics, Chemistry), your job is to write a well-structured Python Manim script that visualizes this concept.
You MUST return ONLY the Python code for the complete, runnable Manim scene. Do not include extra pleasantries.
Only return python code blocks."""

    def get_prompt(self):
        return PromptTemplate.from_template(self.system_prompt + "\n\nUser: {human_input}\nAnimator:")

    def generate_response(self, user_input: str) -> str:
        prompt = self.get_prompt().format(human_input=user_input)
        response = self.llm.invoke(prompt)
        return response.content

animator_agent = AnimatorAgent()
