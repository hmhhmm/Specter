"""
Quick test to verify NEW google-genai API works
Tests both gemini-2.0-flash-exp and gemini-2.5-pro models
"""
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

# Test NEW API
try:
    from google import genai
    from google.genai import types
    
    print("✓ google-genai package imported successfully")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("✗ GOOGLE_API_KEY not found in .env")
        exit(1)
    
    print(f"✓ API key found: {api_key[:20]}...")
    
    # Initialize client
    client = genai.Client(api_key=api_key)
    print("✓ Gemini client initialized")
    
    # Test simple text prompt with different models
    test_models = ["gemini-2.0-flash-exp", "gemini-2.5-pro", "gemini-1.5-flash"]
    
    for model_name in test_models:
        print(f"\n🧪 Testing {model_name}...")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=["What is 2+2? Answer with just the number."]
            )
            print(f"   ✓ {model_name} works! Response: {response.text.strip()}")
        except Exception as e:
            print(f"   ✗ {model_name} failed: {e}")
    
    # Test with image (if there's a screenshot)
    import glob
    screenshots = glob.glob("screenshots/tile_*.png")
    if screenshots:
        test_image = screenshots[0]
        print(f"\n🖼️  Testing image analysis with {test_image}...")
        
        with open(test_image, 'rb') as f:
            image_bytes = f.read()
        
        for model_name in ["gemini-2.0-flash-exp", "gemini-2.5-pro"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type='image/png'),
                        "Describe what you see in this image in one sentence."
                    ]
                )
                print(f"   ✓ {model_name} image test: {response.text.strip()[:80]}...")
            except Exception as e:
                print(f"   ✗ {model_name} image test failed: {e}")
    
    print("\n✅ All tests complete!")
    
except ImportError as e:
    print(f"✗ Failed to import google-genai: {e}")
    print("Run: pip install google-genai")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
