from flask import Flask, render_template, request, jsonify, Response
import threading
import time
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import database functions
from database import (
    init_db, insert_event, get_recent_events, 
    get_recent_insights, get_summary_stats,
    get_connection
)

# Import agents
from agents.agent1_validator import Agent1Validator
from agents.agent2_redactor import Agent2Redactor
from agents.agent3_insights import Agent3Insights

app = Flask(__name__)

# Global agent instances
agent1 = None
agent2 = None
agent3 = None

# Agent status tracking
agent_status = {
    'agent1': 'Starting...',
    'agent2': 'Starting...',
    'agent3': 'Starting...'
}

def run_agent1():
    """Run Agent 1 in background thread"""
    global agent1, agent_status
    agent1 = Agent1Validator()
    while True:
        try:
            agent1.run()
        except Exception as e:
            agent_status['agent1'] = f"Error: {e}"
            time.sleep(5)

def run_agent2():
    """Run Agent 2 in background thread"""
    global agent2, agent_status
    agent2 = Agent2Redactor()
    while True:
        try:
            agent2.run()
        except Exception as e:
            agent_status['agent2'] = f"Error: {e}"
            time.sleep(5)

def run_agent3():
    """Run Agent 3 in background thread"""
    global agent3, agent_status
    api_key = os.getenv('OPENAI_API_KEY')
    agent3 = Agent3Insights(api_key=api_key)
    while True:
        try:
            agent3.run()
        except Exception as e:
            agent_status['agent3'] = f"Error: {e}"
            time.sleep(10)

@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('index.html')

@app.route('/submit_event', methods=['POST'])
def submit_event():
    """Handle event submission from web form"""
    try:
        data = request.json
        
        # Insert event into database
        event_id = insert_event(
            session_id=data.get('session_id'),
            user_email=data.get('user_email'),
            event_type=data.get('event_type'),
            page_url=data.get('page_url'),
            ip_address=data.get('ip_address'),
            consent_given=data.get('consent_given', False),
            encrypt_email=data.get('encrypt_email', False)
        )
        
        return jsonify({
            'success': True,
            'event_id': event_id,
            'message': 'Event submitted! Watch agents react below...'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/stats')
def get_stats():
    """Get current statistics"""
    try:
        stats = get_summary_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent_events')
def recent_events():
    """Get recent events"""
    try:
        events = get_recent_events(limit=10)
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent_insights')
def recent_insights():
    """Get recent Agent 3 insights"""
    try:
        insights = get_recent_insights(limit=5)
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agent_status')
def get_agent_status():
    """Get current status of all agents"""
    try:
        status = {
            'agent1': agent1.status if agent1 else 'Not started',
            'agent2': agent2.status if agent2 else 'Not started',
            'agent3': agent3.status if agent3 else 'Not started'
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agent1_output')
def get_agent1_output():
    """Get Agent 1 validation results"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT vr.*, re.session_id, re.event_type, re.page_url
            FROM validation_results vr
            JOIN raw_events re ON vr.event_id = re.id
            ORDER BY vr.timestamp DESC
            LIMIT 10
        """)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agent2_output')
def get_agent2_output():
    """Get Agent 2 redaction results"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM redacted_sessions
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask_agent3', methods=['POST'])
def ask_agent3():
    """Ask Agent 3 a question"""
    try:
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Get current stats
        stats = get_summary_stats()
        
        # Get answer from Agent 3
        if agent3:
            answer = agent3.answer_question(question, stats)
        else:
            answer = "Agent 3 is not yet initialized."
        
        return jsonify({
            'question': question,
            'answer': answer
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stream')
def stream():
    """Server-Sent Events endpoint for real-time updates"""
    def event_stream():
        while True:
            try:
                # Send agent status updates
                status = {
                    'agent1': agent1.status if agent1 else 'Not started',
                    'agent2': agent2.status if agent2 else 'Not started',
                    'agent3': agent3.status if agent3 else 'Not started'
                }
                yield f"data: {json.dumps({'type': 'agent_status', 'data': status})}\n\n"
                
                # Send latest insight
                insights = get_recent_insights(limit=1)
                if insights:
                    yield f"data: {json.dumps({'type': 'new_insight', 'data': insights[0]})}\n\n"
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Stream error: {e}")
                time.sleep(5)
    
    return Response(event_stream(), mimetype='text/event-stream')

def start_agents():
    """Start all agents in background threads"""
    print("🚀 Starting all agents...")
    
    # Start Agent 1
    thread1 = threading.Thread(target=run_agent1, daemon=True)
    thread1.start()
    
    # Start Agent 2
    thread2 = threading.Thread(target=run_agent2, daemon=True)
    thread2.start()
    
    # Start Agent 3
    thread3 = threading.Thread(target=run_agent3, daemon=True)
    thread3.start()
    
    print("✅ All agents started in background threads")

if __name__ == '__main__':
    # Initialize database
    print("📊 Initializing database...")
    init_db()
    
    # Start agents
    start_agents()
    
    # Start Flask app
    print("🌐 Starting Flask web server...")
    print("📍 Open http://localhost:5000 in your browser")
    app.run(debug=True, threaded=True, use_reloader=False)
