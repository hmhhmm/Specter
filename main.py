# main.py (The "Pro" Orchestrator)
from backend.mock_data import get_mock_handoff
from backend.expectation_engine import check_expectation
from backend.diagnosis_doctor import diagnose_failure
from backend.escalation_webhook import send_alert
import os

def run_specter_pipeline(handoff_packet):
    print(f"\n👻 Specter Pipeline Triggered for Step {handoff_packet['step_id']}")
    
    # 1. Check Expectation (Generates Pro-Grade Heatmap & Cinematic GIF)
    result = check_expectation(handoff_packet)
    
    if result['status'] == "SUCCESS":
        print("✅ Step passed. No alert needed.")
        return "PASS"
    
    # 2. Add Outcome & Rich Media Paths
    print(f"❌ Failure Detected: {result['reason']}")
    
    # Merge result into handoff packet
    handoff_packet['outcome'] = {
        "status": "FAILED",
        "visual_observation": result['reason'],
        "f_score": result.get('f_score'),
        "calculated_severity": result.get('calculated_severity'), # Key for the Doctor
        "gif_path": result.get('gif_path'),
        "heatmap_path": result.get('heatmap_path')
    }
    
    # 3. Diagnose with Brain (Claude Haiku)
    # The Doctor will now see the 'calculated_severity' and respect it
    final_packet = diagnose_failure(handoff_packet)
    
    # 4. Escalate (Uploads the Cinematic GIF to Slack)
    send_alert(final_packet)
    return "FAIL"

if __name__ == "__main__":
    # Ensure assets folder exists
    if not os.path.exists("backend/assets"):
        os.makedirs("backend/assets")
        print("📁 Created backend/assets directory")

    # Load the Pro-Grade Mock Data
    packet = get_mock_handoff()
    
    # Run the Pipeline
    run_specter_pipeline(packet)