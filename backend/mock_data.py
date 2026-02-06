# mock_data.py
def get_mock_handoff():
    return {
        "step_id": 1,
        "persona": "Rushed Commuter (Low Connectivity)", 
        "action_taken": "Clicked 'Sign Up' button",
        "agent_expectation": "I expect the loading spinner to appear or a success message.",
        "outcome": {}, 
        
        "evidence": { 
            
            "screenshot_before_path": "backend/assets/mock_before.jpg", 
            "screenshot_after_path": "backend/assets/mock_after.jpg",
            "network_logs": [
                {"status": 200, "url": "/api/config"},
                {"status": 500, "url": "/api/register", "error": "Internal Server Error"} 
            ],
            "console_logs": [
                "Warning: React unique key prop missing",
                "Error: POST /api/register 500 (Internal Server Error)"
            ]
        }
    }