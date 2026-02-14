import time
import re
from typing import List, Dict
from database import get_unprocessed_events, mark_event_processed, insert_validation_result

class Agent1Validator:
    """
    Agent 1: Data Ingestion Monitor (Rule-based)
    Validates clickstream events for data quality and compliance issues
    """
    
    def __init__(self):
        self.name = "Agent 1: Data Validator"
        self.status = "Idle"
        self.events_processed = 0
        self.issues_found = 0
        
    def validate_event(self, event: Dict) -> tuple[str, List[str]]:
        """
        Validate a single event and return status + issues
        Returns: (status, issues_list)
        """
        issues = []
        
        # Check required fields
        if not event.get('session_id'):
            issues.append("Missing session_id")
        if not event.get('event_type'):
            issues.append("Missing event_type")
        if not event.get('page_url'):
            issues.append("Missing page_url")
            
        # Check consent flag (CRITICAL - only consented events allowed)
        if event.get('consent_given') is None or event.get('consent_given') == 0:
            issues.append("COMPLIANCE VIOLATION: Event captured without user consent - only consented events are allowed")
        
        # Check email encryption (CRITICAL for clickstream data)
        if event.get('user_email'):
            email = event.get('user_email')
            # Check if email is SHA256 hashed (64 hex characters)
            is_hashed = len(email) == 64 and all(c in '0123456789abcdef' for c in email.lower())
            
            if not is_hashed and not event.get('encrypt_email'):
                issues.append("SECURITY VIOLATION: Unencrypted email detected - clickstream must only capture encrypted emails")
            elif is_hashed:
                # Email is properly hashed, mark as encrypted
                event['encrypt_email'] = True
            
        # Validate email format if present
        if event.get('user_email'):
            email = event.get('user_email')
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                issues.append(f"Invalid email format: {email}")
                
        # Check for suspicious IP patterns (basic check)
        if event.get('ip_address'):
            ip = event.get('ip_address')
            # Check if it's a valid IPv4 format
            ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
            if not re.match(ip_pattern, ip):
                issues.append(f"Invalid IP format: {ip}")
            # Check for localhost/private IPs (optional warning)
            elif ip.startswith('127.') or ip.startswith('0.'):
                issues.append(f"Localhost/invalid IP detected: {ip}")
        
        # Determine status - compliance violations are always ERROR
        if any("VIOLATION" in issue for issue in issues):
            status = "ERROR"
        elif any("Missing" in issue for issue in issues):
            status = "ERROR"
        else:
            status = "VALID"
            
        return status, issues
    
    def run(self):
        """Main agent loop - polls database for new events"""
        print(f"🤖 {self.name} started")
        
        while True:
            try:
                # Get unprocessed events
                events = get_unprocessed_events()
                
                if events:
                    self.status = f"Processing {len(events)} events"
                    print(f"[Agent 1] Found {len(events)} new events to validate")
                    
                    for event in events:
                        # Validate event
                        status, issues = self.validate_event(event)
                        
                        # Log result
                        if issues:
                            self.issues_found += 1
                            print(f"[Agent 1] ⚠️  Event {event['id']} - {status}: {', '.join(issues)}")
                        else:
                            print(f"[Agent 1] ✅ Event {event['id']} - VALID")
                        
                        # Save validation result
                        insert_validation_result(
                            event_id=event['id'],
                            session_id=event['session_id'],
                            status=status,
                            issues=issues
                        )
                        
                        # Mark as processed
                        mark_event_processed(event['id'])
                        self.events_processed += 1
                    
                    self.status = f"Validated {self.events_processed} events | Found {self.issues_found} issues"
                else:
                    self.status = "Monitoring for new events..."
                
                # Poll every 3 seconds
                time.sleep(3)
                
            except Exception as e:
                print(f"[Agent 1] ❌ Error: {e}")
                self.status = f"Error: {e}"
                time.sleep(5)

def start_agent1():
    """Start Agent 1 in background thread"""
    agent = Agent1Validator()
    agent.run()

if __name__ == "__main__":
    start_agent1()
