import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load the API key from your .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env file.")
else:
    # 2. Configure the library
    genai.configure(api_key=api_key)
    
    print(f"✅ API Key loaded: {api_key[:4]}...{api_key[-4:]}")
    print("-" * 30)
    print("Available Gemini Models for Content Generation:")
    
    try:
        # 3. List all models and filter for 'generateContent' support
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f" - {model.name}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")