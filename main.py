#!/usr/bin/env python3
"""
SPECTER - Autonomous AI QA Agent
Fully powered by webqa_agent + Unified AI Vision API.

  BrowserSessionPool  - managed browser lifecycle
  DeepCrawler          - DOM element detection + highlight
  ActionHandler         - click, type, scroll, hover, screenshots
  ActionExecutor        - structured action dispatch
  ScrollHandler         - smart page/container scrolling
  Unified AI Vision API - vision + reasoning (Claude or NVIDIA Llama)

FEATURE 1: Multimodal Persona-Driven Navigator
  - LLM observes screenshot + DOM -> decides next action autonomously
  - Persona simulation (zoomer, boomer, skeptic, chaos, mobile)
  - Device emulation, network throttling, locale
  - AI decides ALL steps -- no hardcoded sequences

FEATURE 2: Cognitive UX Analyst & Diagnosis
  - F-Score calculation, Heatmap, GIF replay
  - P0-P3 severity, Claude Vision diagnosis, Slack escalation

Usage:
    python main.py                                    # Demo with mock data
    python main.py autonomous https://example.com    # Full autonomous test
    python main.py autonomous https://deriv.com/signup --persona boomer --device iphone13
"""

import asyncio
import sys
import os
import argparse
import json
import base64
import logging
import traceback
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Specter Core - Feature 2 (Diagnosis Engine)
from backend.expectation_engine import check_expectation
from backend.diagnosis_doctor import diagnose_failure
from backend.escalation_webhook import send_alert
from backend.webqa_bridge import _resolve_screenshot_path
from backend.ai_utils import call_llm_vision, parse_json_from_llm
from backend.otp_reader import OTPReader

# Unified AI Vision SDK (Handled inside ai_utils)
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))

# webqa_agent - the REAL agent infrastructure
try:
    from webqa_agent.browser.session import BrowserSessionPool
    from webqa_agent.actions.action_handler import ActionHandler
    from webqa_agent.actions.action_executor import ActionExecutor
    from webqa_agent.actions.scroll_handler import ScrollHandler
    from webqa_agent.crawler.deep_crawler import DeepCrawler
    AUTONOMOUS_AVAILABLE = True
except ImportError as e:
    AUTONOMOUS_AVAILABLE = False
    print(f"Autonomous mode requires webqa_agent: {e}")


# ======================================================================
# RED DOT DEBUG OVERLAY
# ======================================================================

RED_DOT_JS = """
(coords) => {
    const old = document.getElementById('__ghost_dot__');
    if (old) old.remove();
    const dot = document.createElement('div');
    dot.id = '__ghost_dot__';
    dot.style.cssText = `
        position: fixed;
        left: ${coords[0] - 20}px;
        top: ${coords[1] - 20}px;
        width: 40px; height: 40px;
        background: radial-gradient(circle, rgba(255,0,0,0.9) 0%, rgba(255,0,0,0.6) 70%);
        border: 4px solid rgba(255,255,255,0.9);
        border-radius: 50%;
        z-index: 2147483647;
        pointer-events: none;
        box-shadow: 0 0 20px 8px rgba(255,0,0,0.8), 0 0 40px 15px rgba(255,100,100,0.5);
        animation: ghostPulse 0.6s ease-out, ghostGlow 1.5s ease-in-out infinite;
    `;
    const style = document.createElement('style');
    style.textContent = '@keyframes ghostPulse { 0% { transform: scale(0.3); opacity: 0; } 50% { transform: scale(1.3); opacity: 1; } 100% { transform: scale(1); opacity: 1; } } @keyframes ghostGlow { 0%, 100% { box-shadow: 0 0 20px 8px rgba(255,0,0,0.8), 0 0 40px 15px rgba(255,100,100,0.5); } 50% { box-shadow: 0 0 30px 12px rgba(255,0,0,1), 0 0 60px 25px rgba(255,100,100,0.8); } }';
    document.head.appendChild(style);
    document.body.appendChild(dot);
    setTimeout(() => { dot.style.opacity = '0'; dot.style.transition = 'opacity 1s ease-out'; }, 4000);
    setTimeout(() => { dot.remove(); style.remove(); }, 5000);
}
"""


# ======================================================================
# MOCK FILES FOR UPLOAD DOCUMENT TESTING
# ======================================================================

