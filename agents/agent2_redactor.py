import time
import re
from typing import List, Dict
from database import (
    get_unredacted_sessions, 
    mark_validation_processed, 
    insert_redacted_session
)

class Agent2Redactor:
    """
    Agent 2: Privacy Compliance Checker (Rule-based)
    Redacts PII from validated sessions to ensure GDPR/privacy compliance
    """
    
    def __init__(self):
        self.name = "Agent 2: Privacy Redactor"
        self.status = "Idle"
        self.sessions_processed = 0
        self.pii_redacted = 0
        
    def hash_email(self, email: str) -> str:
        """Hash email with SHA256"""
        import hashlib
        if not email:
            return email
        return hashlib.sha256(email.encode()).hexdigest()
    
    def redact_ip(self, ip: str) -> str:
        """Generalize IP address: 192.168.1.1 -> 192.168.*.*"""
        if not ip:
            return ip
            
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.*"
        return ip
    
    def apply_redaction(self, session: Dict) -> tuple[str, str, List[str], str]:
        """
        Apply redaction rules to a session
        Returns: (redacted_email, redacted_ip, redaction_log, compliance_status)
        """
        redaction_log = []
        
        # Get original values
        original_email = session.get('user_email', '')
        original_ip = session.get('ip_address', '')
        consent_given = session.get('consent_given', 0)
        
        # Check consent status
        if not consent_given:
            # Full redaction if no consent
            redacted_email = "[REDACTED - NO CONSENT]"
            redacted_ip = "[REDACTED - NO CONSENT]"
            redaction_log.append("Full redaction: User did not provide consent")
            compliance_status = "NON_COMPLIANT"
        else:
            # Check if email is already hashed (SHA256 = 64 hex chars)
            is_hashed = len(original_email) == 64 and all(c in '0123456789abcdef' for c in original_email.lower()) if original_email else False
            
            if original_email:
                if is_hashed:
                    # Email already encrypted, keep it
                    redacted_email = original_email
                    redaction_log.append(f"Email already encrypted (SHA256): {original_email[:16]}...")
                else:
                    # Hash unencrypted email with SHA256
                    redacted_email = self.hash_email(original_email)
                    redaction_log.append(f"Email encrypted with SHA256: {original_email} → {redacted_email[:16]}...")
                    self.pii_redacted += 1
            else:
                redacted_email = None
                
            # Generalize IP
            redacted_ip = self.redact_ip(original_ip) if original_ip else None
            
            if original_ip:
                redaction_log.append(f"IP generalized: {original_ip} → {redacted_ip}")
                self.pii_redacted += 1
                
            compliance_status = "COMPLIANT"
        
        return redacted_email, redacted_ip, redaction_log, compliance_status
    
    def run(self):
        """Main agent loop - polls database for unredacted sessions"""
        print(f"🔒 {self.name} started")
        
        while True:
            try:
                # Get sessions needing redaction
                sessions = get_unredacted_sessions()
                
                if sessions:
                    self.status = f"Redacting {len(sessions)} sessions"
                    print(f"[Agent 2] Found {len(sessions)} sessions to redact")
                    
                    for session in sessions:
                        # Apply redaction
                        redacted_email, redacted_ip, redaction_log, compliance_status = self.apply_redaction(session)
                        
                        # Log result
                        print(f"[Agent 2] 🛡️  Session {session['session_id']} - {compliance_status}")
                        for log_entry in redaction_log:
                            print(f"           {log_entry}")
                        
                        # Save redacted session
                        insert_redacted_session(
                            session_id=session['session_id'],
                            email_redacted=redacted_email,
                            ip_redacted=redacted_ip,
                            event_count=1,  # Could aggregate multiple events per session
                            redaction_log=redaction_log,
                            compliance_status=compliance_status
                        )
                        
                        # Mark as processed
                        mark_validation_processed(session['id'])
                        self.sessions_processed += 1
                    
                    self.status = f"Redacted {self.sessions_processed} sessions | {self.pii_redacted} PII fields masked"
                else:
                    self.status = "Monitoring for sessions to redact..."
                
                # Poll every 3 seconds
                time.sleep(3)
                
            except Exception as e:
                print(f"[Agent 2] ❌ Error: {e}")
                self.status = f"Error: {e}"
                time.sleep(5)

def start_agent2():
    """Start Agent 2 in background thread"""
    agent = Agent2Redactor()
    agent.run()

if __name__ == "__main__":
    start_agent2()
