import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("--- GENERATION MODELS ---")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"{m.name} ({m.display_name})")

print("\n--- EMBEDDING MODELS ---")
for m in genai.list_models():
    if 'embedContent' in m.supported_generation_methods:
        print(f"{m.name} ({m.display_name})")
