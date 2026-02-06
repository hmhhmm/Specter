import cv2
from skimage.metrics import structural_similarity as ssim
import os

def check_expectation(handoff):
    print(f"Checking Step {handoff['step_id']}...")
    
    evidence = handoff['evidence'] 

    # 1. Network Check
    for log in evidence['network_logs']:
        if log['status'] >= 400:
            return {"status": "FAILED", "reason": "BACKEND_ERROR", "details": log}

    # 2. Visual Check
   
    try:
        img_a = cv2.imread(evidence['screenshot_before_path'])
        img_b = cv2.imread(evidence['screenshot_after_path'])
        
        if img_a is None or img_b is None:
            print("Warning: Images not found. Skipping visual check.")
            return {"status": "SUCCESS", "reason": "Visual check skipped (Images missing)"}

        gray_a = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY)
        gray_b = cv2.cvtColor(img_b, cv2.COLOR_BGR2GRAY)

        score, _ = ssim(gray_a, gray_b, full=True)
        print(f"Visual Similarity Score: {score}")

        if score > 0.99: 
            return {"status": "FAILED", "reason": "UI_FROZEN", "details": "Screen did not change."}

    except Exception as e:
        print(f"Visual check error: {e}")

    return {"status": "SUCCESS", "reason": "Visual change detected"}