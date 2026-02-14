import time
import os
from typing import Dict
from database import get_summary_stats, insert_agent_insight, get_recent_insights
from openai import OpenAI

class Agent3Insights:
    """
    Agent 3: Insight Analyst (LLM-based)
    Generates real-time insights and answers questions about clickstream data
    """
    
    def __init__(self, api_key: str = None):
        self.name = "Agent 3: Insight Analyst"
        self.status = "Initializing..."
        self.insights_generated = 0
        self.questions_answered = 0
        
        # Initialize OpenAI client
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.llm_available = True
            print(f"🧠 {self.name} initialized with OpenAI")
        else:
            self.client = None
            self.llm_available = False
            print(f"⚠️  {self.name} running in MOCK mode (no API key)")
        
        self.last_stats = None
        
    def generate_insight(self, stats: Dict) -> str:
        """Generate insight using LLM based on current statistics"""
        if not self.llm_available:
            # Mock insight for demo without API key
            if stats['issues_detected'] > 0:
                return f"⚠️ Alert: {stats['issues_detected']} data quality issues detected. Agent 2 is processing these sessions for compliance."
            return f"✅ System healthy: {stats['total_events']} events processed, {stats['consent_percentage']}% with consent."
        
        try:
            prompt = f"""You are an analytics assistant monitoring a clickstream data pipeline that processes data collected from web analytics (which may or may not have explicit user consent).

Current Statistics:
- Total events processed: {stats['total_events']}
- Events with user consent: {stats['consent_count']} ({stats['consent_percentage']}%)
- Sessions redacted for privacy: {stats['redacted_count']}
- Data quality issues detected: {stats['issues_detected']}

Context: This system demonstrates privacy-preserving data processing. Events without consent are automatically redacted by Agent 2 (Privacy Redactor) to ensure compliance.

Generate a brief, factual insight (1-2 sentences) about the current state. Focus on:
- How the privacy system is working (redaction happening correctly)
- Data quality observations
- System health

Do NOT recommend implementing consent collection - the system is designed to handle data with or without consent through automatic redaction. Use emojis for visual clarity."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"[Agent 3] LLM Error: {e}")
            return f"⚠️ Monitoring {stats['total_events']} events ({stats['consent_percentage']}% consent rate)"
    
    def answer_question(self, question: str, stats: Dict) -> str:
        """Answer user question using LLM"""
        if not self.llm_available:
            # Mock responses for demo
            if "consent" in question.lower():
                return f"Based on current data: {stats['consent_percentage']}% of users ({stats['consent_count']} out of {stats['total_events']}) have provided consent."
            elif "issue" in question.lower() or "problem" in question.lower():
                return f"Currently tracking {stats['issues_detected']} data quality issues that Agent 1 has flagged."
            else:
                return f"I'm monitoring {stats['total_events']} events. {stats['redacted_count']} sessions have been redacted for privacy compliance."
        
        try:
            prompt = f"""You are an analytics assistant monitoring a privacy-preserving clickstream data pipeline.

Current Statistics:
- Total events: {stats['total_events']}
- Events with consent: {stats['consent_count']} ({stats['consent_percentage']}%)
- Redacted sessions: {stats['redacted_count']}
- Issues detected: {stats['issues_detected']}

Context: This system processes clickstream data (which may or may not have user consent). Agent 2 automatically redacts PII from events without consent to ensure privacy compliance.

Question: {question}

Provide a clear, factual answer with specific numbers from the data. Focus on how the privacy system is working, not on suggesting consent collection improvements."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            self.questions_answered += 1
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"[Agent 3] LLM Error: {e}")
            return f"Error processing question. Current stats: {stats['total_events']} events, {stats['consent_percentage']}% consent rate."
    
    def should_generate_insight(self, current_stats: Dict) -> bool:
        """Determine if we should generate a new insight"""
        if not self.last_stats:
            return True
            
        # Generate insight if issues increased
        if current_stats['issues_detected'] > self.last_stats.get('issues_detected', 0):
            return True
            
        # Generate insight if total events increased by 5+
        if current_stats['total_events'] - self.last_stats.get('total_events', 0) >= 5:
            return True
            
        return False
    
    def run(self):
        """Main agent loop - monitors statistics and generates insights"""
        print(f"🧠 {self.name} started")
        self.status = "Monitoring data pipeline..."
        
        while True:
            try:
                # Get current statistics
                stats = get_summary_stats()
                
                # Check if we should generate an insight
                if self.should_generate_insight(stats) and stats['total_events'] > 0:
                    self.status = "Generating insight..."
                    print(f"[Agent 3] 💡 Generating insight...")
                    
                    insight_text = self.generate_insight(stats)
                    
                    # Save insight
                    insert_agent_insight(
                        insight_type="REAL_TIME",
                        insight_text=insight_text,
                        related_sessions=None
                    )
                    
                    self.insights_generated += 1
                    print(f"[Agent 3] {insight_text}")
                    
                    self.last_stats = stats.copy()
                
                self.status = f"Monitoring | {self.insights_generated} insights generated"
                
                # Poll every 10 seconds (less frequent than other agents)
                time.sleep(10)
                
            except Exception as e:
                print(f"[Agent 3] ❌ Error: {e}")
                self.status = f"Error: {e}"
                time.sleep(10)

def start_agent3(api_key: str = None):
    """Start Agent 3 in background thread"""
    agent = Agent3Insights(api_key=api_key)
    agent.run()

if __name__ == "__main__":
    start_agent3()
