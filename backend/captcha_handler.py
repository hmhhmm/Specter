"""
CAPTCHA detection and solving module.
Adapted from: https://github.com/aydinnyunus/ai-captcha-bypass

Original uses Selenium WebDriver — ported to Playwright (async).
Original uses OpenAI/Gemini directly — routed through captcha_ai_utils.py.
"""

import asyncio
import time
import random
import json
import re
import base64
from typing import Optional, Dict, Any
from playwright.async_api import Page, ElementHandle

from backend.captcha_ai_utils import solve_captcha_with_ai, transcribe_audio


class CaptchaDetector:
    """Detects CAPTCHA presence from DOM elements + visual analysis."""
    
    # Known CAPTCHA DOM signatures (adapted from ai-captcha-bypass's navigation targets)
    CAPTCHA_SIGNATURES = {
        "recaptcha_v2": [
            'iframe[src*="recaptcha"]',
            'iframe[src*="google.com/recaptcha"]',
            'div.g-recaptcha',
            '#g-recaptcha',
            '[data-sitekey]',
        ],
        "recaptcha_v3": [
            'input[name="g-recaptcha-response"]',
            '.grecaptcha-badge',
        ],
        "hcaptcha": [
            'iframe[src*="hcaptcha"]',
            'div.h-captcha',
            '[data-hcaptcha-sitekey]',
        ],
        "cloudflare_turnstile": [
            'iframe[src*="challenges.cloudflare.com"]',
            'div.cf-turnstile',
            '#cf-turnstile',
            '.cf-challenge',
        ],
        "text_captcha": [
            'img[id*="captcha" i]',
            'img[class*="captcha" i]',
            'img[src*="captcha" i]',
            'img[alt*="captcha" i]',
            '.mtcap-noborder.mtcap-inputtext',
        ],
        "puzzle_captcha": [
            'div[class*="slider"]',
            'div[class*="puzzle"]',
            'canvas[class*="captcha"]',
            '.geetest_slider',
        ],
    }
    
    async def detect(self, page: Page, elements_json: str, screenshot_b64: str, claude_client=None) -> Dict[str, Any]:
        """
        Returns:
            {
                "has_captcha": bool,
                "captcha_type": str,
                "captcha_selector": str,
                "confidence": float,
                "instruction_text": str
            }
        """
        result = {"has_captcha": False, "captcha_type": "none", "captcha_selector": None, "confidence": 0.0, "instruction_text": ""}
        
        # Phase 1: DOM signature scan
        for captcha_type, selectors in self.CAPTCHA_SIGNATURES.items():
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible or captcha_type in ("recaptcha_v3",):
                            result.update({
                                "has_captcha": True,
                                "captcha_type": captcha_type,
                                "captcha_selector": selector,
                                "confidence": 0.9 if is_visible else 0.6,
                            })
                            
                            # Extract instruction text for grid CAPTCHAs
                            if captcha_type in ("recaptcha_v2", "hcaptcha"):
                                result["instruction_text"] = await self._extract_grid_instruction(page, captcha_type)
                            
                            return result
                except Exception:
                    continue
        
        # Phase 2: Visual fallback
        if claude_client and screenshot_b64:
            visual_result = await self._visual_detection(screenshot_b64, claude_client)
            if visual_result.get("has_captcha"):
                result.update(visual_result)
        
        return result
    
    async def _extract_grid_instruction(self, page: Page, captcha_type: str) -> str:
        """Extract CAPTCHA challenge instruction text from iframe."""
        try:
            if captcha_type == "recaptcha_v2":
                frames = page.frames
                for frame in frames:
                    if "google.com/recaptcha" in frame.url and "bframe" in frame.url:
                        desc_selectors = ['.rc-imageselect-desc-no-canonical', '.rc-imageselect-desc', '.rc-imageselect-instructions']
                        for sel in desc_selectors:
                            try:
                                desc_elem = await frame.query_selector(sel)
                                if desc_elem:
                                    return (await desc_elem.inner_text()).strip()
                            except:
                                continue
            
            elif captcha_type == "hcaptcha":
                for frame in page.frames:
                    if "hcaptcha" in frame.url:
                        try:
                            prompt_elem = await frame.query_selector('.prompt-text')
                            if prompt_elem:
                                return (await prompt_elem.inner_text()).strip()
                        except:
                            continue
        except Exception:
            pass
        
        return ""
    
    async def _visual_detection(self, screenshot_b64: str, claude_client) -> Dict[str, Any]:
        """Use Claude Vision to detect CAPTCHA when DOM scan fails."""
        try:
            response = await claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": screenshot_b64}},
                        {"type": "text", "text": """Look at this screenshot. Is there any CAPTCHA challenge visible?

Types: reCAPTCHA, hCaptcha, text CAPTCHA, slider puzzle, Cloudflare, math CAPTCHA

Return JSON ONLY: {"has_captcha": bool, "captcha_type": "recaptcha_v2|hcaptcha|text|puzzle|cloudflare|none", "confidence": <0.0-1.0>}"""}
                    ]
                }]
            )
            
            result = json.loads(response.content[0].text.strip())
            return {
                "has_captcha": result.get("has_captcha", False),
                "captcha_type": result.get("captcha_type", "none"),
                "captcha_selector": None,
                "confidence": result.get("confidence", 0.5),
                "instruction_text": ""
            }
        except Exception:
            return {"has_captcha": False, "captcha_type": "none", "captcha_selector": None, "confidence": 0.0, "instruction_text": ""}


