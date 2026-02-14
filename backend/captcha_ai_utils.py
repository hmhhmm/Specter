""""
AI utility functions for CAPTCHA solving.
Adapted from: https://github.com/aydinnyunus/ai-captcha-bypass

Supports multiple AI providers (Claude, OpenAI GPT-4o, Google Gemini) with
CAPTCHA-type-specific prompts optimized for each challenge type.
"""

import base64
import os
import json
import re
from typing import Optional, Dict, Any

# Initialize Gemini client at module level (NEW API)
gemini_client = None
try:
    from google import genai
    from google.genai import types
    if os.getenv("GOOGLE_API_KEY"):
        gemini_client = genai.Client()
except ImportError:
    pass  # Gemini not available


# ──────────────────────────────────────────────────────────────────
# Provider: Claude (default — uses Specter's existing client)
# ──────────────────────────────────────────────────────────────────
async def solve_with_claude(client, image_b64: str, captcha_type: str, prompt_context: str = "") -> Dict[str, Any]:
    """
    Uses Specter's existing Anthropic Claude client.
    
    Args:
        client: The anthropic.AsyncAnthropic client from main.py
        image_b64: Base64-encoded screenshot of the CAPTCHA
        captcha_type: One of "text", "complicated_text", "grid", "recaptcha_v2", "puzzle", "tile_check"
        prompt_context: Additional context (e.g., "Select all images with traffic lights")
    
    Returns:
        {"solution": str or list, "confidence": float, "target_object": str or None}
    """
    
    # Build CAPTCHA-type-specific prompt
    if captcha_type in ("text", "complicated_text"):
        system_prompt = """You are a CAPTCHA text reader. Look at the image and read the distorted/warped text.
Reply with ONLY the text characters you see, nothing else.
- Ignore background noise, lines, and color variations
- Pay attention to character case (uppercase/lowercase)
- Common confusions: 0/O, 1/l/I, 5/S, 8/B — look carefully at stroke shapes

Return your response as JSON: {"solution": "<text>", "confidence": <0.0-1.0>}"""
        user_prompt = "Read the CAPTCHA text in this image."
    
    elif captcha_type in ("grid", "recaptcha_v2"):
        # Extract grid size from context if available
        grid_size = "3x3"  # Default
        if "4x4" in prompt_context or "16 tiles" in prompt_context:
            grid_size = "4x4"
        
        rows, cols = (4, 4) if grid_size == "4x4" else (3, 3)
        total_tiles = rows * cols
        
        # Build grid layout visualization
        grid_layout = "\n".join([
            " ".join([f"[{i*cols + j + 1}]" for j in range(cols)])
            for i in range(rows)
        ])
        
        system_prompt = f"""You are analyzing a reCAPTCHA image grid challenge.
The instruction says: '{prompt_context}'

First, identify what object you need to find (e.g., 'traffic lights', 'bicycles', 'crosswalks').

The grid is {rows}x{cols} ({total_tiles} tiles), numbered left-to-right, top-to-bottom:
{grid_layout}

Analyze each tile carefully. Return a JSON object:
{{
  "target_object": "<what the instruction asks to select>",
  "selected_tiles": [<list of tile numbers that contain the target>],
  "confidence": <0.0-1.0>
}}

IMPORTANT: Only return the JSON object, no other text.
Be conservative — only select tiles where you are fairly confident the object appears."""
        user_prompt = "Analyze this CAPTCHA grid and select the correct tiles."
    
    elif captcha_type == "puzzle":
        system_prompt = """You are analyzing a slider puzzle CAPTCHA.
The image shows a background with a missing puzzle piece slot (usually a darker or outlined area).
There is a puzzle piece on the left side that needs to be dragged to the slot.

Identify the X-coordinate (horizontal position) of the center of the puzzle slot
as a percentage of the total image width (0-100).

Return ONLY a JSON object:
{"x_percent": <number>, "confidence": <0.0-1.0>}

Do not include any other text."""
        user_prompt = "Find the puzzle slot position."
    
    # ── FIX #1: Added tile_check type — was missing, fell through to generic "Analyze this CAPTCHA" ──
    elif captcha_type == "tile_check":
        system_prompt = f"""You are checking a single tile from a reCAPTCHA grid challenge.
Determine if this tile image contains: '{prompt_context}'

Rules:
- Even a PARTIAL appearance counts (e.g., part of a traffic light at the edge)
- Look carefully at the ENTIRE tile including edges and corners
- If you can see any recognizable part of the object, answer true

Respond with ONLY 'true' or 'false'. Nothing else."""
        user_prompt = f"Does this tile contain '{prompt_context}'?"
    # ── END FIX #1 ──
    
    else:
        # Fallback for unknown types
        system_prompt = "Analyze this CAPTCHA image and describe what you see."
        user_prompt = "What CAPTCHA challenge is shown?"
    
    try:
        # Use faster Haiku model for tile_check (just needs "true"/"false"), Sonnet for complex tasks
        max_tokens = 10 if captcha_type == "tile_check" else 1024
        model = "claude-3-5-haiku-20241022" if captcha_type == "tile_check" else "claude-sonnet-4-20250514"
        
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_b64
                        }
                    },
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }]
        )
        
        response_text = response.content[0].text.strip()
        
        # ── FIX #1 continued: Handle tile_check response before JSON parsing ──
        if captcha_type == "tile_check":
            answer = response_text.lower()
            contains = "true" in answer
            return {
                "solution": "true" if contains else "false",
                "confidence": 0.85 if contains else 0.8,
                "target_object": prompt_context
            }
        # ── END FIX #1 ──
        
        # Try to parse JSON response
        try:
            result = json.loads(response_text)
            # Normalize result format
            if captcha_type in ("text", "complicated_text"):
                return {
                    "solution": result.get("solution", response_text),
                    "confidence": result.get("confidence", 0.8),
                    "target_object": None
                }
            elif captcha_type in ("grid", "recaptcha_v2"):
                return {
                    "solution": result.get("selected_tiles", []),
                    "confidence": result.get("confidence", 0.7),
                    "target_object": result.get("target_object", "")
                }
            elif captcha_type == "puzzle":
                return {
                    "solution": result.get("x_percent", 50),
                    "confidence": result.get("confidence", 0.7),
                    "target_object": None
                }
        except json.JSONDecodeError:
            # If not JSON, treat as raw text response
            return {
                "solution": response_text,
                "confidence": 0.6,
                "target_object": None
            }
    
    except Exception as e:
        return {
            "solution": None,
            "confidence": 0.0,
            "target_object": None,
            "error": str(e)
        }


