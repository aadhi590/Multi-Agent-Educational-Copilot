import os
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class PlannerAgent:
    def __init__(self):
        # We initialize the Gemini model here. It expects GEMINI_API_KEY in the environment.
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
        self.system_prompt = """You are the Planner Agent, a master curriculum architect. Your primary role is to guide the learner's journey by structuring high-level educational goals into concrete, actionable steps. 
You do not teach specific concepts or test the student. Instead, you create outlines, suggest learning materials, and formulate a roadmap.
When the user expresses a goal, break it down logically. If the user completes a task, provide the next logical step. 
Keep your tone encouraging, organized, and structured. Always provide a clear 'Next Steps' section.
IMPORTANT STRICT SCOPE: You are restricted to answering questions and creating plans ONLY about the following topics:
Data Structures and Algorithms (DSA), Object-Oriented Programming (OOPS), Computer Networks (CN), Database Management Systems (DBMS), Physics, Mathematics, and Chemistry.
If the user asks for a plan outside of these topics, politely decline and inform them of your specialized scope."""

    def get_prompt(self):
        return PromptTemplate.from_template(self.system_prompt + "\n\nUser: {human_input}\nPlanner:")

    def generate_response(self, user_input: str) -> str:
        prompt = self.get_prompt().format(human_input=user_input)
        response = self.llm.invoke(prompt)
        return response.content

planner_agent = PlannerAgent()
