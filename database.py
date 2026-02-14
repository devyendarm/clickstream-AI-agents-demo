import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

DB_NAME = "clickstream.db"

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with all required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table 1: Raw events from web form
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_email TEXT,
            event_type TEXT NOT NULL,
            page_url TEXT,
            ip_address TEXT,
            consent_given BOOLEAN DEFAULT 1,
            encrypt_email BOOLEAN DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            processed_by_agent1 BOOLEAN DEFAULT 0
        )
    """)
    
    # Table 2: Agent 1 validation results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS validation_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            session_id TEXT,
            validation_status TEXT,
            issues TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            processed_by_agent2 BOOLEAN DEFAULT 0,
            FOREIGN KEY (event_id) REFERENCES raw_events(id)
        )
    """)
    
    # Table 3: Agent 2 redacted sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS redacted_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_email_redacted TEXT,
            ip_address_redacted TEXT,
            event_count INTEGER,
            redaction_log TEXT,
            compliance_status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table 4: Agent 3 insights
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            insight_type TEXT,
            insight_text TEXT,
            related_session_ids TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

def insert_event(session_id: str, user_email: str, event_type: str, 
                 page_url: str, ip_address: str, consent_given: bool, encrypt_email: bool = False) -> int:
    """Insert a new clickstream event"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO raw_events (session_id, user_email, event_type, page_url, ip_address, consent_given, encrypt_email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, user_email, event_type, page_url, ip_address, consent_given, encrypt_email))
    
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return event_id

def get_unprocessed_events() -> List[Dict]:
    """Get events not yet processed by Agent 1"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM raw_events 
        WHERE processed_by_agent1 = 0
        ORDER BY timestamp ASC
    """)
    
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return events

def mark_event_processed(event_id: int):
    """Mark event as processed by Agent 1"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE raw_events 
        SET processed_by_agent1 = 1 
        WHERE id = ?
    """, (event_id,))
    
    conn.commit()
    conn.close()

def insert_validation_result(event_id: int, session_id: str, status: str, issues: List[str]):
    """Insert Agent 1 validation result"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO validation_results (event_id, session_id, validation_status, issues)
        VALUES (?, ?, ?, ?)
    """, (event_id, session_id, status, json.dumps(issues)))
    
    conn.commit()
    conn.close()

def get_unredacted_sessions() -> List[Dict]:
    """Get validation results not yet processed by Agent 2"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT vr.*, re.user_email, re.ip_address, re.consent_given
        FROM validation_results vr
        JOIN raw_events re ON vr.event_id = re.id
        WHERE vr.processed_by_agent2 = 0
        ORDER BY vr.timestamp ASC
    """)
    
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sessions

def mark_validation_processed(validation_id: int):
    """Mark validation result as processed by Agent 2"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE validation_results 
        SET processed_by_agent2 = 1 
        WHERE id = ?
    """, (validation_id,))
    
    conn.commit()
    conn.close()

def insert_redacted_session(session_id: str, email_redacted: str, ip_redacted: str, 
                            event_count: int, redaction_log: List[str], compliance_status: str):
    """Insert Agent 2 redacted session"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO redacted_sessions 
        (session_id, user_email_redacted, ip_address_redacted, event_count, redaction_log, compliance_status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, email_redacted, ip_redacted, event_count, json.dumps(redaction_log), compliance_status))
    
    conn.commit()
    conn.close()

def insert_agent_insight(insight_type: str, insight_text: str, related_sessions: Optional[List[str]] = None):
    """Insert Agent 3 insight"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO agent_insights (insight_type, insight_text, related_session_ids)
        VALUES (?, ?, ?)
    """, (insight_type, insight_text, json.dumps(related_sessions) if related_sessions else None))
    
    conn.commit()
    conn.close()

def get_summary_stats() -> Dict:
    """Get aggregated statistics for Agent 3"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total events
    cursor.execute("SELECT COUNT(*) as count FROM raw_events")
    total_events = cursor.fetchone()['count']
    
    # Events with consent
    cursor.execute("SELECT COUNT(*) as count FROM raw_events WHERE consent_given = 1")
    consent_count = cursor.fetchone()['count']
    
    # Redacted sessions
    cursor.execute("SELECT COUNT(*) as count FROM redacted_sessions")
    redacted_count = cursor.fetchone()['count']
    
    # Validation issues
    cursor.execute("SELECT COUNT(*) as count FROM validation_results WHERE validation_status != 'VALID'")
    issues_count = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'total_events': total_events,
        'consent_count': consent_count,
        'redacted_count': redacted_count,
        'issues_detected': issues_count,
        'consent_percentage': round((consent_count / total_events * 100) if total_events > 0 else 0, 1)
    }

def get_recent_events(limit: int = 10) -> List[Dict]:
    """Get recent events for dashboard"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM raw_events 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return events

def get_recent_insights(limit: int = 5) -> List[Dict]:
    """Get recent Agent 3 insights"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM agent_insights 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    
    insights = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return insights

if __name__ == "__main__":
    init_db()