# ──────────────────────────────────────────────────────────────────
# Provider: OpenAI GPT-4o (optional secondary provider)
# ──────────────────────────────────────────────────────────────────
async def solve_with_openai(image_b64: str, captcha_type: str, prompt_context: str = "", model: str = "gpt-4o") -> Dict[str, Any]:
    """
    Uses OpenAI API directly (requires OPENAI_API_KEY in .env).
    Same prompts as Claude but sent via OpenAI's vision API.
    """
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "solution": None,
            "confidence": 0.0,
            "target_object": None,
            "error": "OPENAI_API_KEY not set in .env"
        }
    
    try:
        # Lazy import
        import openai
        client = openai.AsyncOpenAI(api_key=api_key)
        
        # Build prompt based on CAPTCHA type (same as Claude)
        if captcha_type in ("text", "complicated_text"):
            prompt = """Read the distorted text in this CAPTCHA image. Return JSON: {"solution": "<text>", "confidence": <0.0-1.0>}
Ignore noise, pay attention to case, watch for 0/O, 1/l/I, 5/S, 8/B confusions."""
        
        elif captcha_type in ("grid", "recaptcha_v2"):
            rows, cols = (4, 4) if "4x4" in prompt_context or "16 tiles" in prompt_context else (3, 3)
            total_tiles = rows * cols
            grid_layout = "\n".join([
                " ".join([f"[{i*cols + j + 1}]" for j in range(cols)])
                for i in range(rows)
            ])
            
            prompt = f"""This is a reCAPTCHA grid: {prompt_context}

Grid layout ({rows}x{cols}, {total_tiles} tiles):
{grid_layout}

Return JSON: {{"target_object": "<object to find>", "selected_tiles": [<tile numbers>], "confidence": <0.0-1.0>}}
Only select tiles where the target object clearly appears. Be conservative."""
        
        elif captcha_type == "puzzle":
            prompt = """Find the puzzle slot position. The image shows a slider puzzle with a missing slot.
Return JSON: {"x_percent": <horizontal position of slot center as % of image width>, "confidence": <0.0-1.0>}"""
        
        # ── FIX #2: Added tile_check type for OpenAI — was missing ──
        elif captcha_type == "tile_check":
            prompt = f"Does this image clearly contain a '{prompt_context}' or a recognizable part of a '{prompt_context}'? Respond only with 'true' if you are certain. If you are unsure or cannot tell confidently, respond only with 'false'."
        # ── END FIX #2 ──
        
        else:
            prompt = "Analyze this CAPTCHA and describe what you see."
        
        # Create data URI for image
        data_uri = f"data:image/png;base64,{image_b64}"
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_uri}}
                    ]
                }
            ],
            # ── FIX #2 continued: Lower tokens + temperature=0 for tile_check ──
            temperature=0 if captcha_type == "tile_check" else 1,
            max_tokens=10 if captcha_type == "tile_check" else 512
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # ── FIX #2 continued: Handle tile_check response ──
        if captcha_type == "tile_check":
            contains = "true" in response_text.lower()
            return {
                "solution": "true" if contains else "false",
                "confidence": 0.85 if contains else 0.8,
                "target_object": prompt_context
            }
        # ── END FIX #2 ──
        
        # Parse JSON
        try:
            result = json.loads(response_text)
            if captcha_type in ("text", "complicated_text"):
                return {
                    "solution": result.get("solution", response_text),
                    "confidence": result.get("confidence", 0.8),
                    "target_object": None
                }
            elif captcha_type in ("grid", "recaptcha_v2"):
                return {
                    "solution": result.get("selected_tiles", []),
                    "confidence": result.get("confidence", 0.7),
                    "target_object": result.get("target_object", "")
                }
            elif captcha_type == "puzzle":
                return {
                    "solution": result.get("x_percent", 50),
                    "confidence": result.get("confidence", 0.7),
                    "target_object": None
                }
        except json.JSONDecodeError:
            return {
                "solution": response_text,
                "confidence": 0.6,
                "target_object": None
            }
    
    except ImportError:
        return {
            "solution": None,
            "confidence": 0.0,
            "target_object": None,
            "error": "openai package not installed (pip install openai)"
        }
    except Exception as e:
        return {
            "solution": None,
            "confidence": 0.0,
            "target_object": None,
            "error": f"OpenAI API error: {str(e)}"
        }


