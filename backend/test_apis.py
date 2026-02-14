import os
import asyncio
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

async def test_claude():
    print("\n--- Testing Claude (Anthropic) ---")
    api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key or "your_" in api_key:
        print("SKIP: Claude API Key not set.")
        return

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'Claude is online'"}]
        )
        print(f"SUCCESS: {response.content[0].text}")
    except Exception as e:
        print(f"FAILED: {e}")

async def test_nvidia():
    print("\n--- Testing Llama 3 (NVIDIA) ---")
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key or "your_" in api_key:
        print("SKIP: NVIDIA API Key not set.")
        return

    try:
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        payload = {
            "model": "meta/llama-3.2-11b-vision-instruct",
            "messages": [{"role": "user", "content": "Say 'NVIDIA is online'"}],
            "max_tokens": 10
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"SUCCESS: {response.json()['choices'][0]['message']['content']}")
        else:
            print(f"FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"FAILED: {e}")

async def test_gemini():
    print("\n--- Testing Gemini 2 (Google) ---")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or "your_" in api_key:
        print("SKIP: Gemini API Key not set.")
        return

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say 'Gemini is online'"
        )
        print(f"SUCCESS: {response.text}")
    except ImportError:
        print("FAILED: google-genai package not installed. Run: pip install google-genai")
    except Exception as e:
        print(f"FAILED: {e}")

async def main():
    print("Starting API Connectivity Tests...")
    await test_claude()
    await test_nvidia()
    await test_gemini()
    print("\nTests complete.")

if __name__ == "__main__":
    asyncio.run(main())
