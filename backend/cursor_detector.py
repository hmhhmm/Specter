# cursor_detector.py - Cursor Position Detection Utilities

"""
Cursor Detection Module

Since screenshots typically DON'T capture cursor position, this module provides
utilities to extract cursor coordinates from browser automation tools.

RECOMMENDED APPROACH:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Get coordinates from your automation framework (Selenium/Playwright/Puppeteer)
2. Pass them in the handoff packet as 'click_coords' or 'touch_x'/'touch_y'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INTEGRATION EXAMPLES:
"""

import cv2
import numpy as np


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  METHOD 1: Selenium WebDriver (RECOMMENDED)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_cursor_from_selenium_action(element, driver):
    """
    Extract cursor position from Selenium click action.
    
    Example:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        
        driver = webdriver.Chrome()
        driver.get("https://example.com")
        
        element = driver.find_element(By.ID, "signup-button")
        coords = get_cursor_from_selenium_action(element, driver)
        
        # coords = {'click_coords': (x, y), 'touch_x': ratio_x, 'touch_y': ratio_y}
    """
    
    Example:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        
        driver = webdriver.Chrome()
        driver.get("https://example.com")
        
        element = driver.find_element(By.ID, "signup-button")
        coords = get_cursor_from_selenium_action(element, driver)
        
        # coords = {'click_coords': (x, y), 'touch_x': ratio_x, 'touch_y': ratio_y}
    """
    # Get element position and size
    location = element.location
    size = element.size
    
    # Calculate center of element (where click happens)
    click_x = location['x'] + (size['width'] / 2)
    click_y = location['y'] + (size['height'] / 2)
    
    # Get viewport size
    viewport_width = driver.execute_script("return window.innerWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    
    # Convert to ratios (0.0-1.0)
    ratio_x = click_x / viewport_width
    ratio_y = click_y / viewport_height
    
    return {
        'click_coords': (int(click_x), int(click_y)),
        'touch_x': ratio_x,
        'touch_y': ratio_y
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  METHOD 2: Playwright (RECOMMENDED)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_cursor_from_playwright_action(locator, page):
    """
    Extract cursor position from Playwright click action.
    
    Example:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("https://example.com")
            
            locator = page.locator("#signup-button")
            coords = get_cursor_from_playwright_action(locator, page)
    """
    # Get element bounding box
    box = locator.bounding_box()
    
    if not box:
        return {'touch_x': 0.5, 'touch_y': 0.5}
    
    # Calculate center
    click_x = box['x'] + (box['width'] / 2)
    click_y = box['y'] + (box['height'] / 2)
    
    # Get viewport size
    viewport = page.viewport_size
    
    # Convert to ratios
    ratio_x = click_x / viewport['width']
    ratio_y = click_y / viewport['height']
    
    return {
        'click_coords': (int(click_x), int(click_y)),
        'touch_x': ratio_x,
        'touch_y': ratio_y
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  METHOD 3: Puppeteer (Node.js → Python Bridge)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def parse_puppeteer_coords(puppeteer_json):
    """
    Parse cursor coordinates from Puppeteer JSON output.
    
    Puppeteer Example (JavaScript):
        const element = await page.$('#signup-button');
        const box = await element.boundingBox();
        const clickX = box.x + (box.width / 2);
        const clickY = box.y + (box.height / 2);
        
        const viewport = await page.viewport();
        const coords = {
            click_x: clickX,
            click_y: clickY,
            viewport_width: viewport.width,
            viewport_height: viewport.height
        };
        
        // Send to Python via JSON
    
    Python Usage:
        coords = parse_puppeteer_coords(json_data)
    """
    click_x = puppeteer_json.get('click_x', 0)
    click_y = puppeteer_json.get('click_y', 0)
    vp_width = puppeteer_json.get('viewport_width', 1)
    vp_height = puppeteer_json.get('viewport_height', 1)
    
    return {
        'click_coords': (int(click_x), int(click_y)),
        'touch_x': click_x / vp_width,
        'touch_y': click_y / vp_height
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  METHOD 4: Visual Cursor Detection (FALLBACK - Low Accuracy)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def detect_cursor_visual(screenshot_path):
    """
    FALLBACK METHOD: Detect cursor in screenshot using template matching.
    
    WARNING: Very unreliable because:
    - Most screenshot tools don't capture the cursor
    - Cursor appearance varies by OS/theme
    - Requires cursor templates for each OS
    
    Only use this if you can't get coordinates from automation tool.
    """
    img = cv2.imread(screenshot_path)
    if img is None:
        return None
    
    # Load cursor templates (you need to create these)
    # Example: cursor_templates/windows_arrow.png, mac_arrow.png, etc.
    templates = [
        "backend/assets/cursor_templates/default_arrow.png",
        # Add more cursor templates here
    ]
    
    best_match = None
    best_score = 0
    
    for template_path in templates:
        try:
            template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
            if template is None:
                continue
            
            # Template matching
            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_score:
                best_score = max_val
                # Cursor tip is at top-left of template
                best_match = max_loc
        except:
            continue
    
    if best_match and best_score > 0.6:
        height, width = img.shape[:2]
        return {
            'click_coords': best_match,
            'touch_x': best_match[0] / width,
            'touch_y': best_match[1] / height
        }
    
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELPER: Integrate into Handoff Packet
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def enrich_handoff_with_cursor(handoff_packet, automation_framework="selenium", **kwargs):
    """
    Automatically adds cursor coordinates to handoff packet.
    
    Usage:
        # With Selenium
        enrich_handoff_with_cursor(packet, "selenium", element=btn, driver=driver)
        
        # With Playwright
        enrich_handoff_with_cursor(packet, "playwright", locator=btn, page=page)
        
        # With Puppeteer JSON
        enrich_handoff_with_cursor(packet, "puppeteer", json_data=coords)
    """
    coords = None
    
    if automation_framework == "selenium":
        element = kwargs.get('element')
        driver = kwargs.get('driver')
        if element and driver:
            coords = get_cursor_from_selenium_action(element, driver)
    
    elif automation_framework == "playwright":
        locator = kwargs.get('locator')
        page = kwargs.get('page')
        if locator and page:
            coords = get_cursor_from_playwright_action(locator, page)
    
    elif automation_framework == "puppeteer":
        json_data = kwargs.get('json_data')
        if json_data:
            coords = parse_puppeteer_coords(json_data)
    
    # Fallback to visual detection
    if not coords:
        screenshot_path = handoff_packet['evidence'].get('screenshot_before_path')
        if screenshot_path:
            coords = detect_cursor_visual(screenshot_path)
    
    # Update packet
    if coords:
        if 'meta_data' not in handoff_packet:
            handoff_packet['meta_data'] = {}
        
        handoff_packet['meta_data'].update({
            'touch_x': coords['touch_x'],
            'touch_y': coords['touch_y']
        })
        
        handoff_packet['evidence']['click_coords'] = coords.get('click_coords')
    
    return handoff_packet


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  USAGE EXAMPLE IN AGENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
# In your test agent (e.g., agent_test.py):

from selenium import webdriver
from selenium.webdriver.common.by import By
from backend.cursor_detector import enrich_handoff_with_cursor
from backend.mock_data import get_mock_handoff

driver = webdriver.Chrome()
driver.get("https://myapp.com/signup")

# User action
button = driver.find_element(By.ID, "submit-btn")
button.click()

# Create handoff packet
packet = get_mock_handoff()

# Automatically add cursor coordinates
enrich_handoff_with_cursor(packet, "selenium", element=button, driver=driver)

# Now packet has:
# - 'meta_data': {'touch_x': 0.65, 'touch_y': 0.45, ...}
# - 'evidence': {'click_coords': (650, 450), ...}

# Send to Specter
run_specter_pipeline(packet)
"""
