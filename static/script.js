// SHA256 hash function
async function sha256(message) {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
}

// Event Form Submission
document.getElementById('eventForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    let userEmail = document.getElementById('user_email').value;
    const encryptEmail = document.getElementById('encrypt_email').checked;

    // If encrypt checkbox is checked, hash the email with SHA256
    if (encryptEmail && userEmail) {
        userEmail = await sha256(userEmail);
    }

    const formData = {
        session_id: document.getElementById('session_id').value,
        user_email: userEmail,
        event_type: document.getElementById('event_type').value,
        page_url: document.getElementById('page_url').value,
        ip_address: document.getElementById('ip_address').value,
        consent_given: document.getElementById('consent_given').checked,
        encrypt_email: encryptEmail
    };

    try {
        const response = await fetch('/submit_event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        const feedback = document.getElementById('submitFeedback');
        if (result.success) {
            feedback.className = 'feedback success';
            feedback.textContent = result.message;

            // Clear form
            document.getElementById('eventForm').reset();
            document.getElementById('consent_given').checked = true;

            // Refresh event feed
            loadRecentEvents();
        } else {
            feedback.className = 'feedback error';
            feedback.textContent = 'Error: ' + result.error;
        }

        // Hide feedback after 5 seconds
        setTimeout(() => {
            feedback.style.display = 'none';
        }, 5000);

    } catch (error) {
        console.error('Error submitting event:', error);
        const feedback = document.getElementById('submitFeedback');
        feedback.className = 'feedback error';
        feedback.textContent = 'Error submitting event. Please try again.';
    }
});