# ──────────────────────────────────────────────────────────────────
# Provider: Google Gemini (optional secondary provider)
# ── FIX #3: Now uses NEW google.genai API consistently ──
# ── WAS: importing OLD google.generativeai inside this function ──
# ── which CONFLICTS with module-level NEW google.genai client ──
# ──────────────────────────────────────────────────────────────────
async def solve_with_gemini(image_b64: str, captcha_type: str, prompt_context: str = "", model: str = "models/gemini-2.5-flash") -> Dict[str, Any]:
    """
    Uses Google Gemini API (requires GOOGLE_API_KEY in .env).
    FIX #3: Now uses NEW google.genai SDK consistently (was mixing old google.generativeai with new google.genai).
    """
    
    # ── FIX #3: Check gemini_client instead of raw api_key ──
    if not gemini_client:
        return {
            "solution": None,
            "confidence": 0.0,
            "target_object": None,
            "error": "Gemini not available (GOOGLE_API_KEY not set or google-genai not installed)"
        }
    
    try:
        # ── FIX #3: REMOVED old import of google.generativeai ──
        # ── Was: import google.generativeai as genai; genai.configure(api_key=api_key) ──
        # ── Now uses module-level gemini_client (NEW API) ──
        
        # Build prompt (same as Claude/OpenAI)
        if captcha_type in ("text", "complicated_text"):
            prompt = """Read the distorted text in this CAPTCHA. Return JSON: {"solution": "<text>", "confidence": <0.0-1.0>}"""
        
        elif captcha_type in ("grid", "recaptcha_v2"):
            rows, cols = (4, 4) if "4x4" in prompt_context or "16 tiles" in prompt_context else (3, 3)
            grid_layout = "\n".join([
                " ".join([f"[{i*cols + j + 1}]" for j in range(cols)])
                for i in range(rows)
            ])
            
            prompt = f"""reCAPTCHA grid: {prompt_context}

Layout ({rows}x{cols}):
{grid_layout}

Return JSON: {{"target_object": "<object>", "selected_tiles": [<numbers>], "confidence": <0.0-1.0>}}"""
        
        elif captcha_type == "puzzle":
            prompt = """Find puzzle slot X position (% of image width). Return JSON: {"x_percent": <number>, "confidence": <0.0-1.0>}"""
        
        # ── FIX #3: Added tile_check for Gemini ──
        elif captcha_type == "tile_check":
            prompt = f"Does this image clearly contain a '{prompt_context}' or a recognizable part of a '{prompt_context}'? Respond only with 'true' if you are certain. If you are unsure or cannot tell confidently, respond only with 'false'."
        # ── END tile_check ──
        
        else:
            prompt = "Analyze this CAPTCHA."
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_b64)
        
        # ── FIX #3: Use NEW API (gemini_client + types.Part) instead of old genai.GenerativeModel ──
        # ── Was: model_instance = genai.GenerativeModel(model) ──
        # ── Was: response = await model_instance.generate_content_async([...]) ──
        response = gemini_client.models.generate_content(
            model=model,
            contents=[types.Part.from_bytes(data=image_bytes, mime_type='image/png'), prompt]
        )
        # ── END FIX #3 ──
        
        response_text = response.text.strip()
        
        # ── FIX #3: Handle tile_check response ──
        if captcha_type == "tile_check":
            contains = "true" in response_text.lower()
            return {
                "solution": "true" if contains else "false",
                "confidence": 0.85 if contains else 0.8,
                "target_object": prompt_context
            }
        # ── END tile_check ──
        
        # Parse JSON
        try:
            result = json.loads(response_text)
            if captcha_type in ("text", "complicated_text"):
                return {
                    "solution": result.get("solution", response_text),
                    "confidence": result.get("confidence", 0.8),
                    "target_object": None
                }
            elif captcha_type in ("grid", "recaptcha_v2"):
                return {
                    "solution": result.get("selected_tiles", []),
                    "confidence": result.get("confidence", 0.7),
                    "target_object": result.get("target_object", "")
                }
            elif captcha_type == "puzzle":
                return {
                    "solution": result.get("x_percent", 50),
                    "confidence": result.get("confidence", 0.7),
                    "target_object": None
                }
        except json.JSONDecodeError:
            return {
                "solution": response_text,
                "confidence": 0.6,
                "target_object": None
            }
    
    # ── FIX #3: Removed separate ImportError for old google.generativeai ──
    except Exception as e:
        return {
            "solution": None,
            "confidence": 0.0,
            "target_object": None,
            "error": f"Gemini API error: {str(e)}"
        }


