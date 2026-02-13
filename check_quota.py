"""Check if Gemini API quota is available"""
import os
from dotenv import load_dotenv
load_dotenv("backend/.env")

from google import genai
import time

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("🧪 Testing Gemini API quota...")
print("="*60)

# Test with 6 quick requests to see quota limit
for i in range(6):
    try:
        start = time.time()
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=[f"Say the number {i+1}"]
        )
        elapsed = time.time() - start
        print(f"✅ Request {i+1}: Success ({elapsed:.2f}s) - Response: {response.text.strip()}")
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            print(f"❌ Request {i+1}: QUOTA EXCEEDED")
            print(f"   Free tier limit: 5 requests per minute")
            if "retry" in error_str.lower():
                import re
                retry_match = re.search(r'retry.*?(\d+)s', error_str, re.IGNORECASE)
                if retry_match:
                    print(f"   Retry after: {retry_match.group(1)} seconds")
            break
        else:
            print(f"❌ Request {i+1}: {error_str[:100]}")
            break
    time.sleep(0.5)

print("\n" + "="*60)
print("📊 VERDICT:")
print("   - Free tier: 5 requests/minute")
print("   - CAPTCHA needs: 9-16 requests (for 9-16 tiles)")
print("   - Result: ❌ NOT EFFICIENT - Will always hit quota")
print("\n💡 RECOMMENDATION: Switch to Claude (unlimited with your paid key)")
