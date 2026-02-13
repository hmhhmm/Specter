"""List all available Gemini models"""
import os
from dotenv import load_dotenv
load_dotenv("backend/.env")

api_key = os.getenv("GOOGLE_API_KEY")

from google import genai

client = genai.Client(api_key=api_key)

print("📋 Available Gemini models:\n")
print("="*80)

try:
    models = client.models.list()
    for model in models:
        print(f"\n✅ {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"   Methods: {model.supported_generation_methods}")
        if hasattr(model, 'description'):
            print(f"   Description: {model.description[:100] if model.description else 'N/A'}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
    import traceback
    traceback.print_exc()
