#!/usr/bin/env python3
"""
Force a HIGH FRICTION failure to demonstrate complete pipeline
"""

import asyncio
import sys
from pathlib import Path
import os
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from playwright.async_api import async_playwright
from webqa_agent.actions.action_handler import ActionHandler
from main import run_specter_pipeline
from backend.webqa_bridge import _resolve_screenshot_path

async def force_high_friction_test():
    """Test with artificially high friction to trigger full pipeline"""
    
    print("=" * 70)
    print("🔥 HIGH FRICTION TEST: Broken UI with Network Errors")
    print("=" * 70)
    print()
    
    ActionHandler.set_screenshot_config(save_screenshots=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        console_errors = []
        page.on('console', lambda msg: console_errors.append(str(msg.text)) if msg.type in ['error', 'warning'] else None)
        
        print("🌐 Loading broken UI...")
        await page.goto('https://mocked-website.vercel.app/', wait_until='domcontentloaded')
        await asyncio.sleep(2)
        
        action_handler = ActionHandler()
        action_handler.page = page
        
        print("🧪 Simulating confused user struggling with form")
        print("   - Multiple attempts to interact")
        print("   - Long delays (high dwell time)")
        print("   - Network timeouts")
        print()
        
        start_time = datetime.now()
        
        # Before screenshot
        screenshot_before, screenshot_before_path = await action_handler.b64_page_screenshot(
            file_name='high_friction_before',
            context='high_friction'
        )
        
        # Simulate user confusion - multiple clicks, delays
        try:
            submit_btn = await page.query_selector('button[type="submit"], button')
            if submit_btn:
                # First click
                await submit_btn.click()
                await asyncio.sleep(2)
                
                # User waits confused...
                await asyncio.sleep(3)
                
                # Tries again
                await submit_btn.click()
                await asyncio.sleep(2)
        except:
            pass
        
        end_time = datetime.now()
        dwell_time_ms = int(( end_time - start_time).total_seconds() * 1000)
        
        # After screenshot
        screenshot_after, screenshot_after_path = await action_handler.b64_page_screenshot(
            file_name='high_friction_after',
            context='high_friction'
        )
        
        # Simulate network errors
        network_logs = [
            {'status': 502, 'url': '/api/submit', 'duration': 5000},
            {'status': 500, 'url': '/api/auth', 'duration': 3200},
            {'status': 404, 'url': '/api/validate', 'duration': 1500},
        ]
        
        # Add console errors
        console_errors.extend([
            'TypeError: Cannot read property "submit" of null',
            'Network request failed: timeout after 5000ms',
            'Error: Form validation failed',
        ])
        
        # Build HIGH FRICTION handoff
        handoff = {
            'step_id': 1,
            'persona': 'Confused User (iPhone, Slow 3G)',
            'action_taken': 'Multiple click attempts on broken submit button',
            'agent_expectation': 'Form should submit within 2 seconds',
            'outcome': {},
            'meta_data': {
                'touch_x': 0.5,
                'touch_y': 0.75,
                'dwell_time_ms': dwell_time_ms,  # Will be ~7000ms
                'device_type': 'iPhone 13 Pro',
                'network_type': 'Slow 3G',
                'locale': 'en-US',
                'persona': 'confused',
            },
            'evidence': {
                'screenshot_before_path': _resolve_screenshot_path(screenshot_before_path),
                'screenshot_after_path': _resolve_screenshot_path(screenshot_after_path),
                'network_logs': network_logs,
                'console_logs': console_errors,
                'expected_outcome': 'Success message or next page',
                'actual_outcome': 'Page frozen, multiple errors',
            }
        }
        
        print(f"   ⏱️  Dwell time: {dwell_time_ms}ms (very high)")
        error_count = len([l for l in network_logs if l['status'] >= 400])
        print(f"   🌐 Network errors: {error_count}")
        print(f"   🐛 Console errors: {len(console_errors)}")
        print()
        
        # Run Specter pipeline - should trigger FAIL
        result = run_specter_pipeline(handoff)
        
        await browser.close()
        
        print()
        print("=" * 70)
        print("🎉 COMPLETE! Your artifacts are ready:")
        print("=" * 70)
        print()
        
        if screenshot_after_path:
            report_dir = os.path.dirname(os.path.dirname(_resolve_screenshot_path(screenshot_after_path)))
            
            print(f"📁 {report_dir}")
            print(f"   📸 screenshots/         - Before/after captures")
            print(f"   🎨 heatmap.png         - Dynamic AI uncertainty heatmap")
            print(f"   🎬 ghost_replay.gif    - Animated failure replay")
            print()
            print("These are YOUR test artifacts from the broken UI!")
            print()
            
            # Open folder
            import subprocess
            subprocess.run(['explorer', report_dir.replace('/', '\\\\')])
        
        print("=" * 70)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(force_high_friction_test())
