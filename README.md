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
