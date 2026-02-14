# Clickstream Agent System - Privacy-First Demo

A real-time, multi-agent system demonstrating privacy-preserving clickstream data processing with AI-powered insights.

## 🎯 Overview

This system showcases agent-to-agent interaction for clickstream analytics with built-in privacy compliance:

- **Agent 1 (Data Validator)**: Rule-based validation for data quality and compliance
- **Agent 2 (Privacy Redactor)**: PII protection with SHA256 email hashing and IP generalization
- **Agent 3 (Insight Analyst)**: LLM-powered real-time insights (OpenAI)

## ✨ Key Features

- ✅ **Privacy-First Design**: Only consented, encrypted events allowed
- 🔒 **SHA256 Email Encryption**: Client-side email hashing
- 🤖 **3-Agent Architecture**: Validation → Redaction → Insights
- 📊 **Real-time Dashboard**: Live event feed, agent status, and insights
- 💬 **Interactive Q&A**: Ask Agent 3 questions about your data
- 🔐 **Compliance Enforcement**: GDPR/CCPA-style consent validation

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key (optional, has mock mode)

### Local Setup

```bash
# Clone repository
git clone <your-repo-url>
cd AI-Agents-Agents

# Install dependencies
pip install -r requirements.txt

# (Optional) Set OpenAI API key
echo "OPENAI_API_KEY=your-key-here" > .env

# Run application
python app.py
```

Open browser: `http://localhost:5000`

## ☁️ Azure Deployment

See deployment guides:
- **[Azure VM Deployment](AZURE_VM_DEPLOYMENT.md)** - Direct code files (recommended for demos)
- **[Azure Container Instances](AZURE_DEPLOYMENT_UI.md)** - Docker-based deployment

## 🏗️ Architecture

```
User Form → Agent 1 (Validate) → Agent 2 (Redact) → Agent 3 (Insights) → Dashboard
              ↓                      ↓                    ↓
         SQLite DB            SQLite DB            SQLite DB
```

### Data Flow

1. **Event Submission**: User submits clickstream event with consent & encrypted email
2. **Agent 1**: Validates required fields, consent, and email encryption
3. **Agent 2**: Applies SHA256 hashing (if needed) and IP generalization
4. **Agent 3**: Generates insights from aggregated, anonymized data
5. **Dashboard**: Displays real-time agent activity and validation details

## 🔒 Privacy & Compliance

### Two Critical Rules Enforced:

1. **Consent Required**: Events without user consent are flagged as compliance violations
2. **Email Encryption**: Only SHA256-hashed emails are accepted

### Agent 1 Validation:
- ❌ No consent → `COMPLIANCE VIOLATION`
- ❌ Unencrypted email → `SECURITY VIOLATION`
- ✅ Valid event → Passes to Agent 2

### Agent 2 Redaction:
- If consent given: Applies SHA256 to emails, generalizes IPs
- If no consent: Full redaction `[REDACTED - NO CONSENT]`

### Agent 3 Insights:
- **Never sees raw PII** - only aggregated statistics
- Generates insights on data quality and privacy compliance

## 📁 Project Structure

```
AI-Agents-Agents/
├── app.py                      # Flask application & agent orchestration
├── database.py                 # SQLite schema & helper functions
├── agents/
│   ├── agent1_validator.py     # Data validation agent
│   ├── agent2_redactor.py      # Privacy redaction agent
│   └── agent3_insights.py      # LLM insights agent
├── templates/
│   └── index.html              # Dashboard UI
├── static/
│   ├── style.css               # Styling
│   └── script.js               # Frontend logic
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container image
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## 🧪 Testing the System

### Test Case 1: Valid Event (Consent + Encrypted Email)
1. Check "User gave consent (Required)"
2. Check "Encrypt Email"
3. Submit event
4. **Expected**: Agent 1 validates ✅, Agent 2 keeps hash, Agent 3 generates insights

### Test Case 2: No Consent
1. Uncheck "User gave consent"
2. Submit event
3. **Expected**: Agent 1 flags `COMPLIANCE VIOLATION`, Agent 2 fully redacts

### Test Case 3: Unencrypted Email
1. Check consent, but uncheck "Encrypt Email"
2. Submit event
3. **Expected**: Agent 1 flags `SECURITY VIOLATION`, Agent 2 applies SHA256

## 🛠️ Configuration

### Environment Variables

Create `.env` file:
```bash
OPENAI_API_KEY=your-openai-api-key  # Optional, uses mock mode if not set
```

### Database

SQLite database (`clickstream.db`) is auto-created on first run with schema:
- `raw_events` - Incoming clickstream events
- `validation_results` - Agent 1 validation logs
- `redacted_sessions` - Agent 2 redacted data
- `agent_insights` - Agent 3 generated insights

## 📊 Dashboard Features

- **Live Event Feed**: Real-time clickstream events
- **Agent Status**: Current activity of all 3 agents
- **Agent 1 Details**: Validation rules and issues detected
- **Agent 2 Details**: Redaction actions and compliance status
- **Real-time Insights**: Auto-generated business insights
- **Ask Agent 3**: Interactive Q&A with the LLM

## 🔧 Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite
- **LLM**: OpenAI GPT-4
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Real-time**: Server-Sent Events (SSE)

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built as a demonstration of privacy-preserving AI agents for clickstream analytics.**
