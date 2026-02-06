import sys
import os

sys.path.append(os.getcwd())

from backend.mock_data import get_mock_handoff
from backend.expectation_engine import check_expectation
from backend.diagnosis_doctor import diagnose_failure
from backend.escalation_webhook import send_alert

def run_specter_pipeline(handoff_packet):
    print(f"\nSpecter Pipeline Triggered for Step {handoff_packet['step_id']}")
    
    # 1. Check Expectation
    result = check_expectation(handoff_packet)
    
    if result['status'] == "SUCCESS":
        print("Step passed. No alert needed.")
        return "PASS"
    
    # 2. If Failed, Add Outcome
    print(f"Failure Detected: {result['reason']}")
    handoff_packet['outcome'] = {
        "status": "FAILED",
        "visual_observation": result['reason']
    }
    
    # 3. Diagnose with Brain
    final_packet = diagnose_failure(handoff_packet)
    
    # 4. Escalate
    send_alert(final_packet)
    return "FAIL"

if __name__ == "__main__":
    # Simulate a run with mock data
    packet = get_mock_handoff()
    run_specter_pipeline(packet)