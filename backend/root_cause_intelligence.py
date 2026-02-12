"""Root cause intelligence for linking similar issues."""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class RootCauseIntelligence:
    """Analyze and link similar failures for pattern detection."""
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = reports_dir
    
    def calculate_similarity(self, issue1: Dict, issue2: Dict) -> float:
        """Calculate similarity score between two issues (0-100)."""
        score = 0.0
        weights = {
            'error_type': 30,
            'component': 20,
            'diagnosis': 25,
            'team': 15,
            'severity': 10
        }
        
        # Compare error patterns
        if issue1.get('error_type') == issue2.get('error_type'):
            score += weights['error_type']
        
        # Compare affected component
        if issue1.get('component_affected') == issue2.get('component_affected'):
            score += weights['component']
        
        # Compare diagnosis text similarity
        diag1 = issue1.get('diagnosis', '').lower()
        diag2 = issue2.get('diagnosis', '').lower()
        common_words = set(diag1.split()) & set(diag2.split())
        if len(common_words) > 3:
            score += weights['diagnosis'] * (len(common_words) / 10)
        
        # Compare responsible team
        if issue1.get('responsible_team') == issue2.get('responsible_team'):
            score += weights['team']
        
        # Compare severity
        if issue1.get('severity') == issue2.get('severity'):
            score += weights['severity']
        
        return min(score, 100)
    
    def extract_issue_signature(self, report_data: Dict) -> Dict:
        """Extract key characteristics from a test report."""
        outcome = report_data.get('outcome', {})
        steps = report_data.get('steps', [])
        
        # Identify error type from diagnosis
        diagnosis = outcome.get('diagnosis', '').lower()
        error_type = 'unknown'
        if 'network' in diagnosis or 'api' in diagnosis or '500' in diagnosis:
            error_type = 'network'
        elif 'element' in diagnosis or 'button' in diagnosis or 'selector' in diagnosis:
            error_type = 'ui_element'
        elif 'validation' in diagnosis or 'form' in diagnosis:
            error_type = 'validation'
        elif 'timeout' in diagnosis or 'slow' in diagnosis:
            error_type = 'performance'
        
        # Extract affected component from steps
        component = 'unknown'
        for step in steps:
            step_desc = step.get('step_description', '').lower()
            if 'country' in step_desc or 'dropdown' in step_desc:
                component = 'country_selector'
            elif 'email' in step_desc:
                component = 'email_input'
            elif 'password' in step_desc:
                component = 'password_input'
            elif 'submit' in step_desc or 'sign up' in step_desc:
                component = 'submit_button'
        
        return {
            'error_type': error_type,
            'component_affected': component,
            'diagnosis': outcome.get('diagnosis', ''),
            'responsible_team': outcome.get('responsible_team', ''),
            'severity': outcome.get('severity', 'P3'),
            'f_score': outcome.get('f_score', 0)
        }
    
    def find_similar_issues(self, current_issue: Dict, threshold: float = 70) -> List[Dict]:
        """Find historical issues similar to the current one."""
        similar_issues = []
        
        if not os.path.exists(self.reports_dir):
            return similar_issues
        
        # Scan all past reports
        for test_folder in os.listdir(self.reports_dir):
            folder_path = os.path.join(self.reports_dir, test_folder)
            if not os.path.isdir(folder_path):
                continue
            
            # Look for final report JSON
            for file in os.listdir(folder_path):
                if file.endswith('_report.json'):
                    report_path = os.path.join(folder_path, file)
                    try:
                        with open(report_path, 'r', encoding='utf-8') as f:
                            report_data = json.load(f)
                            
                        historical_signature = self.extract_issue_signature(report_data)
                        similarity = self.calculate_similarity(current_issue, historical_signature)
                        
                        if similarity >= threshold:
                            similar_issues.append({
                                'test_id': test_folder,
                                'similarity': round(similarity, 1),
                                'diagnosis': historical_signature['diagnosis'],
                                'severity': historical_signature['severity'],
                                'timestamp': self._parse_timestamp_from_folder(test_folder)
                            })
                    except Exception as e:
                        print(f"Error reading {report_path}: {e}")
                        continue
        
        # Sort by similarity descending
        similar_issues.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_issues[:5]  # Return top 5 matches
    
    def _parse_timestamp_from_folder(self, folder_name: str) -> str:
        """Extract timestamp from folder name like 'test_2026-02-07_15-32-51'."""
        try:
            parts = folder_name.split('_')
            if len(parts) >= 3:
                date = parts[1]
                time = parts[2].split('_')[0]
                return f"{date} {time.replace('-', ':')}"
        except:
            pass
        return "Unknown"
    
    def analyze_with_root_cause(self, report_data: Dict) -> Dict:
        """Enhance diagnosis with root cause intelligence."""
        current_signature = self.extract_issue_signature(report_data)
        similar_issues = self.find_similar_issues(current_signature)
        
        return {
            'current_issue': current_signature,
            'similar_issues': similar_issues,
            'is_recurring': len(similar_issues) > 0,
            'recurrence_count': len(similar_issues),
            'pattern_detected': len(similar_issues) >= 2
        }
