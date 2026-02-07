#!/usr/bin/env python3
"""
Demo that intentionally creates a failure to show heatmap + GIF generation
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.mock_data import get_mock_handoff
from main import run_specter_pipeline

def demo_failure_pipeline():
    """
    Demonstrates complete failure diagnosis with heatmap + GIF
    """
    
    print("=" * 70)
    print("🎬 SPECTER FAILURE DEMO - Full Pipeline")
    print("=" * 70)
    print()
    print("This demo uses mock failure data to show:")
    print("  1. F-Score calculation (friction metric)")
    print("  2. Dynamic heatmap generation")
    print("  3. Animated GIF creation")
    print("  4. Claude Vision diagnosis")
    print("  5. Slack escalation")
    print()
    print("=" * 70)
    print()
    
    # Get mock failure packet
    packet = get_mock_handoff()
    
    # This will trigger all artifact generation
    result = run_specter_pipeline(packet)
    
    print()
    print("=" * 70)
    print("📁 GENERATED ARTIFACTS:")
    print("=" * 70)
    print()
    print("✅ Heatmap: backend/assets/evidence_heatmap.jpg")
    print("✅ GIF:     backend/assets/ghost_replay.gif")
    print("✅ Screenshots: backend/assets/mock_before.jpg")
    print("                backend/assets/mock_after.jpg")
    print()
    print("🔍 Open these files to see the dynamic visualizations!")
    print()
    print("=" * 70)
    
    return result

if __name__ == "__main__":
    demo_failure_pipeline()
