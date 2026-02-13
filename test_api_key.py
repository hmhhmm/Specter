"""Quick test to verify Gemini API key works"""
import os
import sys

# Load environment
from dotenv import load_dotenv
load_dotenv("backend/.env")

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key found: {api_key[:30]}..." if api_key else "❌ No API key found")

if not api_key:
    print("\n❌ GOOGLE_API_KEY not set in backend/.env")
    sys.exit(1)

# Test NEW google-genai API
try:
    from google import genai
    from google.genai import types
    print("✅ google-genai package imported")
    
    # Initialize client
    client = genai.Client(api_key=api_key)
    print("✅ Gemini client initialized")
    
    # Test simple text with different models
    test_models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro", 
        "gemini-2.0-flash-exp",
        "gemini-pro"
    ]
    
    for model in test_models:
        try:
            print(f"\n🧪 Testing {model}...")
            response = client.models.generate_content(
                model=model,
                contents=["What is 2+2? Reply with just the number."]
            )
            result = response.text.strip()
            print(f"   ✅ {model} WORKS! Response: '{result}'")
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                print(f"   ❌ {model} - Model not found (404)")
            elif "403" in error_msg or "API_KEY_INVALID" in error_msg:
                print(f"   ❌ {model} - API KEY INVALID!")
                print(f"      Error: {error_msg[:100]}")
            else:
                print(f"   ❌ {model} - Error: {error_msg[:100]}")
    
    print("\n" + "="*60)
    print("Testing with an actual image from screenshots...")
    
    import glob
    screenshots = glob.glob("screenshots/tile_*.png")
    if screenshots:
        test_img = screenshots[0]
        print(f"Using: {test_img}")
        
        with open(test_img, 'rb') as f:
            img_bytes = f.read()
        
        # Test image with working model
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type='image/png'),
                    "Describe what you see in 5 words."
                ]
            )
            print(f"\n✅ Image analysis works!")
            print(f"   Response: {response.text.strip()}")
        except Exception as e:
            print(f"\n❌ Image analysis failed: {e}")
    else:
        print("No screenshots found to test")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
