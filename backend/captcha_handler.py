import asyncio
import time
import random
import json
import re
import os
import base64
from typing import Optional, Dict, Any, List, Tuple
from playwright.async_api import Page, ElementHandle, Frame

from backend.captcha_ai_utils import solve_captcha_with_ai, transcribe_audio


class CaptchaDetector:
    """Detects CAPTCHA presence from DOM elements + visual analysis."""
    
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
        result = {"has_captcha": False, "captcha_type": "none", "captcha_selector": None, "confidence": 0.0, "instruction_text": ""}
        
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
                            if captcha_type in ("recaptcha_v2", "hcaptcha"):
                                result["instruction_text"] = await self._extract_grid_instruction(page, captcha_type)
                            return result
                except Exception:
                    continue
        
        if claude_client and screenshot_b64:
            visual_result = await self._visual_detection(screenshot_b64, claude_client)
            if visual_result.get("has_captcha"):
                result.update(visual_result)
        
        return result
    
    async def _extract_grid_instruction(self, page: Page, captcha_type: str) -> str:
        try:
            if captcha_type == "recaptcha_v2":
                for frame in page.frames:
                    if "google.com/recaptcha" in frame.url and "bframe" in frame.url:
                        for sel in ['.rc-imageselect-desc-no-canonical', '.rc-imageselect-desc', '.rc-imageselect-instructions']:
                            try:
                                elem = await frame.query_selector(sel)
                                if elem:
                                    return (await elem.inner_text()).strip()
                            except:
                                continue
            elif captcha_type == "hcaptcha":
                for frame in page.frames:
                    if "hcaptcha" in frame.url:
                        try:
                            elem = await frame.query_selector('.prompt-text')
                            if elem:
                                return (await elem.inner_text()).strip()
                        except:
                            continue
        except Exception:
            pass
        return ""
    
    async def _visual_detection(self, screenshot_b64: str, claude_client) -> Dict[str, Any]:
        try:
            response = await claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": screenshot_b64}},
                        {"type": "text", "text": """Look at this screenshot. Is there any CAPTCHA challenge visible?
Types: reCAPTCHA, hCaptcha, text CAPTCHA, slider puzzle, Cloudflare, math CAPTCHA.
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
            return {"has_captcha": False}


class CaptchaSolver:
    """
    Solves CAPTCHAs using multi-provider AI + audio fallback.
    Adapted from ai-captcha-bypass architecture.
    """
    
    def __init__(self, page: Page, claude_client=None, ai_provider: str = "claude", tile_screenshot_dir: str = None):
        self.page = page
        self.claude_client = claude_client
        self.ai_provider = ai_provider
        self.max_attempts = 5
        self.previously_clicked_tiles = set()
        self.tile_screenshot_dir = tile_screenshot_dir or 'screenshots'
        os.makedirs(self.tile_screenshot_dir, exist_ok=True)
    
    async def solve(self, captcha_type: str, captcha_selector: str, instruction_text: str = "") -> Dict[str, Any]:
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
    
    # ══════════════════════════════════════════════════════════════════
    # reCAPTCHA v2 — FIXED VERSION
    # ══════════════════════════════════════════════════════════════════
    async def _solve_recaptcha_v2(self, selector: str, instruction_text: str = "") -> Dict[str, Any]:
        attempts = 0
        
        # ── STEP 1: Click checkbox ONLY if challenge grid is NOT already open ──
        # If the planner already clicked the checkbox, a grid may already be showing.
        # Re-clicking would dismiss it and open a NEW challenge (causing stale tile screenshots).
        challenge_already_open = False
        try:
            for frame in self.page.frames:
                if "google.com/recaptcha" in frame.url and "bframe" in frame.url:
                    table = await frame.query_selector('table[class*="rc-imageselect-table"]')
                    if table:
                        tiles_check = await table.query_selector_all('td')
                        if len(tiles_check) >= 9:
                            challenge_already_open = True
                            print("   Challenge grid already open -- skipping checkbox click")
                            break
        except Exception:
            pass
        
        if not challenge_already_open:
            try:
                # Brief pause before clicking "I'm not a robot"
                await asyncio.sleep(random.uniform(0.8, 1.5))
                
                checkbox_frame = None
                for frame in self.page.frames:
                    if "google.com/recaptcha" in frame.url and "anchor" in frame.url:
                        checkbox_frame = frame
                        break
                
                if checkbox_frame:
                    checkbox = await checkbox_frame.query_selector('.recaptcha-checkbox-border')
                    if checkbox:
                        await self._human_click(checkbox, 200, 500)
                        
                        # Wait for Google to decide if challenge is needed
                        await asyncio.sleep(random.uniform(1.5, 2.5))
                        attempts += 1
                        
                        if await self._check_success("recaptcha_v2"):
                            print("   Checkbox click was enough -- no grid challenge needed")
                            return {"solved": True, "method": "checkbox_click", "attempts": attempts}
            except Exception as e:
                print(f"Checkbox click error: {e}")
        
        # ── STEP 2: Wait for challenge grid to FULLY load ──
        # FIX #1: Wait for both the grid DOM AND the tile images inside it
        print("⏳ Waiting for challenge grid to appear and images to load...")
        challenge_frame = None
        grid_ready = False
        
        for wait_round in range(20):  # 20 * 0.5s = 10s max
            await asyncio.sleep(0.5)
            
            for frame in self.page.frames:
                if "google.com/recaptcha" not in frame.url or "bframe" not in frame.url:
                    continue
                
                challenge_frame = frame
                table = await frame.query_selector('table.rc-imageselect-table-33, table.rc-imageselect-table-44, table[class*="rc-imageselect-table"]')
                if not table:
                    continue
                
                tiles = await table.query_selector_all('td')
                if len(tiles) < 9:
                    continue
                
                # FIX #1: Check that tile images have actually loaded (not just DOM placeholders)
                # Each tile has an <img> with a src that gets populated when the image loads
                images_loaded = await self._check_tile_images_loaded(frame, tiles)
                if images_loaded:
                    print(f"✅ Grid visible with {len(tiles)} tiles, images loaded (waited {(wait_round+1)*0.5:.1f}s)")
                    grid_ready = True
                    break
            
            if grid_ready:
                break
        
        if not grid_ready:
            print("Challenge grid did not fully load within 10s")
            # Try audio as fallback immediately
            audio_result = await self._solve_audio_captcha()
            if audio_result.get("solved"):
                return audio_result
            return {"solved": False, "method": "vision_grid", "attempts": attempts, "error": "Grid did not load"}
        
        if not challenge_frame:
            return {"solved": False, "method": "vision_grid", "attempts": attempts, "error": "No challenge frame"}
        
        # ── Early exit: "Try again later" / "automated queries" (no point continuing)
        try:
            body_text = await challenge_frame.inner_text("body")
            if body_text:
                low = body_text.lower()
                if "try again later" in low or "automated queries" in low or "automated requests" in low:
                    print("❌ reCAPTCHA shows 'Try again later' or 'automated queries' — cannot solve this run.")
                    return {"solved": False, "method": "blocked_by_provider", "attempts": attempts, "error": "Try again later / automated queries"}
        except Exception:
            pass
        
        # ── STEP 3: Solve grid challenges (with retry + tile-refresh handling) ──
        MAX_CHALLENGE_ROUNDS = 5
        clicked_tile_indices = set()
        last_object_name = ""
        num_last_clicks = 0
        grid_attempts = 0
        
        for challenge_round in range(MAX_CHALLENGE_ROUNDS):
            grid_attempts = challenge_round + 1
            try:
                # ── 3-pre: Re-acquire challenge frame to avoid stale references ──
                # The challenge frame/table may have changed since the checkbox click
                # or since the last Verify attempt triggered a new challenge.
                for frame in self.page.frames:
                    if "google.com/recaptcha" in frame.url and "bframe" in frame.url:
                        challenge_frame = frame
                        break
                
                # ── 3a: Read instruction text ──
                instruction_text = ""
                for retry in range(4):
                    instruction_text = await self._read_challenge_instruction(challenge_frame)
                    if instruction_text:
                        break
                    await asyncio.sleep(0.3)
                
                if not instruction_text:
                    print("   [!] No instruction text found -- cannot determine what to look for")
                    break
                
                # ── 3b: Extract target object name ──
                object_name = self._parse_object_name(instruction_text)
                print(f"   [Challenge] '{instruction_text}'")
                print(f"   [Target] '{object_name}'")
                
                # ── 3c: Track if this is a new challenge or continuation ──
                is_new_object = object_name.lower() != last_object_name.lower()
                if is_new_object:
                    print("   New challenge object -- resetting clicked tile tracker")
                    clicked_tile_indices = set()
                    last_object_name = object_name
                elif num_last_clicks >= 3:
                    print("   Previously clicked 3+ tiles -- assuming new challenge, resetting")
                    clicked_tile_indices = set()
                else:
                    print(f"   Same challenge, keeping {len(clicked_tile_indices)} already-clicked tiles")
                
                # ── 3d: Get FRESH tiles from the CURRENT challenge frame ──
                # Critical: re-query table and tiles to avoid using stale DOM references
                table = await challenge_frame.query_selector('table[class*="rc-imageselect-table"]')
                if not table:
                    print("   [!] Grid table not found")
                    break
                
                tiles = await table.query_selector_all('td')
                if not tiles:
                    print("   [!] No tiles found in grid")
                    break
                
                grid_size = len(tiles)
                print(f"   Grid has {grid_size} tiles ({'3x3' if grid_size == 9 else '4x4' if grid_size == 16 else 'unknown'})")
                
                # Wait for tile images to be fully loaded
                # (critical: ensures we screenshot the CURRENT images, not stale placeholders)
                await self._wait_for_tile_images(challenge_frame, tiles, timeout_s=4)
                
                # Brief pause to let images settle
                await asyncio.sleep(random.uniform(0.3, 0.8))
                
                # ── 3e: Screenshot each tile ──
                tile_data = await self._screenshot_all_tiles(tiles, challenge_round)
                
                # FIX #3: Validate screenshots aren't blank
                valid_tiles = [(idx, b64) for idx, b64 in tile_data if b64 is not None]
                if len(valid_tiles) < grid_size * 0.5:
                    print(f"⚠️ Only {len(valid_tiles)}/{grid_size} tiles had valid screenshots — images probably not loaded")
                    print("   Waiting 3 more seconds and retrying screenshots...")
                    await asyncio.sleep(3.0)
                    tile_data = await self._screenshot_all_tiles(tiles, challenge_round)
                    valid_tiles = [(idx, b64) for idx, b64 in tile_data if b64 is not None]
                
                if len(valid_tiles) == 0:
                    print("❌ ZERO valid tile screenshots — NOT clicking Verify (would trigger bot detection)")
                    break
                
                print(f"📸 Got {len(valid_tiles)}/{grid_size} valid tile screenshots")
                
                # ── 3f: Ask AI about each tile ──
                # FIX #2: Use solve_captcha_with_ai which supports ALL providers (claude/openai/gemini)
                tiles_to_click, ai_ok = await self._analyze_tiles_with_ai(valid_tiles, object_name)
                if not ai_ok:
                    print("❌ AI analysis failed for ALL tiles (check CAPTCHA_AI_PROVIDER and API keys: OPENAI_API_KEY / ANTHROPIC / GOOGLE_API_KEY). NOT clicking Verify.")
                    break
                
                # Filter out already-clicked tiles
                new_tiles = set(tiles_to_click) - clicked_tile_indices
                num_last_clicks = len(new_tiles)
                
                print(f"🤖 AI selected tiles: {sorted(list(set(tiles_to_click)))}")
                print(f"   Already clicked: {sorted(list(clicked_tile_indices))}")
                print(f"   New to click: {sorted(list(new_tiles))}")
                
                # ── 3g: Handle "skip if none" case ──
                if object_name.lower() == 'skip' and len(new_tiles) == 0:
                    skip_btn = await challenge_frame.query_selector('button.rc-button-default')
                    if skip_btn:
                        await asyncio.sleep(random.uniform(0.3, 0.6))
                        await self._human_click(skip_btn, 100, 300)
                        await asyncio.sleep(0.5)
                
                # ── 3h: Click tiles + handle dynamic refresh loop ──
                # reCAPTCHA replaces clicked tiles with new images.
                # We must loop: click matches → wait for refresh → re-screenshot
                # → re-analyze → click new matches → ... until stable.
                MAX_REFRESH_ROUNDS = 3
                tiles_to_click_now = sorted(list(new_tiles))
                
                for refresh_round in range(MAX_REFRESH_ROUNDS + 1):  # 0 = initial, 1-3 = refresh rounds
                    if refresh_round > 0:
                        print(f"   -- Refresh round {refresh_round}/{MAX_REFRESH_ROUNDS} --")
                    
                    # Click all identified tiles (fast sequential clicks)
                    actually_clicked = []
                    for tile_idx in tiles_to_click_now:
                        if tile_idx < len(tiles):
                            try:
                                tile = tiles[tile_idx]
                                if await tile.is_visible():
                                    await self._human_click(tile, 100, 350)
                                    print(f"   >> Clicked tile {tile_idx}")
                                    actually_clicked.append(tile_idx)
                            except Exception as e:
                                print(f"   !! Could not click tile {tile_idx}: {e}")
                    
                    clicked_tile_indices.update(actually_clicked)
                    
                    if not actually_clicked:
                        print("   No tiles clicked this round — done with refreshes")
                        break
                    
                    # Wait for reCAPTCHA to replace clicked tiles with new images
                    await asyncio.sleep(random.uniform(0.8, 1.3))
                    
                    # Check if tiles refreshed (new images fading in)
                    refreshed = await self._check_for_tile_refresh(challenge_frame, tiles)
                    if not refreshed:
                        print("   No tile refresh detected — ready to Verify")
                        break
                    
                    print("   Tiles refreshed with new images — re-analyzing...")
                    # Wait for fade-in animation + image load
                    await asyncio.sleep(random.uniform(1.0, 1.8))
                    
                    # Re-get tiles (DOM may have changed)
                    table = await challenge_frame.query_selector('table[class*="rc-imageselect-table"]')
                    if table:
                        tiles = await table.query_selector_all('td')
                    
                    # Wait for new tile images to load
                    await self._wait_for_tile_images(challenge_frame, tiles, timeout_s=3)
                    
                    # Screenshot ALL tiles again (need fresh state)
                    refresh_tile_data = await self._screenshot_all_tiles(tiles, challenge_round, suffix=f"_r{refresh_round}")
                    refresh_valid = [(idx, b64) for idx, b64 in refresh_tile_data if b64 is not None]
                    
                    if not refresh_valid:
                        print("   No valid screenshots after refresh — stopping")
                        break
                    
                    print(f"   Got {len(refresh_valid)}/{len(tiles)} screenshots after refresh")
                    
                    # Analyze ALL tiles again
                    refresh_clicks, refresh_ok = await self._analyze_tiles_with_ai(refresh_valid, object_name)
                    if not refresh_ok:
                        print("   AI failed on refresh round — stopping")
                        break
                    
                    # Only click tiles we haven't clicked before
                    refresh_new = sorted(list(set(refresh_clicks) - clicked_tile_indices))
                    print(f"   Refresh AI selected: {sorted(refresh_clicks)}, new to click: {refresh_new}")
                    
                    if not refresh_new:
                        print("   No new matching tiles after refresh — ready to Verify")
                        break
                    
                    tiles_to_click_now = refresh_new
                
                # ── 3i: Click Verify ──
                await asyncio.sleep(random.uniform(0.4, 0.9))
                
                verify_btn = await challenge_frame.query_selector('#recaptcha-verify-button')
                if verify_btn:
                    await self._human_click(verify_btn, 150, 400)
                    print("   Clicked Verify")
                    
                    # Wait for Google to evaluate
                    await asyncio.sleep(random.uniform(1.5, 2.5))
                    
                    # Check if solved
                    if await self._check_success("recaptcha_v2"):
                        print("✅ reCAPTCHA solved via grid challenge!")
                        return {"solved": True, "method": "vision_grid", "attempts": attempts + grid_attempts}
                    
                    # Check if the challenge iframe closed (another sign of success)
                    still_has_challenge = False
                    for frame in self.page.frames:
                        if "google.com/recaptcha" in frame.url and "bframe" in frame.url:
                            table_check = await frame.query_selector('table[class*="rc-imageselect-table"]')
                            if table_check:
                                still_has_challenge = True
                            break
                    
                    if not still_has_challenge:
                        print("✅ Challenge frame closed — likely solved!")
                        return {"solved": True, "method": "vision_grid", "attempts": attempts + grid_attempts}
                    
                    print(f"❌ Round {challenge_round + 1} did not solve — new challenge may have appeared")
                else:
                    print("❌ Verify button not found")
                    break
            
            except Exception as e:
                print(f"❌ Challenge round {challenge_round + 1} error: {e}")
                import traceback
                traceback.print_exc()
                break
        
        # ── STEP 4: Audio fallback (after 3+ failed grid attempts) ──
        if grid_attempts >= 3:
            print("🔊 Grid solving failed — trying audio fallback...")
            audio_result = await self._solve_audio_captcha()
            if audio_result.get("solved"):
                audio_result["attempts"] = attempts + grid_attempts
                return audio_result
        
        return {"solved": False, "method": "vision_grid", "attempts": attempts + grid_attempts, "error": "Max attempts reached"}
    
    # ══════════════════════════════════════════════════════════════════
    # TILE HELPER METHODS (NEW — fixes the core issues)
    # ══════════════════════════════════════════════════════════════════
    
    async def _check_tile_images_loaded(self, frame: Frame, tiles: list) -> bool:
        """
        FIX #1: Check that tile images have actually loaded, not just DOM placeholders.
        reCAPTCHA tiles contain <img> elements whose src gets populated async.
        Returns True if at least 80% of tiles have loaded images.
        """
        try:
            loaded_count = 0
            for tile in tiles:
                img = await tile.query_selector('img')
                if img:
                    src = await img.get_attribute('src')
                    if src and len(src) > 50:  # Real image src is a long data URI or URL
                        loaded_count += 1
                else:
                    # Some reCAPTCHA versions use background-image CSS instead of <img>
                    style = await tile.get_attribute('style')
                    if style and 'background-image' in style and 'url(' in style:
                        loaded_count += 1
            
            threshold = len(tiles) * 0.8
            return loaded_count >= threshold
        except Exception:
            return False
    
    async def _wait_for_tile_images(self, frame: Frame, tiles: list, timeout_s: int = 8):
        """
        FIX #1: Poll until tile images are loaded or timeout.
        """
        for i in range(timeout_s * 2):  # Check every 0.5s
            if await self._check_tile_images_loaded(frame, tiles):
                return True
            await asyncio.sleep(0.5)
        print(f"⚠️ Tile images not fully loaded after {timeout_s}s — proceeding anyway")
        return False
    
    async def _screenshot_all_tiles(self, tiles: list, round_num: int, suffix: str = "") -> List[Tuple[int, Optional[str]]]:
        """
        Screenshot each tile and return (index, base64_or_None) pairs.
        FIX #3: Validates each screenshot has actual content (not blank).
        """
        # Avoid crash when tile_screenshot_dir not set (e.g. main didn't pass it)
        save_dir = self.tile_screenshot_dir if self.tile_screenshot_dir else os.path.join(os.getcwd(), "screenshots")
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        results = []
        for i, tile in enumerate(tiles):
            try:
                img_bytes = await tile.screenshot()
                
                # FIX #3: Check screenshot isn't too small (blank tile = ~200 bytes, real tile = ~5000+)
                if len(img_bytes) < 500:
                    print(f"  ⚠️ Tile {i}: Screenshot too small ({len(img_bytes)} bytes) — likely blank")
                    results.append((i, None))
                    continue
                
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
                # Save to disk for debugging
                tile_path = os.path.join(save_dir, f'tile_r{round_num}_{i}{suffix}.png')
                with open(tile_path, 'wb') as f:
                    f.write(img_bytes)
                
                results.append((i, img_b64))
            except Exception as e:
                print(f"  ❌ Tile {i}: Screenshot failed — {e}")
                results.append((i, None))
        
        return results
    
    async def _analyze_tiles_with_ai(self, tile_data: List[Tuple[int, str]], object_name: str) -> Tuple[List[int], bool]:
        """
        Analyze ALL tiles concurrently (all 9 or 16 at once for speed).
        Uses solve_captcha_with_ai which supports ALL providers (claude/openai/gemini).
        
        Returns (list of tile indices that contain the target object, at_least_one_ai_succeeded).
        If all AI calls fail (no API key / wrong model), we must NOT click Verify.
        """
        selected_tiles = []
        at_least_one_success = False
        
        async def analyze_single_tile(tile_idx: int, tile_b64: str) -> Tuple[int, bool, bool]:
            try:
                result = await solve_captcha_with_ai(
                    image_b64=tile_b64,
                    captcha_type="tile_check",
                    prompt_context=object_name,
                    provider=self.ai_provider,
                    claude_client=self.claude_client
                )
                if result.get("error"):
                    print(f"  Tile {tile_idx}: AI error -- {result.get('error')}")
                    return (tile_idx, False, False)
                answer = str(result.get("solution", "false")).lower().strip()
                confidence = float(result.get("confidence", 0.0))
                contains_object = answer in ("true", "yes", "1") and confidence >= 0.5
                print(f"  Tile {tile_idx}: '{object_name}'? -> {answer} (conf: {confidence:.2f})")
                return (tile_idx, contains_object, True)
            except Exception as e:
                print(f"  Tile {tile_idx}: AI exception -- {e}")
                return (tile_idx, False, False)
        
        # Fire ALL tile analyses concurrently (9 or 16 at once)
        tasks = [analyze_single_tile(idx, b64) for idx, b64 in tile_data]
        all_results = await asyncio.gather(*tasks)
        
        for tile_idx, contains, ok in all_results:
            if ok:
                at_least_one_success = True
            if contains:
                selected_tiles.append(tile_idx)
        
        return selected_tiles, at_least_one_success
    
    async def _check_for_tile_refresh(self, frame: Frame, tiles: list) -> bool:
        """
        After clicking tiles, reCAPTCHA sometimes replaces individual tiles 
        with new images (fade-in animation). Detect if any tiles have changed.
        
        Checks for the 'rc-imageselect-dynamic-selected' class which appears on
        tiles that are being refreshed with new images.
        """
        try:
            refreshing = await frame.query_selector_all('.rc-imageselect-dynamic-selected, .rc-imageselect-tileselected')
            if refreshing and len(refreshing) > 0:
                return True
            
            # Also check if any tile has the "loading" indicator
            loading = await frame.query_selector('.rc-imageselect-progress')
            if loading:
                return True
        except Exception:
            pass
        
        return False
    
    def _parse_object_name(self, instruction_text: str) -> str:
        """
        Extract the target object from reCAPTCHA instruction text.
        e.g., "Select all images with traffic lights" → "traffic lights"
              "Select all images with a bus" → "a bus"  
              "Select all squares with motorcycles\nIf there are none, click skip" → "motorcycles"
        """
        low = instruction_text.lower()
        
        # Pattern 1: "Select all images with <object>"
        match = re.search(r'(?:select all (?:images|squares) with\s+)(.+?)(?:\s*\.\s*|\s*if there|\s*click|\n|$)', low, re.DOTALL | re.IGNORECASE)
        if match:
            return re.sub(r'\s+', ' ', match.group(1).strip())
        
        # Pattern 2: "Select all images that contain <object>"
        match = re.search(r'(?:that contain\s+)(.+?)(?:\s*\.\s*|\s*if there|\s*click|\n|$)', low, re.DOTALL | re.IGNORECASE)
        if match:
            return re.sub(r'\s+', ' ', match.group(1).strip())
        
        # Pattern 3: "If there are none, click skip"
        if 'if there are none' in low and 'skip' in low:
            return 'skip'
        
        # Fallback: last meaningful phrase
        words = low.split()
        return ' '.join(words[-2:]) if len(words) >= 2 else (words[0] if words else "unknown")
    
    async def _read_challenge_instruction(self, frame: Frame) -> str:
        """Read the instruction text from the challenge frame (e.g. 'Select all images with buses')."""
        # Primary: known reCAPTCHA class names
        for sel in ['.rc-imageselect-desc-no-canonical', '.rc-imageselect-desc', '.rc-imageselect-instructions', '[class*="rc-imageselect-desc"]']:
            try:
                elem = await frame.query_selector(sel)
                if elem:
                    text = (await elem.inner_text()).strip()
                    if text and ("select" in text.lower() or "with" in text.lower() or "contain" in text.lower() or "skip" in text.lower()):
                        return text
            except Exception:
                continue
        # Fallback: any element that looks like the instruction (reCAPTCHA can vary)
        try:
            body = await frame.inner_text("body")
            if body:
                for line in body.splitlines():
                    line = line.strip()
                    if not line or len(line) < 10:
                        continue
                    if "select all" in line.lower() or ("with" in line.lower() and "click" not in line.lower()) or "if there are none" in line.lower():
                        return line
        except Exception:
            pass
        return ""
    
    # ══════════════════════════════════════════════════════════════════
    # TEXT CAPTCHA
    # ══════════════════════════════════════════════════════════════════
    
    async def _solve_text_captcha(self, selector: str) -> Dict[str, Any]:
        attempts = 0
        
        while attempts < self.max_attempts:
            try:
                captcha_img = await self.page.query_selector(selector)
                if not captcha_img:
                    captcha_img = await self.page.query_selector('img[id*="captcha" i], img[class*="captcha" i]')
                if not captcha_img:
                    return {"solved": False, "method": "vision_text", "attempts": attempts, "error": "Image not found"}
                
                img_bytes = await captcha_img.screenshot()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
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
                
                input_field = await self.page.query_selector(
                    'input[type="text"][id*="captcha" i], input[type="text"][name*="captcha" i], .mtcap-noborder'
                )
                if not input_field:
                    input_field = await self.page.query_selector('input[type="text"]')
                if not input_field:
                    return {"solved": False, "method": "vision_text", "attempts": attempts, "error": "Input not found"}
                
                await input_field.click()
                await asyncio.sleep(random.uniform(0.3, 0.6))
                for char in solution:
                    await self.page.keyboard.type(char)
                    await asyncio.sleep(random.uniform(0.05, 0.15))
                
                submit_btn = await self.page.query_selector(
                    'button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Verify")'
                )
                if submit_btn:
                    await asyncio.sleep(random.uniform(0.8, 1.5))
                    await submit_btn.click()
                    await asyncio.sleep(2)
                
                error_msg = await self.page.query_selector('.error, .captcha-error, [class*="error"]')
                if not error_msg:
                    return {"solved": True, "method": "vision_text", "attempts": attempts + 1}
                
                attempts += 1
            except Exception as e:
                attempts += 1
                if attempts >= self.max_attempts:
                    return {"solved": False, "method": "vision_text", "attempts": attempts, "error": str(e)}
        
        return {"solved": False, "method": "vision_text", "attempts": attempts, "error": "Max attempts"}
    
    # ══════════════════════════════════════════════════════════════════
    # PUZZLE / SLIDER CAPTCHA
    # ══════════════════════════════════════════════════════════════════
    
    async def _solve_puzzle_captcha(self, selector: str) -> Dict[str, Any]:
        attempts = 0
        
        while attempts < self.max_attempts:
            try:
                puzzle_elem = await self.page.query_selector(selector)
                if not puzzle_elem:
                    puzzle_elem = await self.page.query_selector('.geetest_slider, div[class*="slider"], div[class*="puzzle"]')
                if not puzzle_elem:
                    return {"solved": False, "method": "puzzle_slide", "attempts": attempts, "error": "Puzzle not found"}
                
                puzzle_bytes = await puzzle_elem.screenshot()
                puzzle_b64 = base64.b64encode(puzzle_bytes).decode('utf-8')
                
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
                
                bbox = await puzzle_elem.bounding_box()
                if not bbox:
                    return {"solved": False, "method": "puzzle_slide", "attempts": attempts, "error": "Not visible"}
                
                target_x = bbox['x'] + (bbox['width'] * x_percent / 100)
                
                handle = await puzzle_elem.query_selector('.slider-handle, .geetest_slider_button, button')
                if not handle:
                    return {"solved": False, "method": "puzzle_slide", "attempts": attempts, "error": "Handle not found"}
                
                handle_bbox = await handle.bounding_box()
                if not handle_bbox:
                    return {"solved": False, "method": "puzzle_slide", "attempts": attempts, "error": "Handle not visible"}
                
                start_x = handle_bbox['x'] + handle_bbox['width'] / 2
                start_y = handle_bbox['y'] + handle_bbox['height'] / 2
                drag_distance = target_x - start_x
                
                await self.page.mouse.move(start_x, start_y)
                await asyncio.sleep(random.uniform(0.2, 0.4))
                await self.page.mouse.down()
                await asyncio.sleep(random.uniform(0.1, 0.2))
                
                steps = random.randint(15, 25)
                for i in range(steps):
                    progress = (i + 1) / steps
                    eased = 1 - (1 - progress) ** 2
                    step_x = start_x + (drag_distance * eased)
                    await self.page.mouse.move(
                        step_x + random.uniform(-2, 2),
                        start_y + random.uniform(-3, 3)
                    )
                    await asyncio.sleep(random.uniform(0.01, 0.03))
                
                await asyncio.sleep(random.uniform(0.05, 0.15))
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
    
    # ══════════════════════════════════════════════════════════════════
    # AUDIO CAPTCHA FALLBACK
    # ══════════════════════════════════════════════════════════════════
    
    async def _solve_audio_captcha(self) -> Dict[str, Any]:
        try:
            challenge_frame = None
            for frame in self.page.frames:
                if "google.com/recaptcha" in frame.url and "bframe" in frame.url:
                    challenge_frame = frame
                    break
            
            if not challenge_frame:
                return {"solved": False, "method": "audio_whisper", "error": "Frame not found"}
            
            audio_btn = await challenge_frame.query_selector('#recaptcha-audio-button, button[aria-label*="audio"]')
            if not audio_btn:
                return {"solved": False, "method": "audio_whisper", "error": "Audio button not found"}
            
            await self._human_click(audio_btn, 400, 900)
            await asyncio.sleep(random.uniform(3.0, 5.0))
            
            audio_link = await challenge_frame.query_selector('.rc-audiochallenge-tdownload-link')
            if not audio_link:
                return {"solved": False, "method": "audio_whisper", "error": "Audio link not found"}
            
            audio_url = await audio_link.get_attribute('href')
            if not audio_url:
                return {"solved": False, "method": "audio_whisper", "error": "Audio URL not found"}
            
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
            transcribed_text = await transcribe_audio(audio_bytes, provider="openai")
            
            if not transcribed_text:
                return {"solved": False, "method": "audio_whisper", "error": "Transcription failed"}
            
            audio_input = await challenge_frame.query_selector('#audio-response, input[id*="audio"]')
            if not audio_input:
                return {"solved": False, "method": "audio_whisper", "error": "Input not found"}
            
            await audio_input.click()
            await audio_input.fill(transcribed_text)
            await asyncio.sleep(random.uniform(0.8, 1.5))
            
            verify_btn = await challenge_frame.query_selector('#recaptcha-verify-button')
            if verify_btn:
                await self._human_click(verify_btn, 300, 700)
                await asyncio.sleep(random.uniform(2.0, 3.5))
            
            if await self._check_success("recaptcha_v2"):
                return {"solved": True, "method": "audio_whisper"}
            
            return {"solved": False, "method": "audio_whisper", "error": "Transcription incorrect"}
        except Exception as e:
            return {"solved": False, "method": "audio_whisper", "error": str(e)}
    
    # ══════════════════════════════════════════════════════════════════
    # CLOUDFLARE TURNSTILE
    # ══════════════════════════════════════════════════════════════════
    
    async def _solve_turnstile(self, selector: str) -> Dict[str, Any]:
        try:
            turnstile_frame = None
            for _ in range(5):
                for frame in self.page.frames:
                    if "challenges.cloudflare.com" in frame.url:
                        turnstile_frame = frame
                        break
                if turnstile_frame:
                    break
                await asyncio.sleep(1)
            
            if turnstile_frame:
                checkbox = await turnstile_frame.query_selector('input[type="checkbox"]')
                if checkbox:
                    await self._human_click(checkbox, 300, 700)
            
            for _ in range(15):
                if await self._check_success("turnstile"):
                    return {"solved": True, "method": "turnstile_wait", "attempts": 1}
                await asyncio.sleep(1)
            
            return {"solved": False, "method": "turnstile_wait", "attempts": 1, "error": "Timeout"}
        except Exception as e:
            return {"solved": False, "method": "turnstile_wait", "attempts": 1, "error": str(e)}
    
    # ══════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ══════════════════════════════════════════════════════════════════
    
    async def _human_click(self, element, min_delay_ms: int = 300, max_delay_ms: int = 800):
        """Click with mouse movement + jitter + delay to avoid bot detection."""
        await asyncio.sleep(random.uniform(min_delay_ms / 1000, max_delay_ms / 1000))
        box = await element.bounding_box()
        if not box:
            await element.click()
            return
        cx = box['x'] + box['width'] / 2
        cy = box['y'] + box['height'] / 2
        jx = random.uniform(-4, 4)
        jy = random.uniform(-4, 4)
        await self.page.mouse.move(cx + jx, cy + jy)
        await asyncio.sleep(random.uniform(0.05, 0.2))
        await self.page.mouse.click(cx + jx, cy + jy)
    
    async def _check_success(self, captcha_type: str) -> bool:
        try:
            if captcha_type == "recaptcha_v2":
                for frame in self.page.frames:
                    if "google.com/recaptcha" in frame.url and "anchor" in frame.url:
                        checked = await frame.query_selector('.recaptcha-checkbox-checked, [aria-checked="true"]')
                        if checked:
                            return True
                response = await self.page.query_selector('textarea[name="g-recaptcha-response"]')
                if response:
                    val = await response.input_value()
                    if val and len(val) > 20:
                        return True
            
            elif captcha_type == "turnstile":
                response = await self.page.query_selector('input[name*="cf-turnstile-response"]')
                if response:
                    val = await response.input_value()
                    if val and len(val) > 10:
                        return True
            
            elif captcha_type == "puzzle":
                success = await self.page.query_selector('.geetest_success, .puzzle-success, [class*="success"]')
                if success:
                    return True
        except Exception:
            pass
        return False