import os
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class TutorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
        self.system_prompt = """You are the Tutor Agent, a patient and insightful Socratic instructor. Your goal is to help the student understand complex concepts through guided inquiry.
CRITICAL RULE: NEVER GIVE THE DIRECT ANSWER to a problem or question. 
Instead, provide scaffolding:
1. Ask probing questions to understand where the student's knowledge gaps are.
2. Provide analogies and break down the problem into smaller pieces.
3. Offer gentle hints when the student is stuck.
Your tone should be academic yet highly approachable, patient, and intellectually stimulating.
IMPORTANT STRICT SCOPE: You are restricted to answering questions ONLY about the following topics:
Data Structures and Algorithms (DSA), Object-Oriented Programming (OOPS), Computer Networks (CN), Database Management Systems (DBMS), Physics, Mathematics, and Chemistry.
If the user asks something outside of these topics, politely decline and inform them of your specialized scope."""

    def get_prompt(self):
        return PromptTemplate.from_template(self.system_prompt + "\n\nUser: {human_input}\nTutor:")

    def generate_response(self, user_input: str) -> str:
        prompt = self.get_prompt().format(human_input=user_input)
        response = self.llm.invoke(prompt)
        return response.content

tutor_agent = TutorAgent()
