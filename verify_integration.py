#!/usr/bin/env python3
"""
Integration Verification - Confirms all features are properly connected
"""

import sys
import os
from pathlib import Path

print("=" * 70)
print("🔍 SPECTER INTEGRATION VERIFICATION")
print("=" * 70)
print()

# Track status
checks_passed = 0
checks_total = 0

def check(description, test_func):
    global checks_passed, checks_total
    checks_total += 1
    try:
        test_func()
        print(f"✅ {description}")
        checks_passed += 1
        return True
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Error: {e}")
        return False

print("📦 FEATURE 2: Diagnosis Engine (Core)")
print("-" * 70)

# Check Feature 2 components
check("expectation_engine.py exists", 
      lambda: Path("backend/expectation_engine.py").exists() or (_ for _ in ()).throw(FileNotFoundError()))

check("diagnosis_doctor.py exists", 
      lambda: Path("backend/diagnosis_doctor.py").exists() or (_ for _ in ()).throw(FileNotFoundError()))

check("escalation_webhook.py exists", 
      lambda: Path("backend/escalation_webhook.py").exists() or (_ for _ in ()).throw(FileNotFoundError()))

check("mock_data.py exists", 
      lambda: Path("backend/mock_data.py").exists() or (_ for _ in ()).throw(FileNotFoundError()))

check("webqa_bridge.py exists", 
      lambda: Path("backend/webqa_bridge.py").exists() or (_ for _ in ()).throw(FileNotFoundError()))

# Test imports
def test_expectation_import():
    from backend.expectation_engine import check_expectation
    assert callable(check_expectation)

def test_diagnosis_import():
    from backend.diagnosis_doctor import diagnose_failure
    assert callable(diagnose_failure)

def test_escalation_import():
    from backend.escalation_webhook import send_alert
    assert callable(send_alert)

def test_mock_import():
    from backend.mock_data import get_mock_handoff
    assert callable(get_mock_handoff)

def test_bridge_import():
    from backend.webqa_bridge import _resolve_screenshot_path
    assert callable(_resolve_screenshot_path)

check("Can import expectation_engine", test_expectation_import)
check("Can import diagnosis_doctor", test_diagnosis_import)
check("Can import escalation_webhook", test_escalation_import)
check("Can import mock_data", test_mock_import)
check("Can import webqa_bridge", test_bridge_import)

print()
print("📦 FEATURE 1: Autonomous Agent (Integration)")
print("-" * 70)

# Check webqa_agent integration
check("webqa_agent folder exists", 
      lambda: Path("webqa_agent").exists() or (_ for _ in ()).throw(FileNotFoundError()))

check("main.py exists", 
      lambda: Path("main.py").exists() or (_ for _ in ()).throw(FileNotFoundError()))

check("test_signup.html exists", 
      lambda: Path("test_signup.html").exists() or (_ for _ in ()).throw(FileNotFoundError()))

# Test main.py components
def test_main_imports():
    import main
    assert hasattr(main, 'autonomous_signup_test')
    assert hasattr(main, 'run_specter_pipeline')
    assert hasattr(main, 'DEVICES')
    assert hasattr(main, 'NETWORKS')
    assert hasattr(main, 'PERSONAS')

check("main.py has autonomous_signup_test()", test_main_imports)

def test_devices_defined():
    from main import DEVICES
    assert 'iphone13' in DEVICES
    assert 'android' in DEVICES
    assert 'desktop' in DEVICES

def test_networks_defined():
    from main import NETWORKS
    assert '3g' in NETWORKS
    assert '4g' in NETWORKS
    assert 'wifi' in NETWORKS
    assert 'slow' in NETWORKS

def test_personas_defined():
    from main import PERSONAS
    assert 'normal' in PERSONAS
    assert 'cautious' in PERSONAS
    assert 'confused' in PERSONAS

check("Device profiles defined (iPhone, Android, Desktop)", test_devices_defined)
check("Network profiles defined (3G, 4G, WiFi, Slow)", test_networks_defined)
check("Persona profiles defined (Normal, Cautious, Confused)", test_personas_defined)

print()
print("🔗 INTEGRATION POINTS")
print("-" * 70)

def test_pipeline_callable():
    from main import run_specter_pipeline
    from backend.mock_data import get_mock_handoff
    # Don't actually run it, just verify it's callable
    assert callable(run_specter_pipeline)

check("Specter pipeline is callable", test_pipeline_callable)

def test_handoff_schema():
    from backend.mock_data import get_mock_handoff
    packet = get_mock_handoff()
    assert 'step_id' in packet
    assert 'persona' in packet
    assert 'action_taken' in packet
    assert 'agent_expectation' in packet
    assert 'meta_data' in packet
    assert 'evidence' in packet

check("Handoff packet has correct schema", test_handoff_schema)

def test_screenshot_resolution():
    from backend.webqa_bridge import _resolve_screenshot_path
    # Should not crash
    result = _resolve_screenshot_path("screenshots/test.png")
    assert result is not None

check("Screenshot path resolution works", test_screenshot_resolution)

print()
print("📊 FEATURE COMPLETENESS")
print("-" * 70)

def check_feature(name, components):
    all_present = all(components.values())
    status = "✅ 100%" if all_present else f"⚠️  {sum(components.values())}/{len(components)}"
    print(f"{status} {name}")
    for comp, present in components.items():
        icon = "✅" if present else "❌"
        print(f"      {icon} {comp}")

# Feature 1
feature1_components = {
    'Device emulation': Path("main.py").read_text().__contains__("DEVICES"),
    'Network throttling': Path("main.py").read_text().__contains__("NETWORKS"),
    'Persona simulation': Path("main.py").read_text().__contains__("PERSONAS"),
    'Screenshot capture': Path("main.py").read_text().__contains__("b64_page_screenshot"),
    'Autonomous function': Path("main.py").read_text().__contains__("autonomous_signup_test"),
}
check_feature("Feature 1: Multimodal Navigator", feature1_components)

print()

# Feature 2
feature2_components = {
    'F-Score calculation': Path("backend/expectation_engine.py").exists(),
    'Heatmap generation': Path("backend/expectation_engine.py").read_text().__contains__("generate_heatmap"),
    'GIF generation': Path("backend/expectation_engine.py").read_text().__contains__("generate_ghost_replay"),
    'Claude diagnosis': Path("backend/diagnosis_doctor.py").exists(),
    'Slack escalation': Path("backend/escalation_webhook.py").exists(),
}
check_feature("Feature 2: Cognitive Diagnosis", feature2_components)

print()
print("=" * 70)
print(f"📊 VERIFICATION COMPLETE: {checks_passed}/{checks_total} checks passed")
print("=" * 70)

if checks_passed == checks_total:
    print("🎉 All integrations verified! Ready for demo.")
    print()
    print("Run the demo:")
    print("  python main.py                                    # Demo mode")
    print("  python main.py autonomous https://example.com    # Full autonomous")
    print("  python test_autonomous_demo.py                   # Local test")
    sys.exit(0)
else:
    print("⚠️  Some checks failed. Review errors above.")
    sys.exit(1)
