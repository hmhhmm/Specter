import os
import asyncio
import base64
from dotenv import load_dotenv
from google import genai

# Load environment variables from backend/.env
load_dotenv(os.path.join("backend", ".env"))

async def test_text():
    print("--- Test 1: Simple Text ---")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: No GEMINI_API_KEY found in backend/.env")
        return

    client = genai.Client(api_key=api_key)
    model_id = "gemini-2.0-flash"
    
    try:
        print(f"Calling {model_id} with text: 'Hello, are you online?'...")
        response = client.models.generate_content(
            model=model_id,
            contents=["Hello, are you online?"]
        )
        print(f"Success! Response: {response.text}")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

async def test_multimodal():
    print("\n--- Test 2: Multimodal (Image) ---")
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    model_id = "gemini-2.0-flash"

    # Create a tiny 1x1 transparent PNG as a test
    tiny_png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==")
    
    try:
        from google.genai import types
        print(f"Calling {model_id} with a tiny test image...")
        response = client.models.generate_content(
            model=model_id,
            contents=[
                "What is in this image?",
                types.Part.from_bytes(data=tiny_png, mime_type="image/png")
            ]
        )
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    success = asyncio.run(test_text())
    if success:
        asyncio.run(test_multimodal())