// Load Recent Events
async function loadRecentEvents() {
    try {
        const response = await fetch('/api/recent_events');
        const events = await response.json();

        const feed = document.getElementById('eventFeed');

        if (events.length === 0) {
            feed.innerHTML = '<p class="placeholder">No events yet. Submit an event above to get started!</p>';
            return;
        }

        feed.innerHTML = events.map(event => `
            <div class="event-item">
                <strong>${event.event_type}</strong> - ${event.page_url}
                <br>
                <span class="time">Session: ${event.session_id} | ${new Date(event.timestamp).toLocaleTimeString()}</span>
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading events:', error);
    }
}

// Load Agent 1 Output
async function loadAgent1Output() {
    try {
        const response = await fetch('/api/agent1_output');
        const results = await response.json();

        const output = document.getElementById('agent1Output');

        if (results.length === 0) {
            output.innerHTML = '<p class="placeholder">Waiting for Agent 1 to validate events...</p>';
            return;
        }

        output.innerHTML = results.map(result => {
            const issues = JSON.parse(result.issues || '[]');
            const statusClass = result.validation_status.toLowerCase();

            return `
                <div class="output-item ${statusClass}">
                    <div class="status">${result.validation_status}: Session ${result.session_id}</div>
                    <div class="details">
                        <span class="rule">Event Type:</span> ${result.event_type || 'N/A'}<br>
                        <span class="rule">Page URL:</span> ${result.page_url || 'N/A'}<br>
                        ${issues.length > 0 ? `<span class="rule">Issues Detected:</span><br>` : ''}
                        ${issues.map(issue => `  • ${issue}`).join('<br>')}
                    </div>
                    <span class="time">${new Date(result.timestamp).toLocaleTimeString()}</span>
                </div>
            `;
        }).join('');

    } catch (error) {
        console.error('Error loading Agent 1 output:', error);
    }
}

// Load Agent 2 Output
async function loadAgent2Output() {
    try {
        const response = await fetch('/api/agent2_output');
        const results = await response.json();

        const output = document.getElementById('agent2Output');

        if (results.length === 0) {
            output.innerHTML = '<p class="placeholder">Waiting for Agent 2 to redact sessions...</p>';
            return;
        }

        output.innerHTML = results.map(result => {
            const redactionLog = JSON.parse(result.redaction_log || '[]');
            const statusClass = result.compliance_status === 'COMPLIANT' ? 'valid' : 'warning';

            return `
                <div class="output-item ${statusClass}">
                    <div class="status">${result.compliance_status}: Session ${result.session_id}</div>
                    <div class="details">
                        <span class="rule">Email Redacted:</span> ${result.user_email_redacted || 'N/A'}<br>
                        <span class="rule">IP Redacted:</span> ${result.ip_address_redacted || 'N/A'}<br>
                        ${redactionLog.length > 0 ? `<span class="rule">Redaction Actions:</span><br>` : ''}
                        ${redactionLog.map(log => `  • ${log}`).join('<br>')}
                    </div>
                    <span class="time">${new Date(result.timestamp).toLocaleTimeString()}</span>
                </div>
            `;
        }).join('');

    } catch (error) {
        console.error('Error loading Agent 2 output:', error);
    }
}

// Load Recent Insights
async function loadRecentInsights() {
    try {
        const response = await fetch('/api/recent_insights');
        const insights = await response.json();

        const feed = document.getElementById('insightFeed');

        if (insights.length === 0) {
            feed.innerHTML = '<p class="placeholder">Waiting for Agent 3 to generate insights...</p>';
            return;
        }

        feed.innerHTML = insights.map(insight => {
            const isWarning = insight.insight_text.includes('⚠️') || insight.insight_text.includes('Alert');
            return `
                <div class="insight-item ${isWarning ? 'warning' : ''}">
                    ${insight.insight_text}
                    <span class="time">${new Date(insight.timestamp).toLocaleTimeString()}</span>
                </div>
            `;
        }).join('');

    } catch (error) {
        console.error('Error loading insights:', error);
    }
}

// Update Agent Status
async function updateAgentStatus() {
    try {
        const response = await fetch('/api/agent_status');
        const status = await response.json();

        document.getElementById('agent1Status').textContent = status.agent1 || 'Not started';
        document.getElementById('agent2Status').textContent = status.agent2 || 'Not started';
        document.getElementById('agent3Status').textContent = status.agent3 || 'Not started';

    } catch (error) {
        console.error('Error updating agent status:', error);
    }
}

// Ask Agent 3
async function askAgent3() {
    const questionInput = document.getElementById('questionInput');
    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    // Add user message to chat
    addChatMessage('user', question);

    // Clear input
    questionInput.value = '';

    // Show loading
    addChatMessage('agent', 'Thinking...');

    try {
        const response = await fetch('/ask_agent3', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        const result = await response.json();

        // Remove loading message
        const chatHistory = document.getElementById('chatHistory');
        chatHistory.removeChild(chatHistory.lastChild);

        // Add agent response
        addChatMessage('agent', result.answer);

    } catch (error) {
        console.error('Error asking Agent 3:', error);

        // Remove loading message
        const chatHistory = document.getElementById('chatHistory');
        chatHistory.removeChild(chatHistory.lastChild);

        addChatMessage('agent', 'Sorry, I encountered an error. Please try again.');
    }
}

// Add message to chat history
function addChatMessage(sender, text) {
    const chatHistory = document.getElementById('chatHistory');

    // Remove placeholder if exists
    const placeholder = chatHistory.querySelector('.placeholder');
    if (placeholder) {
        placeholder.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    messageDiv.innerHTML = `<div class="message-bubble">${text}</div>`;

    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Allow Enter key to ask question
document.getElementById('questionInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        askAgent3();
    }
});

// Server-Sent Events for real-time updates
const eventSource = new EventSource('/stream');

eventSource.addEventListener('message', (e) => {
    try {
        const data = JSON.parse(e.data);

        if (data.type === 'agent_status') {
            document.getElementById('agent1Status').textContent = data.data.agent1;
            document.getElementById('agent2Status').textContent = data.data.agent2;
            document.getElementById('agent3Status').textContent = data.data.agent3;
        } else if (data.type === 'new_insight') {
            loadRecentInsights();
        }
    } catch (error) {
        console.error('Error processing SSE:', error);
    }
});

eventSource.onerror = (error) => {
    console.error('SSE connection error:', error);
};

// Periodic Updates (fallback if SSE fails)
setInterval(() => {
    loadRecentEvents();
    loadAgent1Output();
    loadAgent2Output();
    loadRecentInsights();
    updateAgentStatus();
}, 5000);

// Initial Load
window.addEventListener('load', () => {
    loadRecentEvents();
    loadAgent1Output();
    loadAgent2Output();
    loadRecentInsights();
    updateAgentStatus();
});
