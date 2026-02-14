import os
import asyncio
import base64
import json
import requests
import io
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join("backend", ".env"))

# Clients
_ANTHROPIC_CLIENT = None

def get_anthropic_client():
    global _ANTHROPIC_CLIENT
    if _ANTHROPIC_CLIENT is None:
        api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if api_key and not api_key.startswith("your_"):
            import anthropic
            _ANTHROPIC_CLIENT = anthropic.Anthropic(api_key=api_key)
    return _ANTHROPIC_CLIENT

def _stitch_images_side_by_side(images_b64: List[str]) -> str:
    """
    Stitch multiple base64 images into a single side-by-side image.
    Used for models that only support 1 image per prompt (like NVIDIA Llama).
    """
    try:
        from PIL import Image
        
        images = []
        for img_b64 in images_b64:
            if "," in img_b64:
                img_b64 = img_b64.split(",")[1]
            img_data = base64.b64decode(img_b64)
            images.append(Image.open(io.BytesIO(img_data)))
        
        if not images:
            return ""
            
        # Calculate dimensions
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)
        
        # Create canvas
        new_img = Image.new('RGB', (total_width, max_height))
        
        # Paste images
        x_offset = 0
        for img in images:
            new_img.paste(img, (x_offset, 0))
            x_offset += img.width
            
        # Convert back to base64
        buffered = io.BytesIO()
        new_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Image stitching failed: {e}")
        # Fallback: just return the first image if stitching fails
        return images_b64[0] if images_b64 else ""

async def call_llm_vision(
    system_prompt: str,
    user_prompt: str,
    images_b64: Optional[List[str]] = None,
    max_tokens: int = 1024,
    fallback_to_nvidia: bool = True,
) -> str:
    """
    Call LLM with vision support.
    Prioritizes Claude, falls back to NVIDIA (Llama 3.2 Vision) if configured.
    """

    # 1. Try Claude first
    anthropic_client = get_anthropic_client()
    if anthropic_client:
        try:
            content = []
            if images_b64:
                for img_b64 in images_b64:
                    if "," in img_b64:
                        img_b64 = img_b64.split(",")[1]

                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_b64,
                        },
                    })

            content.append({"type": "text", "text": user_prompt})
            model = "claude-3-5-sonnet-20241022"

            response = await asyncio.to_thread(
                anthropic_client.messages.create,
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": content}],
            )
            return response.content[0].text
        except Exception as e:
            print(f"Claude API failed: {e}")
            if not fallback_to_nvidia:
                raise

    # 2. Try NVIDIA Llama 3.2 Vision fallback
    if fallback_to_nvidia:
        api_key = os.getenv("NVIDIA_API_KEY")
        if api_key:
            try:
                invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
                
                # Handling NVIDIA's 1-image limit
                final_images = []
                final_prompt = user_prompt
                
                if images_b64 and len(images_b64) > 1:
                    print(f"  [NVIDIA Fallback] Stitching {len(images_b64)} images into 1...")
                    stitched_b64 = _stitch_images_side_by_side(images_b64)
                    final_images = [stitched_b64]
                    final_prompt = f"{user_prompt}\n\nNOTE: The image provided is a side-by-side stitch of {len(images_b64)} screenshots (Before action on the left, After action on the right)."
                else:
                    final_images = images_b64 or []

                # Format messages for Llama 3.2 Vision
                content = [{"type": "text", "text": final_prompt}]
                
                for img_b64 in final_images:
                    if not img_b64.startswith("data:"):
                        img_b64 = f"data:image/png;base64,{img_b64}"
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": img_b64}
                    })

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "application/json"
                }

                # Use Llama 3.2 11B Vision for much faster response times (< 10s)
                model_id = "meta/llama-3.2-11b-vision-instruct"

                payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": system_prompt + "\n\nIMPORTANT: You must respond ONLY with a valid JSON object. Do not include any conversational text, markdown formatting (like ```json), or explanations outside the JSON object itself."},
                        {"role": "user", "content": content}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.1, # Even lower for stricter JSON adherence
                    "top_p": 0.7,
                    "stream": False
                }

                response = await asyncio.to_thread(
                    requests.post, invoke_url, headers=headers, json=payload, timeout=60
                )
                
                if response.status_code != 200:
                    raise Exception(f"NVIDIA API Error {response.status_code}: {response.text}")
                
                result = response.json()
                return result['choices'][0]['message']['content']
            except Exception as e:
                print(f"NVIDIA API failed: {e}")
                raise

    raise ValueError("No LLM clients available. Please set CLAUDE_API_KEY or NVIDIA_API_KEY.")

def parse_json_from_llm(text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON from LLM response with robust fallback."""
    if not text:
        return None

    text = text.strip()
    
    # 1. Clean markdown code blocks if present
    if "```" in text:
        # Try to find content between ```json and ``` or just ``` and ```
        import re
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if json_match:
            text = json_match.group(1).strip()
        else:
            # Fallback: just remove the ``` markers
            text = text.replace("```json", "").replace("```", "").strip()

    # 2. Try standard parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 3. Last resort: regex search for anything looking like a JSON object
        import re
        # Find the first { and the last }
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            json_str = match.group()
            try:
                return json.loads(json_str)
            except:
                # Still failed? Try to clean up trailing commas which often break small LLM outputs
                try:
                    cleaned = re.sub(r",\s*([\]}])", r"\1", json_str)
                    return json.loads(cleaned)
                except:
                    pass
        return None