class CaptchaSolver:
    """
    Solves CAPTCHAs using multi-provider AI + audio fallback.
    Adapted from ai-captcha-bypass architecture.
    """
    
    def __init__(self, page: Page, claude_client=None, ai_provider: str = "claude"):
        self.page = page
        self.claude_client = claude_client
        self.ai_provider = ai_provider
        self.max_attempts = 5
        self.previously_clicked_tiles = set()
    
    async def solve(self, captcha_type: str, captcha_selector: str, instruction_text: str = "") -> Dict[str, Any]:
        """
        Returns: {"solved": bool, "method": str, "attempts": int, "time_taken_ms": int, "error": str or None}
        """
        start_ms = int(time.time() * 1000)
        result = {"solved": False, "method": "unknown", "attempts": 0, "error": None}
        
        try:
            if captcha_type in ("recaptcha_v2", "hcaptcha"):
                result = await self._solve_recaptcha_v2(captcha_selector, instruction_text)
            elif captcha_type in ("text_captcha", "complicated_text"):
                result = await self._solve_text_captcha(captcha_selector)
            elif captcha_type == "puzzle_captcha":
                result = await self._solve_puzzle_captcha(captcha_selector)
            elif captcha_type == "cloudflare_turnstile":
                result = await self._solve_turnstile(captcha_selector)
            elif captcha_type == "recaptcha_v3":
                result = {"solved": True, "method": "invisible_v3", "attempts": 0}
            else:
                result = {"solved": False, "method": "unknown", "error": f"Unsupported: {captcha_type}", "attempts": 0}
        except Exception as e:
            result = {"solved": False, "method": "error", "error": str(e), "attempts": 0}
        
        result["time_taken_ms"] = int(time.time() * 1000) - start_ms
        return result
    
    async def _solve_recaptcha_v2(self, selector: str, instruction_text: str = "") -> Dict[str, Any]:
        """
        reCAPTCHA v2: checkbox → grid challenge (tile-by-tile) → audio fallback
        Uses ai-captcha-bypass method: screenshot each tile and ask AI individually
        """
        attempts = 0
        
        # Step 1: Click checkbox
        try:
            checkbox_frame = None
            for frame in self.page.frames:
                if "google.com/recaptcha" in frame.url and "anchor" in frame.url:
                    checkbox_frame = frame
                    break
            
            if checkbox_frame:
                checkbox = await checkbox_frame.query_selector('.recaptcha-checkbox-border')
                if checkbox:
                    await self._human_click(checkbox, 200, 500)
                    await asyncio.sleep(random.uniform(2, 3))
                    attempts += 1
                    
                    if await self._check_success("recaptcha_v2"):
                        return {"solved": True, "method": "checkbox_click", "attempts": attempts}
        except Exception:
            pass
        
        # Step 2: Grid challenge (tile-by-tile approach from ai-captcha-bypass)
        MAX_CHALLENGE_ATTEMPTS = 5
        clicked_tile_indices = set()
        last_object_name = ""
        num_last_clicks = 0
        
        for challenge_attempt in range(MAX_CHALLENGE_ATTEMPTS):
            try:
                challenge_frame = None
                for frame in self.page.frames:
                    if "google.com/recaptcha" in frame.url and "bframe" in frame.url:
                        challenge_frame = frame
                        break
                
                if not challenge_frame:
                    print("No challenge frame found, assuming solved")
                    break
                
                # Get instruction and extract object name
                instruction_elem = await challenge_frame.query_selector('.rc-imageselect-instructions')
                if not instruction_elem:
                    break
                
                instruction_text = await instruction_elem.inner_text()
                
                # Extract object name from instruction (e.g., "Select all images with motorcycles" → "motorcycles")
                import re
                match = re.search(r'with\s+(\w+)', instruction_text.lower())
                if match:
                    object_name = match.group(1)
                elif 'skip' in instruction_text.lower():
                    object_name = 'skip'
                else:
                    object_name = instruction_text.split()[-1] if instruction_text else ""
                
                print(f"AI identified target object: '{object_name}'")
                
                # Check if new challenge
                is_new_object = object_name.lower() != last_object_name.lower()
                if is_new_object:
                    print(f"New challenge object detected. Resetting clicked tiles.")
                    clicked_tile_indices = set()
                    last_object_name = object_name
                elif num_last_clicks >= 3:
                    print("Previously clicked 3+ tiles, assuming new challenge. Resetting.")
                    clicked_tile_indices = set()
                else:
                    print("Same challenge, will not re-click already selected tiles.")
                
                # Get all tiles - use contains selector like ai-captcha-bypass
                table = await challenge_frame.query_selector('table[class*="rc-imageselect-table"]')
                if not table:
                    print(f"❌ No table found with class containing 'rc-imageselect-table'")
                    break
                
                tiles = await table.query_selector_all('td')
                if not tiles:
                    print(f"❌ No td elements found in table")
                    break
                
                print(f"Found {len(tiles)} tiles to analyze")
                
                # Save tiles to FILES (like ai-captcha-bypass) not base64
                import os
                os.makedirs('screenshots', exist_ok=True)
                
                tile_paths = []
                for i, tile in enumerate(tiles):
                    try:
                        tile_path = f'screenshots/tile_{challenge_attempt + 1}_{i}.png'
                        await tile.screenshot(path=tile_path)
                        tile_paths.append((i, tile_path))
                        print(f"  Tile {i}: Saved to {tile_path}")
                    except Exception as e:
                        print(f"  Tile {i}: Screenshot FAILED - {e}")
                        tile_paths.append((i, None))
                
                # Check tiles using AI (adapted from ai-captcha-bypass)
                print(f"\n🔍 Checking {len(tile_paths)} tiles with {self.ai_provider} for '{object_name}'")
                
                tiles_to_click_this_round = []
                from backend.captcha_ai_utils import ask_if_tile_contains_object_gemini, ask_if_tile_contains_object_chatgpt
                
                for tile_idx, tile_path in tile_paths:
                    if not tile_path:
                        continue
                    
                    try:
                        decision_str = ''
                        if self.ai_provider == 'openai':
                            decision_str = await asyncio.to_thread(
                                ask_if_tile_contains_object_chatgpt, 
                                tile_path, 
                                object_name, 
                                None
                            )
                        else:  # gemini
                            decision_str = await asyncio.to_thread(
                                ask_if_tile_contains_object_gemini, 
                                tile_path, 
                                object_name, 
                                None
                            )
                        
                        print(f"Tile {tile_idx}: Does it contain '{object_name}'? AI says: {decision_str}")
                        
                        if decision_str == 'true':
                            tiles_to_click_this_round.append(tile_idx)
                            print(f"  ✓ Tile {tile_idx} contains '{object_name}'")
                    
                    except Exception as e:
                        print(f"Error checking tile {tile_idx}: {e}")
                        continue
                
                # Determine new tiles to click
                current_attempt_tiles = set(tiles_to_click_this_round)
                new_tiles_to_click = current_attempt_tiles - clicked_tile_indices
                num_last_clicks = len(new_tiles_to_click)

                
                print(f"AI identified tiles: {sorted(list(current_attempt_tiles))}")
                print(f"Already clicked: {sorted(list(clicked_tile_indices))}")
                print(f"Clicking {len(new_tiles_to_click)} new tiles...")
                
                # Click new tiles
                for i in sorted(list(new_tiles_to_click)):
                    try:
                        if await tiles[i].is_visible() and await tiles[i].is_enabled():
                            await self._human_click(tiles[i], 200, 500)
                    except Exception as e:
                        print(f"Could not click tile {i}: {e}")
                
                clicked_tile_indices.update(new_tiles_to_click)
                
                # Click verify button
                try:
                    verify_btn = await challenge_frame.query_selector('#recaptcha-verify-button')
                    if verify_btn:
                        await asyncio.sleep(random.uniform(0.5, 1.0))
                        await verify_btn.click()
                        await asyncio.sleep(1.5)
                        
                        # Check if button is disabled (success)
                        verify_btn_after = await challenge_frame.query_selector('#recaptcha-verify-button')
                        if verify_btn_after:
                            is_disabled = await verify_btn_after.get_attribute("disabled")
                            if is_disabled:
                                print("Verify button disabled, challenge passed!")
                                if await self._check_success("recaptcha_v2"):
                                    return {"solved": True, "method": "tile_by_tile", "attempts": attempts + challenge_attempt + 1}
                except Exception as e:
                    print(f"Verify button interaction failed: {e}")
                    break
                
                attempts += 1
                await asyncio.sleep(2)
            
            except Exception as e:
                print(f"Challenge attempt {challenge_attempt + 1} error: {e}")
                break
        
        # Step 3: Audio fallback
        if grid_attempts >= 3:
            audio_result = await self._solve_audio_captcha()
            if audio_result.get("solved"):
                audio_result["attempts"] = attempts + grid_attempts
                return audio_result
        
        return {"solved": False, "method": "vision_grid", "attempts": attempts + grid_attempts, "error": "Max attempts"}
    
    async def _solve_text_captcha(self, selector: str) -> Dict[str, Any]:
        """Text CAPTCHA: screenshot → AI read → type solution"""
        attempts = 0
        
        while attempts < self.max_attempts:
            try:
                # Find CAPTCHA image
                captcha_img = await self.page.query_selector(selector)
                if not captcha_img:
                    captcha_img = await self.page.query_selector('img[id*="captcha" i], img[class*="captcha" i]')
                
                if not captcha_img:
                    return {"solved": False, "method": "vision_text", "attempts": attempts, "error": "Image not found"}
                
                # Screenshot
                img_bytes = await captcha_img.screenshot()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
                # AI solve
                ai_result = await solve_captcha_with_ai(
                    image_b64=img_b64,
                    captcha_type="text",
                    provider=self.ai_provider,
                    claude_client=self.claude_client
                )
                
                solution = ai_result.get("solution")
                if not solution:
                    attempts += 1
                    continue
                
                # Find input
                input_field = await self.page.query_selector('input[type="text"][id*="captcha" i], input[type="text"][name*="captcha" i], .mtcap-noborder')
                if not input_field:
                    input_field = await self.page.query_selector('input[type="text"]')
                
                if not input_field:
                    return {"solved": False, "method": "vision_text", "attempts": attempts, "error": "Input not found"}
                
                # Type with delays
                await input_field.click()
                await asyncio.sleep(0.3)
                for char in solution:
                    await self.page.keyboard.type(char)
                    await asyncio.sleep(random.uniform(0.05, 0.15))
                
                # Submit
                submit_btn = await self.page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Verify")')
                if submit_btn:
                    await asyncio.sleep(0.5)
                    await submit_btn.click()
                    await asyncio.sleep(2)
                
                # Check success
                error_msg = await self.page.query_selector('.error, .captcha-error, [class*="error"]')
                if not error_msg:
                    return {"solved": True, "method": "vision_text", "attempts": attempts + 1}
                
                attempts += 1
            
            except Exception as e:
                attempts += 1
                if attempts >= self.max_attempts:
                    return {"solved": False, "method": "vision_text", "attempts": attempts, "error": str(e)}
        
        return {"solved": False, "method": "vision_text", "attempts": attempts, "error": "Max attempts"}
    
    async def _solve_puzzle_captcha(self, selector: str) -> Dict[str, Any]:
        """Slider puzzle: AI detects slot → human-like drag"""
        attempts = 0
        
        while attempts < self.max_attempts:
            try:
                # Find puzzle
                puzzle_elem = await self.page.query_selector(selector)
                if not puzzle_elem:
                    puzzle_elem = await self.page.query_selector('.geetest_slider, div[class*="slider"], div[class*="puzzle"]')
                
                if not puzzle_elem:
                    return {"solved": False, "method": "puzzle_slide", "attempts": attempts, "error": "Puzzle not found"}
                
                # Screenshot
                puzzle_bytes = await puzzle_elem.screenshot()
                puzzle_b64 = base64.b64encode(puzzle_bytes).decode('utf-8')
                
                # AI analyze
                ai_result = await solve_captcha_with_ai(
                    image_b64=puzzle_b64,
                    captcha_type="puzzle",
                    provider=self.ai_provider,
                    claude_client=self.claude_client
                )
                
                x_percent = ai_result.get("solution", 50)
                if not isinstance(x_percent, (int, float)):
                    attempts += 1
                    continue
                
                # Get dimensions
                bbox = await puzzle_elem.bounding_box()
                if not bbox:
                    return {"solved": False, "method": "puzzle_slide", "attempts": attempts, "error": "Not visible"}
                
                target_x = bbox['x'] + (bbox['width'] * x_percent / 100)
                
                # Find handle
                handle = await puzzle_elem.query_selector('.slider-handle, .geetest_slider_button, button')
                if not handle:
                    return {"solved": False, "method": "puzzle_slide", "attempts": attempts, "error": "Handle not found"}
                
                handle_bbox = await handle.bounding_box()
                if not handle_bbox:
                    return {"solved": False, "method": "puzzle_slide", "attempts": attempts, "error": "Handle not visible"}
                
                start_x = handle_bbox['x'] + handle_bbox['width'] / 2
                start_y = handle_bbox['y'] + handle_bbox['height'] / 2
                drag_distance = target_x - start_x
                
                # Human-like drag with jitter (key ai-captcha-bypass pattern)
                await self.page.mouse.move(start_x, start_y)
                await self.page.mouse.down()
                await asyncio.sleep(random.uniform(0.1, 0.2))
                
                steps = random.randint(15, 25)
                for i in range(steps):
                    progress = (i + 1) / steps
                    eased_progress = 1 - (1 - progress) ** 2  # Ease-out curve
                    
                    step_x = start_x + (drag_distance * eased_progress)
                    jitter_x = random.uniform(-2, 2)
                    jitter_y = random.uniform(-3, 3)
                    
                    await self.page.mouse.move(step_x + jitter_x, start_y + jitter_y)
                    await asyncio.sleep(random.uniform(0.01, 0.03))
                
                await self.page.mouse.up()
                await asyncio.sleep(2)
                
                if await self._check_success("puzzle"):
                    return {"solved": True, "method": "puzzle_slide", "attempts": attempts + 1}
                
                attempts += 1
            
            except Exception as e:
                attempts += 1
                if attempts >= self.max_attempts:
                    return {"solved": False, "method": "puzzle_slide", "attempts": attempts, "error": str(e)}
        
        return {"solved": False, "method": "puzzle_slide", "attempts": attempts, "error": "Max attempts"}
    
    async def _solve_audio_captcha(self) -> Dict[str, Any]:
        """Audio fallback via OpenAI Whisper transcription"""
        try:
            challenge_frame = None
            for frame in self.page.frames:
                if "google.com/recaptcha" in frame.url and "bframe" in frame.url:
                    challenge_frame = frame
                    break
            
            if not challenge_frame:
                return {"solved": False, "method": "audio_whisper", "error": "Frame not found"}
            
            # Click audio button
            audio_btn = await challenge_frame.query_selector('#recaptcha-audio-button, button[aria-label*="audio"]')
            if not audio_btn:
                return {"solved": False, "method": "audio_whisper", "error": "Audio button not found"}
            
            await audio_btn.click()
            await asyncio.sleep(3)
            
            # Get audio URL
            audio_link = await challenge_frame.query_selector('.rc-audiochallenge-tdownload-link')
            if not audio_link:
                return {"solved": False, "method": "audio_whisper", "error": "Audio link not found"}
            
            audio_url = await audio_link.get_attribute('href')
            if not audio_url:
                return {"solved": False, "method": "audio_whisper", "error": "Audio URL not found"}
            
            # Fetch audio via JS
            audio_bytes_b64 = await self.page.evaluate(f"""
                async () => {{
                    const response = await fetch('{audio_url}');
                    const blob = await response.blob();
                    return new Promise((resolve) => {{
                        const reader = new FileReader();
                        reader.onloadend = () => resolve(reader.result.split(',')[1]);
                        reader.readAsDataURL(blob);
                    }});
                }}
            """)
            
            audio_bytes = base64.b64decode(audio_bytes_b64)
            
            # Transcribe with Whisper
            transcribed_text = await transcribe_audio(audio_bytes, provider="openai")
            
            if not transcribed_text:
                return {"solved": False, "method": "audio_whisper", "error": "Transcription failed"}
            
            # Type response
            audio_input = await challenge_frame.query_selector('#audio-response, input[id*="audio"]')
            if not audio_input:
                return {"solved": False, "method": "audio_whisper", "error": "Input not found"}
            
            await audio_input.click()
            await audio_input.fill(transcribed_text)
            await asyncio.sleep(0.5)
            
            # Verify
            verify_btn = await challenge_frame.query_selector('#recaptcha-verify-button')
            if verify_btn:
                await verify_btn.click()
                await asyncio.sleep(2)
            
            if await self._check_success("recaptcha_v2"):
                return {"solved": True, "method": "audio_whisper"}
            
            return {"solved": False, "method": "audio_whisper", "error": "Transcription didn't solve"}
        
        except Exception as e:
            return {"solved": False, "method": "audio_whisper", "error": str(e)}
    
    async def _solve_turnstile(self, selector: str) -> Dict[str, Any]:
        """Cloudflare Turnstile auto-wait"""
        try:
            turnstile_frame = None
            for _ in range(5):
                for frame in self.page.frames:
                    if "challenges.cloudflare.com" in frame.url or "cf-turnstile" in frame.url:
                        turnstile_frame = frame
                        break
                if turnstile_frame:
                    break
                await asyncio.sleep(1)
            
            if turnstile_frame:
                checkbox = await turnstile_frame.query_selector('input[type="checkbox"], .cf-turnstile-checkbox')
                if checkbox:
                    await self._human_click(checkbox, 200, 500)
            
            # Wait for auto-resolution
            for _ in range(15):
                if await self._check_success("turnstile"):
                    return {"solved": True, "method": "turnstile_wait", "attempts": 1}
                await asyncio.sleep(1)
            
            return {"solved": False, "method": "turnstile_wait", "attempts": 1, "error": "Timeout"}
        
        except Exception as e:
            return {"solved": False, "method": "turnstile_wait", "attempts": 1, "error": str(e)}
    
    async def _human_click(self, element, min_delay_ms: int = 300, max_delay_ms: int = 800):
        """Human-like click with random delay"""
        await asyncio.sleep(random.uniform(min_delay_ms / 1000, max_delay_ms / 1000))
        await element.click()
    
    async def _check_success(self, captcha_type: str) -> bool:
        """Verify CAPTCHA solved successfully"""
        try:
            if captcha_type == "recaptcha_v2":
                for frame in self.page.frames:
                    if "google.com/recaptcha" in frame.url and "anchor" in frame.url:
                        checked = await frame.query_selector('.recaptcha-checkbox-checked, [aria-checked="true"]')
                        if checked:
                            return True
                
                response_elem = await self.page.query_selector('textarea[name="g-recaptcha-response"]')
                if response_elem:
                    value = await response_elem.input_value()
                    if value and len(value) > 20:
                        return True
            
            elif captcha_type == "turnstile":
                response_elem = await self.page.query_selector('input[name*="cf-turnstile-response"]')
                if response_elem:
                    value = await response_elem.input_value()
                    if value and len(value) > 10:
                        return True
            
            elif captcha_type == "puzzle":
                success_elem = await self.page.query_selector('.geetest_success, .puzzle-success, [class*="success"]')
                if success_elem:
                    return True
        
        except Exception:
            pass
        
        return False