# ──────────────────────────────────────────────────────────────────
# Audio transcription (for audio CAPTCHA fallback)
# ──────────────────────────────────────────────────────────────────
async def transcribe_audio(audio_bytes: bytes, provider: str = "openai") -> str:
    """
    Transcribes audio CAPTCHA challenge.
    
    OpenAI path (default):
        Uses Whisper API — openai.audio.transcriptions.create()
        Model: "whisper-1"
    
    Returns the transcribed text (digits/letters).
    Requires OPENAI_API_KEY.
    """
    
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in .env")
        
        try:
            import openai
            import io
            
            client = openai.AsyncOpenAI(api_key=api_key)
            
            # Create file-like object from bytes
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "captcha_audio.mp3"
            
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            
            return response.text.strip()
        
        except ImportError:
            raise ImportError("openai package not installed (pip install openai)")
        except Exception as e:
            raise Exception(f"Whisper API error: {str(e)}")
    
    else:
        raise ValueError(f"Unsupported audio transcription provider: {provider}")


# ──────────────────────────────────────────────────────────────────
# Provider router
# ──────────────────────────────────────────────────────────────────
async def solve_captcha_with_ai(
    image_b64: str, 
    captcha_type: str, 
    prompt_context: str = "",
    provider: str = "claude",          # "claude" | "openai" | "gemini"
    claude_client = None,              # Required if provider=="claude"
    model: str = None                  # Override default model
) -> Dict[str, Any]:
    """
    Routes to the appropriate provider.
    
    Default chain (try in order if previous fails):
    1. Claude (Specter's existing client — no extra API key needed)
    2. OpenAI GPT-4o (if OPENAI_API_KEY available)
    3. Gemini (if GOOGLE_API_KEY available)
    
    Now supports all captcha types including tile_check.
    
    Returns: {"solution": ..., "confidence": ..., "provider_used": str, "target_object": str or None}
    """
    
    providers_to_try = []
    
    if provider == "claude":
        providers_to_try = ["claude", "openai", "gemini"]
    elif provider == "openai":
        providers_to_try = ["openai", "claude", "gemini"]
    elif provider == "gemini":
        providers_to_try = ["gemini", "claude", "openai"]
    else:
        providers_to_try = ["claude", "openai", "gemini"]
    
    last_error = None
    
    for prov in providers_to_try:
        try:
            if prov == "claude":
                if not claude_client:
                    continue
                result = await solve_with_claude(claude_client, image_b64, captcha_type, prompt_context)
            elif prov == "openai":
                result = await solve_with_openai(image_b64, captcha_type, prompt_context, model or "gpt-4o")
            elif prov == "gemini":
                # ── FIX #3: Default model uses "models/" prefix for new API ──
                result = await solve_with_gemini(image_b64, captcha_type, prompt_context, model or "models/gemini-2.5-flash")
            else:
                continue
            
            # Check if result is valid
            if result.get("error"):
                last_error = result["error"]
                continue
            
            if result.get("solution") is not None and result.get("confidence", 0) > 0:
                result["provider_used"] = prov
                return result
        
        except Exception as e:
            last_error = str(e)
            continue
    
    # All providers failed
    return {
        "solution": None,
        "confidence": 0.0,
        "target_object": None,
        "provider_used": "none",
        "error": f"All providers failed. Last error: {last_error}"
    }


