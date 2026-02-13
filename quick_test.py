"""Quick test with correct model name"""
import os
from dotenv import load_dotenv
load_dotenv("backend/.env")

from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Test text
print("🧪 Testing models/gemini-2.5-flash with text...")
response = client.models.generate_content(
    model="models/gemini-2.5-flash",
    contents=["What is 2+2? Reply with just the number."]
)
print(f"✅ Text works: {response.text.strip()}\n")

# Test image
import glob
screenshots = glob.glob("screenshots/tile_*.png")
if screenshots:
    test_img = screenshots[0]
    print(f"🧪 Testing with image: {test_img}")
    
    with open(test_img, 'rb') as f:
        img_bytes = f.read()
    
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=img_bytes, mime_type='image/png'),
            "Does this image contain a bicycle? Reply only 'true' or 'false'."
        ]
    )
    print(f"✅ Image analysis: {response.text.strip()}")
else:
    print("❌ No screenshots found")
