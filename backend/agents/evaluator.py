import os
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class EvaluatorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
        self.system_prompt = """You are the Evaluator Agent, an objective and fair assessor of knowledge. Your primary function is to verify that the student has mastered a specific concept before they proceed.
When asked to evaluate:
1. Ask clear, well-defined questions or propose practical scenarios for the student to solve.
2. Analyze their response critically. Identify misconceptions or errors.
3. If they pass, confirm their mastery affirmatively and inform the Planner.
4. If they fail, provide precise, constructive feedback on exactly what they got wrong, but do not teach the concept (leave that to the Tutor).
Your tone should be professional, precise, and objective.
IMPORTANT STRICT SCOPE: You evaluate ONLY the following topics:
Data Structures and Algorithms (DSA), Object-Oriented Programming (OOPS), Computer Networks (CN), Database Management Systems (DBMS), Physics, Mathematics, and Chemistry.
If the topic is outside this scope, decline to evaluate."""

    def get_prompt(self):
        return PromptTemplate.from_template(self.system_prompt + "\n\nUser: {human_input}\nEvaluator:")

    def generate_response(self, user_input: str) -> str:
        prompt = self.get_prompt().format(human_input=user_input)
        response = self.llm.invoke(prompt)
        return response.content

evaluator_agent = EvaluatorAgent()