# ──────────────────────────────────────────────────────────────────
# Tile-by-Tile reCAPTCHA Checker (ai-captcha-bypass method)
# ──────────────────────────────────────────────────────────────────
async def check_tile_contains_object(image_b64: str, object_name: str, provider: str = "gemini", claude_client=None) -> bool:
    """
    Ask AI if a single tile contains the specified object.
    This is the accurate method from ai-captcha-bypass.
    
    Args:
        image_b64: Base64-encoded tile screenshot
        object_name: Object to look for (e.g., "motorcycles", "traffic lights")
        provider: AI provider to use
        claude_client: Claude client if using Claude provider
    
    Returns:
        True if tile contains object, False otherwise
    """
    prompt = f"Does this image clearly contain a '{object_name}' or a recognizable part of a '{object_name}'? Respond only with 'true' if you are certain. If you are unsure or cannot tell confidently, respond only with 'false'."
    
    try:
        if provider == "claude" and claude_client:
            response = await claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_b64}},
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            answer = response.content[0].text.strip().lower()
            return "true" in answer
        
        elif provider == "openai":
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                    ]
                }],
                temperature=0,
                max_tokens=10
            )
            answer = response.choices[0].message.content.strip().lower()
            return "true" in answer
        
        elif provider == "gemini":
            # ── FIX #3: Use NEW API (gemini_client) instead of old google.generativeai ──
            # ── Was: import google.generativeai as genai; genai.configure(...); model = genai.GenerativeModel(...) ──
            # ── Was: from PIL import Image; img = Image.open(...); response = model.generate_content([prompt, img]) ──
            if not gemini_client:
                print("Error: Gemini not available")
                return False
            
            image_data = base64.b64decode(image_b64)
            response = gemini_client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=[types.Part.from_bytes(data=image_data, mime_type='image/png'), prompt]
            )
            answer = response.text.strip().lower()
            return "true" in answer
            # ── END FIX #3 ──
        
        else:
            return False
            
    except Exception as e:
        print(f"Error in tile check: {e}")
        return False


# ──────────────────────────────────────────────────────────────────
# FILE-BASED Functions (ai-captcha-bypass pattern)
# ──────────────────────────────────────────────────────────────────

def ask_if_tile_contains_object_chatgpt(image_path: str, object_name: str, model=None):
    """
    OpenAI GPT-4o vision check for tile (file-based).
    EXACT implementation from: https://github.com/aydinnyunus/ai-captcha-bypass/blob/main/ai_utils.py
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Read image file and convert to base64
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        prompt = f"Does this image clearly contain a '{object_name}' or a recognizable part of a '{object_name}'? Respond only with 'true' if you are certain. If you are unsure or cannot tell confidently, respond only with 'false'."
        model_to_use = model if model else "gpt-4o"
        
        response = client.chat.completions.create(
            model=model_to_use,
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]}
            ],
            temperature=0,
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"Error in OpenAI tile check: {e}")
        return "false"


def ask_if_tile_contains_object_gemini(image_path: str, object_name: str, model=None):
    """
    Google Gemini vision check for tile (file-based).
    EXACT implementation from: https://github.com/aydinnyunus/ai-captcha-bypass/blob/main/ai_utils.py
    """
    if not gemini_client:
        print("Error: Gemini API key not configured or google-genai not installed")
        return "false"
    
    try:
        prompt = f"Does this image clearly contain a '{object_name}' or a recognizable part of a '{object_name}'? Respond only with 'true' if you are certain. If you are unsure or cannot tell confidently, respond only with 'false'."
        
        # Read image file
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        # Use NEW API structure matching ai-captcha-bypass exactly
        # CRITICAL: Model name MUST include "models/" prefix
        # Available: models/gemini-2.5-flash (fast), models/gemini-2.5-pro (accurate)
        model_to_use = model if model else "models/gemini-2.5-flash"
        
        response = gemini_client.models.generate_content(
            model=model_to_use,
            contents=[types.Part.from_bytes(data=image_bytes, mime_type='image/png'), prompt]
        )
        
        return response.text.strip().lower()
    except Exception as e:
        print(f"Error in Gemini tile check: {e}")
        return "false"
