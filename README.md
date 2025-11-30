# GlassBox - AI-Powered Technical Interview Auditor

🧠 **Real-time candidate evaluation system** that monitors coding activity, analyzes verbal explanations, and generates comprehensive session reports.

## 🎯 Features

- **Real-Time Audio Transcription**: Captures candidate's spoken explanations during coding
- **AI-Powered Analysis**: OpenAI GPT evaluates coherence, terminology, and completeness
- **Activity Monitoring**: Tracks CODING, RESEARCHING, and IDLE states
- **Interactive Dashboard**: Streamlit-based UI with live session metrics
- **Session Recording**: Full audio + transcript saved for review

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows OS (for window tracking)
- Microphone (WO Mic recommended)
- OpenAI API Key

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd IMPAD

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Application

**Option 1: Dashboard (Recommended)**
```bash
streamlit run src/dashboard/dashboard_app.py --server.port 8502
```
Then:
1. Open http://localhost:8502
2. Login as Guest
3. Start Interview
4. Speak while coding
5. Submit solution

**Option 2: CLI Mode**
```bash
python src/main.py
```

## 📊 How It Works

```
┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│ Audio Input  │─────→│  Cognitive  │─────→│   Session    │
│  (Voice)     │      │   Engine    │      │    Logger    │
└──────────────┘      └─────────────┘      └──────────────┘
                              │                    │
                              ↓                    ↓
┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│  Activity    │─────→│ Real-time   │←─────│ Dashboard UI │
│  Monitor     │      │  Analysis   │      │  (Streamlit) │
└──────────────┘      └─────────────┘      └──────────────┘
```

## 🔧 Configuration

Edit `.env`:
```bash
# LLM Mode: "real" for OpenAI API, "fake" for demo
LLM_MODE=real

# Your OpenAI API Key
OPENAI_API_KEY=sk-...

# Model
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.3

# Debug mode
DEBUG=False
```

## 📁 Project Structure

```
IMPAD/
├── src/
│   ├── core/            # Session logic & models
│   ├── sensors/         # Activity & Audio monitoring
│   ├── cognitive/       # AI analysis engine
│   └── dashboard/       # Streamlit UI
├── data/                # Session logs & transcripts
├── docs/                # Documentation
├── submissions/         # User submissions
├── main.py              # Entry point
└── requirements.txt
```

## 🎨 Dashboard Features

- **🎯 Challeng

es Tab**: Start interview, write code in browser
- **📊 Live Audit Tab**: Real-time metrics, timeline, clarity scores
- **👤 Mock Authentication**: Simulated user login
- **💾 Code Submission**: Integrated code editor with auto-save

## 🧪 Testing

Run a quick demo:
```bash
python -c "from SessionLogger import SessionLogger; logger = SessionLogger('test'); logger.log_state('CODING'); logger.finish_session(80, 70, 'PASS'); print('Demo complete!')"
```

## 📝 Sample Output

```json
{
  "session_id": "abc-123",
  "candidate_id": "hacker_007",
  "started_at": 1764456249.138,
  "events": [
    {"ts": 0.0, "type": "STATE", "payload": {"state": "RESEARCHING"}},
    {"ts": 15.2, "type": "CLARITY", "payload": {
      "coherence": 70,
      "terminology": 80,
      "completeness": 60,
      "comment": "Good technical explanation with minor gaps."
    }}
  ],
  "ended_at": 1764456300.456,
  "summary": {
    "hard_score": 80,
    "soft_score": 70,
    "verdict": "PASS"
  }
}
```

## 🛠️ Troubleshooting

**Audio not recording:**
- Check microphone device in `audio_listener.py`
- Ensure "WO Mic" is connected
- Try running `python check_audio_devices.py`

**Dashboard not loading:**
- Refresh browser (F5)
- Check Streamlit is running on port 8502
- Look for errors in terminal

**AI giving all zeros:**
- Speak for at least 5-10 seconds
- Use technical language (e.g., "I'm implementing bcrypt hashing...")
- Check OPENAI_API_KEY in `.env`

## 👥 Team

Developed for **megabrAIns Hackathon 2025**

## 📜 License

MIT License - feel free to use and modify!
# 🧊 GlassBox: The AI-Powered Recruitment Protocol
> "Don’t judge the code. Judge the coder."

---

## 🚨 The Problem: The "Black Box" of Hiring
In the era of ChatGPT and Copilot, the final code proves nothing. 
* Did the candidate write it, or generate it? 
* Do they understand the logic, or did they just get lucky?
* Recruiters waste hundreds of hours on interviews to find out what GlassBox reveals in 3 minutes.

## 💡 The Solution: Process Audit
GlassBox is an automated exam environment that makes the candidate's thinking process visible, measurable, and verifiable. We introduce Vocal Coding protocols combined with sensor fusion to evaluate potential, not just syntax.

---

## ⚙️ How It Works

GlassBox replaces the "silent test task" with a transparent session:

1.  🎙️ Vocal Coding: The candidate solves the task while "thinking aloud." The Cognitive Engine analyzes their speech for logic, clarity, and terminology.
2.  👁️ Work Patterns (Sensors): We track the active environment. Is the candidate coding in the IDE or researching in the Browser?.
3.  🧠 AI Cross-Check: The system correlates Speech (Plan) vs Action (Code). 
    * *Example:* Candidate says "I'll fix the loop" -> Candidate actually edits the loop -> High Consistency Score.
4.  🔒 Proof of Skill: The session is hashed (SHA-256). A PDF Certificate is generated, guaranteeing the result cannot be faked.

---

## 📊 The Dashboard (What Recruiters See)

No more watching 1-hour videos. The recruiter gets a **Smart Dashboard**

### 1. The Timeline (X-Ray Vision)
A visual bar showing the exact flow of the session:
* 🟢 CODING
* 🟡 RESEARCHING (Google/StackOverflow)
* ⚪ IDLE (Stuck/Thinking)

### 2. Key Metrics
| Metric | Description | Source |
| :--- | :--- | :--- |
| 🧠 Clarity Score | Coherence, terminology, and completeness of the explanation. | LLM Analysis |
| 🛠️ Hard Score | Balance between independent coding and external research. | Window Sensor |
| ⚖️ Verdict | Math-based PASS / FAIL recommendation. | Aggregated Data |

---

## 💰 Business Value

### For Companies (B2B)
* Scale: Screen 1,000 candidates overnight without burning Senior Engineer hours.
* Safety: Filter out "ChatGPT-coders" before the first interview.
* Cost: The cost of one GlassBox report is <1% of the cost of a bad hire.

### For Candidates
* Fairness: Get credit for your *thought process*, even if the code isn't perfect.
* Asset: Receive a blockchain-ready Certificate with your Hard/Soft scores to prove your skills to any employer.

---

## 🛠️ Architecture & Tech Stack

The project is built by a cross-functional team, delivering a complete MVP in 24 hours.

*👤 Role 1 (Core):** Orchestrator, JSON Schema Contract, SessionLogger. 
*👤 Role 2 (AI):** Cognitive Engine (LLM Integration), Clarity Analysis.
*👤 Role 3 (Sensors):** Active Window Monitoring, Threading, Pattern Recognition. 
*👤 Role 4 (UI):** Streamlit Dashboard, Plotly Visualization.
*👤 Role 5 (Product):** PDF Generation, Hashing, Business Logic.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.9+
* OpenAI API Key

###