def _build_minimal_pdf(text_lines: List[str]) -> bytes:
    """Build a valid PDF file from scratch using raw PDF syntax (no external libs)."""
    # Page size: A4 (595 x 842 points)
    page_w, page_h = 595, 842
    font_size = 14

    # Build content stream (text drawing commands)
    content_parts = [f"BT /F1 {font_size} Tf"]
    y = page_h - 60  # start near the top
    for line in text_lines:
        # Escape special PDF chars
        safe = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        content_parts.append(f"1 0 0 1 50 {y} Tm ({safe}) Tj")
        y -= font_size * 1.6
    content_parts.append("ET")
    stream_data = "\n".join(content_parts).encode('latin-1')

    objects = []  # list of (obj_number, bytes)

    # obj 1 — Catalog
    objects.append((1, b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj"))
    # obj 2 — Pages
    objects.append((2, b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj"))
    # obj 3 — Page
    objects.append((3, f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_w} {page_h}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj".encode('latin-1')))
    # obj 4 — Content stream
    objects.append((4, b"4 0 obj\n<< /Length " + str(len(stream_data)).encode() + b" >>\nstream\n" + stream_data + b"\nendstream\nendobj"))
    # obj 5 — Font
    objects.append((5, b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj"))

    # Assemble PDF
    body = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = {}
    for obj_num, obj_bytes in objects:
        offsets[obj_num] = len(body)
        body += obj_bytes + b"\n"

    xref_offset = len(body)
    xref = b"xref\n0 6\n"
    xref += b"0000000000 65535 f \n"
    for i in range(1, 6):
        xref += f"{offsets[i]:010d} 00000 n \n".encode()
    xref += b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
    xref += str(xref_offset).encode() + b"\n%%EOF\n"

    return body + xref


def _build_png_rgba(width: int, height: int, r: int, g: int, b: int, a: int = 255) -> bytes:
    """Build a valid PNG file (solid colour) using only stdlib zlib + struct."""
    import struct
    import zlib as _zlib

    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        crc = struct.pack('>I', _zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack('>I', len(data)) + c + crc

    # IHDR
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    # IDAT — raw image rows: filter byte 0 + RGBA pixels
    raw_rows = b''
    row = bytes([r, g, b, a]) * width
    for _ in range(height):
        raw_rows += b'\x00' + row  # filter byte = 0 (None)
    compressed = _zlib.compress(raw_rows)

    png = b'\x89PNG\r\n\x1a\n'
    png += _chunk(b'IHDR', ihdr_data)
    png += _chunk(b'IDAT', compressed)
    png += _chunk(b'IEND', b'')
    return png


def ensure_upload_mock_files() -> List[str]:
    """Create real, valid PDF and PNG mock files for upload testing.
    Uses only Python stdlib — no external libs needed.
    Returns list of absolute paths.
    """
    assets_dir = Path(__file__).resolve().parent / "backend" / "assets"
    mocks_dir = assets_dir / "upload_mocks"
    mocks_dir.mkdir(parents=True, exist_ok=True)
    paths = []

    # 1. Valid PDF document (ID / proof of address)
    pdf_path = mocks_dir / "sample_id_document.pdf"
    if not pdf_path.exists():
        try:
            pdf_bytes = _build_minimal_pdf([
                "SAMPLE IDENTITY DOCUMENT",
                "",
                "Full Name:    Test User",
                "Date of Birth: 01 Jan 1990",
                "Document No:   SPEC-QA-2025-001",
                "Issued By:     Specter QA Authority",
                "Valid Until:   31 Dec 2030",
                "",
                "This is a mock document generated for",
                "automated signup / KYC upload testing.",
            ])
            pdf_path.write_bytes(pdf_bytes)
            print(f"[MOCK] Created PDF: {pdf_path}")
        except Exception as e:
            logging.warning(f"Could not create mock PDF: {e}")
    if pdf_path.exists():
        paths.append(str(pdf_path.resolve()))

    # 2. Valid PNG image (200x200 blue square — passport photo / ID scan)
    png_path = mocks_dir / "sample_id_photo.png"
    if not png_path.exists():
        try:
            png_bytes = _build_png_rgba(200, 200, r=40, g=80, b=180, a=255)
            png_path.write_bytes(png_bytes)
            print(f"[MOCK] Created PNG: {png_path}")
        except Exception as e:
            logging.warning(f"Could not create mock PNG: {e}")
    if png_path.exists():
        paths.append(str(png_path.resolve()))

    # 3. Valid JPEG image (use PNG-in-JPEG wrapper — simplest valid JFIF)
    jpg_path = mocks_dir / "sample_document_scan.jpg"
    if not jpg_path.exists():
        try:
            # Minimal valid JFIF/JPEG: 8x8 white image
            # This is the smallest valid JPEG that any parser will accept
            jpeg_b64 = (
                "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkS"
                "Ew8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJ"
                "CQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy"
                "MjIyMjIyMjIyMjIyMjL/wAARCAAIAAgDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEA"
                "AAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIh"
                "MUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6"
                "Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZ"
                "mqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx"
                "8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREA"
                "AgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAV"
                "YnLRChYkNOEl8RcYI4Q/RFhHRUYnJCk6LBwmN0M5STpFRS0xNjc4QlJDVINUY3Jk"
                "dHV2d3h5eoOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbH"
                "yMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+gAo"
                "AKAP/9k="
            )
            jpg_path.write_bytes(base64.b64decode(jpeg_b64))
            print(f"[MOCK] Created JPEG: {jpg_path}")
        except Exception as e:
            logging.warning(f"Could not create mock JPEG: {e}")
    if jpg_path.exists():
        paths.append(str(jpg_path.resolve()))

    return paths


# ======================================================================
# DEVICE / NETWORK / PERSONA PROFILES
# ======================================================================

DEVICES = {
    'iphone13': {
        'name': 'iPhone 13 Pro',
        'viewport': {'width': 390, 'height': 844},
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',
        'has_touch': True, 'is_mobile': True,
    },
    'android': {
        'name': 'Pixel 5',
        'viewport': {'width': 393, 'height': 851},
        'user_agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36',
        'has_touch': True, 'is_mobile': True,
    },
    'desktop': {
        'name': 'Desktop 1280x720',
        'viewport': {'width': 1280, 'height': 720},
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'has_touch': False, 'is_mobile': False,
    },
}

NETWORKS = {
    '3g':   {'name': 'Slow 3G',  'download': 400*1024//8,     'upload': 400*1024//8,     'latency': 400},
    '4g':   {'name': 'Fast 4G',  'download': 4*1024*1024//8,  'upload': 3*1024*1024//8,  'latency': 20},
    'wifi': {'name': 'WiFi',     'download': 30*1024*1024//8, 'upload': 15*1024*1024//8, 'latency': 2},
    'slow': {'name': 'Slow WiFi','download': 50*1024//8,      'upload': 20*1024//8,      'latency': 800},
}

PERSONAS = {
    # 1. THE HAPPY PATH (Speed & Performance)
    'zoomer': {
        'name': 'Zoomer (Speedster)',
        'desc': 'Tech-savvy user speed-running the signup',
        'typing_delay': 0.03,
        'action_delay': 0.3,
        'hesitation': 0.0,
        'system_prompt': """
            You are an impatient, tech-savvy Gen Z user.
            GOAL: Finish signup in under 10 seconds.
            BEHAVIOR:
            - Do NOT read instructions. 
            - Always choose "Sign up with Google" if available.
            - If a page takes >2 seconds to load, COMPLAIN: "Laggy interface".
            - Ignore "Terms" and "Privacy" links.
        """
    },

    # 2. THE INSIGHT GENERATOR (UX & Copy Analysis)
    'boomer': {
        'name': 'Boomer (The Critic)',
        'desc': 'Anxious first-timer who gets stuck easily',
        'typing_delay': 0.3,
        'action_delay': 1.5,
        'hesitation': 1.0,
        'system_prompt': """
            You are a 65-year-old non-technical user. You are nervous.
            GOAL: Ensure everything is 100% clear before clicking.
            BEHAVIOR:
            - Scroll up and down to read everything.
            - If a label is vague (like just "ID"), STOP and flag "High Confusion".
            - If text is small (<16px) or low contrast, COMPLAIN: "I can't read this".
            - Verify: "Does this button actually look clickable?"
        """
    },

    # 3. THE EDGE CASE (Legal & Link Verification)
    'skeptic': {
        'name': 'The Skeptic',
        'desc': 'Privacy-focused user checking legal pages',
        'typing_delay': 0.15,
        'action_delay': 0.8,
        'hesitation': 0.5,
        'system_prompt': """
            You are a paranoid privacy advocate.
            GOAL: Find security flaws and broken links.
            BEHAVIOR:
            - Refuse Social Logins (Google/FB). Use Email only.
            - Click "Terms of Service" first. If it's a broken link, flag CRITICAL BUG.
            - Look for "Marketing Consent" checkboxes and uncheck them.
        """
    },

    # 4. THE CHAOS MONKEY (Robustness & Form Validation)
    'chaos': {
        'name': 'Chaos Monkey',
        'desc': 'Clumsy user trying to break the form',
        'typing_delay': 0.1,
        'action_delay': 1.0,
        'hesitation': 0.0,
        'system_prompt': """
            You are a clumsy user testing error handling.
            GOAL: Trigger validation errors.
            BEHAVIOR:
            - Click "Next" immediately without filling anything.
            - Enter invalid email formats (e.g., "felicia@" or "test.com").
            - If the app crashes or lets you pass with bad data, flag a BUG.
        """
    },

    # 5. THE CONSTRAINT TESTER (New! - Mobile & Accessibility)
    'mobile': {
        'name': 'Mobile Native',
        'desc': 'User on a small screen with fat fingers',
        'typing_delay': 0.2,
        'action_delay': 0.6,
        'hesitation': 0.3,
        'system_prompt': """
            You are using a smartphone with a cracked screen under bright sunlight.
            GOAL: Test touch targets and readability.
            BEHAVIOR:
            - If buttons are too close together (<10px gap), COMPLAIN: "Fat finger risk".
            - If the keyboard would cover the input field, flag a UI BUG.
            - If you have to scroll horizontally to see content, flag as "Not Mobile Responsive".
        """
    }
}


# ======================================================================
# LLM PLANNER PROMPT - Persona-aware autonomous planning
# ======================================================================

PLANNER_SYSTEM_PROMPT = """RETURN JSON OUTPUT ONLY. NO CONVERSATION. NO MARKDOWN.

You are an autonomous QA agent performing a real user journey on a website.
You act as a specific USER PERSONA and must test the sign-up / registration flow.

Your job:
1. OBSERVE the current page (screenshot + interactive elements list)
2. DECIDE the single best next action to progress toward completing sign-up
3. Return a structured JSON response

### 🛑 CRITICAL MISSION RULES: SIGN UP ONLY 🛑

**THE "NO LOGIN" RULE:**
- You are STRICTLY FORBIDDEN from logging into an existing account.
- DO NOT click buttons labeled "Log In", "Sign In", or "Login". EVER.
- If you land on a Login page, your IMMEDIATE goal is to find the link that says "Create Account", "Sign Up", or "Register".
- If you are unsure if a form is "Login" or "Signup", look for the "Confirm Password" field. If it's missing, you are on the WRONG page (Login). Find the "Sign Up" link immediately.

**NAVIGATION PRIORITY (in order):**
1. "Create Account" / "Register" / "Sign Up"
2. "Get Started" / "Try for Free"
3. INVALID: "Sign In" / "Log In" — IGNORE these unless they lead to a toggle for Sign Up

**THE "NO NEW EMAIL PROVIDER" RULE:**
- DO NOT attempt to create a new Gmail, Outlook, or Yahoo account.
- DO NOT navigate to google.com or yahoo.com to "make an email".
- You MUST use the existing test email provided below.

### SOCIAL SIGN-IN/SIGN-UP BUTTONS — DO NOT TOUCH ###
- NEVER click Google, Facebook, Apple, or any social sign-in/sign-up button. SKIP THEM ENTIRELY.
- Instead, SCROLL DOWN past the social buttons to find the email input field.
- The email signup field is usually BELOW the social buttons. Use Scroll action if you cannot see it.
- Your FIRST action on the signup page (after residence selection) should be to SCROLL DOWN to find the email field.
- Only interact with the email/password text input fields — never with social OAuth buttons.

### CREDENTIALS TO USE (MANDATORY — EXACT VALUES) ###
  - Email: __TEST_EMAIL__
  - Password: __TEST_PASSWORD__
  - Name: __TEST_NAME__
  - Phone: __TEST_PHONE__
  - OTP: Do NOT type any code manually. Use WaitForOTP action to auto-read the real code from the email inbox.
- ⚠️ You MUST type EXACTLY "__TEST_EMAIL__" into the email field. Copy-paste it character by character if needed.
- NEVER invent or make up a random email. NEVER use any other email address (e.g. specter_test@deriv.com, test@test.com, etc.).
- ALWAYS use the exact email above — the OTP reader monitors this inbox and will ONLY find codes sent to this address.
- If the form rejects the test email, report it as a UX issue and set done=true.

### OTP / VERIFICATION HANDLING (CRITICAL — REAL EMAIL) ###
- The OTP will be sent to the REAL email inbox (__TEST_EMAIL__). We read it automatically via IMAP.
- If the site asks for a verification code / OTP sent to email, use: {"action": {"type": "WaitForOTP"}, ...}
- If the site asks to click a magic link in email, use: {"action": {"type": "WaitForMagicLink"}, ...}
- Do NOT type random numbers (like 111111, 123456, etc.) into OTP fields. ALWAYS use WaitForOTP to auto-retrieve the REAL code.
- After WaitForOTP fills the code, check if there's a "Verify" / "Confirm" / "Submit" button and click it.

### FORM COMPLETION STRATEGY (CRITICAL - STRICT ORDER) ###
- Keep filling every required field until the Create Account button is pressed. Do not stop and do not set done=true until you have clicked Create Account / Sign Up / Register.
- Fill fields in STRICT top-to-bottom order as they appear on the page. Do NOT skip ahead.
- ORDER RULE: First name → Last name → Email → Password → Country (or residence) → any document upload → checkboxes → then CLICK Create Account button. Never fill Email or Password before First name and Last name.
- If you see a signup form with "First name", "Last name", "Email", "Password": fill First name FIRST, then Last name, then Email, then Password, then any other fields in visible order. Scroll if needed to see the next field, but always fill in this sequence.
- ACT on every turn. Do NOT spend more than 1 turn observing/scrolling without performing an Input/Tap/Select.
- After filling the LAST visible field, SCROLL to find any remaining fields or the submit button. Keep going until there are no empty required fields left.
- Only when ALL fields are filled (including country, document upload if present, checkboxes): CLICK THE CREATE ACCOUNT / SIGN UP / REGISTER button. Do not set done=true until you have clicked that button and see the result.
- If the submit button is not visible, SCROLL DOWN — it is almost certainly below the fold.
- DO NOT waste steps re-observing a page you already analyzed. Fill the next empty field in order; if the next field is off-screen, Scroll to bring it into view then fill it.
- Once a field is filled, do NOT scroll back to it or interact with it again. Move only to the next empty field or the next step (e.g. country, then Continue/Create Account).
- If you see a checkbox (e.g. Terms & Conditions, age verification), CHECK IT before clicking submit.
- If you see "Upload document" or file input for ID/proof, use Upload action with the provided mock file path to test the upload.

RULES:
- Perform ONE action per turn.
- Action types: Tap, Input, Scroll, KeyboardPress, Sleep, GoToPage, GoBack, Hover, Select, WaitForOTP, WaitForMagicLink, Upload
- For Tap/Input/Scroll/Hover/Select/Upload, reference an element by its numeric ID from the elements list.
- UPLOAD DOCUMENT: If the page has "Upload document", "Upload file", "Choose file", or an file input for ID/proof, use Upload to test it. Use the file path provided in the current step instructions (pick one randomly). Example: {"type":"Upload","element_id":<id>,"value":"<absolute_path>","element_description":"Upload document button"}
- MISSION END = REGISTRATION COMPLETED: The mission is finished only when registration/signup is completed. Set "done": true only when you see a clear success state (see below). Do NOT set done=true just because you filled the form or clicked something — wait for the success/confirmation screen.
- LAST STEP = CREATE ACCOUNT: Your final action before success must be clicking the "Create Account" / "Sign Up" / "Register" / "Submit" button that submits the form. Only after that click, set "done": true when you see the success/confirmation page. Do NOT set done=true while still on the form with the submit button visible.
- Set "done": true only when you see (after having clicked Create Account / Sign Up / Register):
  * Registration completed: success/confirmation page ("Account Created", "Welcome", "Verify your email", "You're registered")
  * Final submission confirmation ("You're all set", "Check your email", "Registration complete")
  * Or: error that blocks ALL progress ("Service Unavailable", infinite loading), or stuck in a loop (same action failing 3+ times)
- If you see a cookie consent banner, dismiss it first.
- If you need to scroll to find more elements, use Scroll.

DROPDOWN/SELECT HANDLING (CRITICAL):
- For country/region selectors, dropdowns, and comboboxes, ALWAYS use the Select action:
  Select: {"type":"Select","element_id":<dropdown_id>,"value":"<option text>"}
  Example: {"type":"Select","element_id":42,"value":"Indonesia"}
- The Select action handles opening the dropdown, finding the option, and selecting it automatically
- Do NOT use Tap to select dropdown options — Tap does not trigger the selection mechanism
- If you see a dropdown showing "Select" or a placeholder, use Select with the dropdown's element_id
- For native <select> elements, also use Select with the option text as value
- IMPORTANT: If a dropdown LABEL is visible but not the dropdown itself, look for an INPUT field or a clickable 
  element NEAR the label. Country dropdowns are often searchable text inputs — use Input to type the country name, 
  then Tap the matching option that appears in the suggestion list.
- Fallback approach if Select fails:
  1. Tap the dropdown/input field to open it
  2. Input the country name (e.g., "Indonesia") into the search field
  3. Wait for suggestions, then Tap the matching option from the dropdown list

COUNTRY SELECTION STRATEGY (CRITICAL — DO NOT KEEP SCROLLING):
- When you see "Country of residence" or "Country" label (or the form has name, email, password filled), the next step is to SELECT COUNTRY. Do NOT use Scroll repeatedly to "find" the country field. Use Select or Tap on the country dropdown/input.
- First try: Look in the elements list for any element related to "country", "residence", "select country", or a <select>/<input>/<combobox> near the country label. Use Select on it: {"type":"Select","element_id":<that_element_id>,"value":"Indonesia"}
- If you do not see a dedicated dropdown element but see the "Country of residence" label: TAP on the label element itself, or TAP on the closest clickable element near it (it may open a dropdown).
- If you see a "Continue" or "Next" button on the form and the country is not visible as a separate field, the country field might appear on the next page — Tap "Continue" / "Next" to proceed.
- Do NOT use Scroll more than once for the country field. If Scroll already happened, immediately try Select or Tap on the country-related element or the Continue/Next button.
- IMPORTANT: Many financial/trading sites RESTRICT certain countries (US, UK, etc). If a country fails, try a DIFFERENT one!
- Good options: Indonesia, Malaysia, Singapore, Japan, Germany, France, Australia, Brazil, India
- DO NOT keep retrying the same country if it fails or shows "No result found"

OTP HANDLING (CRITICAL — NEVER type OTP digits manually):
- If the page says "Enter the code sent to your email" or "Verify your email" or shows OTP input fields:
  {"action": {"type": "WaitForOTP"}, "observation": "OTP verification required", ...}
- Use exactly ONE WaitForOTP action. The system will automatically fill ALL OTP boxes and click Verify — even if the email reader fails, a fallback code will be entered.
- NEVER use multiple Input actions to type OTP digits one by one (e.g. "1", "2", "3"...). This is BANNED.
- If WaitForOTP fails or returns an error, use EXACTLY ONE more WaitForOTP. Do NOT switch to manual Input.
- If the page says "Click the link in your email" or "Verify via email link":
  {"action": {"type": "WaitForMagicLink"}, "observation": "Magic link verification required", ...}
- Do NOT type random numbers into OTP fields. Always use WaitForOTP.

AVOIDING REPETITION:
- Check PREVIOUS ACTIONS history - do NOT repeat an action that already failed
- If Scroll failed 2+ times: do NOT scroll again. Try Select or Tap on the target (e.g. country dropdown) using its element_id from the elements list.
- If you tried searching for a country and it failed, try a DIFFERENT country or tap a visible option
- If stuck for 2+ steps on the same element, try an alternative approach (e.g. after Scroll fails, use Select or Tap)
- On a signup form: fill First name first, then Last name, then Email, then Password. Do not fill Email or Password until First name and Last name are filled.

RESPONSE FORMAT (valid JSON only, NO markdown fences, NO extra text):
{"observation":"<what you see>","reasoning":"<why this action, from persona perspective>","action":{"type":"Tap","element_id":5,"value":null,"element_description":"Sign up button"},"ux_issues":["issue1"],"confusion_score":2,"done":false,"done_reason":null}

UX ISSUES TO DETECT:
- Form or important elements are below the fold (not visible without scrolling) after clicking a CTA
- No auto-scroll to bring user attention to the expected next step
- Form placement: signup form should be immediately visible after clicking "Create Account" or "Sign Up"
- Confusing layout, unclear next steps, poor contrast, small buttons
- Missing feedback (no loading state, no error messages, no confirmation)

CONFUSION SCORE (rate the CURRENT PAGE, not your action):
- 0-1: Crystal clear, obvious next step
- 2-3: Slightly unclear labels or small buttons
- 4-6: Confusing layout, hard to find elements, unclear flow
- 7-8: Highly confusing, ambiguous options, poor UX
- 9-10: Completely stuck, no clear path forward, page broken

If an action FAILS or nothing changes, increase confusion score on next step!

RETURN JSON OUTPUT ONLY. NO CONVERSATION. NO MARKDOWN."""


def _get_system_prompt():
    """Build system prompt with real test credentials from .env."""
    test_email = os.getenv('TEST_EMAIL_ADDRESS', 'specter_test@deriv.com')
    test_password = os.getenv('TEST_SIGNUP_PASSWORD', 'Testing123!')
    test_name = os.getenv('TEST_SIGNUP_NAME', 'Test User')
    test_phone = os.getenv('TEST_SIGNUP_PHONE', '+1234567890')
    return (
        PLANNER_SYSTEM_PROMPT
        .replace('__TEST_EMAIL__', test_email)
        .replace('__TEST_PASSWORD__', test_password)
        .replace('__TEST_NAME__', test_name)
        .replace('__TEST_PHONE__', test_phone)
    )


def build_planner_prompt(persona_cfg, device_cfg, elements_json, page_url, page_title, step_num, history, upload_mock_paths=None):
    history_text = ""
    failure_warning = ""
    
    if history:
        history_text = "\n\nPREVIOUS ACTIONS (learn from failures - DO NOT repeat failed actions):\n"
        failed_count = 0
        for h in history[-5:]:
            status_marker = "⚠️ FAILED" if "FAIL" in h['outcome'] or "No result" in h['outcome'] else "✓"
            history_text += f"  Step {h['step']}: {h['action_desc']} -> {h['outcome']} {status_marker}\n"
            if "FAIL" in h['outcome']:
                failed_count += 1
        
        # Check for repeated failures
        recent_actions = [h['action_desc'] for h in history[-3:]]
        if len(recent_actions) >= 2 and recent_actions[-1] == recent_actions[-2]:
            history_text += "\n  ⚠️ WARNING: You are repeating the same action! Try something DIFFERENT.\n"
            failure_warning = "\n⚠️ CRITICAL: Last action did nothing or failed. Increase confusion_score (7-10) and try different approach!"
        
        # If last action failed, remind to increase confusion score
        if history and "FAIL" in history[-1].get('outcome', ''):
            failure_warning = "\n⚠️ Last action FAILED - set confusion_score higher (6-9) to reflect the difficulty!"
        
        # If last 2 actions were Scroll and failed, force switch to Select/Tap (e.g. for country)
        recent_two = history[-2:] if len(history) >= 2 else history
        scroll_fails = [h for h in recent_two if "Scroll" in h.get('action_desc', '') and "FAIL" in h.get('outcome', '')]
        if len(scroll_fails) >= 2:
            history_text += "\n  ⚠️ Scroll failed multiple times. Do NOT use Scroll again. Use Select or Tap on the country dropdown/input (pick its element_id from the elements list) to open and choose a country.\n"
    
    upload_hint = ""
    if upload_mock_paths:
        pick = random.choice(upload_mock_paths)
        upload_hint = f"\n- UPLOAD: To test document upload use action type Upload with element_id of the upload button/input and value = \"{pick}\" (use this exact path).\n"
    
    return f"""CURRENT STATE:
- Step: {step_num}
- URL: {page_url}
- Page Title: {page_title}
- Device: {device_cfg['name']} ({device_cfg['viewport']['width']}x{device_cfg['viewport']['height']})
- Persona: {persona_cfg['name']} -- {persona_cfg['desc']}
- Persona Behavior: {persona_cfg['system_prompt']}
{history_text}{failure_warning}{upload_hint}

INTERACTIVE ELEMENTS ON PAGE:
{elements_json}

Decide your SINGLE next action. Respond with valid JSON only."""


# ======================================================================
# UNIFIED AI VISION HELPERS
# ======================================================================

async def _call_llm_vision(system_prompt, user_prompt, images_b64=None, max_tokens=2048):
    """Call LLM with vision support (Claude with Gemini fallback)."""
    return await call_llm_vision(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        images_b64=images_b64,
        max_tokens=max_tokens
    )


def _parse_llm_json(text):
    """Extract JSON from LLM response."""
    return parse_json_from_llm(text)


def _build_action_dict(action_type, element_id, value, element_buffer=None):
    """Build action dict for ActionExecutor.execute().
    
    If element_buffer is provided and action is Tap on a dropdown-like element,
    automatically converts to SelectDropdown for reliable selection.
    """
    # Auto-detect: if Tap targets a dropdown option, convert to SelectDropdown
    if action_type == 'Tap' and element_buffer and element_id is not None:
        elem = element_buffer.get(str(element_id), {})
        tag = (elem.get('tagName') or '').lower()
        role = (elem.get('role') or '').lower()
        class_name = (elem.get('className') or '').lower()
        parent_tag = (elem.get('parentTagName') or '').lower()
        text = (elem.get('innerText') or '').strip()
        # Detect dropdown option patterns: <option>, role=option, ant-select items, listbox items
        is_dropdown_option = (
            tag in ('option', 'li') and role in ('option', 'listbox', '') and
            any(kw in class_name for kw in ('select', 'dropdown', 'option', 'menu-item', 'ant-select', 'listbox'))
        ) or role == 'option' or (
            tag == 'select'
        )
        if is_dropdown_option and text:
            logging.info(f'Auto-converting Tap on dropdown option #{element_id} ("{text[:40]}") to SelectDropdown')
            action_type = 'Select'
            value = text

    action = {"type": action_type, "locate": {}, "param": {}}
    if action_type in ('Tap', 'Hover', 'Scroll'):
        action["locate"]["id"] = str(element_id) if element_id is not None else "0"
    elif action_type == 'Input':
        action["locate"]["id"] = str(element_id) if element_id is not None else "0"
        action["param"]["value"] = value or ""
        action["param"]["clear_before_type"] = True
    elif action_type == 'Select':
        # Use SelectDropdown for proper dropdown handling
        action["type"] = "SelectDropdown"
        action["locate"]["dropdown_id"] = str(element_id) if element_id is not None else "0"
        action["param"]["selection_path"] = value if value else ""
    elif action_type == 'KeyboardPress':
        action["param"]["value"] = value or "Enter"
    elif action_type == 'Sleep':
        action["param"]["timeMs"] = int(value) if value and str(value).isdigit() else 1000
    elif action_type == 'WaitForOTP':
        action["type"] = "WaitForOTP"
        action["param"]["sender_filter"] = value or ""
    elif action_type == 'WaitForMagicLink':
        action["type"] = "WaitForMagicLink"
        action["param"]["sender_filter"] = value or ""
    elif action_type == 'GoToPage':
        action["param"]["url"] = value or ""
    elif action_type == 'Upload':
        action["locate"]["id"] = str(element_id) if element_id is not None else "0"
        action["param"]["file_path"] = value or ""
    return action


async def _show_red_dot(page, element_buffer, element_id):
    """Show red dot on element by crawler ID."""
    try:
        eid = str(element_id)
        elem = element_buffer.get(eid) or element_buffer.get(int(eid), {})
        if elem:
            cx, cy = elem.get('center_x'), elem.get('center_y')
            if cx is not None and cy is not None:
                await page.evaluate(RED_DOT_JS, [int(cx), int(cy)])
                await asyncio.sleep(0.5)
    except Exception:
        pass


async def _diagnose_before_after(before_b64, after_b64, action_desc, expectation):
    """Dual-screenshot diagnosis via unified AI (Claude or NVIDIA)."""
    prompt = f"""Compare BEFORE and AFTER screenshots of a browser action.
Action: {action_desc}
Expected: {expectation}
Respond JSON only: {{"status":"PASSED"|"FAILED"|"PARTIAL","visual_observation":"<what changed>","diagnosis":"<root cause if failed>","severity":"P0 - Critical"|"P1 - Major"|"P2 - Minor"|"P3 - Cosmetic","responsible_team":"Frontend"|"Backend"|"UX/Design"|"N/A"}}"""
    try:
        raw = await _call_llm_vision(
            "You are a visual QA diagnosis expert. Respond with JSON only.",
            prompt,
            images_b64=[before_b64, after_b64],
            max_tokens=1024,
        )
        return _parse_llm_json(raw)
    except Exception as e:
        print(f"      Diagnosis error: {e}")
        return None


# ======================================================================
# OTP HELPER — fill all boxes in one shot, screenshot, click Verify
# ======================================================================

async def _fill_otp_boxes_and_submit(page, otp_code, action_handler, screenshot_callback, screenshot_dir, step_num, context_msg):
    """Fill OTP boxes (multi-box or single) in one shot, send screenshot, click Verify.
    Returns (success: bool, exec_msg: str)."""
    print(f"[OTP] Filling OTP code: {otp_code} ({context_msg})")

    # 1. Try multi-box OTP (e.g. 6 separate inputs with maxlength=1)
    multi_selectors = [
        'input[inputmode="numeric"][maxlength="1"]',
        'input[maxlength="1"][type="text"]',
        'input[maxlength="1"][type="tel"]',
        'input[maxlength="1"][type="number"]',
        'input[name*="code"][maxlength="1"]',
        'input[autocomplete="one-time-code"]',
    ]
    filled = False
    for multi_sel in multi_selectors:
        try:
            inputs = await page.query_selector_all(multi_sel)
            visible = [inp for inp in inputs if await inp.is_visible()]
            if len(visible) >= len(otp_code):
                async def get_xy(e):
                    b = await e.bounding_box()
                    return ((b.get('y') or 0) if b else 0, (b.get('x') or 0) if b else 0)
                with_pos = []
                for inp in visible:
                    pos = await get_xy(inp)
                    with_pos.append((pos, inp))
                with_pos.sort(key=lambda t: t[0])
                for i, (_, inp) in enumerate(with_pos[:len(otp_code)]):
                    await inp.fill(otp_code[i])
                filled = True
                print(f"[OTP] Filled {len(otp_code)} boxes in one shot via {multi_sel}")
                break
        except Exception:
            continue

    if not filled:
        # 2. Try single OTP input
        single_selectors = [
            'input[name*="otp" i]', 'input[name*="code" i]', 'input[name*="verification" i]',
            'input[name*="token" i]', 'input[type="tel"]', 'input[type="number"]',
            'input[autocomplete="one-time-code"]', 'input[inputmode="numeric"]',
        ]
        otp_input = None
        for sel in single_selectors:
            try:
                otp_input = await page.query_selector(sel)
                if otp_input and await otp_input.is_visible():
                    break
                otp_input = None
            except Exception:
                continue
        if otp_input:
            await otp_input.click()
            await asyncio.sleep(0.1)
            await otp_input.fill(otp_code)
            filled = True
            print(f"[OTP] Filled single OTP field in one shot")
        else:
            await page.keyboard.type(otp_code)
            filled = True
            print(f"[OTP] No OTP input found; typed into focused element")

    await asyncio.sleep(0.5)

    # 3. Screenshot → frontend
    if screenshot_callback:
        try:
            otp_b64, otp_path = await action_handler.b64_page_screenshot(
                file_name=f'step_{step_num:02d}_otp_filled', context='autonomous',
            )
            if otp_path:
                p = Path(otp_path)
                abs_p = str(p) if p.is_absolute() else str(Path(screenshot_dir) / p)
                await screenshot_callback(abs_p, step_num, f"OTP entered: {otp_code}")
        except Exception as cb_err:
            print(f"[OTP] Screenshot callback error: {cb_err}")

    await asyncio.sleep(0.3)

    # 4. Click Verify / Submit
    verify_selectors = [
        'button[type="submit"]',
        'button:has-text("Verify")', 'button:has-text("Verify Code")',
        'button:has-text("Confirm")', 'button:has-text("Submit")',
        'button:has-text("Continue")', 'button:has-text("Next")',
        'input[type="submit"]', '[role="button"]:has-text("Verify")',
    ]
    verify_btn = None
    for selector in verify_selectors:
        try:
            verify_btn = await page.query_selector(selector)
            if verify_btn and await verify_btn.is_visible():
                await verify_btn.click()
                print(f"[OTP] Clicked verify button: {selector}")
                break
            verify_btn = None
        except Exception:
            continue
    if not verify_btn:
        await page.keyboard.press('Enter')
        print(f"[OTP] Pressed Enter to submit OTP")

    return True, f"OTP entered: {otp_code} ({context_msg})"


# ======================================================================
# AUTONOMOUS AGENT - Fully powered by webqa_agent + Unified AI
# ======================================================================

async def autonomous_signup_test(
    url: str,
    device: str = 'desktop',
    network: str = 'wifi',
    persona: str = 'zoomer',
    locale: str = 'en-US',
    max_steps: int = 20,
    screenshot_callback = None,
    diagnostic_callback = None,
    page_callback = None,
    headless: bool = False,
    test_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Autonomous signup testing -- AI decides every step.
    
    Args:
        screenshot_callback: Optional async callback(screenshot_path, step, action) for streaming
        diagnostic_callback: Optional async callback(step, diagnostic_data) for streaming analysis results

    Uses:
    - BrowserSessionPool: browser lifecycle
    - DeepCrawler: DOM element detection + highlighting
    - ActionHandler + ActionExecutor: action execution
    - ScrollHandler: intelligent scrolling
    - Unified AI Vision API: vision + reasoning (Claude or NVIDIA)
    """
    if not AUTONOMOUS_AVAILABLE:
        print("Autonomous mode not available. Install webqa_agent.")
        return {'status': 'ERROR', 'reason': 'Dependencies missing'}

    device_cfg = DEVICES[device]
    network_cfg = NETWORKS[network]
    persona_cfg = PERSONAS[persona]

    print("\n" + "=" * 70)
    print("SPECTER AUTONOMOUS AGENT (webqa_agent + Unified AI Vision)")
    print("=" * 70)
    print(f"  URL: {url}")
    print(f"  Device: {device_cfg['name']}")
    print(f"  Network: {network_cfg['name']}")
    print(f"  Persona: {persona_cfg['name']} -- {persona_cfg['desc']}")
    print(f"  Locale: {locale}")
    print(f"  Max Steps: {max_steps}")
    print("=" * 70 + "\n")

    # -- 1. Browser via BrowserSessionPool --
    browser_config = {
        'browser_type': 'chromium',
        'viewport': device_cfg['viewport'],
        'headless': headless,
        'language': locale,
    }

    pool = BrowserSessionPool(pool_size=1, browser_config=browser_config)
    pool.disable_tab_interception = True   # Allow multi-tab / page navigation
    session = await pool.acquire(browser_config=browser_config)

    try:
        page = session.page

        # Expose the live page object to callers (e.g. live endpoint)
        if page_callback:
            await page_callback(page)

        # Network throttling via CDP
        try:
            cdp = await page.context.new_cdp_session(page)
            await cdp.send('Network.emulateNetworkConditions', {
                'offline': False,
                'downloadThroughput': network_cfg['download'],
                'uploadThroughput': network_cfg['upload'],
                'latency': network_cfg['latency'],
            })
        except Exception as e:
            print(f"  Network throttling skipped: {e}")

        # Network + console log capture
        network_logs: List[Dict] = []
        console_logs: List[str] = []

        def on_response(response):
            if response.status >= 400 or "/api" in response.url:
                network_logs.append({"status": response.status, "url": response.url, "method": response.request.method})

        def on_console(msg):
            if msg.type in ("error", "warning"):
                console_logs.append(f"[{msg.type}] {msg.text}")

        page.on("response", on_response)
        page.on("console", on_console)

        # -- 2. Navigate --
        print(f"Navigating to {url}...")
        await session.navigate_to(url)
        await asyncio.sleep(3)
        print("Page loaded\n")

        test_start_time = datetime.now()
        test_email = os.getenv('TEST_EMAIL_ADDRESS', 'specter_test@deriv.com')
        print(f"OTP reader will monitor inbox: {test_email}")
        print(f"Agent will sign up with email: {test_email}")
        print(f"Test start time (local): {test_start_time}")

        # -- 3. Initialize webqa_agent tools --
        # Ensure any prior in-process screenshot session is cleared so each
        # test run creates a fresh, unique report directory.
        ActionHandler.clear_screenshot_session()

        # Prefer initializing the screenshot session directory BEFORE creating
        # the ActionHandler instance to avoid any timing/race conditions.
        # Configure screenshot saving behavior (class-level) BEFORE initializing
        # the session so init will create the desired directory.
        ActionHandler.set_screenshot_config(save_screenshots=True)

        if test_id:
            custom_reports_dir = os.path.join('reports', test_id)
            os.makedirs(custom_reports_dir, exist_ok=True)
            screenshot_dir = ActionHandler.init_screenshot_session(custom_report_dir=custom_reports_dir)
        else:
            screenshot_dir = ActionHandler.init_screenshot_session()
        action_handler = ActionHandler()
        await action_handler.initialize(page)
        reports_dir = str(screenshot_dir.parent)
        os.makedirs(reports_dir, exist_ok=True)
        print(f"Report directory: {reports_dir}")

        executor = ActionExecutor(action_handler)
        await executor.initialize()

        crawler = DeepCrawler(page)
        scroll_handler = ScrollHandler(page)

        # Mock files for upload-document testing (no user-provided files needed)
        upload_mock_paths = ensure_upload_mock_files()
        if upload_mock_paths:
            print(f"Upload mocks: {len(upload_mock_paths)} files available for document upload steps")

        # -- 4. Autonomous Loop --
        print(f"AI will decide actions based on persona: {persona_cfg['name']}\n")

        results = []
        history = []
        confusion_scores = []

        for step_num in range(1, max_steps + 1):
            print(f"{'~' * 55}")
            print(f"Step {step_num}/{max_steps}")

            # Minimal timing between steps for speed
            if step_num > 1:
                await asyncio.sleep(0.3)  # Just enough for page to stabilize

            start_time = datetime.now()
            network_logs.clear()
            console_logs.clear()

            try:
                # -- RECOVER: If page was closed (navigation/new tab), get the latest page --
                if page.is_closed():
                    context = session.context
                    if context and context.pages:
                        page = context.pages[-1]
                        session._page = page  # Update session's internal page ref
                        crawler = DeepCrawler(page)
                        scroll_handler = ScrollHandler(page)
                        await action_handler.initialize(page)
                        await executor.initialize()
                        page.on("response", on_response)
                        page.on("console", on_console)
                        print(f"  [Recovery] Switched to new page: {page.url[:80]}")
                        await asyncio.sleep(2)
                    else:
                        print(f"  [Recovery] No pages available in context, stopping")
                        results.append({'step': step_num, 'result': 'ERROR', 'error': 'All pages closed'})
                        break

                # -- OBSERVE: Crawl DOM + Screenshot --
                crawl_result = await crawler.crawl(
                    highlight=True,
                    cache_dom=True,
                    viewport_only=False,
                )

                element_buffer = crawl_result.raw_dict()
                action_handler.set_page_element_buffer(element_buffer)

                elements_json = crawl_result.to_llm_json()

                screenshot_b64, screenshot_path = await action_handler.b64_page_screenshot(
                    file_name=f'step_{step_num:02d}_observe',
                    context='autonomous',
                )

                await crawler.remove_marker()
                
                # Stream screenshot to frontend if callback provided
                # Line 815-827 in main.py
                if screenshot_callback:
                    from pathlib import Path
                    abs_screenshot_path = None
                    try:
                        if screenshot_path:
                            p = Path(screenshot_path)
                            # FIX: Check if path is already absolute OR construct from screenshot_dir
                            if p.is_absolute():
                                abs_screenshot_path = str(p)
                            else:
                                 # Use the full relative path, not just the filename
                                 abs_screenshot_path = str(Path(screenshot_dir) / p)  # Changed from p.name to p
                    except Exception:
                        abs_screenshot_path = str(Path(screenshot_dir) / Path(screenshot_path or '').name)
    
                    await screenshot_callback(abs_screenshot_path, step_num, "Analyzing page...")
                
    
 
                print(f"  📸 Screenshot saved:")
                print(f"     Expected dir: {screenshot_dir}")
                print(f"     Returned path: {screenshot_path}")
                if screenshot_path:
                    print(f"     Path exists: {os.path.exists(screenshot_path)}")
                    print(f"     Is absolute: {Path(screenshot_path).is_absolute()}")
                page_url, page_title = await session.get_url()

                # -- DECIDE: Ask Claude what to do --
                user_prompt = build_planner_prompt(
                    persona_cfg, device_cfg, elements_json,
                    page_url, page_title, step_num, history,
                    upload_mock_paths=upload_mock_paths,
                )

                raw_response = await call_llm_vision(
                    _get_system_prompt(),
                    user_prompt,
                    images_b64=[screenshot_b64] if screenshot_b64 else None,
                    max_tokens=2048,
                )

                plan = _parse_llm_json(raw_response)
                if not plan:
                    print(f"  LLM response not parseable, retrying...")
                    raw_response = await call_llm_vision(
                        _get_system_prompt(),
                        user_prompt + "\n\nCRITICAL: Respond with valid JSON only. No markdown. No extra text.",
                        images_b64=[screenshot_b64] if screenshot_b64 else None,
                        max_tokens=2048,
                    )
                    plan = _parse_llm_json(raw_response)

                if not plan:
                    print(f"  LLM failed to return valid JSON")
                    results.append({'step': step_num, 'result': 'ERROR', 'error': 'Unparseable LLM response'})
                    continue

                observation = plan.get('observation', '')
                reasoning = plan.get('reasoning', '')
                action_plan = plan.get('action', {})
                ux_issues = plan.get('ux_issues', [])
                confusion = plan.get('confusion_score', 0)
                done = plan.get('done', False)

                print(f"  Observe: {observation[:100]}")
                print(f"  Reason:  {reasoning[:100]}")

                if confusion > 0:
                    confusion_scores.append(confusion)
                    label = "HIGH!" if confusion >= 7 else "Moderate" if confusion >= 4 else "Minor"
                    print(f"  Confusion: {confusion}/10 ({label})")

                if ux_issues:
                    for issue in ux_issues[:3]:
                        print(f"  UX Issue: {issue}")

                if done:
                    done_reason = plan.get('done_reason', 'Flow completed')
                    print(f"  DONE: {done_reason}")
                    await action_handler.b64_page_screenshot(file_name=f'step_{step_num:02d}_done', context='autonomous')
                    results.append({'step': step_num, 'result': 'DONE', 'reason': done_reason})
                    break

                # -- ACT: Execute via ActionExecutor --
                action_type = action_plan.get('type', 'Sleep')
                element_id = action_plan.get('element_id')
                value = action_plan.get('value', '')
                element_desc = action_plan.get('element_description', '')

                act_msg = f"  Action: {action_type}"
                if element_id is not None:
                    act_msg += f" #{element_id} ({element_desc})"
                if value and action_type == 'Input':
                    act_msg += f' -> "{value}"'
                print(act_msg)

                if element_id is not None:
                    await _show_red_dot(page, element_buffer, element_id)

                action_dict = _build_action_dict(action_type, element_id, value, element_buffer)

                # SAFEGUARD: If LLM tries to manually Input a single digit into an OTP field,
                # intercept and auto-fill ALL OTP boxes in one shot instead.
                if action_type == 'Input' and value and len(value) == 1 and value.isdigit():
                    # Check if the page has multi-box OTP inputs
                    otp_box_selectors = [
                        'input[inputmode="numeric"][maxlength="1"]',
                        'input[maxlength="1"][type="text"]',
                        'input[maxlength="1"][type="tel"]',
                        'input[maxlength="1"][type="number"]',
                        'input[name*="code"][maxlength="1"]',
                    ]
                    has_otp_boxes = False
                    for _sel in otp_box_selectors:
                        try:
                            _inputs = await page.query_selector_all(_sel)
                            _vis = [i for i in _inputs if await i.is_visible()]
                            if len(_vis) >= 4:  # at least 4 boxes = likely OTP
                                has_otp_boxes = True
                                break
                        except Exception:
                            continue
                    if has_otp_boxes:
                        print(f"[SAFEGUARD] LLM tried to Input single digit '{value}' into OTP box — intercepting to fill all boxes at once")
                        fallback_code = "123456"
                        success, exec_msg = await _fill_otp_boxes_and_submit(
                            page, fallback_code, action_handler, screenshot_callback,
                            screenshot_dir, step_num, "Intercepted single-digit Input; filled all OTP boxes"
                        )
                        # Skip the rest of the action execution below
                        step_result = 'OK' if success else 'FAIL'
                        result_entry = {
                            'step': step_num,
                            'action': action_type,
                            'target': element_desc or value,
                            'result': step_result,
                            'details': exec_msg,
                        }
                        results.append(result_entry)
                        _log_step(step_num, f"OTP auto-fill (intercepted)", step_result)
                        if ws_callback:
                            await ws_callback(step_num, f"OTP auto-fill (intercepted)", step_result, exec_msg)
                        continue  # skip to next step

                # Handle special action types that bypass ActionExecutor
                if action_type == 'WaitForOTP':
                    otp_email = os.getenv('TEST_EMAIL_ADDRESS')
                    otp_password = os.getenv('TEST_EMAIL_APP_PASSWORD')
                    imap_server = os.getenv('TEST_EMAIL_IMAP_SERVER', 'imap.gmail.com')
                    # For Gmail aliases (user+tag@gmail.com), IMAP login must use the real address
                    imap_login_email = os.getenv('TEST_EMAIL_IMAP_ADDRESS', otp_email)

                    if not otp_email or not otp_password:
                        # Config missing — use fallback code and fill all boxes in one shot
                        print(f"[OTP] Config missing — using fallback code and filling all OTP boxes in one shot")
                        fallback_code = "123456"
                        success, exec_msg = await _fill_otp_boxes_and_submit(
                            page, fallback_code, action_handler, screenshot_callback,
                            screenshot_dir, step_num, "OTP config missing; used fallback code"
                        )
                    else:
                        print(f"[OTP] Reading OTP from {otp_email} (IMAP login: {imap_login_email}) via {imap_server}")
                        print(f"[OTP] Polling inbox for new emails since test start...")
                        reader = OTPReader(imap_login_email, otp_password, imap_server=imap_server)
                        sender_filter = value or action_dict.get('param', {}).get('sender_filter')
                        if sender_filter:
                            print(f"[OTP] Filtering by sender: {sender_filter}")

                        try:
                            otp_result = await reader.wait_for_otp(
                                sender_filter=sender_filter,
                                since_timestamp=test_start_time,
                                timeout_seconds=120  # Extended timeout for OTP delivery
                            )

                            if otp_result['found']:
                                otp_code = otp_result['code']
                                print(f"[OTP] Found OTP code: {otp_code} (subject: {otp_result.get('email_subject', 'N/A')})")
                                success, exec_msg = await _fill_otp_boxes_and_submit(
                                    page, otp_code, action_handler, screenshot_callback,
                                    screenshot_dir, step_num, f"OTP from email (waited {otp_result['wait_time_ms']}ms)"
                                )
                                ux_issues.append(f"OTP required - {otp_result['wait_time_ms']}ms wait time")
                            else:
                                # OTP not received — use fallback code and fill all boxes
                                print(f"[OTP] OTP not received — using fallback code")
                                fallback_code = "123456"
                                success, exec_msg = await _fill_otp_boxes_and_submit(
                                    page, fallback_code, action_handler, screenshot_callback,
                                    screenshot_dir, step_num, "OTP timeout; used fallback code"
                                )
                        except Exception as e:
                            # OTP reader crashed — use fallback code and fill all boxes
                            print(f"[OTP] Exception: {e} — using fallback code")
                            traceback.print_exc()
                            fallback_code = "123456"
                            success, exec_msg = await _fill_otp_boxes_and_submit(
                                page, fallback_code, action_handler, screenshot_callback,
                                screenshot_dir, step_num, f"OTP error ({e}); used fallback code"
                            )

                elif action_type == 'WaitForMagicLink':
                    otp_email = os.getenv('TEST_EMAIL_ADDRESS')
                    otp_password = os.getenv('TEST_EMAIL_APP_PASSWORD')
                    imap_server = os.getenv('TEST_EMAIL_IMAP_SERVER', 'imap.gmail.com')
                    imap_login_email = os.getenv('TEST_EMAIL_IMAP_ADDRESS', otp_email)

                    if not otp_email or not otp_password:
                        success = False
                        exec_msg = "Magic link reader not configured (missing TEST_EMAIL_ADDRESS/TEST_EMAIL_APP_PASSWORD in .env)"
                        print(f"[MagicLink] ERROR: TEST_EMAIL_ADDRESS={'set' if otp_email else 'MISSING'}, TEST_EMAIL_APP_PASSWORD={'set' if otp_password else 'MISSING'}")
                    else:
                        print(f"[MagicLink] Reading magic link from {otp_email} (IMAP: {imap_login_email}) via {imap_server}")
                        reader = OTPReader(imap_login_email, otp_password, imap_server=imap_server)
                        sender_filter = value or action_dict.get('param', {}).get('sender_filter')

                        try:
                            link_result = await reader.wait_for_magic_link(
                                sender_filter=sender_filter,
                                since_timestamp=test_start_time,
                                timeout_seconds=120  # Extended timeout for email delivery
                            )

                            if link_result['found']:
                                print(f"[MagicLink] Found link: {link_result['link'][:80]}...")
                                await page.goto(link_result['link'])
                                success = True
                                exec_msg = f"Magic link opened (waited {link_result['wait_time_ms']}ms)"
                                ux_issues.append(f"Magic link required - {link_result['wait_time_ms']}ms wait time")
                            else:
                                success = False
                                exec_msg = f"Magic link not received within timeout: {link_result.get('error', 'timeout')}"
                                print(f"[MagicLink] {exec_msg}")
                        except Exception as e:
                            success = False
                            exec_msg = f"Magic link reader error: {str(e)}"
                            print(f"[MagicLink] Exception: {e}")
                            traceback.print_exc()

                elif action_type == 'Select' and element_id is not None:
                    # ── CUSTOM SELECT FLOW: open → screenshot → pick ──
                    # Phase 1: OPEN the dropdown (tap the element)
                    print(f"  [Select] Phase 1: Opening dropdown...")
                    tap_dict = {"type": "Tap", "locate": {"id": str(element_id)}, "param": {}}
                    await executor.execute(tap_dict)
                    await asyncio.sleep(1.5)  # wait for dropdown animation

                    # Phase 1b: Take "dropdown open" screenshot and send to frontend BEFORE selecting
                    try:
                        open_b64, open_path = await action_handler.b64_page_screenshot(
                            file_name=f'step_{step_num:02d}_dropdown_open', context='autonomous',
                        )
                        if screenshot_callback and open_path:
                            p = Path(open_path)
                            abs_open = str(p) if p.is_absolute() else str(Path(screenshot_dir) / p)
                            await screenshot_callback(abs_open, step_num, f"Select '{element_desc}' — dropdown open")
                            print(f"  [Select] Sent 'dropdown open' screenshot to frontend")
                    except Exception as ss_err:
                        print(f"  [Select] Dropdown-open screenshot error: {ss_err}")

                    await asyncio.sleep(1.0)

                    # Phase 2: Try the built-in SelectDropdown executor first
                    exec_result = await executor.execute(action_dict)
                    success = exec_result.get('success', False) if isinstance(exec_result, dict) else bool(exec_result)
                    exec_msg = exec_result.get('message', '') if isinstance(exec_result, dict) else str(exec_result)

                    # FALLBACK: If SelectDropdown failed, try type-and-pick approach
                    if not success and value:
                        print(f"  [Select] SelectDropdown failed, trying type-and-pick fallback...")
                        try:
                            # Re-open if it closed
                            await executor.execute(tap_dict)
                            await asyncio.sleep(0.5)

                            # Type the search text
                            await page.keyboard.type(value, delay=50)
                            await asyncio.sleep(1.0)

                            # Re-crawl to find matching option
                            new_crawl = await crawler.crawl(highlight=True, cache_dom=True, viewport_only=False)
                            new_buffer = new_crawl.raw_dict()
                            value_lower = value.lower()

                            matched_option_id = None
                            for eid, elem in new_buffer.items():
                                elem_text = (elem.get('innerText') or '').strip().lower()
                                elem_role = (elem.get('role') or '').lower()
                                elem_tag = (elem.get('tagName') or '').lower()
                                if elem_text and value_lower in elem_text and (
                                    elem_role in ('option', 'listbox', 'menuitem', '') or
                                    elem_tag in ('li', 'div', 'span', 'option')
                                ):
                                    if elem_text == value_lower:
                                        matched_option_id = eid
                                        break
                                    elif matched_option_id is None:
                                        matched_option_id = eid

                            if matched_option_id:
                                opt_tap = {"type": "Tap", "locate": {"id": str(matched_option_id)}, "param": {}}
                                action_handler.set_page_element_buffer(new_buffer)
                                opt_result = await executor.execute(opt_tap)
                                opt_success = opt_result.get('success', False) if isinstance(opt_result, dict) else bool(opt_result)
                                if opt_success:
                                    success = True
                                    exec_msg = f"Selected '{value}' via type-and-pick fallback"
                                    print(f"  [Select] Fallback SUCCESS: Selected '{value}'")
                                else:
                                    print(f"  [Select] Fallback: Found option but tap failed")
                            else:
                                await page.keyboard.press('Enter')
                                await asyncio.sleep(0.3)
                                success = True
                                exec_msg = f"Typed '{value}' and pressed Enter (fallback)"
                                print(f"  [Select] Fallback: No exact match, pressed Enter")
                        except Exception as fb_err:
                            print(f"  [Select] Fallback error: {fb_err}")

                else:
                    # Normal action execution through ActionExecutor
                    exec_result = await executor.execute(action_dict)
                    success = exec_result.get('success', False) if isinstance(exec_result, dict) else bool(exec_result)
                    exec_msg = exec_result.get('message', '') if isinstance(exec_result, dict) else str(exec_result)

                print(f"  Result: {'OK' if success else 'FAIL'} - {exec_msg[:80]}")

                # AUTO-DETECT COUNTRY: After a Scroll that was looking for country, proactively find & open the dropdown
                if action_type == 'Scroll' and success:
                    obs_lower = (observation + reasoning + element_desc).lower()
                    if 'country' in obs_lower or 'residence' in obs_lower:
                        print(f"  [Country Auto-Detect] Scroll was for country field — searching for dropdown on page...")
                        country_selectors = [
                            'select[name*="country" i]',
                            'select[id*="country" i]',
                            '[data-testid*="country" i]',
                            'input[placeholder*="country" i]',
                            'input[placeholder*="residence" i]',
                            'input[name*="country" i]',
                            '[role="combobox"][aria-label*="country" i]',
                            '[role="combobox"][aria-label*="residence" i]',
                            '.country-select', '.country-dropdown',
                            # Generic: any select/input near a "Country" label
                            'label:has-text("Country") + select',
                            'label:has-text("Country") + div select',
                            'label:has-text("Country") + div input',
                            'label:has-text("Country") ~ select',
                            'label:has-text("Country") ~ div select',
                            'label:has-text("residence") + select',
                            'label:has-text("residence") + div select',
                            'label:has-text("residence") + div input',
                        ]
                        country_elem = None
                        for cs in country_selectors:
                            try:
                                country_elem = await page.query_selector(cs)
                                if country_elem and await country_elem.is_visible():
                                    print(f"  [Country Auto-Detect] Found country element: {cs}")
                                    break
                                country_elem = None
                            except Exception:
                                continue

                        if country_elem:
                            try:
                                await country_elem.click()
                                await asyncio.sleep(1)
                                print(f"  [Country Auto-Detect] Clicked country element to open dropdown")
                                # Re-crawl so the LLM sees the dropdown options in the next step
                                crawl_result = await crawler.crawl(highlight=True, cache_dom=True, viewport_only=False)
                                element_buffer = crawl_result.raw_dict()
                                action_handler.set_page_element_buffer(element_buffer)
                            except Exception as ce:
                                print(f"  [Country Auto-Detect] Click failed: {ce}")
                        else:
                            print(f"  [Country Auto-Detect] No country element found via selectors; LLM will try next step")

                if action_type == 'Input' and value:
                    await asyncio.sleep(len(str(value)) * persona_cfg['typing_delay'])

                end_time = datetime.now()
                dwell_time_ms = int((end_time - start_time).total_seconds() * 1000)

                await asyncio.sleep(0.3)

                # -- AFTER screenshot --
                screenshot_after_b64, screenshot_after_path = await action_handler.b64_page_screenshot(
                    file_name=f'step_{step_num:02d}_after', context='autonomous',
                )

                # -- Broadcast REAL action to frontend --
                real_action_desc = action_type
                if element_desc:
                    real_action_desc += f" '{element_desc}'"
                if value and action_type == 'Input':
                    real_action_desc += f" → \"{value}\""
                real_action_desc += f" — {'OK' if success else 'FAIL'}"

                after_abs_path = None
                if screenshot_after_path:
                    p = Path(screenshot_after_path)
                    after_abs_path = str(p) if p.is_absolute() else str(Path(screenshot_dir) / p)
                if screenshot_callback and after_abs_path:
                    await screenshot_callback(after_abs_path, step_num, real_action_desc)

                # -- VERIFY: Dual-screenshot diagnosis --
                dual_diagnosis = None
                if screenshot_b64 and screenshot_after_b64 and screenshot_b64 != screenshot_after_b64:
                    dual_diagnosis = await _diagnose_before_after(
                        screenshot_b64, screenshot_after_b64,
                        f"{action_type} on {element_desc}",
                        "Action should progress the sign-up flow",
                    )
                    if dual_diagnosis:
                        print(f"  Diagnosis: {dual_diagnosis.get('status', '?')} - {dual_diagnosis.get('visual_observation', '')[:70]}")

                # Build history
                action_desc_text = f"{action_type}"
                if element_desc:
                    action_desc_text += f" '{element_desc}'"
                if value and action_type == 'Input':
                    action_desc_text += f" = '{value}'"
                outcome = "OK" if success else f"FAIL: {exec_msg[:40]}"
                history.append({'step': step_num, 'action_desc': action_desc_text, 'outcome': outcome})

                # -- HANDOFF to Feature 2 --
                touch_x, touch_y = 0.5, 0.5
                if element_id is not None:
                    eid = str(element_id)
                    elem = element_buffer.get(eid) or element_buffer.get(int(eid), {})
                    if elem:
                        vp = page.viewport_size
                        touch_x = elem.get('center_x', vp['width']//2) / vp['width']
                        touch_y = elem.get('center_y', vp['height']//2) / vp['height']

                handoff = {
                    'step_id': step_num,
                    'persona': f"{persona_cfg['name']} ({device_cfg['name']}, {network_cfg['name']})",
                    'action_taken': f"{action_desc_text} -> {outcome}",
                    'agent_expectation': 'Action progresses the sign-up flow',
                    'outcome': {},
                    'meta_data': {
                        'touch_x': touch_x, 'touch_y': touch_y,
                        'dwell_time_ms': dwell_time_ms,
                        'device_type': device_cfg['name'],
                        'network_type': network_cfg['name'],
                        'locale': locale, 'persona': persona_cfg['name'],
                    },
                    'evidence': {
                        'screenshot_before_path': _resolve_screenshot_path(screenshot_path) if screenshot_path else 'backend/assets/mock_before.jpg',
                        'screenshot_after_path': _resolve_screenshot_path(screenshot_after_path) if screenshot_after_path else 'backend/assets/mock_after.jpg',
                        'network_logs': list(network_logs),
                        'console_logs': list(console_logs),
                        'expected_outcome': 'Action progresses the sign-up flow',
                        'actual_outcome': action_desc_text,
                        'ui_analysis': {
                            'issues': ux_issues,
                            'confusion_score': confusion,
                            'accessibility_score': 0,
                            'elderly_friendly': confusion < 4,
                        },
                        'dual_diagnosis': dual_diagnosis,
                    },
                }

                # Build initial step report (confusion score, ux issues, evidence collected first)
                step_report = {
                    'step_id': step_num,
                    'timestamp': datetime.now().isoformat(),
                    'persona': persona_cfg['name'],
                    'device': device_cfg['name'],
                    'network': network_cfg['name'],
                    'action': action_desc_text,
                    'observation': observation,
                    'reasoning': reasoning,
                    'confusion_score': confusion,
                    'ux_issues': ux_issues,
                    'dwell_time_ms': dwell_time_ms,
                    'outcome': dual_diagnosis if dual_diagnosis else {'status': 'OK' if success else 'FAIL'},
                    'evidence': handoff['evidence'],
                }

                # Feature 2 pipeline - adds diagnosis, severity, team, f_score to handoff['outcome']
                pipeline_result = await run_specter_pipeline(handoff)
                
                # Update step_report with enriched outcome (now has diagnosis, severity, team, f_score)
                step_report['outcome'] = handoff.get('outcome', step_report['outcome'])
                
                # Save complete step report with diagnosis
                report_path = os.path.join(reports_dir, f"step_{step_num:02d}_report.json")
                with open(report_path, 'w') as f:
                    json.dump(step_report, f, indent=2)
                
                # Ensure GIF is generated for vault evidence (if screenshots exist)
                try:
                    screenshot_before = step_report.get('evidence', {}).get('screenshot_before_path')
                    screenshot_after = step_report.get('evidence', {}).get('screenshot_after_path')
                    if screenshot_before and screenshot_after:
                        # GIF should already be generated, but verify it exists
                        gif_path = os.path.join(reports_dir, f"step_{step_num:02d}.gif")
                        if not os.path.exists(gif_path):
                            print(f"  [Vault] Warning: GIF not found for step {step_num}")
                except Exception as e:
                    print(f"  [Vault] GIF check error: {e}")
                
                results.append({
                    'step': step_num, 'action': action_desc_text,
                    'result': pipeline_result, 'dwell_time': dwell_time_ms,
                    'confusion': confusion,
                })
                print(f"  Specter: {pipeline_result}")
                
                # AUTO-STOP DETECTION: Prevent wasted tokens on stuck flows
                if len(results) >= 3:
                    # Only stop when same action repeated 3 times (not 2), so agent can try Select after Scroll fails twice
                    last_3_actions = [r.get('action') for r in results[-3:]]
                    if (last_3_actions[0] == last_3_actions[1] == last_3_actions[2] and last_3_actions[0]
                            and "Scroll" not in str(last_3_actions[0])):  # allow Scroll retries so we can then try Select
                        print()
                        print("  🛑 AUTO-STOP: Same action repeated 3 times")
                        print(f"  Stuck on: {last_3_actions[0]}")
                        results.append({'step': step_num + 1, 'result': 'DONE', 'reason': 'Auto-stopped: action repetition detected'})
                        break
                
                if len(results) >= 5:
                    last_5_results = [r.get('result') for r in results[-5:]]
                    # Stop only after 5 consecutive failures (was 3) so agent can try Select/Tap after Scroll fails
                    if all(result == 'FAIL' for result in last_5_results):
                        print()
                        print("  🛑 AUTO-STOP: 5 consecutive failures detected")
                        print("  Flow appears stuck - stopping early to save tokens")
                        results.append({'step': step_num + 1, 'result': 'DONE', 'reason': 'Auto-stopped: stuck in failure loop'})
                        break
                
                # Broadcast complete diagnostic data to frontend (after diagnosis)
                if diagnostic_callback:
                    try:
                        await diagnostic_callback(step_num, step_report)
                    except Exception as cb_err:
                        print(f"  Diagnostic callback error: {cb_err}")

            except Exception as e:
                print(f"  Step error: {e}")
                traceback.print_exc()
                results.append({'step': step_num, 'result': 'ERROR', 'error': str(e)})

            print()

    finally:
        await pool.release(session)
        await pool.close_all()

    # -- Summary --
    passed = sum(1 for r in results if r.get('result') in ('PASS', 'DONE'))
    failed = len(results) - passed
    avg_confusion = sum(confusion_scores) / len(confusion_scores) if confusion_scores else 0

    print("=" * 70)
    print("AUTONOMOUS TEST COMPLETE")
    print("=" * 70)
    print(f"  Passed: {passed}/{len(results)}")
    print(f"  Failed: {failed}/{len(results)}")
    print(f"  Avg Confusion: {avg_confusion:.1f}/10" +
          (" (High!)" if avg_confusion >= 7 else " (Moderate)" if avg_confusion >= 4 else ""))
    print(f"  Reports: {reports_dir}")
    
    # Count evidence files saved to vault
    evidence_count = 0
    try:
        for file in os.listdir(reports_dir):
            if file.endswith(('.png', '.jpg', '.gif', '.json')):
                evidence_count += 1
        print(f"  Vault Evidence: {evidence_count} files saved")
    except Exception:
        pass
    
    print("=" * 70)
    
    # 🚨 SEND SUMMARY ALERT ONCE AT END (if there were failures)
    if failed > 0:
        print("\n📊 FINAL ANALYSIS SUMMARY")
        print("=" * 70)
        
        # Collect ALL issues from all steps (not just most severe)
        all_issue_reports = []
        most_severe_report = None
        severity_rank = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        
        for step_file in sorted(os.listdir(reports_dir)):
            if step_file.startswith('step_') and step_file.endswith('_report.json'):
                with open(os.path.join(reports_dir, step_file), 'r') as f:
                    report = json.load(f)
                    outcome = report.get('outcome', {})
                    dual_diag = report.get('evidence', {}).get('dual_diagnosis', {})
                    
                    # Check if there's an issue in EITHER outcome OR dual_diagnosis
                    has_outcome_issue = outcome.get('status') in ['FAILED', 'UX_ISSUE'] and outcome.get('diagnosis')
                    has_dual_diag_issue = dual_diag.get('status') == 'FAILED'
                    
                    if has_outcome_issue or has_dual_diag_issue:
                        # If outcome is empty but dual_diagnosis exists, copy it to outcome for PDF rendering
                        if not outcome.get('diagnosis') and has_dual_diag_issue:
                            report['outcome'] = {
                                'status': dual_diag['status'],
                                'diagnosis': dual_diag.get('diagnosis', ''),
                                'severity': dual_diag.get('severity', 'P2'),
                                'responsible_team': dual_diag.get('responsible_team', 'QA'),
                                'visual_observation': dual_diag.get('visual_observation', ''),
                                'recommendations': []  # dual_diagnosis doesn't have recommendations
                            }
                            outcome = report['outcome']
                        
                        all_issue_reports.append(report)
                        
                        current_severity = outcome.get('severity', 'P3')
                        current_rank = severity_rank.get(current_severity.split(' - ')[0], 3)
                        
                        if most_severe_report is None:
                            most_severe_report = report
                        else:
                            best_rank = severity_rank.get(most_severe_report['outcome'].get('severity', 'P3').split(' - ')[0], 3)
                            if current_rank < best_rank:
                                most_severe_report = report
        
        # Group issues by team and send separate PDFs to each team
        if all_issue_reports:
            try:
                # Group reports by responsible team
                from collections import defaultdict
                issues_by_team = defaultdict(list)
                overall_most_severe = all_issue_reports[0]
                
                for report in all_issue_reports:
                    team = report['outcome'].get('responsible_team', 'QA')
                    issues_by_team[team].append(report)
                    
                    # Track overall most severe for frontend update
                    current_severity = report['outcome'].get('severity', 'P3')
                    best_severity = overall_most_severe['outcome'].get('severity', 'P3')
                    current_rank = severity_rank.get(current_severity.split(' - ')[0], 3)
                    best_rank = severity_rank.get(best_severity.split(' - ')[0], 3)
                    if current_rank < best_rank:
                        overall_most_severe = report
                
                print(f"  📊 Issues found: {len(all_issue_reports)} steps across {len(issues_by_team)} teams")
                teams_alerted = list(issues_by_team.keys())
                
                # Send separate alert to each team with only their issues
                for team, team_issues in issues_by_team.items():
                    # Find most severe issue for this team
                    team_most_severe = team_issues[0]
                    for issue in team_issues[1:]:
                        current_severity = issue['outcome'].get('severity', 'P3')
                        best_severity = team_most_severe['outcome'].get('severity', 'P3')
                        current_rank = severity_rank.get(current_severity.split(' - ')[0], 3)
                        best_rank = severity_rank.get(best_severity.split(' - ')[0], 3)
                        if current_rank < best_rank:
                            team_most_severe = issue
                    
                    # Build handoff packet for this team ONLY
                    handoff_for_alert = {
                        'step_id': team_most_severe['step_id'],
                        'persona': team_most_severe['persona'],
                        'action_taken': team_most_severe['action'],
                        'agent_expectation': 'Complete signup flow',
                        'outcome': team_most_severe['outcome'],
                        'evidence': team_most_severe['evidence'],
                        'meta_data': {
                            'device_type': team_most_severe['device'],
                            'network_type': team_most_severe['network']
                        },
                        'all_issues': team_issues  # Only this team's issues
                    }
                    
                    severity = team_most_severe['outcome'].get('severity', 'P2')
                    diagnosis = team_most_severe['outcome'].get('diagnosis', 'Issues detected')
                    
                    print(f"  🚨 Sending alert to {team} team")
                    print(f"     Issues: {len(team_issues)} step(s), Severity: {severity}")
                    print(f"     Diagnosis: {diagnosis[:80]}...")
                    
                    try:
                        success = send_alert(handoff_for_alert)
                        if success:
                            print(f"  ✅ {team} PDF sent to their Slack channel")
                        else:
                            print(f"  ⚠️ {team} alert failed or no evidence; PDF generation attempted")
                    except Exception as e:
                        print(f"  ⚠️ send_alert raised exception: {e}")
                
                # Send final diagnostic update to indicate alert has been sent
                if diagnostic_callback:
                    try:
                        # Update the most severe report to indicate completion
                        teams_text = ', '.join(teams_alerted)
                        completion_update = {
                            **overall_most_severe,
                            'outcome': {
                                **overall_most_severe['outcome'],
                                'diagnosis': f"{overall_most_severe['outcome'].get('diagnosis', '')}\n\n✅ Analysis completed - PDFs sent to {teams_text} team(s)",
                                'alert_sent': True,
                                'analysis_complete': True
                            }
                        }
                        await diagnostic_callback(overall_most_severe['step_id'], completion_update)
                        print(f"  📤 Frontend updated with completion status")
                    except Exception as cb_err:
                        print(f"  Diagnostic callback error: {cb_err}")
                
            except Exception as e:
                print(f"  ⚠️  Alert failed: {e}")
                if "channel_not_found" in str(e):
                    print(f"  💡 Solution: Invite bot to channel with /invite @Specter Bot")
        
        print("=" * 70 + "\n")
    else:
        print("  ✅ No alerts needed - all steps passed!")
        
        # Send completion update to frontend
        if diagnostic_callback and len(results) > 0:
            try:
                # Send a success completion message for the last step
                last_step = results[-1]['step']
                completion_msg = {
                    'step_id': last_step,
                    'timestamp': datetime.now().isoformat(),
                    'outcome': {
                        'status': 'SUCCESS',
                        'diagnosis': '✅ Analysis completed - All steps passed successfully',
                        'analysis_complete': True,
                        'f_score': 0,
                        'severity': 'P3 - Cosmetic'
                    },
                    'evidence': {},
                    'confusion_score': 0
                }
                await diagnostic_callback(last_step, completion_msg)
                print(f"  📤 Frontend updated with completion status")
            except Exception as cb_err:
                print(f"  Diagnostic callback error: {cb_err}")
        
        print("=" * 70 + "\n")

    return {
        'status': 'PASS' if failed == 0 else 'FAIL',
        'device': device, 'network': network, 'persona': persona,
        'steps': results, 'passed': passed, 'failed': failed,
        'avg_confusion_score': round(avg_confusion, 2),
        'reports_dir': reports_dir,
    }


# ======================================================================
# SPECTER PIPELINE - Feature 2: Diagnosis Engine
# ======================================================================

async def run_specter_pipeline(handoff_packet: Dict[str, Any]) -> str:
    print(f"  Checking Step {handoff_packet['step_id']}...")
    result = check_expectation(handoff_packet)

    # Check if there are UX issues even if test passed
    ux_issues = handoff_packet.get('evidence', {}).get('ui_analysis', {}).get('issues', [])
    has_ux_issues = len(ux_issues) > 0

    if result['status'] == "SUCCESS" and not has_ux_issues:
        return "PASS"
    
    # If there are UX issues but test passed, create a UX-focused alert (but don't send yet)
    if result['status'] == "SUCCESS" and has_ux_issues:
        handoff_packet['outcome'] = {
            "status": "UX_ISSUE",
            "visual_observation": f"UX issues detected: {', '.join(ux_issues[:2])}",
            "f_score": result.get('f_score', 100),
            "calculated_severity": "P2 - Minor",  # UX-only issues are typically P2
            "gif_path": result.get('gif_path'),
            "heatmap_path": result.get('heatmap_path'),
        }
        final_packet = await diagnose_failure(handoff_packet, use_vision=True)
        
        # Mark for alert but don't send yet (will send at end of test)
        responsible_team = final_packet.get('outcome', {}).get('responsible_team', 'Design')
        print(f"  ⚠️  UX Issues ({len(ux_issues)}) detected - Will alert {responsible_team} team at test end")
        
        return "PASS_WITH_UX_ISSUES"

    handoff_packet['outcome'] = {
        "status": "FAILED",
        "visual_observation": result['reason'],
        "f_score": result.get('f_score'),
        "calculated_severity": result.get('calculated_severity'),
        "gif_path": result.get('gif_path'),
        "heatmap_path": result.get('heatmap_path'),
    }

    final_packet = await diagnose_failure(handoff_packet, use_vision=True)
    
    # Mark issue but don't send alert yet (will send summary at test end)
    severity = final_packet.get('outcome', {}).get('severity', '')
    responsible_team = final_packet.get('outcome', {}).get('responsible_team', 'Unknown')
    print(f"   Issue detected: {severity} - {responsible_team} team (Alert queued for end)")
    
    return "FAIL"


# ======================================================================
# CLI INTERFACE
# ======================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Specter: Autonomous AI QA Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py https://deriv.com/signup
  python main.py https://example.com --persona boomer --device iphone13
  python main.py https://example.com --network 3g --max-steps 20
        """
    )
    parser.add_argument('url', help='URL to test')
    parser.add_argument('--persona', default='zoomer', choices=PERSONAS.keys())
    parser.add_argument('--device', default='desktop', choices=DEVICES.keys())
    parser.add_argument('--network', default='wifi', choices=NETWORKS.keys())
    parser.add_argument('--locale', default='en-US')
    parser.add_argument('--max-steps', type=int, default=20)
    return parser.parse_args()


async def main_async():
    args = parse_args()
    os.makedirs("backend/assets", exist_ok=True)
    return await autonomous_signup_test(
        url=args.url, device=args.device, network=args.network,
        persona=args.persona, locale=args.locale, max_steps=args.max_steps,
    )


def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    result = asyncio.run(main_async())
    sys.exit(0 if result.get('status') in ('PASS', 'SUCCESS', 'DONE') else 1)


if __name__ == "__main__":
    main()
