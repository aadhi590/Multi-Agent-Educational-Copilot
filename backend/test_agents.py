import sys
import os
from dotenv import load_dotenv

# Ensure we load .env
load_dotenv()

sys.path.append(os.getcwd())

from agents.tutor import tutor_agent

try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("CRITICAL: GEMINI_API_KEY not found in environment!")
    else:
        print(f"API Key found (Length: {len(api_key)})")
        
    print(f"Using Model: {tutor_agent.llm.model}")
    print("Sending request to Gemini...")
    response = tutor_agent.generate_response("What is a Linked List?")
    print("-" * 20)
    print(f"Tutor Response: {response}")
    print("-" * 20)
except Exception as e:
    print(f"Caught Exception: {type(e).__name__}")
    print(f"Details: {e}")
